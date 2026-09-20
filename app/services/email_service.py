"""
Servicio de Email Transaccional con Resend.
Asignado a: COLABORADOR 1
Plantillas HTML diseñadas con los tokens oficiales de la marca Dulce Paz.
"""

import logging
from typing import Dict, Any, Optional
import resend
from app.core.config import settings

logger = logging.getLogger("dulcepaz.email")

# Configurar API Key si existe
if settings.RESEND_API_KEY:
    resend.api_key = settings.RESEND_API_KEY


def _get_base_html(title: str, content_html: str) -> str:
    """
    Plantilla base corporativa HTML con la identidad visual oficial de Dulce Paz.
    Colores: #883F9B (Passionate Purple), #2A8ED1 (Ticino Blueous), #F7F7E8 (Pure Beige), #A56A2E (Camel)
    """
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: #F7F7E8;
                color: #2D2D2D;
                margin: 0;
                padding: 24px 12px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #FFFFFF;
                border-radius: 20px;
                border: 1px solid #B2BFEB;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0,0,0,0.04);
            }}
            .header {{
                background-color: #883F9B;
                padding: 32px 24px;
                text-align: center;
                color: #FFFFFF;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                letter-spacing: -0.5px;
            }}
            .header p {{
                margin: 6px 0 0 0;
                font-size: 13px;
                color: #F7F7E8;
                font-weight: 300;
            }}
            .content {{
                padding: 32px 28px;
                font-size: 15px;
                line-height: 1.6;
                color: #374151;
            }}
            .badge {{
                display: inline-block;
                padding: 4px 12px;
                background-color: #F7F7E8;
                color: #883F9B;
                border: 1px solid #B2BFEB;
                border-radius: 999px;
                font-size: 12px;
                font-weight: bold;
                margin-bottom: 16px;
            }}
            .card {{
                background-color: #F7F7E8;
                border: 1px solid #B2BFEB;
                border-radius: 14px;
                padding: 20px;
                margin: 20px 0;
            }}
            .btn {{
                display: inline-block;
                background-color: #2A8ED1;
                color: #FFFFFF !important;
                padding: 14px 28px;
                border-radius: 12px;
                text-decoration: none;
                font-weight: bold;
                font-size: 14px;
                margin-top: 16px;
                text-align: center;
            }}
            .footer {{
                background-color: #F7F7E8;
                border-top: 1px solid #B2BFEB;
                padding: 24px;
                text-align: center;
                font-size: 12px;
                color: #6B7280;
            }}
            .footer a {{
                color: #2A8ED1;
                text-decoration: none;
            }}
            .quote {{
                color: #A56A2E;
                font-style: italic;
                margin-top: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Dulce Paz</h1>
                <p>Psicología y Salud Mental &bull; La Paz, Bolivia</p>
            </div>
            <div class="content">
                {content_html}
            </div>
            <div class="footer">
                <p><strong>Dulce Paz | Centro de Acompañamiento Integral</strong></p>
                <p>Calle 15 de Calacoto, Edificio Parque, La Paz, Bolivia</p>
                <p>WhatsApp: +591 76543210 &bull; Correo: <a href="mailto:contacto@dulcepaz.com">contacto@dulcepaz.com</a></p>
                <p class="quote">“Comprendernos mejor también es parte del proceso de sentirnos mejor.”</p>
            </div>
        </div>
    </body>
    </html>
    """


def send_contact_notification(contact_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Envía dos correos por cada consulta recibida:
    1. Notificación interna al equipo clínico de Dulce Paz.
    2. Acuse de recibo y bienvenida al consultante.
    """
    nombre = contact_data.get("nombre", "")
    email = contact_data.get("email", "")
    telefono = contact_data.get("telefono") or "No proporcionado"
    motivo = contact_data.get("motivo", "Consulta general")
    mensaje = contact_data.get("mensaje", "")

    # Validar si Resend está configurado con API Key real
    if not settings.RESEND_API_KEY or settings.RESEND_API_KEY.startswith("re_placeholder") or settings.RESEND_API_KEY == "":
        logger.info(f"[SIMULACIÓN EMAIL RESEND] Notificación de contacto para {email} procesada en modo local.")
        return {"id": "mock-contact-email-id", "status": "simulated"}

    resend.api_key = settings.RESEND_API_KEY
    results = {}

    # 1. Correo interno para el equipo
    internal_html = _get_base_html(
        title=f"Nueva Consulta: {motivo}",
        content_html=f"""
        <span class="badge">NUEVA CONSULTA RECIBIDA</span>
        <h2 style="color: #883F9B; margin-top: 0;">Consulta desde el Portal Web</h2>
        <p>Has recibido un nuevo mensaje a través del formulario de contacto institucional:</p>
        
        <div class="card">
            <p style="margin: 4px 0;"><strong>Nombre:</strong> {nombre}</p>
            <p style="margin: 4px 0;"><strong>Correo:</strong> <a href="mailto:{email}">{email}</a></p>
            <p style="margin: 4px 0;"><strong>Teléfono / WhatsApp:</strong> {telefono}</p>
            <p style="margin: 4px 0;"><strong>Motivo:</strong> {motivo}</p>
        </div>

        <h3 style="color: #883F9B; font-size: 16px;">Mensaje o Consulta:</h3>
        <blockquote style="background: #FFFFFF; border-left: 4px solid #883F9B; margin: 0; padding: 12px 16px; font-style: italic; color: #4B5563;">
            {mensaje}
        </blockquote>
        <br>
        <p style="font-size: 13px; color: #6B7280;">Por favor, responder antes del plazo de 24 horas hábiles.</p>
        """
    )

    try:
        res_internal = resend.Emails.send({
            "from": settings.RESEND_FROM_EMAIL,
            "to": [settings.NOTIFICATION_EMAIL],
            "subject": f"[{motivo}] Mensaje de {nombre} - Dulce Paz Web",
            "html": internal_html,
        })
        results["internal"] = res_internal
    except Exception as e:
        logger.error(f"Error enviando correo interno: {e}")
        results["internal_error"] = str(e)

    # 2. Correo de acuse de recibo al usuario
    user_html = _get_base_html(
        title="Hemos recibido tu mensaje - Dulce Paz",
        content_html=f"""
        <span class="badge">HEMOS RECIBIDO TU CONSULTA</span>
        <h2 style="color: #883F9B; margin-top: 0;">Hola, {nombre}</h2>
        <p>Gracias por comunicarte con el equipo de <strong>Dulce Paz | Psicología y Salud Mental</strong>.</p>
        <p>Queremos confirmarte que recibimos tu mensaje respecto a: <strong>{motivo}</strong>.</p>
        
        <div class="card">
            <p style="margin: 0; font-size: 14px;">Un miembro de nuestro equipo profesional revisará tu solicitud y se pondrá en contacto contigo en un plazo máximo de <strong>24 horas hábiles</strong>.</p>
        </div>

        <p>Si tu consulta requiere atención inmediata o deseas agendar una cita directamente, puedes utilizar nuestro agendador en línea:</p>
        <div style="text-align: center;">
            <a href="https://dulcepaz.com/agendar" class="btn">Agendar una Cita Ahora</a>
        </div>
        """
    )

    try:
        res_user = resend.Emails.send({
            "from": settings.RESEND_FROM_EMAIL,
            "to": [email],
            "subject": f"Hemos recibido tu consulta - Dulce Paz",
            "html": user_html,
        })
        results["user"] = res_user
    except Exception as e:
        logger.error(f"Error enviando correo de confirmación al usuario: {e}")
        results["user_error"] = str(e)

    return results


def send_event_rsvp_confirmation(rsvp_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Envía el pase digital y confirmación de asistencia al Desayuno Corporativo (Código QR 1).
    """
    company = rsvp_data.get("company_name") or rsvp_data.get("companyName", "")
    representative = rsvp_data.get("representative_name") or rsvp_data.get("representativeName", "")
    job_title = rsvp_data.get("job_title") or rsvp_data.get("jobTitle", "")
    email = rsvp_data.get("email", "")
    attendees = rsvp_data.get("attendees_count") or rsvp_data.get("attendeesCount", 1)
    pass_code = rsvp_data.get("pass_code") or rsvp_data.get("passCode", "CORP-DP-0000")

    if not settings.RESEND_API_KEY or settings.RESEND_API_KEY.startswith("re_placeholder") or settings.RESEND_API_KEY == "":
        logger.info(f"[SIMULACIÓN EMAIL RESEND] Pase de evento {pass_code} para {email} procesado en modo local.")
        return {"id": "mock-event-email-id", "passCode": pass_code, "status": "simulated"}

    resend.api_key = settings.RESEND_API_KEY

    event_html = _get_base_html(
        title=f"Pase Institucional VIP: {pass_code}",
        content_html=f"""
        <span class="badge">ACREDITACIÓN CORPORATIVA OFICIAL</span>
        <h2 style="color: #883F9B; margin-top: 0;">¡Asistencia Confirmada!</h2>
        <p>Estimado(a) <strong>{representative}</strong> ({job_title}),</p>
        <p>Es un placer para el equipo de <strong>Dulce Paz</strong> confirmar la participación de <strong>{company}</strong> en nuestro próximo encuentro:</p>
        
        <div class="card" style="border-left: 4px solid #2A8ED1;">
            <h3 style="margin-top: 0; color: #883F9B;">Desayuno de Trabajo Corporativo: Salud Mental en las Organizaciones</h3>
            <p style="margin: 6px 0;"><strong>📅 Fecha:</strong> Viernes, 23 de Octubre de 2026</p>
            <p style="margin: 6px 0;"><strong>⏰ Horario:</strong> 10:00 a 12:00 (Hora de Bolivia GMT-4)</p>
            <p style="margin: 6px 0;"><strong>📍 Sede:</strong> Auditorio Dulce Paz (Calle 15 de Calacoto, Edificio Parque, La Paz)</p>
            <p style="margin: 6px 0;"><strong>👥 Delegados Acreditados:</strong> {attendees} {'persona' if attendees == 1 else 'personas'}</p>
        </div>

        <div style="text-align: center; background-color: #883F9B; color: #FFFFFF; border-radius: 14px; padding: 18px; margin: 20px 0;">
            <span style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; display: block; opacity: 0.9;">CÓDIGO DE ACCESO / PASE VIP</span>
            <span style="font-size: 26px; font-weight: 800; letter-spacing: 2px; font-family: monospace; display: block; margin-top: 4px;">{pass_code}</span>
        </div>

        <p style="font-size: 13px; color: #4B5563;">Presenta este código al ingresar en la recepción del auditorio para recibir las credenciales y material de trabajo del evento.</p>
        """
    )

    try:
        res = resend.Emails.send({
            "from": settings.RESEND_FROM_EMAIL,
            "to": [email],
            "subject": f"Pase Institucional: Desayuno de Salud Mental [{pass_code}] - Dulce Paz",
            "html": event_html,
        })
        return res
    except Exception as e:
        logger.error(f"Error enviando correo de confirmación de evento: {e}")
        return {"error": str(e)}
