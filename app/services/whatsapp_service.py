"""
Servicio de Mensajería con Meta WhatsApp Cloud API.
Asignado a: COLABORADOR 2
Despacho de notificaciones oficiales interactivas de confirmación de cita y plan de contingencia wa.me.
"""

import logging
from typing import Dict, Any, Optional
import urllib.parse
from app.core.config import settings

logger = logging.getLogger("dulcepaz.whatsapp")


class WhatsAppService:
    """
    Gestiona el envío de notificaciones por WhatsApp usando la API de Meta Graph Cloud.
    """

    def __init__(self):
        self.api_token = settings.WHATSAPP_API_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.endpoint = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"

    async def send_booking_confirmation(
        self,
        to_phone: str,
        client_name: str,
        service_name: str,
        therapist_name: str,
        date_str: str,
        time_str: str,
        meet_link_or_location: str
    ) -> Dict[str, Any]:
        """
        Envía plantilla oficial aprobada en Meta Cloud API.
        Si la API no está configurada, genera la URL de contingencia directa de wa.me.
        """
        # Formatear mensaje para contingencia
        clean_phone = "".join(filter(str.isdigit, to_phone))
        message_text = (
            f"Hola {client_name}, tu cita en Dulce Paz ha sido confirmada.\n"
            f"Especialidad: {service_name}\n"
            f"Profesional: {therapist_name}\n"
            f"Fecha y Hora: {date_str} a las {time_str} (GMT-4)\n"
            f"Lugar/Enlace: {meet_link_or_location}\n\n"
            f"Consultorio: Calle 15 de Calacoto, La Paz."
        )
        encoded_text = urllib.parse.quote(message_text)
        fallback_url = f"https://wa.me/59176543210?text={encoded_text}"

        # TODO [COLABORADOR 2]:
        # Si self.api_token y self.phone_number_id están presentes:
        # Realizar POST httpx a self.endpoint con payload de template 'booking_confirmation'

        logger.info(f"[STUB WHATSAPP] Notificación para {to_phone} generada con fallback wa.me")
        return {
            "sent_via_api": bool(self.api_token),
            "fallback_url": fallback_url,
            "status": "ready"
        }


whatsapp_service = WhatsAppService()
