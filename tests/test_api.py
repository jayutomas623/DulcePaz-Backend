"""
Suite de Pruebas Automatizadas para Dulce Paz API.
Cubre endpoints base, Contacto, Eventos QR 1 y stubs de arquitectura.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.email_service import (
    _get_base_html,
    send_contact_notification,
    send_event_rsvp_confirmation
)

client = TestClient(app)


def test_root_endpoint():
    """Verifica que el endpoint raíz responda con los metadatos de la API."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Dulce Paz" in data["app"]


def test_health_check():
    """Verifica que el health check reporte estado saludable y la zona horaria correcta."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["timezone"] == "America/La_Paz"


def test_contact_submission_success():
    """Prueba el envío exitoso de un formulario de contacto."""
    payload = {
        "nombre": "Lic. María Flores",
        "email": "maria.flores@ejemplo.com",
        "telefono": "+591 76543210",
        "motivo": "Consulta general",
        "mensaje": "Quisiera información sobre los aranceles para terapia de pareja."
    }
    response = client.post("/api/v1/contact", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == payload["nombre"]
    assert data["email"] == payload["email"]
    assert data["status"] == "pending"
    assert "id" in data
    assert data["id"] is not None


def test_contact_submission_validation_error():
    """Prueba que los campos obligatorios o emails inválidos devuelvan error 422."""
    payload = {
        "nombre": "A", # Demasiado corto (< 3)
        "email": "correo-invalido",
        "mensaje": "" # Vacío (< 5)
    }
    response = client.post("/api/v1/contact", json=payload)
    assert response.status_code == 422


def test_events_info():
    """Prueba que el endpoint informativo del Desayuno de Salud Mental devuelva los datos oficiales."""
    response = client.get("/api/v1/events/info")
    assert response.status_code == 200
    data = response.json()
    assert "Desayuno de Trabajo Corporativo" in data["event_name"]
    assert data["max_attendees_per_company"] == 3


def test_event_rsvp_camelcase_payload():
    """
    Prueba que el endpoint /api/v1/events/rsvp acepte el payload en formato camelCase
    generado por el componente TypeScript de Next.js (app/registro-evento/page.tsx).
    """
    payload = {
        "companyName": "Banco de Desarrollo S.A.",
        "representativeName": "Ing. Roberto Siles",
        "jobTitle": "Director de Gestión Humana",
        "phone": "+591 71234567",
        "email": "rsiles@bancodesarrollo.com.bo",
        "attendeesCount": 2
    }
    response = client.post("/api/v1/events/rsvp", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["companyName"] == payload["companyName"]
    assert data["representativeName"] == payload["representativeName"]
    assert data["attendeesCount"] == 2
    assert data["passCode"].startswith("CORP-DP-")
    assert data["status"] == "confirmed"


def test_event_rsvp_snakecase_payload():
    """
    Prueba que el endpoint /api/v1/events/rsvp acepte también nombres en snake_case.
    """
    payload = {
        "company_name": "Industrias Andinas Ltda.",
        "representative_name": "Lic. Valeria Rios",
        "job_title": "Jefe de Bienestar y Salud Ocupacional",
        "phone": "+591 79876543",
        "email": "vrios@industriasandinas.bo",
        "attendees_count": 3
    }
    response = client.post("/api/v1/events/rsvp", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["companyName"] == payload["company_name"]
    assert data["attendeesCount"] == 3
    assert data["passCode"].startswith("CORP-DP-")


def test_event_rsvp_max_attendees_limit():
    """Prueba que el límite de 3 delegados por institución sea validado estrictamente."""
    payload = {
        "companyName": "Empresa Minera Central",
        "representativeName": "Carlos Camacho",
        "jobTitle": "Supervisor",
        "phone": "+591 70000000",
        "email": "ccamacho@minera.bo",
        "attendeesCount": 4 # Supera el máximo permitido (1 a 3)
    }
    response = client.post("/api/v1/events/rsvp", json=payload)
    assert response.status_code == 422


def test_email_service_templates():
    """Verifica que el generador de HTML de Resend cree plantillas válidas con los colores oficiales."""
    html = _get_base_html("Prueba", "<p>Contenido de prueba</p>")
    assert "#883F9B" in html # Passionate Purple
    assert "#2A8ED1" in html # Ticino Blueous
    assert "#F7F7E8" in html # Pure Beige

    # Notificaciones en modo local/mock
    contact_res = send_contact_notification({
        "nombre": "Test User",
        "email": "test@test.com",
        "mensaje": "Mensaje de prueba"
    })
    assert "status" in contact_res

    rsvp_res = send_event_rsvp_confirmation({
        "company_name": "Empresa Test",
        "representative_name": "Delegado Test",
        "email": "delegado@test.com",
        "pass_code": "CORP-DP-9999"
    })
    assert "status" in rsvp_res or "passCode" in rsvp_res


def test_availability_slots_stub():
    """Verifica que el router de disponibilidad de horarios responda correctamente."""
    response = client.get("/api/v1/availability/slots?date=2026-10-15&therapistId=nikki-paz")
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == "2026-10-15"
    assert data["therapistId"] == "nikki-paz"
    assert len(data["slots"]) > 0


def test_booking_creation_stub():
    """Verifica que el router de creación de citas del Wizard procese el contrato Zod correctamente."""
    payload = {
        "serviceId": "individual",
        "modality": "virtual",
        "therapistId": "nikki-paz",
        "date": "2026-10-15",
        "timeSlot": "10:30",
        "clientName": "Ana Morales",
        "clientPhone": "+591 76543210",
        "clientEmail": "ana.morales@ejemplo.com",
        "consultationReason": "Manejo de ansiedad",
        "consentAccepted": True
    }
    response = client.post("/api/v1/bookings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["bookingReference"].startswith("DP-2026-")
    assert data["modality"] == "virtual"
    assert "meet.google.com" in data["locationOrMeetLink"]
