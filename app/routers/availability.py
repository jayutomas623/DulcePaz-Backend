"""
Router para cálculo y consulta de disponibilidad de horarios en tiempo real.
Asignado a: COLABORADOR 2
Zona Horaria Oficial: America/La_Paz (GMT-4).
"""

from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Query
from app.schemas.booking import DayAvailabilityResponse, TimeSlot

router = APIRouter(prefix="/availability", tags=["Disponibilidad de Horarios"])

# Horarios estándar de consulta definidos en el informe técnico
STANDARD_SLOTS = ["09:00", "10:30", "14:30", "16:00", "17:30"]


@router.get(
    "/slots",
    response_model=DayAvailabilityResponse,
    summary="Consultar franjas horarias disponibles para un día y especialista",
    description="Endpoint asignado al Colaborador 2. Consulta en Supabase las citas agendadas y los bloqueos manuales del terapeuta en la fecha seleccionada para retornar los slots habilitados y ocupados."
)
async def get_available_slots(
    date_str: str = Query(..., alias="date", pattern=r"^\d{4}-\d{2}-\d{2}$", description="Fecha AAAA-MM-DD"),
    therapist_id: str = Query(..., alias="therapistId", description="ID del especialista o 'any'")
):
    # TODO [COLABORADOR 2]:
    # 1. Validar que la fecha no sea en el pasado.
    # 2. Excluir domingos (domingos sin atención).
    # 3. Consultar tabla 'bookings' en Supabase para therapist_id y date_str.
    # 4. Consultar tabla 'blocked_schedules' para horarios bloqueados por la psicóloga.
    # 5. Marcar is_available = False para los slots que coincidan.

    # Respuesta simulada funcional
    slots = [
        TimeSlot(time=slot, isAvailable=True) for slot in STANDARD_SLOTS
    ]

    return DayAvailabilityResponse(
        date=date_str,
        therapistId=therapist_id,
        slots=slots
    )
