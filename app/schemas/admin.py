"""
Esquemas Pydantic v2 para el Panel Administrativo de Gestión Clínica (/admin).
Asignado a: COLABORADOR 2
"""

from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator


BookingStatus = Literal[
    "confirmed",
    "completed",
    "cancelled_by_patient",
    "no_show"
]

STATUS_MAP_ES_TO_EN = {
    "confirmada": "confirmed",
    "confirmed": "confirmed",
    "completada": "completed",
    "completed": "completed",
    "cancelada por paciente": "cancelled_by_patient",
    "cancelada": "cancelled_by_patient",
    "cancelled_by_patient": "cancelled_by_patient",
    "no asistió": "no_show",
    "no asistio": "no_show",
    "no_show": "no_show",
}


class BookingStatusUpdate(BaseModel):
    """
    Payload para actualizar el estado de una cita en el panel de control.
    Acepta tanto la nomenclatura técnica (confirmed) como la usada en la UI (Confirmada).
    """
    model_config = ConfigDict(populate_by_name=True)

    status: str = Field(..., description="Nuevo estado: confirmed, completed, cancelled_by_patient, no_show")
    admin_notes: Optional[str] = Field(None, alias="adminNotes", max_length=1000)

    @field_validator("status")
    @classmethod
    def normalize_status(cls, v: str) -> str:
        clean = v.strip().lower()
        if clean in STATUS_MAP_ES_TO_EN:
            return STATUS_MAP_ES_TO_EN[clean]
        raise ValueError(
            f"Estado '{v}' no válido. Opciones permitidas: confirmed, completed, cancelled_by_patient, no_show"
        )


class ScheduleBlockCreate(BaseModel):
    """
    Payload para inhabilitar franjas horarias por parte del profesional.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True
    )

    therapist_id: str = Field(..., alias="therapistId", description="ID del terapeuta (ej. 'nikki-paz')")
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Fecha AAAA-MM-DD")
    time_slot: str = Field(..., alias="timeSlot", pattern=r"^\d{2}:\d{2}$", description="Horario a inhabilitar ej. 09:00")
    reason: Optional[str] = Field(
        "No disponible / Bloqueo administrativo",
        description="Motivo institucional o personal del bloqueo"
    )


# Alias para cumplir con la especificación de nombres
BlockedScheduleCreate = ScheduleBlockCreate


class BlockedScheduleResponse(BaseModel):
    """
    Respuesta al registrar un bloqueo de horario.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True
    )

    id: str
    therapist_id: str = Field(..., alias="therapistId", serialization_alias="therapistId")
    date: str
    time_slot: str = Field(..., alias="timeSlot", serialization_alias="timeSlot")
    reason: str
    created_at: Optional[str] = Field(None, alias="createdAt", serialization_alias="createdAt")


class AdminBookingItem(BaseModel):
    """
    Ficha de cita clínica adaptada para las vistas de la PWA (/admin/agenda y /admin/coordinacion).
    """
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        from_attributes=True
    )

    id: str
    booking_reference: str = Field(..., alias="bookingReference", serialization_alias="bookingReference")
    therapist_id: str = Field(..., alias="therapistId", serialization_alias="therapistId")
    therapist_name: str = Field(..., alias="therapistName", serialization_alias="therapistName")
    service_id: str = Field(..., alias="serviceId", serialization_alias="serviceId")
    service_name: str = Field(..., alias="serviceName", serialization_alias="serviceName")
    time: str = Field(..., alias="time", serialization_alias="time")
    date: str
    client_name: str = Field(..., alias="clientName", serialization_alias="clientName")
    client_phone: str = Field(..., alias="clientPhone", serialization_alias="clientPhone")
    client_email: str = Field(..., alias="clientEmail", serialization_alias="clientEmail")
    modality: str
    consultation_reason: Optional[str] = Field(None, alias="consultationReason", serialization_alias="consultationReason")
    status: str
    meet_url: Optional[str] = Field(None, alias="meetUrl", serialization_alias="meetUrl")
    admin_notes: Optional[str] = Field(None, alias="adminNotes", serialization_alias="adminNotes")
    created_at: Optional[str] = Field(None, alias="createdAt", serialization_alias="createdAt")


class AgendaResponse(BaseModel):
    """
    Colección de citas para la agenda del día o vista consolidada.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True
    )

    date: Optional[str] = None
    therapist_id: Optional[str] = Field(None, alias="therapistId", serialization_alias="therapistId")
    total: int
    appointments: List[AdminBookingItem]
    user: Optional[Dict[str, Any]] = None


class AgendaQuery(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    date: Optional[str] = None
    therapist_id: Optional[str] = Field(None, alias="therapistId")

