-- ==============================================================================
-- DULCE PAZ - SISTEMA DE SALUD MENTAL Y BIENESTAR INTEGRAL
-- 01_core_tables.sql: Tablas Core del Colaborador 1 (Contactos y Eventos QR 1)
-- Zona Horaria Oficial: America/La_Paz (GMT-4)
-- ==============================================================================

-- Habilitar extensión para generación de UUIDs si no está habilitada
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ------------------------------------------------------------------------------
-- 1. TABLA: contacts (Consultas y Mensajes del Formulario de Contacto /contacto)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL,
    telefono VARCHAR(50),
    motivo VARCHAR(100) NOT NULL DEFAULT 'Consulta general',
    mensaje TEXT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'contacted', 'resolved', 'archived')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('America/La_Paz', now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('America/La_Paz', now())
);

-- Comentarios explicativos
COMMENT ON TABLE public.contacts IS 'Mensajes y solicitudes enviadas desde la página /contacto';
COMMENT ON COLUMN public.contacts.motivo IS 'Motivo clasificado: Consulta general, Convenios corporativos, Talleres/Eventos, etc.';
COMMENT ON COLUMN public.contacts.status IS 'Estado de seguimiento de la consulta clínica o institucional';

-- Índices de búsqueda y ordenación
CREATE INDEX IF NOT EXISTS idx_contacts_created_at ON public.contacts (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON public.contacts (email);
CREATE INDEX IF NOT EXISTS idx_contacts_status ON public.contacts (status);

-- Seguridad por Fila (Row Level Security - RLS)
ALTER TABLE public.contacts ENABLE ROW LEVEL SECURITY;

-- Política 1: Cualquier visitante web (anon) puede enviar una consulta
DROP POLICY IF EXISTS "Permitir insercion publica de contactos" ON public.contacts;
CREATE POLICY "Permitir insercion publica de contactos"
    ON public.contacts
    FOR INSERT
    TO anon, authenticated, service_role
    WITH CHECK (true);

-- Política 2: Solo personal clínico autenticado o service_role puede leer y actualizar
DROP POLICY IF EXISTS "Lectura administrativa de contactos" ON public.contacts;
CREATE POLICY "Lectura administrativa de contactos"
    ON public.contacts
    FOR SELECT
    TO authenticated, service_role
    USING (true);

DROP POLICY IF EXISTS "Actualizacion administrativa de contactos" ON public.contacts;
CREATE POLICY "Actualizacion administrativa de contactos"
    ON public.contacts
    FOR UPDATE
    TO authenticated, service_role
    USING (true)
    WITH CHECK (true);

-- ------------------------------------------------------------------------------
-- 2. TABLA: event_rsvps (Confirmación Express a Eventos QR 1 /registro-evento)
-- Desayuno de Trabajo Corporativo: Salud Mental en las Organizaciones
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.event_rsvps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(200) NOT NULL,
    representative_name VARCHAR(150) NOT NULL,
    job_title VARCHAR(150) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    attendees_count INT NOT NULL DEFAULT 1 CHECK (attendees_count BETWEEN 1 AND 3),
    pass_code VARCHAR(50) UNIQUE NOT NULL,
    event_name VARCHAR(200) NOT NULL DEFAULT 'Desayuno de Trabajo Corporativo: Salud Mental en las Organizaciones',
    event_date VARCHAR(50) NOT NULL DEFAULT '2026-10-23',
    event_time VARCHAR(50) NOT NULL DEFAULT '10:00 a 12:00',
    event_location VARCHAR(255) NOT NULL DEFAULT 'Auditorio Dulce Paz (Calle 15 de Calacoto, Edif. Parque, La Paz)',
    status VARCHAR(30) NOT NULL DEFAULT 'confirmed' CHECK (status IN ('confirmed', 'attended', 'cancelled')),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('America/La_Paz', now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('America/La_Paz', now())
);

-- Comentarios explicativos
COMMENT ON TABLE public.event_rsvps IS 'Acreditaciones corporativas para el desayuno de salud mental (Código QR 1)';
COMMENT ON COLUMN public.event_rsvps.pass_code IS 'Código VIP único de acreditación institucional (ej. CORP-DP-4821)';
COMMENT ON COLUMN public.event_rsvps.attendees_count IS 'Número de delegados reservados (máximo 3 por empresa)';

-- Índices de búsqueda y unicidad
CREATE INDEX IF NOT EXISTS idx_event_rsvps_pass_code ON public.event_rsvps (pass_code);
CREATE INDEX IF NOT EXISTS idx_event_rsvps_email ON public.event_rsvps (email);
CREATE INDEX IF NOT EXISTS idx_event_rsvps_company ON public.event_rsvps (company_name);
CREATE INDEX IF NOT EXISTS idx_event_rsvps_created_at ON public.event_rsvps (created_at DESC);

-- Seguridad por Fila (Row Level Security - RLS)
ALTER TABLE public.event_rsvps ENABLE ROW LEVEL SECURITY;

-- Política 1: Cualquier empresa con el QR 1 puede registrar su asistencia
DROP POLICY IF EXISTS "Permitir insercion publica de rsvps" ON public.event_rsvps;
CREATE POLICY "Permitir insercion publica de rsvps"
    ON public.event_rsvps
    FOR INSERT
    TO anon, authenticated, service_role
    WITH CHECK (true);

-- Política 2: Consulta pública individual por pass_code (para validar el pase digital)
DROP POLICY IF EXISTS "Validacion publica de pase por codigo" ON public.event_rsvps;
CREATE POLICY "Validacion publica de pase por codigo"
    ON public.event_rsvps
    FOR SELECT
    TO anon, authenticated, service_role
    USING (pass_code = current_setting('request.jwt.claim.pass_code', true) OR auth.role() IN ('authenticated', 'service_role'));

-- Política 3: Gestión completa para usuarios autenticados / coordinación
DROP POLICY IF EXISTS "Gestion total administrativa de rsvps" ON public.event_rsvps;
CREATE POLICY "Gestion total administrativa de rsvps"
    ON public.event_rsvps
    FOR ALL
    TO authenticated, service_role
    USING (true)
    WITH CHECK (true);

-- Trigger para auto-actualización de updated_at
CREATE OR REPLACE FUNCTION public.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('America/La_Paz', now());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_contacts_updated_at ON public.contacts;
CREATE TRIGGER tr_contacts_updated_at
    BEFORE UPDATE ON public.contacts
    FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();

DROP TRIGGER IF EXISTS tr_event_rsvps_updated_at ON public.event_rsvps;
CREATE TRIGGER tr_event_rsvps_updated_at
    BEFORE UPDATE ON public.event_rsvps
    FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();
