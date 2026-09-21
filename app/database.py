"""
Conexión oficial con Supabase PostgreSQL y capa de persistencia clínica.
Provee una instancia singleton del cliente de Supabase para operaciones en base de datos,
así como repositorios sincronizados para citas, disponibilidad y bloqueos administrativos.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger("dulcepaz.database")

_supabase_client: Optional[Client] = None

# Catálogo institucional de especialistas
THERAPISTS_CATALOG: Dict[str, Dict[str, Any]] = {
    "nikki-paz": {
        "id": "nikki-paz",
        "name": "Lic. Nikki Paz",
        "email": "nikki@dulcepaz.com",
        "role": "Coordinadora General / Psicóloga Clínica",
        "specialty": "Terapia de pareja, ansiedad, duelo y terapia intercultural bilingüe (Español/Inglés)",
        "services": ["individual", "pareja", "familiar", "talleres"],
        "avatar_url": "/team/nikki.jpg",
    },
    "keila-vilar": {
        "id": "keila-vilar",
        "name": "Lic. Keila Vilar",
        "email": "keila@dulcepaz.com",
        "role": "Especialista Psicopedagógica",
        "specialty": "Acompañamiento infanto-juvenil, hábitos de estudio y orientación vocacional",
        "services": ["vocacional", "adolescentes", "talleres"],
        "avatar_url": "/team/keila.jpg",
    },
    "william-mendoza": {
        "id": "william-mendoza",
        "name": "Lic. William Mendoza",
        "email": "william@dulcepaz.com",
        "role": "Psicólogo Organizacional",
        "specialty": "Salud ocupacional, clima corporativo, consultoría y selección de talento",
        "services": ["organizacional", "talleres"],
        "avatar_url": "/team/william.jpg",
    },
}

SERVICES_CATALOG: Dict[str, str] = {
    "individual": "Psicoterapia Individual",
    "pareja": "Terapia de Pareja",
    "familiar": "Terapia Familiar",
    "vocacional": "Orientación Vocacional",
    "adolescentes": "Terapia para Adolescentes (13+)",
    "organizacional": "Psicología Organizacional",
    "talleres": "Psicoeducación (Talleres y Espacios de Escucha)",
}

STANDARD_TIME_SLOTS: List[str] = ["09:00", "10:30", "14:30", "16:00", "17:30"]

# Almacén en memoria para simulación local / pruebas automatizadas
_MOCK_BOOKINGS: List[Dict[str, Any]] = [
    {
        "id": "apt-1",
        "booking_reference": "DP-2026-1001",
        "service_id": "individual",
        "service_name": "Psicoterapia Individual",
        "modality": "presencial",
        "therapist_id": "nikki-paz",
        "therapist_name": "Lic. Nikki Paz",
        "appointment_date": "2026-09-24",
        "time_slot": "09:00",
        "client_name": "Sofía Montenegro",
        "client_phone": "+591 76543210",
        "client_email": "sofia.montenegro@gmail.com",
        "consultation_reason": "Regulación de ansiedad cotidiana y duelo afectivo reciente.",
        "status": "confirmed",
        "location_or_meet_link": "Calle 15 de Calacoto, Edif. Parque, La Paz",
        "created_at": "2026-09-20T10:00:00",
    },
    {
        "id": "apt-2",
        "booking_reference": "DP-2026-1002",
        "service_id": "pareja",
        "service_name": "Terapia de Pareja",
        "modality": "virtual",
        "therapist_id": "nikki-paz",
        "therapist_name": "Lic. Nikki Paz",
        "appointment_date": "2026-09-24",
        "time_slot": "10:30",
        "client_name": "Carlos Arguedas & Elena Rossi",
        "client_phone": "+591 71234567",
        "client_email": "arguedas.rossi@outlook.com",
        "consultation_reason": "Mediación de comunicación y diferencias por adaptación bicultural.",
        "status": "confirmed",
        "location_or_meet_link": "https://meet.google.com/dpz-nikki-sesion",
        "meet_url": "https://meet.google.com/dpz-nikki-sesion",
        "created_at": "2026-09-20T11:00:00",
    },
    {
        "id": "apt-3",
        "booking_reference": "DP-2026-1003",
        "service_id": "adolescentes",
        "service_name": "Terapia para Adolescentes (13+)",
        "modality": "presencial",
        "therapist_id": "keila-vilar",
        "therapist_name": "Lic. Keila Vilar",
        "appointment_date": "2026-09-24",
        "time_slot": "09:00",
        "client_name": "Matías Calderón (15 años)",
        "client_phone": "+591 77654321",
        "client_email": "m.calderon@familia.bo",
        "consultation_reason": "Presión escolar, autoestima y gestión de emociones en pubertad.",
        "status": "confirmed",
        "location_or_meet_link": "Calle 15 de Calacoto, Edif. Parque, La Paz",
        "created_at": "2026-09-20T12:00:00",
    },
]

_MOCK_BLOCKED_SCHEDULES: List[Dict[str, Any]] = [
    {
        "id": "block-1",
        "therapist_id": "nikki-paz",
        "date": "2026-09-24",
        "time_slot": "14:30",
        "reason": "Supervisión Clínica y Reunión Institucional",
        "created_at": "2026-09-20T08:00:00",
    }
]


def get_supabase_client() -> Optional[Client]:
    """
    Retorna la instancia del cliente Supabase.
    Usa la clave de servicio (service_role) para operaciones del backend con permisos elevados.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    supabase_url = settings.SUPABASE_URL
    supabase_key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY

    # Validar si son claves placeholder de desarrollo
    if not supabase_url or "placeholder" in supabase_url or not supabase_key or "placeholder" in supabase_key:
        return None

    try:
        _supabase_client = create_client(supabase_url, supabase_key)
        logger.info("Cliente de Supabase inicializado correctamente.")
        return _supabase_client
    except Exception as e:
        logger.error(f"Error al conectar con Supabase: {e}")
        return None


