"""
Router para cálculo y consulta de disponibilidad de horarios en tiempo real.
Asignado a: COLABORADOR 2
Zona Horaria Oficial: America/La_Paz (GMT-4).
"""

import logging
from typing import List
from datetime import datetime, date
from fastapi import APIRouter, Query, HTTPException, status
from app.schemas.booking import DayAvailabilityResponse, TimeSlot
from app.database import (
    THERAPISTS_CATALOG,
    STANDARD_TIME_SLOTS,
    get_booked_and_blocked_slots,
    is_slot_booked_or_blocked,
)

logger = logging.getLogger("dulcepaz.routers.availability")

router = APIRouter(prefix="/availability", tags=["Disponibilidad de Horarios"])


@router.get(
    "/slots",
    response_model=DayAvailabilityResponse,
    summary="Consultar franjas horarias disponibles para un día y especialista",
    description="Calcula en tiempo real las franjas horarias disponibles. Bloquea domingos, fechas pasadas y cruza con las tablas bookings y blocked_schedules de Supabase.",
    response_model_by_alias=True
)
async def get_available_slots(
    date_str: str = Query(..., alias="date", pattern=r"^\d{4}-\d{2}-\d{2}$", description="Fecha AAAA-MM-DD"),
    therapist_id: str = Query(..., alias="therapistId", description="ID del especialista (ej. 'nikki-paz') o 'any'")
):
    # 1. Validar validez de la fecha
    try:
        query_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fecha inválida. Use formato AAAA-MM-DD"
        )

    # 2. Excluir domingos (el centro permanece cerrado)
    if query_date.weekday() == 6:
        return DayAvailabilityResponse(
            date=date_str,
            therapistId=therapist_id,
            slots=[],
            timezone="America/La_Paz"
        )

    # 3. Comprobar si la fecha es pasada
    today = date.today()
    is_past_date = query_date < today

    # 4. Cálculo de slots según terapeuta seleccionado
    slots: List[TimeSlot] = []

    if is_past_date:
        # Fechas pasadas no permiten agendamiento
        slots = [TimeSlot(time=s, isAvailable=False) for s in STANDARD_TIME_SLOTS]
    elif therapist_id == "any":
        # Para "any", un slot está libre si al menos UN terapeuta del centro tiene ese horario libre
        all_therapist_ids = list(THERAPISTS_CATALOG.keys())
        for slot in STANDARD_TIME_SLOTS:
            has_free_therapist = any(
                not is_slot_booked_or_blocked(tid, date_str, slot)
                for tid in all_therapist_ids
            )
            slots.append(TimeSlot(time=slot, isAvailable=has_free_therapist))
    else:
        # Para un terapeuta específico, consultar citas activas y bloqueos manuales
        occupied_slots = get_booked_and_blocked_slots(therapist_id, date_str)
        for slot in STANDARD_TIME_SLOTS:
            is_avail = slot not in occupied_slots
            slots.append(TimeSlot(time=slot, isAvailable=is_avail))

    return DayAvailabilityResponse(
        date=date_str,
        therapistId=therapist_id,
        slots=slots,
        timezone="America/La_Paz"
    )

