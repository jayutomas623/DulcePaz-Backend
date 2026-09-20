"""
Router para gestión de eventos comunitarios e institucionales (Código QR 1 /registro-evento).
Asignado a: COLABORADOR 1
"""

import random
import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from app.schemas.event import EventRSVPCreate, EventRSVPResponse
from app.services.email_service import send_event_rsvp_confirmation
from app.database import get_supabase_client

logger = logging.getLogger("dulcepaz.routers.events")

router = APIRouter(prefix="/events", tags=["Eventos y Talleres"])


@router.get(
    "/info",
    summary="Obtener detalles del evento corporativo activo (Código QR 1)",
    description="Devuelve la fecha, lugar y detalles del Desayuno de Salud Mental en las Organizaciones."
)
async def get_active_event_info():
    return {
        "event_name": "Desayuno de Trabajo Corporativo: Salud Mental en las Organizaciones",
        "badge": "Invitación Especial • Código QR 1",
        "date": "Viernes, 23 de Octubre de 2026",
        "time": "10:00 a 12:00 (Hora de Bolivia GMT-4)",
        "location": "Auditorio Dulce Paz",
        "address": "Calle 15 de Calacoto, Edificio Parque, La Paz, Bolivia",
        "max_attendees_per_company": 3,
        "description": "Un encuentro exclusivo para líderes de talento humano y directivos. Espacio de diálogo estratégico sobre bienestar laboral y diagnóstico organizacional ético."
    }


@router.post(
    "/rsvp",
    response_model=EventRSVPResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar confirmación de asistencia al evento (RSVP)",
    description="Registra la institución y su delegado para el Desayuno de Trabajo, genera el pase digital VIP 'CORP-DP-XXXX', persiste en Supabase y despacha el correo de acreditación."
)
async def register_event_rsvp(
    payload: EventRSVPCreate,
    background_tasks: BackgroundTasks
):
    # Generar código de pase único
    random_num = random.randint(1000, 9999)
    pass_code = f"CORP-DP-{random_num}"
    rsvp_id = str(uuid.uuid4())
    created_at_str = datetime.now().isoformat()

    rsvp_dict = {
        "company_name": payload.company_name,
        "representative_name": payload.representative_name,
        "job_title": payload.job_title,
        "phone": payload.phone,
        "email": payload.email,
        "attendees_count": payload.attendees_count,
        "pass_code": pass_code,
    }

    # 1. Almacenar en Supabase
    supabase = get_supabase_client()
    if supabase:
        try:
            insert_data = {
                **rsvp_dict,
                "status": "confirmed",
                "event_name": "Desayuno de Trabajo Corporativo: Salud Mental en las Organizaciones",
                "event_date": "2026-10-23",
                "event_time": "10:00 a 12:00",
                "event_location": "Auditorio Dulce Paz (Calle 15 de Calacoto, Edif. Parque, La Paz)"
            }
            res = supabase.table("event_rsvps").insert(insert_data).execute()
            if res.data and len(res.data) > 0:
                rsvp_id = res.data[0].get("id", rsvp_id)
                pass_code = res.data[0].get("pass_code", pass_code)
                created_at_str = res.data[0].get("created_at", created_at_str)
                logger.info(f"RSVP persistido en Supabase con código {pass_code}")
        except Exception as e:
            logger.error(f"Error persistiendo RSVP en Supabase: {e}")
    else:
        logger.info(f"[MODO LOCAL] RSVP procesado en modo local: {pass_code}")

    # 2. Despachar correo con credencial digital en segundo plano
    background_tasks.add_task(send_event_rsvp_confirmation, {**rsvp_dict, "pass_code": pass_code})

    return EventRSVPResponse(
        id=rsvp_id,
        passCode=pass_code,
        companyName=payload.company_name,
        representativeName=payload.representative_name,
        jobTitle=payload.job_title,
        attendeesCount=payload.attendees_count,
        event_name="Desayuno de Trabajo Corporativo: Salud Mental en las Organizaciones",
        event_date="Viernes, 23 de Octubre de 2026",
        event_time="10:00 a 12:00 (Hora de Bolivia GMT-4)",
        event_location="Auditorio Dulce Paz (Calle 15 de Calacoto, Edif. Parque, La Paz)",
        status="confirmed",
        message="¡Asistencia confirmada! Hemos registrado la participación de su institución. Les esperamos el 23 de octubre.",
        created_at=created_at_str
    )