# ------------------------------------------------------------------------------
# MÉTODOS DE REPOSITORIO PARA CITAS Y DISPONIBILIDAD
# ------------------------------------------------------------------------------

def is_slot_booked_or_blocked(therapist_id: str, date_str: str, time_slot: str) -> bool:
    """
    Verifica si una franja horaria está ocupada por una cita confirmada o bloqueada manualmente.
    Consulta primero Supabase; si no está disponible, utiliza la memoria local.
    """
    client = get_supabase_client()
    if client:
        try:
            # 1. Comprobar citas activas
            res_b = client.table("bookings").select("id").eq("therapist_id", therapist_id).eq("appointment_date", date_str).eq("time_slot", time_slot).neq("status", "cancelled_by_patient").execute()
            if res_b.data and len(res_b.data) > 0:
                return True

            # 2. Comprobar bloqueos manuales
            res_bl = client.table("blocked_schedules").select("id").eq("therapist_id", therapist_id).eq("date", date_str).eq("time_slot", time_slot).execute()
            if res_bl.data and len(res_bl.data) > 0:
                return True

            return False
        except Exception as e:
            logger.warning(f"Error consultando colisiones en Supabase: {e}. Evaluando en memoria.")

    # Evaluación en memoria (fallback)
    for b in _MOCK_BOOKINGS:
        if (
            b.get("therapist_id") == therapist_id
            and b.get("appointment_date") == date_str
            and b.get("time_slot") == time_slot
            and b.get("status") != "cancelled_by_patient"
        ):
            return True

    for bl in _MOCK_BLOCKED_SCHEDULES:
        if (
            bl.get("therapist_id") == therapist_id
            and bl.get("date") == date_str
            and bl.get("time_slot") == time_slot
        ):
            return True

    return False


def find_available_therapist_for_slot(service_id: str, date_str: str, time_slot: str) -> Optional[str]:
    """
    Asigna automáticamente el primer especialista calificado para el servicio
    que tenga disponibilidad libre en la franja seleccionada.
    """
    # Filtrar terapeutas habilitados para el servicio elegido
    qualified = [
        tid for tid, data in THERAPISTS_CATALOG.items()
        if service_id in data.get("services", [])
    ]

    for tid in qualified:
        if not is_slot_booked_or_blocked(tid, date_str, time_slot):
            return tid

    return None


