"""
Punto de entrada principal de la API Dulce Paz.
Configuración de FastAPI, CORS, middleware de seguridad y montaje de routers.
Asignado: COLABORADOR 1 (Base inicial compartida)
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database import get_supabase_client
from app.routers import (
    contact_router,
    events_router,
    bookings_router,
    availability_router,
    admin_router,
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("dulcepaz.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida de la aplicación.
    Inicializa clientes y recursos al arrancar y limpia al cerrar.
    """
    logger.info(f"Iniciando {settings.PROJECT_NAME} en entorno: {settings.ENVIRONMENT}")
    logger.info(f"Zona horaria oficial: {settings.TIMEZONE}")
    logger.info(f"Orígenes CORS habilitados: {settings.CORS_ORIGINS}")
    
    # Probar conexión con Supabase
    supabase = get_supabase_client()
    if supabase:
        logger.info("Conexión con Supabase verificada.")
    else:
        logger.info("Operando en modo desarrollo local sin Supabase activo.")
        
    yield
    
    logger.info("Cerrando recursos de Dulce Paz API.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description=(
        "API oficial de Dulce Paz | Psicología y Salud Mental. "
        "Gestión de canales de contacto, acreditación a eventos corporativos (QR 1), "
        "motor de agendamiento de citas clínicas (Google Calendar/Meet, WhatsApp) y panel administrativo PWA."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ------------------------------------------------------------------------------
# Configuración de Middleware CORS
# Permite solicitudes seguras desde el frontend (Next.js en localhost:3000 y producción)
# ------------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["General"])
async def root():
    """
    Información de estado y bienvenida a la API.
    """
    return {
        "app": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "online",
        "institution": "Dulce Paz | Psicología y Salud Mental",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["General"])
async def health_check():
    """
    Endpoint de monitoreo y health check para Render y UptimeRobot.
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "timezone": settings.TIMEZONE,
        "timestamp": datetime.now().isoformat(),
        "cors_origins": settings.CORS_ORIGINS,
    }


# ------------------------------------------------------------------------------
# Inclusión de Routers de la API (/api/v1)
# ------------------------------------------------------------------------------
app.include_router(contact_router, prefix=settings.API_V1_STR)
app.include_router(events_router, prefix=settings.API_V1_STR)
app.include_router(bookings_router, prefix=settings.API_V1_STR)
app.include_router(availability_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
