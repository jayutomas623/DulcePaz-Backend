"""
Esquemas Pydantic v2 para el Motor de Agendamiento de Citas (/agendar).
Asignado a: COLABORADOR 2
Garantiza validación estricta y sincronización bidireccional (camelCase y snake_case).
"""

from typing import Optional, List, Literal
from datetime import datetime, date
import re
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


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

BookingStatusType = Literal[
    "confirmed",
    "completed",
    "cancelled_by_patient",
    "no_show"
]


class BookingCreate(BaseModel):
    """
    Contrato de datos de entrada equivalente a BookingSchema de Zod en el frontend.
    Acepta tanto camelCase (desde el cliente Next.js) como snake_case.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"
    )

    service_id: ServiceType = Field(
        ...,
        alias="serviceId",
        description="ID de la especialidad clínica o psicoeducativa"
    )
    modality: ModalityType = Field(
        ...,
        alias="modality",
        description="Modalidad de atención: 'presencial' o 'virtual'"
    )
    therapist_id: str = Field(
        ...,
        alias="therapistId",
        min_length=1,
        description="ID del especialista (ej. 'nikki-paz') o 'any'"
    )
    date: str = Field(
        ...,
        alias="date",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Fecha de la cita en formato AAAA-MM-DD"
    )
    time_slot: str = Field(
        ...,
        alias="timeSlot",
        pattern=r"^\d{2}:\d{2}$",
        description="Horario de la cita en formato HH:MM (ej. 09:00, 10:30)"
    )
    client_name: str = Field(
        ...,
        alias="clientName",
        min_length=3,
        max_length=150,
        description="Nombre completo del paciente o consultante"
    )
    client_phone: str = Field(
        ...,
        alias="clientPhone",
        min_length=8,
        max_length=50,
        description="Número de celular o WhatsApp con código de país"
    )
    client_email: EmailStr = Field(
        ...,
        alias="clientEmail",
        description="Correo electrónico válido para el envío de comprobantes"
    )
    consultation_reason: Optional[str] = Field(
        None,
        alias="consultationReason",
        max_length=500,
        description="Motivo o síntoma clínico inicial (opcional)"
    )
    consent_accepted: bool = Field(
        True,
        alias="consentAccepted",
        description="Consentimiento informado y políticas de privacidad aceptadas"
    )

    @field_validator("date")
    @classmethod
    def validate_date_format_and_validity(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Formato de fecha inválido o día inexistente. Use AAAA-MM-DD")
        return v

    @field_validator("time_slot")
    @classmethod
    def validate_time_slot_format(cls, v: str) -> str:
        parts = v.split(":")
        if len(parts) != 2:
            raise ValueError("Formato de hora inválido. Use HH:MM")
        try:
            hour, minute = int(parts[0]), int(parts[1])
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError()
        except Exception:
            raise ValueError("Hora o minuto fuera de rango permitido (00:00 - 23:59)")
        return v


class BookingResponse(BaseModel):
    """
    Respuesta detallada al agendar la cita con éxito (Paso 5 del Wizard).
    """
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        from_attributes=True
    )

    id: Optional[str] = Field(None, alias="id")
    booking_reference: str = Field(
        ...,
        alias="bookingReference",
        serialization_alias="bookingReference",
        description="Código único de reserva (ej. DP-2026-8491)"
    )
    service_id: str = Field(
        ...,
        alias="serviceId",
        serialization_alias="serviceId"
    )
    service_title: Optional[str] = Field(
        None,
        alias="serviceTitle",
        serialization_alias="serviceTitle"
    )
    modality: str = Field(
        ...,
        alias="modality",
        serialization_alias="modality"
    )
    therapist_id: str = Field(
        ...,
        alias="therapistId",
        serialization_alias="therapistId"
    )
    therapist_name: str = Field(
        ...,
        alias="therapistName",
        serialization_alias="therapistName"
    )
    appointment_date: str = Field(
        ...,
        alias="appointmentDate",
        serialization_alias="appointmentDate"
    )
    time_slot: str = Field(
        ...,
        alias="timeSlot",
        serialization_alias="timeSlot"
    )
    client_name: str = Field(
        ...,
        alias="clientName",
        serialization_alias="clientName"
    )
    client_email: str = Field(
        ...,
        alias="clientEmail",
        serialization_alias="clientEmail"
    )
    client_phone: str = Field(
        ...,
        alias="clientPhone",
        serialization_alias="clientPhone"
    )
    location_or_meet_link: str = Field(
        ...,
        alias="locationOrMeetLink",
        serialization_alias="locationOrMeetLink"
    )
    google_meet_link: Optional[str] = Field(
        None,
        alias="googleMeetLink",
        serialization_alias="googleMeetLink"
    )
    whatsapp_fallback_url: Optional[str] = Field(
        None,
        alias="whatsappFallbackUrl",
        serialization_alias="whatsappFallbackUrl"
    )
    status: str = Field(
        "confirmed",
        alias="status",
        serialization_alias="status"
    )
    message: str = Field(
        "¡Tu cita ha sido agendada con éxito! Te hemos enviado un correo y WhatsApp de confirmación.",
        alias="message",
        serialization_alias="message"
    )
    created_at: Optional[str] = Field(
        None,
        alias="createdAt",
        serialization_alias="createdAt"
    )


class TimeSlot(BaseModel):
    """
    Franja horaria con indicación de disponibilidad.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True
    )

    time: str = Field(..., description="Horario en formato HH:MM (ej. '09:00')")
    is_available: bool = Field(
        ...,
        alias="isAvailable",
        serialization_alias="isAvailable",
        description="True si el slot está libre para reserva; False si está ocupado o bloqueado"
    )


class DayAvailabilityResponse(BaseModel):
    """
    Respuesta para el calendario de selección de slots del Paso 3.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True
    )

    date: str = Field(..., description="Fecha consultada AAAA-MM-DD")
    therapist_id: str = Field(
        ...,
        alias="therapistId",
        serialization_alias="therapistId",
        description="ID del terapeuta consultado o 'any'"
    )
    slots: List[TimeSlot] = Field(..., description="Lista de slots y su estado de disponibilidad")
    timezone: str = Field(
        "America/La_Paz",
        alias="timezone",
        serialization_alias="timezone",
        description="Zona horaria oficial (GMT-4)"
    )


class AvailabilityQuery(BaseModel):
    """
    Parámetros de consulta de disponibilidad.
    """
    model_config = ConfigDict(populate_by_name=True)

    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    therapist_id: str = Field(..., alias="therapistId")