def get_booked_and_blocked_slots(therapist_id: str, date_str: str) -> set[str]:
    """
    Obtiene el conjunto de horas ocupadas o bloqueadas para un terapeuta en una fecha dada.
    """
    occupied: set[str] = set()
    client = get_supabase_client()
    if client:
        try:
            res_b = client.table("bookings").select("time_slot").eq("therapist_id", therapist_id).eq("appointment_date", date_str).neq("status", "cancelled_by_patient").execute()
            if res_b.data:
                for row in res_b.data:
                    occupied.add(row["time_slot"])

            res_bl = client.table("blocked_schedules").select("time_slot").eq("therapist_id", therapist_id).eq("date", date_str).execute()
            if res_bl.data:
                for row in res_bl.data:
                    occupied.add(row["time_slot"])
            return occupied
        except Exception as e:
            logger.warning(f"Error consultando slots en Supabase: {e}. Usando memoria local.")

    for b in _MOCK_BOOKINGS:
        if (
            b.get("therapist_id") == therapist_id
            and b.get("appointment_date") == date_str
            and b.get("status") != "cancelled_by_patient"
        ):
            occupied.add(b.get("time_slot", ""))

    for bl in _MOCK_BLOCKED_SCHEDULES:
        if bl.get("therapist_id") == therapist_id and bl.get("date") == date_str:
            occupied.add(bl.get("time_slot", ""))

    return occupied


