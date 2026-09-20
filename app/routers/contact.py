"""
Router para recepción y gestión de mensajes de contacto (/contacto).
Asignado a: COLABORADOR 1
"""

import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from app.schemas.contact import ContactCreate, ContactResponse
from app.services.email_service import send_contact_notification
from app.database import get_supabase_client

logger = logging.getLogger("dulcepaz.routers.contact")

router = APIRouter(prefix="/contact", tags=["Contacto"])


@router.post(
    "",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar mensaje desde el formulario de contacto",
    description="Valida los datos del formulario institucional, los almacena en la tabla 'contacts' de Supabase y despacha las notificaciones por correo vía Resend."
)
async def submit_contact_form(
    payload: ContactCreate,
    background_tasks: BackgroundTasks
):
    contact_dict = payload.model_dump()
    contact_id = str(uuid.uuid4())
    created_at_str = datetime.now().isoformat()

    # 1. Almacenar en Supabase
    supabase = get_supabase_client()
    if supabase:
        try:
            insert_data = {
                "nombre": payload.nombre,
                "email": payload.email,
                "telefono": payload.telefono,
                "motivo": payload.motivo,
                "mensaje": payload.mensaje,
                "status": "pending"
            }
            res = supabase.table("contacts").insert(insert_data).execute()
            if res.data and len(res.data) > 0:
                contact_id = res.data[0].get("id", contact_id)
                created_at_str = res.data[0].get("created_at", created_at_str)
                logger.info(f"Mensaje de contacto persistido en Supabase con id: {contact_id}")
        except Exception as e:
            logger.error(f"Error persistiendo contacto en Supabase: {e}")
            # Se continúa para asegurar el despacho del correo transaccional
    else:
        logger.info(f"[MODO LOCAL] Mensaje de contacto procesado sin conexión activa a Supabase: {contact_id}")

    # 2. Despachar notificaciones de correo en segundo plano
    background_tasks.add_task(send_contact_notification, contact_dict)

    return ContactResponse(
        id=contact_id,
        nombre=payload.nombre,
        email=payload.email,
        motivo=payload.motivo,
        status="pending",
        message="¡Mensaje Enviado con Éxito! Un profesional de nuestro equipo se pondrá en contacto a la brevedad.",
        created_at=created_at_str
    )
