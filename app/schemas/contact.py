"""
Esquemas Pydantic para el Formulario de Contacto (/contacto).
Asignado a: COLABORADOR 1
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactCreate(BaseModel):
    nombre: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Nombre completo del consultante o interesado",
        examples=["Lic. María Flores"]
    )
    email: EmailStr = Field(
        ...,
        description="Correo electrónico válido de contacto",
        examples=["maria.flores@ejemplo.com"]
    )
    telefono: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Número de WhatsApp o celular con código de país",
        examples=["+591 76543210"]
    )
    motivo: str = Field(
        default="Consulta general",
        max_length=100,
        description="Motivo de la consulta o área temática",
        examples=["Consulta general", "Convenios corporativos", "Talleres/Eventos"]
    )
    mensaje: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Detalle o consulta del usuario",
        examples=["Deseo consultar sobre los horarios de atención para psicoterapia individual."]
    )

    @field_validator("nombre", "motivo", "mensaje", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v


class ContactResponse(BaseModel):
    id: Optional[str] = Field(None, description="Identificador único del mensaje registrado")
    nombre: str
    email: str
    motivo: str
    status: str = "pending"
    message: str = "Mensaje recibido correctamente. El equipo de Dulce Paz se pondrá en contacto a la brevedad."
    created_at: Optional[str] = None
