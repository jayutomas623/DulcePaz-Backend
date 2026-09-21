"""
Suite de Pruebas Automatizadas para Colaborador 2:
- Motor de Agendamiento de Citas (/api/v1/bookings)
- Disponibilidad en Tiempo Real (/api/v1/availability/slots)
- Integraciones Google Calendar/Meet y Meta WhatsApp Cloud API
- Panel Administrativo (/api/v1/admin/*)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.calendar_service import calendar_service
from app.services.whatsapp_service import whatsapp_service

from app.core.config import settings

client = TestClient(app)
AUTH_HEADERS = {"Authorization": f"Bearer {settings.ADMIN_SECRET_KEY}"}


def test_availability_weekday_standard_slots():
    """Verifica que un día hábil (jueves 15 de octubre de 2026) devuelva las 5 franjas horarias."""
    response = client.get("/api/v1/availability/slots?date=2026-10-15&therapistId=nikki-paz")
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == "2026-10-15"
    assert data["therapistId"] == "nikki-paz"
    assert data["timezone"] == "America/La_Paz"
    assert len(data["slots"]) == 5
    times = [s["time"] for s in data["slots"]]
    assert "09:00" in times
    assert "10:30" in times
    assert "14:30" in times
    assert "16:00" in times
    assert "17:30" in times


def test_availability_sunday_closed():
    """Verifica que los domingos (18 de octubre de 2026) el centro reporte 0 slots disponibles."""
    response = client.get("/api/v1/availability/slots?date=2026-10-18&therapistId=nikki-paz")
    assert response.status_code == 200
    data = response.json()
    assert data["slots"] == []


def test_availability_any_therapist():
    """Verifica la consulta de disponibilidad cuando se selecciona 'any'."""
    response = client.get("/api/v1/availability/slots?date=2026-10-21&therapistId=any")
    assert response.status_code == 200
    data = response.json()
    assert data["therapistId"] == "any"
    assert len(data["slots"]) == 5
    assert any(s["isAvailable"] for s in data["slots"])


def test_booking_creation_presencial_calacoto():
    """Verifica el agendamiento presencial asignando la dirección de Calacoto."""
    payload = {
        "serviceId": "individual",
        "modality": "presencial",
        "therapistId": "nikki-paz",
        "date": "2026-10-22",
        "timeSlot": "09:00",
        "clientName": "Gabriel Cornejo",
        "clientPhone": "+591 76543210",
        "clientEmail": "gabriel.cornejo@email.com",
        "consultationReason": "Manejo de estrés laboral",
        "consentAccepted": True
    }
    response = client.post("/api/v1/bookings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["bookingReference"].startswith("DP-2026-")
    assert data["modality"] == "presencial"
    assert "Calacoto" in data["locationOrMeetLink"]
    assert "wa.me" in data["whatsappFallbackUrl"]
    assert data["status"] == "confirmed"


def test_booking_creation_virtual_meet():
    """Verifica el agendamiento virtual inyectando enlace Google Meet."""
    payload = {
        "serviceId": "pareja",
        "modality": "virtual",
        "therapistId": "nikki-paz",
        "date": "2026-10-22",
        "timeSlot": "10:30",
        "clientName": "Rodrigo Paz & Andrea Rios",
        "clientPhone": "+591 71239988",
        "clientEmail": "rodrigo.andrea@email.com",
        "consultationReason": "Terapia de pareja bilingüe",
        "consentAccepted": True
    }
    response = client.post("/api/v1/bookings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["bookingReference"].startswith("DP-2026-")
    assert data["modality"] == "virtual"
    assert "meet.google.com" in data["locationOrMeetLink"]
    assert "meet.google.com" in data["googleMeetLink"]


def test_booking_collision_anti_collision_409():
    """Verifica que dos pacientes no puedan reservar al mismo terapeuta en el mismo slot."""
    payload = {
        "serviceId": "individual",
        "modality": "presencial",
        "therapistId": "william-mendoza",
        "date": "2026-10-27",
        "timeSlot": "16:00",
        "clientName": "Paciente Uno",
        "clientPhone": "+591 70001122",
        "clientEmail": "paciente1@email.com",
        "consentAccepted": True
    }
    # Primera reserva: exitosa
    res1 = client.post("/api/v1/bookings", json=payload)
    assert res1.status_code == 201

    # Segunda reserva idéntica: colisión 409
    payload_dupe = payload.copy()
    payload_dupe["clientName"] = "Paciente Dos"
    payload_dupe["clientEmail"] = "paciente2@email.com"
    res2 = client.post("/api/v1/bookings", json=payload_dupe)
    assert res2.status_code == 409
    assert "ya no se encuentra disponible" in res2.json()["detail"]


def test_booking_auto_assignment_any():
    """Verifica asignación automática de especialista calificado cuando therapistId == 'any'."""
    payload = {
        "serviceId": "vocacional", # Calificada exclusivamente: Keila Vilar
        "modality": "virtual",
        "therapistId": "any",
        "date": "2026-10-28",
        "timeSlot": "14:30",
        "clientName": "Mateo Soria",
        "clientPhone": "+591 76998811",
        "clientEmail": "mateo.soria@colegio.edu.bo",
        "consentAccepted": True
    }
    response = client.post("/api/v1/bookings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["therapistId"] == "keila-vilar"
    assert "Keila Vilar" in data["therapistName"]


def test_booking_sunday_rejected():
    """Verifica que intentar agendar en domingo devuelva 400 Bad Request."""
    payload = {
        "serviceId": "individual",
        "modality": "presencial",
        "therapistId": "nikki-paz",
        "date": "2026-10-25", # Domingo
        "timeSlot": "09:00",
        "clientName": "Test Domingo",
        "clientPhone": "+591 70000000",
        "clientEmail": "test@domingo.com",
        "consentAccepted": True
    }
    response = client.post("/api/v1/bookings", json=payload)
    assert response.status_code == 400
    assert "domingos" in response.json()["detail"]


@pytest.mark.asyncio
async def test_calendar_service_direct():
    """Verifica la función create_appointment_event de CalendarService."""
    res_presencial = await calendar_service.create_appointment_event(
        therapist_id="nikki-paz",
        therapist_email="nikki@dulcepaz.com",
        service_title="Psicoterapia Individual",
        modality="presencial",
        appointment_date="2026-10-15",
        time_slot="09:00",
        client_name="Test Directo",
        client_email="test@directo.com",
        client_phone="+591 76543210"
    )
    assert res_presencial["status"] == "confirmed"
    assert "Calacoto" in res_presencial["location"]
    assert res_presencial["google_meet_link"] is None

    res_virtual = await calendar_service.create_appointment_event(
        therapist_id="nikki-paz",
        therapist_email="nikki@dulcepaz.com",
        service_title="Terapia de Pareja",
        modality="virtual",
        appointment_date="2026-10-15",
        time_slot="10:30",
        client_name="Test Directo Virtual",
        client_email="test@directo.com",
        client_phone="+591 76543210"
    )
    assert res_virtual["status"] == "confirmed"
    assert "meet.google.com" in res_virtual["google_meet_link"]


@pytest.mark.asyncio
async def test_whatsapp_service_fallback_direct():
    """Verifica el despacho y plan de contingencia wa.me de WhatsAppService."""
    url = whatsapp_service.generate_fallback_url(
        client_name="Valeria Paz",
        service_name="Psicoterapia Individual",
        therapist_name="Lic. Nikki Paz",
        date_str="2026-10-15",
        time_str="09:00",
        meet_link_or_location="Calle 15 de Calacoto, La Paz",
        booking_ref="DP-2026-9999"
    )
    assert "wa.me" in url
    assert "59176543210" in url
    assert "DP-2026-9999" in url

    dispatch_res = await whatsapp_service.send_booking_confirmation(
        to_phone="+591 76543210",
        client_name="Valeria Paz",
        service_name="Psicoterapia Individual",
        therapist_name="Lic. Nikki Paz",
        date_str="2026-10-15",
        time_str="09:00",
        meet_link_or_location="Calle 15 de Calacoto, La Paz"
    )
    assert "fallback_url" in dispatch_res
    assert "status" in dispatch_res


def test_admin_endpoints_auth_protection():
    """Verifica que los endpoints administrativos requieran Bearer Token."""
    res_no_auth = client.get("/api/v1/admin/agenda")
    assert res_no_auth.status_code == 401

    res_auth = client.get("/api/v1/admin/agenda", headers=AUTH_HEADERS)
    assert res_auth.status_code == 200
    data = res_auth.json()
    assert "appointments" in data
    assert "total" in data


def test_admin_update_status():
    """Verifica el cambio de estado de una cita en el panel administrativo."""
    res = client.patch(
        "/api/v1/admin/bookings/apt-1/status",
        json={"status": "completed", "adminNotes": "Sesión concluida exitosamente."},
        headers=AUTH_HEADERS
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert data["admin_notes"] == "Sesión concluida exitosamente."


def test_admin_schedule_block_and_unblock_cycle():
    """
    Verifica el flujo completo de bloqueo de horario por administración:
    1. Bloquear horario -> Aparece en blocked-schedules.
    2. Comprobar que en availability se reporta como no disponible.
    3. Desbloquear horario -> Se elimina de blocked-schedules.
    """
    block_payload = {
        "therapistId": "william-mendoza",
        "date": "2026-10-29",
        "timeSlot": "09:00",
        "reason": "Reunión de directorio corporativo"
    }

    # 1. Bloquear
    res_block = client.post("/api/v1/admin/blocked-schedules", json=block_payload, headers=AUTH_HEADERS)
    assert res_block.status_code == 201
    block_data = res_block.json()
    block_id = block_data["id"]
    assert block_data["therapistId"] == "william-mendoza"
    assert block_data["timeSlot"] == "09:00"

    # 2. Verificar que availability marque el slot como ocupado
    res_avail = client.get("/api/v1/availability/slots?date=2026-10-29&therapistId=william-mendoza")
    assert res_avail.status_code == 200
    slots = res_avail.json()["slots"]
    slot_09 = next(s for s in slots if s["time"] == "09:00")
    assert slot_09["isAvailable"] is False

    # 3. Desbloquear
    res_del = client.delete(f"/api/v1/admin/blocked-schedules/{block_id}", headers=AUTH_HEADERS)
    assert res_del.status_code == 200
    assert res_del.json()["status"] == "deleted"

    # 4. Verificar que el slot vuelve a estar disponible
    res_avail2 = client.get("/api/v1/availability/slots?date=2026-10-29&therapistId=william-mendoza")
    assert res_avail2.status_code == 200
    slots2 = res_avail2.json()["slots"]
    slot_09_after = next(s for s in slots2 if s["time"] == "09:00")
    assert slot_09_after["isAvailable"] is True
