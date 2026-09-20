"""
Esquemas Pydantic para el Registro a Eventos Institucionales (Código QR 1 /registro-evento).
Asignado a: COLABORADOR 1
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class EventRSVPCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    company_name: str = Field(
        ...,
        alias="companyName",
        min_length=2,
        max_length=200,
        description="Nombre de la empresa o institución invitada",
        examples=["Corporación Andina S.A."]
    )
    representative_name: str = Field(
        ...,
        alias="representativeName",
        min_length=3,
        max_length=150,
        description="Nombre completo del delegado o representante principal",
        examples=["Lic. Claudia Mendoza"]
    )
    job_title: str = Field(
        ...,
        alias="jobTitle",
        min_length=2,
        max_length=150,
        description="Cargo institucional del representante",
        examples=["Gerente de RRHH / Talento Humano"]
    )
    phone: str = Field(
        ...,
        alias="phone",
        min_length=8,
        max_length=50,
        description="Número de WhatsApp corporativo para envío del pase digital",
        examples=["+591 76543210"]
    )
    email: EmailStr = Field(
        ...,
        alias="email",
        description="Correo electrónico corporativo para confirmación y credencial",
        examples=["cmendoza@empresa.com"]
    )
    attendees_count: int = Field(
        default=1,
        alias="attendeesCount",
        ge=1,
        le=3,
        description="Número de asistentes delegados (máximo 3 personas por institución)",
        examples=[2]
    )

    @field_validator("company_name", "representative_name", "job_title", "phone", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v


class EventRSVPResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = None
    pass_code: str = Field(..., alias="passCode", description="Código alfanumérico VIP del pase digital")
    company_name: str = Field(..., alias="companyName")
    representative_name: str = Field(..., alias="representativeName")
    job_title: str = Field(..., alias="jobTitle")
    attendees_count: int = Field(..., alias="attendeesCount")
    event_name: str = "Desayuno de Trabajo Corporativo: Salud Mental en las Organizaciones"
    event_date: str = "Viernes, 23 de Octubre de 2026"
    event_time: str = "10:00 a 12:00 (Hora de Bolivia GMT-4)"
    event_location: str = "Auditorio Dulce Paz (Calle 15 de Calacoto, Edif. Parque, La Paz)"
    status: str = "confirmed"
    message: str = "¡Asistencia confirmada! Hemos registrado la participación de su institución."
    created_at: Optional[str] = None
