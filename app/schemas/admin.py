"""
Esquemas Pydantic para el Panel Administrativo de Gestión Clínica (/admin).
Asignado a: COLABORADOR 2
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

BookingStatus = Literal["confirmed", "completed", "cancelled_by_patient", "no_show"]


class BookingStatusUpdate(BaseModel):
    status: BookingStatus
    admin_notes: Optional[str] = None


class ScheduleBlockCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    therapist_id: str = Field(..., alias="therapistId")
    date: str = Field(..., description="Fecha AAAA-MM-DD")
    time_slot: str = Field(..., alias="timeSlot", description="Horario a bloquear ej. 09:00")
    reason: Optional[str] = Field("No disponible / Bloqueo administrativo", description="Motivo del bloqueo")


class TherapistScheduleResponse(BaseModel):
    therapist_id: str
    therapist_name: str
    appointments_count: int
    appointments: list[dict]
