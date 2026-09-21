"""
Router para el Motor de Agendamiento de Citas (/agendar).
Asignado a: COLABORADOR 2
Implementa anti-colisión, asignación inteligente ('any'), tareas en segundo plano
(Google Calendar & WhatsApp) y persistencia en Supabase.
"""

import uuid
import random
import logging
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.calendar_service import calendar_service
from app.services.whatsapp_service import whatsapp_service
from app.database import (
    THERAPISTS_CATALOG,
    SERVICES_CATALOG,
    is_slot_booked_or_blocked,
    find_available_therapist_for_slot,
    save_booking_record,
)

logger = logging.getLogger("dulcepaz.routers.bookings")

router = APIRouter(prefix="/bookings", tags=["Citas y Reservas"])


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva cita clínica o psicoeducativa",
    description="Valida la disponibilidad del slot, aplica anti-colisión, asigna terapeuta si se seleccionó 'any', guarda la cita en Supabase, y despacha en segundo plano eventos en Google Calendar/Meet y notificaciones WhatsApp.",
    response_model_by_alias=True
)
async def create_booking(
    payload: BookingCreate,
    background_tasks: BackgroundTasks
):
    # 1. Validación de fecha: Bloquear domingos
    date_obj = datetime.strptime(payload.date, "%Y-%m-%d").date()
    if date_obj.weekday() == 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El centro de atención permanece cerrado los domingos. Por favor selecciona una fecha de lunes a sábado."
        )

    # 2. Resolución de terapeuta y detección de colisiones
    assigned_therapist_id = payload.therapist_id

    if assigned_therapist_id == "any":
        # Asignación automática: Buscar el primer terapeuta calificado libre
        found_therapist = find_available_therapist_for_slot(
            service_id=payload.service_id,
            date_str=payload.date,
            time_slot=payload.time_slot
        )
        if not found_therapist:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No hay especialistas disponibles para esta especialidad en el horario seleccionado."
            )
        assigned_therapist_id = found_therapist
    else:
        # Terapeuta específico seleccionado: Verificar que no haya colisión
        if is_slot_booked_or_blocked(assigned_therapist_id, payload.date, payload.time_slot):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El horario {payload.time_slot} del {payload.date} ya no se encuentra disponible con el especialista seleccionado."
            )

    # 3. Metadatos del terapeuta y servicio
    therapist_info = THERAPISTS_CATALOG.get(
        assigned_therapist_id,
        {
            "name": "Lic. Nikki Paz",
            "email": "contacto@dulcepaz.com",
            "role": "Psicóloga Clínica"
        }
    )
    therapist_name = therapist_info.get("name", "Lic. Nikki Paz")
    therapist_email = therapist_info.get("email", "contacto@dulcepaz.com")
    service_title = SERVICES_CATALOG.get(payload.service_id, "Consulta Psicológica")

    # 4. Generación de códigos únicos
    ref_number = random.randint(1000, 9999)
    booking_ref = f"DP-2026-{ref_number}"
    booking_id = str(uuid.uuid4())

    # 5. Determinación de ubicación o enlace Google Meet
    if payload.modality == "virtual":
        meet_link = f"https://meet.google.com/dpz-sano-paz"
        location_or_meet_link = meet_link
    else:
        meet_link = None
        location_or_meet_link = "Calle 15 de Calacoto, Edificio Parque, La Paz"

    # 6. Generar URL de fallback para WhatsApp
    fallback_whatsapp = whatsapp_service.generate_fallback_url(
        client_name=payload.client_name,
        service_name=service_title,
        therapist_name=therapist_name,
        date_str=payload.date,
        time_str=payload.time_slot,
        meet_link_or_location=location_or_meet_link,
        booking_ref=booking_ref
    )

    # 7. Persistir cita en base de datos
    booking_record = {
        "id": booking_id,
        "booking_reference": booking_ref,
        "service_id": payload.service_id,
        "service_name": service_title,
        "modality": payload.modality,
        "therapist_id": assigned_therapist_id,
        "therapist_name": therapist_name,
        "appointment_date": payload.date,
        "time_slot": payload.time_slot,
        "client_name": payload.client_name,
        "client_phone": payload.client_phone,
        "client_email": payload.client_email,
        "consultation_reason": payload.consultation_reason,
        "consent_accepted": payload.consent_accepted,
        "google_meet_link": meet_link,
        "location_or_meet_link": location_or_meet_link,
        "status": "confirmed",
        "created_at": datetime.now().isoformat(),
    }
    save_booking_record(booking_record)

    # 8. Despacho asíncrono en segundo plano (BackgroundTasks)
    background_tasks.add_task(
        calendar_service.create_appointment_event,
        therapist_id=assigned_therapist_id,
        therapist_email=therapist_email,
        service_title=service_title,
        modality=payload.modality,
        appointment_date=payload.date,
        time_slot=payload.time_slot,
        client_name=payload.client_name,
        client_email=payload.client_email,
        client_phone=payload.client_phone,
        consultation_reason=payload.consultation_reason
    )

    background_tasks.add_task(
        whatsapp_service.send_booking_confirmation,
        to_phone=payload.client_phone,
        client_name=payload.client_name,
        service_name=service_title,
        therapist_name=therapist_name,
        date_str=payload.date,
        time_str=payload.time_slot,
        meet_link_or_location=location_or_meet_link,
        booking_ref=booking_ref
    )

    logger.info(
        f"[NUEVA CITA] Ref: {booking_ref} | {therapist_name} | {payload.date} {payload.time_slot} | {payload.client_name}"
    )

    return BookingResponse(
        id=booking_id,
        bookingReference=booking_ref,
        serviceId=payload.service_id,
        serviceTitle=service_title,
        modality=payload.modality,
        therapistId=assigned_therapist_id,
        therapistName=therapist_name,
        appointmentDate=payload.date,
        timeSlot=payload.time_slot,
        clientName=payload.client_name,
        clientEmail=payload.client_email,
        clientPhone=payload.client_phone,
        locationOrMeetLink=location_or_meet_link,
        googleMeetLink=meet_link,
        whatsappFallbackUrl=fallback_whatsapp,
        status="confirmed",
        message="¡Tu cita ha sido agendada con éxito! Te hemos enviado un correo y WhatsApp de confirmación.",
        createdAt=booking_record["created_at"]
    )

