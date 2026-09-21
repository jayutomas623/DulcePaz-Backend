"""
Servicio de Mensajería con Meta WhatsApp Cloud API.
Asignado a: COLABORADOR 2
Despacho de notificaciones oficiales interactivas de confirmación de cita y plan de contingencia wa.me.
"""

import logging
from typing import Dict, Any, Optional
import urllib.parse
import httpx
from app.core.config import settings

logger = logging.getLogger("dulcepaz.whatsapp")


class WhatsAppService:
    """
    Gestiona el envío de notificaciones por WhatsApp usando la API oficial de Meta Graph Cloud
    con mecanismo automático de fallback a wa.me.
    """

    def __init__(self):
        self.api_token = settings.WHATSAPP_API_TOKEN.strip() if settings.WHATSAPP_API_TOKEN else ""
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID.strip() if settings.WHATSAPP_PHONE_NUMBER_ID else ""
        self.endpoint = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages" if self.phone_number_id else ""

    def generate_fallback_url(
        self,
        client_name: str,
        service_name: str,
        therapist_name: str,
        date_str: str,
        time_str: str,
        meet_link_or_location: str,
        booking_ref: Optional[str] = None
    ) -> str:
        """
        Genera el enlace directo a WhatsApp (wa.me) con el mensaje de confirmación precargado
        para el plan de contingencia especificado en la sección 4.3 del informe técnico.
        """
        fallback_phone = "".join(filter(str.isdigit, settings.WHATSAPP_FALLBACK_PHONE or "59176543210"))
        if not fallback_phone.startswith("591"):
            fallback_phone = f"591{fallback_phone}"

        ref_str = f" con el código *{booking_ref}*" if booking_ref else ""
        message_text = (
            f"¡Hola Dulce Paz! Acabo de registrar mi cita en la web{ref_str}.\n"
            f"• *Servicio:* {service_name}\n"
            f"• *Especialista:* {therapist_name}\n"
            f"• *Fecha:* {date_str} a las {time_str} (Hora Bolivia GMT-4)\n"
            f"• *Modalidad / Lugar:* {meet_link_or_location}\n"
            f"• *Consultante:* {client_name}\n"
            f"Agradezco confirmar la reserva."
        )
        encoded_text = urllib.parse.quote(message_text)
        return f"https://wa.me/{fallback_phone}?text={encoded_text}"

    async def send_booking_confirmation(
        self,
        to_phone: str,
        client_name: str,
        service_name: str,
        therapist_name: str,
        date_str: str,
        time_str: str,
        meet_link_or_location: str,
        booking_ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envía plantilla oficial aprobada en Meta Cloud API.
        Si la API no está configurada o la llamada falla, retorna el enlace de contingencia wa.me.
        """
        clean_phone = "".join(filter(str.isdigit, to_phone))
        # Formatear a código de país de Bolivia si no lo tiene
        if len(clean_phone) == 8:
            clean_phone = f"591{clean_phone}"

        fallback_url = self.generate_fallback_url(
            client_name=client_name,
            service_name=service_name,
            therapist_name=therapist_name,
            date_str=date_str,
            time_str=time_str,
            meet_link_or_location=meet_link_or_location,
            booking_ref=booking_ref
        )

        # Si no hay credenciales activas de Meta, opera inmediatamente en modo contingencia
        if not self.api_token or not self.phone_number_id or "placeholder" in self.api_token.lower():
            logger.info(
                f"[WHATSAPP FALLBACK] Notificación lista para {client_name} ({clean_phone}) vía enlace wa.me."
            )
            return {
                "sent_via_api": False,
                "whatsapp_message_id": None,
                "fallback_url": fallback_url,
                "status": "ready"
            }

        # Intentar envío con plantilla oficial en Meta WhatsApp Cloud API
        try:
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": clean_phone,
                "type": "template",
                "template": {
                    "name": "booking_confirmation",
                    "language": {"code": "es"},
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {"type": "text", "text": client_name},
                                {"type": "text", "text": service_name},
                                {"type": "text", "text": therapist_name},
                                {"type": "text", "text": f"{date_str} a las {time_str}"},
                                {"type": "text", "text": meet_link_or_location}
                            ]
                        }
                    ]
                }
            }
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(self.endpoint, headers=headers, json=payload)
                if res.status_code in (200, 201):
                    res_data = res.json()
                    message_id = res_data.get("messages", [{}])[0].get("id")
                    logger.info(f"Mensaje WhatsApp despachado exitosamente: {message_id}")
                    return {
                        "sent_via_api": True,
                        "whatsapp_message_id": message_id,
                        "fallback_url": fallback_url,
                        "status": "sent"
                    }
                else:
                    logger.warning(
                        f"Error en respuesta de Meta WhatsApp API ({res.status_code}): {res.text}. Activando fallback wa.me."
                    )
        except Exception as e:
            logger.error(f"Fallo al conectar con Meta WhatsApp API: {e}. Activando fallback wa.me.")

        return {
            "sent_via_api": False,
            "whatsapp_message_id": None,
            "fallback_url": fallback_url,
            "status": "fallback"
        }


whatsapp_service = WhatsAppService()

