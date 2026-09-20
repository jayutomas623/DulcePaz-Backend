"""
Conexión oficial con Supabase PostgreSQL.
Provee una instancia singleton del cliente de Supabase para operaciones en base de datos.
"""

import logging
from typing import Optional
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger("dulcepaz.database")

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """
    Retorna la instancia del cliente Supabase.
    Usa la clave de servicio (service_role) para operaciones del backend con permisos elevados,
    o la clave anónima como alternativa.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    supabase_url = settings.SUPABASE_URL
    # Preferir service role key para el backend (permite inserción/lectura administrativa saltando RLS cuando corresponde)
    supabase_key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY

    # Validar si son claves placeholder de desarrollo
    if not supabase_url or "placeholder" in supabase_url or not supabase_key or "placeholder" in supabase_key:
        logger.warning(
            "Supabase URL o Key no configurados con valores reales. "
            "Operando en modo desarrollo local/mock."
        )
        return None

    try:
        _supabase_client = create_client(supabase_url, supabase_key)
        logger.info("Cliente de Supabase inicializado correctamente.")
        return _supabase_client
    except Exception as e:
        logger.error(f"Error al conectar con Supabase: {e}")
        return None
