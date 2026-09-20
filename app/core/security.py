"""
Seguridad y Autenticación para Dulce Paz API.
Gestión de cabeceras de autorización y validación de tokens de Supabase Auth.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security_scheme = HTTPBearer(auto_error=False)


async def get_current_admin_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme)
) -> Dict[str, Any]:
    """
    Valida las credenciales de acceso para endpoints de administración (/admin).
    Acepta el token JWT emitido por Supabase Auth o la clave administrativa secreta.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere token de autorización Bearer",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # 1. Verificación rápida contra ADMIN_SECRET_KEY para llamadas internas/servicios
    if settings.ADMIN_SECRET_KEY and token == settings.ADMIN_SECRET_KEY:
        return {"sub": "service-admin", "role": "admin", "email": "admin@dulcepaz.com"}

    # 2. Validación de sesión con Supabase Auth
    # [Colaborador 2 expandirá con supabase.auth.get_user(token)]
    try:
        from app.database import get_supabase_client
        supabase = get_supabase_client()
        if supabase:
            user_response = supabase.auth.get_user(token)
            if user_response and user_response.user:
                return {
                    "sub": user_response.user.id,
                    "email": user_response.user.email,
                    "role": user_response.user.role or "authenticated"
                }
    except Exception:
        pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o sesión expirada",
        headers={"WWW-Authenticate": "Bearer"},
    )
