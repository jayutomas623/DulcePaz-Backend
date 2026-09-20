"""
Configuración centralizada de la aplicación Dulce Paz API.
Carga variables de entorno y provee validación fuertemente tipada con Pydantic Settings.
"""

from typing import List, Union
import json
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Proyecto y Rutas
    PROJECT_NAME: str = "Dulce Paz API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    TIMEZONE: str = "America/La_Paz"

    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://dulcepaz.com",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000"]

    # Supabase (PostgreSQL / Auth / Storage)
    SUPABASE_URL: str = "https://placeholder-project.supabase.co"
    SUPABASE_KEY: str = "placeholder-anon-key"
    SUPABASE_SERVICE_ROLE_KEY: str = "placeholder-service-role-key"

    # Email Transaccional (Resend) - [COLABORADOR 1]
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "Dulce Paz <contacto@dulcepaz.com>"
    NOTIFICATION_EMAIL: str = "contacto@dulcepaz.com"

    # Google Workspace / Calendar - [COLABORADOR 2]
    GOOGLE_SERVICE_ACCOUNT_JSON: str = ""
    GOOGLE_CALENDAR_ADMIN_EMAIL: str = "contacto@dulcepaz.com"

    # Meta WhatsApp Cloud API - [COLABORADOR 2]
    WHATSAPP_API_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = ""
    WHATSAPP_FALLBACK_PHONE: str = "+59176543210"

    # Seguridad / JWT
    ADMIN_SECRET_KEY: str = "dulcepaz_dev_secret_key"


settings = Settings()
