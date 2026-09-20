# Dulce Paz | Backend API (FastAPI + Supabase + Resend)

> **Centro de Acompañamiento Integral y Salud Mental**  
> Repositorio oficial del Backend: [jayutomas623/DulcePaz-Backend](https://github.com/jayutomas623/DulcePaz-Backend)  
> Zona Horaria Oficial: **Hora de Bolivia (America/La_Paz - GMT-4)**  
> Servidor de Producción: **Render (Plan Starter)**

---

## 1. Arquitectura del Sistema

El backend de Dulce Paz está desacoplado del frontend (Next.js 14 alojado en Cloudflare Pages / Vercel), operando como una API RESTful moderna, asíncrona y de alto rendimiento.

```
[ Frontend: Next.js 14 ] (Cloudflare Pages)
         │
         │ (REST API / JSON - CORS localhost:3000 y produccion)
         ▼
[ Backend: FastAPI (Python 3.11+) ] (Render Starter)
  ├── Base de Datos: Supabase (PostgreSQL con RLS)
  ├── Email Transaccional: Resend (Plantillas HTML marca Dulce Paz)
  ├── Calendario & Videollamadas: Google Calendar + Google Meet API
  ├── Mensajería Instantánea: Meta WhatsApp Cloud API (+ contingencia wa.me)
  └── Tareas Programadas: Supabase pg_cron (Recordatorios 24h antes)
```

---

## 2. Estructura del Proyecto

```text
backend/dulce-paz-api/
├── app/
│   ├── __init__.py
│   ├── main.py                     # [COMPARTIDO - Base inicial Colab 1] FastAPI, CORS, health check
│   ├── database.py                 # [COMPARTIDO - Base inicial Colab 1] Cliente oficial Supabase
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py               # [COMPARTIDO] Pydantic Settings y variables de entorno
│   │   └── security.py             # [COMPARTIDO] Autenticación Bearer y JWT de Supabase Auth
│   │
│   ├── schemas/                    # Contratos de datos (Pydantic v2)
│   │   ├── __init__.py
│   │   ├── contact.py              # [COLABORADOR 1] Validación formulario /contacto
│   │   ├── event.py                # [COLABORADOR 1] Validación RSVP eventos QR 1
│   │   ├── booking.py              # [COLABORADOR 2] Esquema de reservas y disponibilidad
│   │   └── admin.py                # [COLABORADOR 2] Esquema panel clínico y bloqueos
│   │
│   ├── routers/                    # Endpoints de la API
│   │   ├── __init__.py
│   │   ├── contact.py              # [COLABORADOR 1] POST /api/v1/contact
│   │   ├── events.py               # [COLABORADOR 1] POST /api/v1/events/rsvp y GET /info
│   │   ├── bookings.py             # [COLABORADOR 2] POST /api/v1/bookings
│   │   ├── availability.py         # [COLABORADOR 2] GET /api/v1/availability/slots
│   │   └── admin.py                # [COLABORADOR 2] Endpoints de gestión /admin/*
│   │
│   └── services/                   # Lógica de negocio y APIs externas
│       ├── __init__.py
│       ├── email_service.py        # [COLABORADOR 1] Resend con plantillas corporativas HTML
│       ├── calendar_service.py     # [COLABORADOR 2] Google Calendar & enlaces Meet
│       └── whatsapp_service.py     # [COLABORADOR 2] WhatsApp Cloud API y contingencia wa.me
│
├── sql/
│   ├── 01_core_tables.sql          # [COLABORADOR 1] Tablas contacts y event_rsvps con RLS
│   └── 02_bookings_tables.sql      # [COLABORADOR 2] Tablas bookings, therapists, blocked_schedules
├── tests/
│   ├── __init__.py
│   └── test_api.py                 # Suite de pruebas automatizadas con pytest
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 3. Instalación y Ejecución Local

### Prerrequisitos
- Python 3.11 o superior instalado.
- Git.

### Pasos de inicialización:
```bash
# 1. Posicionarse en la carpeta del backend
cd "backend/dulce-paz-api"

# 2. Crear y activar el entorno virtual
# En Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

# En Linux/macOS:
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Supabase y Resend

# 5. Ejecutar la suite de pruebas unitarias
pytest -v

# 6. Iniciar el servidor de desarrollo
uvicorn app.main:app --reload --port 8000
```

### Documentación Interactiva:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

---

## 4. Estado de Implementación: COLABORADOR 1 (Finalizado)

El **Colaborador 1** ha completado y validado al 100% las siguientes funcionalidades:

1. **Arquitectura Base & CORS:**
   - FastAPI estructurado con lifespan asíncrono.
   - CORS habilitado para `http://localhost:3000` (desarrollo frontend) y dominios en Cloudflare Pages.
   - Health check activo con reporte de zona horaria oficial `America/La_Paz`.
2. **Cliente de Base de Datos (Supabase):**
   - Conexión singleton `get_supabase_client()` en `app/database.py`.
   - Soporte para claves con privilegios administrativos (`SUPABASE_SERVICE_ROLE_KEY`) y modo local tolerante a fallos.
3. **Módulo de Contacto (`/api/v1/contact`):**
   - Validaciones estrictas con Pydantic (`app/schemas/contact.py`).
   - Inserción en la tabla `contacts` de Supabase.
   - Notificación por correo vía Resend (`email_service.py`): alerta interna al equipo a `contacto@dulcepaz.com` y acuse de recibo al consultante.
4. **Módulo de Eventos QR 1 (`/api/v1/events/rsvp`):**
   - Destinado al Desayuno de Salud Mental en las Organizaciones (`/registro-evento`).
   - Soporte para camelCase (`companyName`, `representativeName`, `attendeesCount`) y snake_case.
   - Generación de código de acreditación VIP único (ej. `CORP-DP-4821`).
   - Persistencia en Supabase y envío automático del pase digital al correo institucional del delegado.
5. **Base de Datos y Seguridad (SQL):**
   - Archivo `sql/01_core_tables.sql` con políticas de seguridad por fila (RLS), índices optimizados y triggers de timestamp.
6. **Estrategia de Ramas Git:**
   - Rama principal: `main`.
   - Rama de desarrollo Colaborador 1: `feat/core-contact-events`.

---

## 5. GUÍA TÉCNICA DE ASIGNACIÓN PARA EL COLABORADOR 2

> **Estimado(a) Colaborador(a) 2:**  
> La infraestructura base, la base de datos, los contratos de datos y la conexión con el frontend ya están listos y testeados. Tu misión es dar vida al **Motor de Citas Clínicas (Wizard de 5 Pasos)**, la sincronización con **Google Calendar & Meet**, las notificaciones interactivas por **WhatsApp Cloud API** y los endpoints del **Panel Administrativo PWA**.

### 5.1. Flujo de Trabajo en Git para el Colaborador 2

```bash
# 1. Asegúrate de tener la última versión de main
git checkout main
git pull origin main

# 2. Crea tu rama exclusiva de trabajo
git checkout -b feat/bookings-calendar-whatsapp

# 3. Desarrolla tus módulos asignados (ver abajo)
# 4. Corre las pruebas:
pytest -v

# 5. Haz tus commits y publica tu rama:
git add .
git commit -m "feat(bookings): implementacion motor de citas, google calendar y whatsapp"
git push -u origin feat/bookings-calendar-whatsapp
```

---

### 5.2. Tareas Detalladas Asignadas al Colaborador 2

#### Tarea 1: Motor de Creación de Citas (`app/routers/bookings.py` y `app/schemas/booking.py`)
- **Endpoint:** `POST /api/v1/bookings`
- **Contrato de Entrada:** Ya preparado en `BookingCreate` (coincide al 100% con `BookingSchema` de Zod del frontend):
  - `serviceId`: 'individual' | 'pareja' | 'familiar' | 'vocacional' | 'adolescentes' | 'organizacional' | 'talleres'
  - `modality`: 'presencial' | 'virtual'
  - `therapistId`: 'nikki-paz' | 'keila-vilar' | 'william-mendoza' | 'any'
  - `date`: Formato `AAAA-MM-DD`
  - `timeSlot`: Franjas estándar `HH:MM` ('09:00', '10:30', '14:30', '16:00', '17:30')
  - `clientName`, `clientPhone`, `clientEmail`, `consultationReason`, `consentAccepted`.
- **Lógica que debes implementar:**
  1. Si `therapistId == 'any'`, asigna automáticamente al profesional habilitado según el servicio (ej. `SERVICES_DATA` y `THERAPISTS_DATA`).
  2. **Validación anti-colisión:** Realiza un `SELECT` en la tabla `bookings` para asegurar que el par `(therapist_id, appointment_date, time_slot)` no esté ocupado. Si está ocupado, levanta `HTTPException(409, "El horario seleccionado ya no se encuentra disponible")`.
  3. Inserta la cita en la tabla `bookings` de Supabase.
  4. Dispara en segundo plano (`BackgroundTasks`):
     - Creación del evento en Google Calendar (`calendar_service`).
     - Despacho de mensaje WhatsApp (`whatsapp_service`).
     - Envío de comprobante por correo con archivo `.ics` descargable.

#### Tarea 2: Disponibilidad de Horarios en Tiempo Real (`app/routers/availability.py`)
- **Endpoint:** `GET /api/v1/availability/slots?date=AAAA-MM-DD&therapistId=xyz`
- **Lógica que debes implementar:**
  1. Horarios base definidos en la clínica: `['09:00', '10:30', '14:30', '16:00', '17:30']`.
  2. Si la fecha es domingo, retorna todos los slots como no disponibles (`isAvailable: false`).
  3. Consulta en Supabase:
     - Citas existentes en `bookings` para la fecha y terapeuta.
     - Bloqueos manuales registrados en `blocked_schedules`.
  4. Retorna el listado de slots marcando `isAvailable: false` a los ocupados o bloqueados.

#### Tarea 3: Integración Google Calendar & Google Meet (`app/services/calendar_service.py`)
- **Cuenta institucional:** `contacto@dulcepaz.com`.
- **Lógica que debes implementar:**
  1. En `create_appointment_event(...)`:
     - Si `modality == 'presencial'`: El evento fija como `location`: *"Calle 15 de Calacoto, Edificio Parque, La Paz, Bolivia"*.
     - Si `modality == 'virtual'`: Invoca a la API de Calendar solicitando `conferenceData` con `createRequest` tipo `hangoutsMeet` para generar el link único cifrado de Google Meet.
  2. Guarda el `google_event_id` y `google_meet_link` en el registro de la cita en Supabase.

#### Tarea 4: Integración Meta WhatsApp Cloud API (`app/services/whatsapp_service.py`)
- **Credenciales en `.env`:** `WHATSAPP_API_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`.
- **Lógica que debes implementar:**
  1. Enviar el template interactivo de confirmación con los parámetros: Nombre, Servicio, Fecha, Hora y Enlace Meet / Dirección.
  2. **Plan de Contingencia:** El stub ya provee el generador de enlace directo a `wa.me/59176543210?text=...` para garantizar que si Meta demora en validar la cuenta de empresa, el paciente pueda abrir su confirmación inmediatamente en WhatsApp sin fallas.

#### Tarea 5: Endpoints del Panel Administrativo PWA (`app/routers/admin.py` y `app/schemas/admin.py`)
- **Autenticación:** Utiliza la dependencia `Depends(get_current_admin_user)` ya configurada en `app/core/security.py`.
- **Endpoints a completar:**
  1. `GET /api/v1/admin/agenda`: Citas de la semana del terapeuta autenticado.
  2. `PATCH /api/v1/admin/bookings/{id}/status`: Cambiar estado a `confirmed`, `completed`, `cancelled_by_patient` o `no_show`.
  3. `POST /api/v1/admin/schedules/block`: Insertar bloqueo en `blocked_schedules` (por vacaciones, reuniones o imprevistos).

#### Tarea 6: Base de Datos y Automatización `pg_cron` (`sql/02_bookings_tables.sql`)
- Ejecuta en el Editor SQL de Supabase el script `sql/02_bookings_tables.sql` que ya hemos dejado preparado con:
  - Tablas `therapists`, `blocked_schedules` y `bookings`.
  - Configuración de la extensión `pg_cron` para el job programado a las 08:00 AM que despacha los recordatorios 24h antes.

---

## 6. Variables de Entorno Requeridas (`.env`)

| Variable | Responsable | Propósito |
| :--- | :--- | :--- |
| `SUPABASE_URL` | Colab 1 / 2 | URL del proyecto Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | Colab 1 / 2 | Clave con privilegios para inserciones backend |
| `RESEND_API_KEY` | Colaborador 1 | Clave para envío de emails transaccionales |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Colaborador 2 | Credenciales Service Account Google Calendar/Meet |
| `WHATSAPP_API_TOKEN` | Colaborador 2 | Token de acceso de Meta Developer Cloud API |
| `WHATSAPP_PHONE_NUMBER_ID` | Colaborador 2 | ID del número telefónico de WhatsApp Business |

---

## 7. Despliegue en Render (Producción)

1. En [Render.com](https://render.com), crea un nuevo **Web Service**.
2. Conecta el repositorio `jayutomas623/DulcePaz-Backend`.
3. Configuración:
   - **Environment:** `Python 3`
   - **Root Directory:** `backend/dulce-paz-api` (si el repo está anidado) o raíz del repo.
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Starter ($7/mes - sin arranques en frío para no demorar la selección de horarios).
4. Agrega las variables de entorno en la pestaña *Environment* de Render.