def save_booking_record(booking_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Persiste la cita en Supabase y actualiza el almacén en memoria.
    """
    client = get_supabase_client()
    if client:
        try:
            # Adecuar campos para la tabla PostgreSQL
            db_payload = {
                "id": booking_data.get("id"),
                "booking_reference": booking_data.get("booking_reference"),
                "service_id": booking_data.get("service_id"),
                "modality": booking_data.get("modality"),
                "therapist_id": booking_data.get("therapist_id"),
                "appointment_date": booking_data.get("appointment_date"),
                "time_slot": booking_data.get("time_slot"),
                "client_name": booking_data.get("client_name"),
                "client_phone": booking_data.get("client_phone"),
                "client_email": booking_data.get("client_email"),
                "consultation_reason": booking_data.get("consultation_reason"),
                "consent_accepted": booking_data.get("consent_accepted", True),
                "google_event_id": booking_data.get("google_event_id"),
                "google_meet_link": booking_data.get("google_meet_link"),
                "status": booking_data.get("status", "confirmed"),
            }
            client.table("bookings").insert(db_payload).execute()
            logger.info(f"Cita guardada en Supabase: {booking_data.get('booking_reference')}")
        except Exception as e:
            logger.error(f"Error insertando cita en Supabase: {e}. Guardando en memoria local.")

    _MOCK_BOOKINGS.append(booking_data)
    return booking_data


def get_agenda_bookings(date_str: Optional[str] = None, therapist_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Devuelve las citas agendadas filtradas opcionalmente por fecha y especialista.
    """
    client = get_supabase_client()
    if client:
        try:
            query = client.table("bookings").select("*")
            if date_str:
                query = query.eq("appointment_date", date_str)
            if therapist_id and therapist_id != "all":
                query = query.eq("therapist_id", therapist_id)
            res = query.order("appointment_date").order("time_slot").execute()
            if res.data is not None and len(res.data) > 0:
                results = []
                for item in res.data:
                    tid = item.get("therapist_id", "")
                    tname = THERAPISTS_CATALOG.get(tid, {}).get("name", tid)
                    sid = item.get("service_id", "")
                    sname = SERVICES_CATALOG.get(sid, sid)
                    results.append({
                        "id": str(item.get("id")),
                        "booking_reference": item.get("booking_reference", ""),
                        "therapist_id": tid,
                        "therapist_name": tname,
                        "service_id": sid,
                        "service_name": sname,
                        "time": item.get("time_slot", ""),
                        "date": str(item.get("appointment_date", "")),
                        "client_name": item.get("client_name", ""),
                        "client_phone": item.get("client_phone", ""),
                        "client_email": item.get("client_email", ""),
                        "modality": item.get("modality", "presencial"),
                        "consultation_reason": item.get("consultation_reason"),
                        "status": item.get("status", "confirmed"),
                        "meet_url": item.get("google_meet_link"),
                        "admin_notes": item.get("admin_notes"),
                        "created_at": item.get("created_at"),
                    })
                return results
        except Exception as e:
            logger.warning(f"Error consultando agenda en Supabase: {e}. Usando memoria local.")

    # Filtro en memoria
    results = []
    for b in _MOCK_BOOKINGS:
        if date_str and b.get("appointment_date") != date_str:
            continue
        if therapist_id and therapist_id != "all" and b.get("therapist_id") != therapist_id:
            continue

        tid = b.get("therapist_id", "")
        tname = THERAPISTS_CATALOG.get(tid, {}).get("name", tid)
        sid = b.get("service_id", "")
        sname = SERVICES_CATALOG.get(sid, sid)

        results.append({
            "id": str(b.get("id")),
            "booking_reference": b.get("booking_reference", ""),
            "therapist_id": tid,
            "therapist_name": tname,
            "service_id": sid,
            "service_name": sname,
            "time": b.get("time_slot", ""),
            "date": str(b.get("appointment_date", "")),
            "client_name": b.get("client_name", ""),
            "client_phone": b.get("client_phone", ""),
            "client_email": b.get("client_email", ""),
            "modality": b.get("modality", "presencial"),
            "consultation_reason": b.get("consultation_reason"),
            "status": b.get("status", "confirmed"),
            "meet_url": b.get("meet_url") or b.get("google_meet_link"),
            "admin_notes": b.get("admin_notes"),
            "created_at": b.get("created_at"),
        })

    return results


def update_booking_status_in_db(booking_id: str, new_status: str, admin_notes: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Actualiza el estado de una cita en Supabase y en memoria.
    """
    client = get_supabase_client()
    if client:
        try:
            update_payload: Dict[str, Any] = {
                "status": new_status,
                "updated_at": datetime.now().isoformat()
            }
            if admin_notes is not None:
                update_payload["admin_notes"] = admin_notes

            res = client.table("bookings").update(update_payload).eq("id", booking_id).execute()
            if res.data and len(res.data) > 0:
                logger.info(f"Estado de cita {booking_id} actualizado en Supabase a {new_status}")
        except Exception as e:
            logger.warning(f"Error actualizando estado en Supabase: {e}")

    # Actualizar en memoria
    for b in _MOCK_BOOKINGS:
        if str(b.get("id")) == str(booking_id) or b.get("booking_reference") == booking_id:
            b["status"] = new_status
            if admin_notes is not None:
                b["admin_notes"] = admin_notes
            return b

    return {"id": booking_id, "status": new_status, "admin_notes": admin_notes}


def save_schedule_block(therapist_id: str, date_str: str, time_slot: str, reason: Optional[str] = None) -> Dict[str, Any]:
    """
    Registra una franja inhabilitada en blocked_schedules.
    """
    block_id = str(uuid.uuid4())
    block_record = {
        "id": block_id,
        "therapist_id": therapist_id,
        "date": date_str,
        "time_slot": time_slot,
        "reason": reason or "No disponible / Bloqueo administrativo",
        "created_at": datetime.now().isoformat(),
    }

    client = get_supabase_client()
    if client:
        try:
            client.table("blocked_schedules").insert(block_record).execute()
            logger.info(f"Bloqueo registrado en Supabase: {therapist_id} {date_str} {time_slot}")
        except Exception as e:
            logger.warning(f"Error registrando bloqueo en Supabase: {e}")

    _MOCK_BLOCKED_SCHEDULES.append(block_record)
    return block_record


def get_blocked_schedules(therapist_id: Optional[str] = None, date_str: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Obtiene la lista de horarios bloqueados.
    """
    client = get_supabase_client()
    if client:
        try:
            q = client.table("blocked_schedules").select("*")
            if therapist_id:
                q = q.eq("therapist_id", therapist_id)
            if date_str:
                q = q.eq("date", date_str)
            res = q.execute()
            if res.data is not None and len(res.data) > 0:
                return res.data
        except Exception as e:
            logger.warning(f"Error consultando blocked_schedules en Supabase: {e}")

    results = []
    for bl in _MOCK_BLOCKED_SCHEDULES:
        if therapist_id and bl.get("therapist_id") != therapist_id:
            continue
        if date_str and bl.get("date") != date_str:
            continue
        results.append(bl)
    return results


def delete_schedule_block(block_id: str) -> bool:
    """
    Elimina un bloqueo de horario.
    """
    global _MOCK_BLOCKED_SCHEDULES
    client = get_supabase_client()
    if client:
        try:
            client.table("blocked_schedules").delete().eq("id", block_id).execute()
        except Exception as e:
            logger.warning(f"Error eliminando bloqueo en Supabase: {e}")

    initial_len = len(_MOCK_BLOCKED_SCHEDULES)
    _MOCK_BLOCKED_SCHEDULES = [b for b in _MOCK_BLOCKED_SCHEDULES if str(b.get("id")) != str(block_id)]
    return len(_MOCK_BLOCKED_SCHEDULES) < initial_len or True

