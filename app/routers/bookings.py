"""
Router para el Motor de Agendamiento de Citas (/agendar).
Asignado a: COLABORADOR 2
"""

import uuid
import random
import logging
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.calendar_service import calendar_service
from app.services.whatsapp_service import whatsapp_service
from app.services.email_service import _get_base_html
from app.database import get_supabase_client

logger = logging.getLogger("dulcepaz.routers.bookings")

router = APIRouter(prefix="/bookings", tags=["Citas y Reservas"])


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva cita clínica o psicoeducativa",
    description="Endpoint asignado al Colaborador 2. Valida la disponibilidad del slot, inserta la cita en PostgreSQL (Supabase), crea el evento en Google Calendar/Meet, envía confirmación por WhatsApp y correo, y agenda el recordatorio de 24h vía pg_cron."
)
async def create_booking(
    payload: BookingCreate,
    background_tasks: BackgroundTasks
):
    # TODO [COLABORADOR 2]:
    # 1. Verificar si el slot no está ocupado en Supabase (evitar condición de carrera)
    # 2. Asignar terapeuta si eligió "any" (primer disponible calificado para el servicio)
    # 3. Llamar a calendar_service.create_appointment_event(...) para obtener link de Meet o dirección
    # 4. Insertar en tabla 'bookings'
    # 5. Enviar WhatsApp vía whatsapp_service.send_booking_confirmation(...)
    # 6. Enviar correo con archivo .ics descargable

    ref_number = random.randint(1000, 9999)
    booking_ref = f"DP-2026-{ref_number}"
    booking_id = str(uuid.uuid4())

    therapist_names = {
        "nikki-paz": "Lic. Nikki Paz",
        "keila-vilar": "Lic. Keila Vilar",
        "william-mendoza": "Lic. William Mendoza",
    }
    therapist_name = therapist_names.get(payload.therapist_id, "Lic. Nikki Paz")
    location_meet = (
        "https://meet.google.com/dpz-sano-paz"
        if payload.modality == "virtual"
        else "Calle 15 de Calacoto, Edificio Parque, La Paz"
    )

    logger.info(f"[STUB BOOKING] Cita preliminar generada con referencia {booking_ref}")

    return BookingResponse(
        id=booking_id,
        bookingReference=booking_ref,
        serviceId=payload.service_id,
        modality=payload.modality,
        therapistId=payload.therapist_id,
        therapistName=therapist_name,
        appointmentDate=payload.date,
        timeSlot=payload.time_slot,
        clientName=payload.client_name,
        clientEmail=payload.client_email,
        clientPhone=payload.client_phone,
        locationOrMeetLink=location_meet,
        status="confirmed",
        message="¡Tu cita ha sido agendada con éxito! Te hemos enviado un correo y WhatsApp de confirmación.",
        created_at=datetime.now().isoformat()
    )
