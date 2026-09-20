"""
Esquemas Pydantic para el Motor de Agendamiento de Citas (/agendar).
Asignado a: COLABORADOR 2
"""

from typing import Optional, Literal
from datetime import date
from pydantic import BaseModel, EmailStr, Field, ConfigDict

ServiceType = Literal[
    "individual",
    "pareja",
    "familiar",
    "vocacional",
    "adolescentes",
    "organizacional",
    "talleres"
]

ModalityType = Literal["presencial", "virtual"]


class BookingCreate(BaseModel):
    """
    Contrato de datos de entrada equivalente a BookingSchema de Zod en el frontend.
    """
    model_config = ConfigDict(populate_by_name=True)

    service_id: ServiceType = Field(..., alias="serviceId", description="ID de la especialidad clínica")
    modality: ModalityType = Field(..., alias="modality", description="Modalidad de atención: presencial o virtual")
    therapist_id: str = Field(..., alias="therapistId", description="ID del terapeuta o 'any'")
    date: str = Field(..., alias="date", description="Fecha de la cita en formato AAAA-MM-DD")
    time_slot: str = Field(..., alias="timeSlot", description="Horario de la cita HH:MM (ej. 09:00, 10:30)")
    client_name: str = Field(..., alias="clientName", min_length=3, description="Nombre completo del paciente")
    client_phone: str = Field(..., alias="clientPhone", min_length=8, description="WhatsApp o celular")
    client_email: EmailStr = Field(..., alias="clientEmail", description="Correo electrónico del consultante")
    consultation_reason: Optional[str] = Field(None, alias="consultationReason", max_length=500)
    consent_accepted: bool = Field(True, alias="consentAccepted", description="Aceptación de consentimiento informado")


class BookingResponse(BaseModel):
    """
    Respuesta al agendar la cita con éxito (Paso 5 del Wizard).
    """
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = None
    booking_reference: str = Field(..., alias="bookingReference", description="Código único ej: DP-2026-8912")
    service_id: str = Field(..., alias="serviceId")
    modality: str = Field(..., alias="modality")
    therapist_id: str = Field(..., alias="therapistId")
    therapist_name: str = Field(..., alias="therapistName")
    appointment_date: str = Field(..., alias="appointmentDate")
    time_slot: str = Field(..., alias="timeSlot")
    client_name: str = Field(..., alias="clientName")
    client_email: str = Field(..., alias="clientEmail")
    client_phone: str = Field(..., alias="clientPhone")
    location_or_meet_link: str = Field(..., alias="locationOrMeetLink")
    status: str = "confirmed"
    message: str = "¡Tu cita ha sido agendada con éxito! Te hemos enviado un correo y WhatsApp de confirmación."
    created_at: Optional[str] = None


class TimeSlot(BaseModel):
    time: str # "09:00", "10:30", etc.
    is_available: bool = Field(..., alias="isAvailable")


class DayAvailabilityResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    date: str
    therapist_id: str = Field(..., alias="therapistId")
    slots: list[TimeSlot]
