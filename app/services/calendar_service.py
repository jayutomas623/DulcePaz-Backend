"""
Servicio de Integración con Google Calendar y Google Meet API.
Asignado a: COLABORADOR 2
Lógica para inserción de eventos en calendarios por especialista y generación de salas Meet seguras.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger("dulcepaz.calendar")


class CalendarService:
    """
    Gestiona la sincronización con Google Calendar a través de la cuenta de servicio
    de Google Workspace (contacto@dulcepaz.com).
    """

    def __init__(self):
        # TODO [COLABORADOR 2]:
        # 1. Configurar google-auth y google-api-python-client
        # 2. Cargar credenciales desde settings.GOOGLE_SERVICE_ACCOUNT_JSON
        # 3. Inicializar Resource 'calendar', 'v3'
        pass

    async def create_appointment_event(
        self,
        therapist_id: str,
        therapist_email: str,
        service_title: str,
        modality: str,
        appointment_date: str,
        time_slot: str,
        client_name: str,
        client_email: str,
        client_phone: str,
        consultation_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crea un evento en el Google Calendar institucional.
        Si modality == 'virtual', debe generar un enlace seguro de Google Meet (conferenceData).
        Si modality == 'presencial', debe asignar la dirección física del consultorio en Calacoto.
        """
        # TODO [COLABORADOR 2]:
        # Estructura del evento:
        # summary = f"Sesión: {service_title} - {client_name}"
        # location = "Calle 15 de Calacoto, Edificio Parque, La Paz" if modality == "presencial" else None
        # conferenceData = {...} si modality == "virtual"
        
        logger.info(
            f"[STUB CALENDAR] Programando cita para {client_name} con terapeuta {therapist_id} el {appointment_date} {time_slot}"
        )
        
        # Retorno simulado mientras Colaborador 2 implementa las credenciales oficiales
        dummy_meet = "https://meet.google.com/dpz-sano-paz" if modality == "virtual" else "Calle 15 de Calacoto, Edif. Parque"
        return {
            "google_event_id": f"gcal_evt_{therapist_id}_{appointment_date.replace('-', '')}",
            "google_meet_link": dummy_meet,
            "status": "confirmed"
        }


calendar_service = CalendarService()
