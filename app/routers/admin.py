"""
Router para el Panel Administrativo de Gestión Clínica (/admin).
Asignado a: COLABORADOR 2
Protegido por Supabase Auth / Security Bearer token.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_admin_user
from app.schemas.admin import BookingStatusUpdate, ScheduleBlockCreate

router = APIRouter(prefix="/admin", tags=["Administración Clínica"])


@router.get(
    "/agenda",
    summary="Obtener agenda del terapeuta autenticado",
    description="Endpoint asignado al Colaborador 2. Devuelve las citas asignadas al especialista autenticado con filtros por fecha."
)
async def get_therapist_agenda(
    current_user: dict = Depends(get_current_admin_user)
):
    # TODO [COLABORADOR 2]:
    # Consultar citas asignadas a current_user['sub'] o email en Supabase
    return {
        "user": current_user,
        "message": "Agenda clínica institucional",
        "appointments": []
    }


@router.patch(
    "/bookings/{booking_id}/status",
    summary="Actualizar estado de una cita clínica",
    description="Endpoint asignado al Colaborador 2. Permite marcar la cita como Confirmada, Completada, Cancelada o No asistió."
)
async def update_booking_status(
    booking_id: str,
    payload: BookingStatusUpdate,
    current_user: dict = Depends(get_current_admin_user)
):
    # TODO [COLABORADOR 2]:
    # Actualizar estado en la tabla 'bookings' en Supabase
    return {
        "booking_id": booking_id,
        "status": payload.status,
        "admin_notes": payload.admin_notes,
        "updated_by": current_user["email"]
    }


@router.post(
    "/schedules/block",
    summary="Bloquear horario por motivos personales/académicos",
    description="Endpoint asignado al Colaborador 2. Inserta un registro en 'blocked_schedules' para inhabilitar el slot en el wizard público."
)
async def block_schedule_slot(
    payload: ScheduleBlockCreate,
    current_user: dict = Depends(get_current_admin_user)
):
    # TODO [COLABORADOR 2]:
    # Insertar en 'blocked_schedules' en Supabase
    return {
        "therapist_id": payload.therapist_id,
        "date": payload.date,
        "time_slot": payload.time_slot,
        "status": "blocked",
        "message": "Franja horaria bloqueada exitosamente."
    }
