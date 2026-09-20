"""
Esquemas Pydantic v2 para validación de datos de entrada y respuesta de la API.
"""

from app.schemas.contact import ContactCreate, ContactResponse
from app.schemas.event import EventRSVPCreate, EventRSVPResponse

__all__ = [
    "ContactCreate",
    "ContactResponse",
    "EventRSVPCreate",
    "EventRSVPResponse",
]
