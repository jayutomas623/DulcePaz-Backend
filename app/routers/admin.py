"""
Router para el Panel Administrativo de Gestión Clínica (/admin).
Asignado a: COLABORADOR 2
Protegido por Supabase Auth / Security Bearer token.
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.core.security import get_current_admin_user
from app.schemas.admin import (
    BookingStatusUpdate,
    ScheduleBlockCreate,
    BlockedScheduleResponse,
    AdminBookingItem,
    AgendaResponse,
)
from app.database import (
    get_agenda_bookings,
    update_booking_status_in_db,
    save_schedule_block,
    get_blocked_schedules,
    delete_schedule_block,
)

logger = logging.getLogger("dulcepaz.routers.admin")

router = APIRouter(prefix="/admin", tags=["Administración Clínica"])


@router.get(
    "/agenda",
    response_model=AgendaResponse,
    summary="Consultar agenda clínica consolidada o por terapeuta",
    description="Devuelve las citas agendadas filtradas por fecha y terapeuta. Requiere autenticación de administrador o terapeuta.",
    response_model_by_alias=True
)
async def get_therapist_agenda(
    date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Fecha AAAA-MM-DD"),
    therapist_id: Optional[str] = Query(None, alias="therapistId", description="ID del terapeuta o 'all'"),
    current_user: dict = Depends(get_current_admin_user)
):
    # Si el usuario es un terapeuta específico y no es admin global, se puede filtrar a su ID
    query_therapist = therapist_id
    if not query_therapist and current_user.get("role") != "admin":
        # Extraer posible ID del email del terapeuta (ej. nikki@dulcepaz.com -> nikki-paz)
        email = current_user.get("email", "").lower()
        if "nikki" in email:
            query_therapist = "nikki-paz"
        elif "keila" in email:
            query_therapist = "keila-vilar"
        elif "william" in email:
            query_therapist = "william-mendoza"

    raw_appointments = get_agenda_bookings(date_str=date, therapist_id=query_therapist)

    appointments_list = [
        AdminBookingItem(**apt) for apt in raw_appointments
    ]

    return AgendaResponse(
        date=date,
        therapistId=query_therapist,
        total=len(appointments_list),
        appointments=appointments_list,
        user=current_user
    )


@router.patch(
    "/bookings/{booking_id}/status",
    summary="Actualizar estado de una cita clínica",
    description="Permite marcar la cita como confirmed, completed, cancelled_by_patient o no_show. Requiere autenticación."
)
async def update_booking_status(
    booking_id: str,
    payload: BookingStatusUpdate,
    current_user: dict = Depends(get_current_admin_user)
):
    updated = update_booking_status_in_db(
        booking_id=booking_id,
        new_status=payload.status,
        admin_notes=payload.admin_notes
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cita con ID o referencia '{booking_id}' no encontrada."
        )

    logger.info(
        f"[ADMIN] Cita {booking_id} actualizada a {payload.status} por {current_user.get('email', 'admin')}"
    )

    return {
        "booking_id": booking_id,
        "status": payload.status,
        "admin_notes": payload.admin_notes,
        "updated_by": current_user.get("email", "admin"),
        "message": f"Estado actualizado exitosamente a '{payload.status}'."
    }


@router.post(
    "/blocked-schedules",
    response_model=BlockedScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bloquear franja horaria manualmente",
    description="Inhabilita un slot para un terapeuta y fecha dada, impidiendo reservas desde el agendador web.",
    response_model_by_alias=True
)
async def create_blocked_schedule(
    payload: ScheduleBlockCreate,
    current_user: dict = Depends(get_current_admin_user)
):
    block_record = save_schedule_block(
        therapist_id=payload.therapist_id,
        date_str=payload.date,
        time_slot=payload.time_slot,
        reason=payload.reason
    )
    return BlockedScheduleResponse(**block_record)


@router.post(
    "/schedules/block",
    response_model=BlockedScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Alias de bloqueo de horario (compatibilidad)",
    include_in_schema=False
)
async def block_schedule_slot_alias(
    payload: ScheduleBlockCreate,
    current_user: dict = Depends(get_current_admin_user)
):
    """Ruta alias para compatibilidad retroactiva."""
    return await create_blocked_schedule(payload, current_user)


@router.get(
    "/blocked-schedules",
    response_model=List[BlockedScheduleResponse],
    summary="Listar horarios bloqueados",
    description="Obtiene las franjas horarias inhabilitadas con filtros opcionales por terapeuta y fecha.",
    response_model_by_alias=True
)
async def list_blocked_schedules(
    therapist_id: Optional[str] = Query(None, alias="therapistId"),
    date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    current_user: dict = Depends(get_current_admin_user)
):
    blocks = get_blocked_schedules(therapist_id=therapist_id, date_str=date)
    return [BlockedScheduleResponse(**b) for b in blocks]


@router.delete(
    "/blocked-schedules/{block_id}",
    summary="Eliminar bloqueo de horario",
    description="Desbloquea una franja horaria previamente inhabilitada, volviendo a dejarla disponible en el agendador público."
)
async def delete_blocked_schedule_endpoint(
    block_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    success = delete_schedule_block(block_id)
    return {
        "status": "deleted",
        "id": block_id,
        "message": "Franja horaria desbloqueada exitosamente."
    }

