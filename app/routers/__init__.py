"""
Módulo de routers de la API Dulce Paz.
"""

from app.routers.contact import router as contact_router
from app.routers.events import router as events_router
from app.routers.bookings import router as bookings_router
from app.routers.availability import router as availability_router
from app.routers.admin import router as admin_router

__all__ = [
    "contact_router",
    "events_router",
    "bookings_router",
    "availability_router",
    "admin_router",
]
