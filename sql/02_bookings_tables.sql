-- ==============================================================================
-- DULCE PAZ - SISTEMA DE SALUD MENTAL Y BIENESTAR INTEGRAL
-- 02_bookings_tables.sql: Tablas y Automatizaciones asignadas al Colaborador 2
-- (Terapeutas, Bloqueos de Horario, Citas y pg_cron)
-- Zona Horaria Oficial: America/La_Paz (GMT-4)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. TABLA: therapists (Especialistas del Centro)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.therapists (
    id VARCHAR(50) PRIMARY KEY, -- 'nikki-paz', 'keila-vilar', 'william-mendoza'
    name VARCHAR(150) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(150) NOT NULL,
    specialty TEXT NOT NULL,
    quote TEXT,
    services_offered TEXT[] NOT NULL,
    avatar_url TEXT,
    google_calendar_id VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('America/La_Paz', now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('America/La_Paz', now())
);

-- Seed de terapeutas institucionales oficiales
INSERT INTO public.therapists (id, name, email, role, specialty, quote, services_offered, avatar_url, is_active)
VALUES
('nikki-paz', 'Lic. Nikki Paz', 'nikki@dulcepaz.com', 'Coordinadora General / Psicóloga Clínica', 'Terapia de pareja, ansiedad, duelo y terapia intercultural bilingüe (Español/Inglés)', 'Nuestra prioridad es guiarte hacia un espacio de paz interna en medio de las complejidades cotidianas de la vida.', ARRAY['individual', 'pareja', 'familiar', 'talleres'], '/team/nikki.jpg', true),
('keila-vilar', 'Lic. Keila Vilar', 'keila@dulcepaz.com', 'Especialista Psicopedagógica', 'Acompañamiento infanto-juvenil, hábitos de estudio y orientación vocacional', 'El aprendizaje florece cuando las niñas, niños y jóvenes se sienten escuchados, validados y acompañados con paciencia.', ARRAY['vocacional', 'adolescentes', 'talleres'], '/team/keila.jpg', true),
('william-mendoza', 'Lic. William Mendoza', 'william@dulcepaz.com', 'Psicólogo Organizacional', 'Salud ocupacional, clima corporativo, consultoría y selección de talento', 'Organizaciones sanas y humanas logran resultados extraordinarios y sostenibles en el tiempo.', ARRAY['organizacional', 'talleres'], '/team/william.jpg', true)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    email = EXCLUDED.email,
    role = EXCLUDED.role,
    specialty = EXCLUDED.specialty,
    quote = EXCLUDED.quote,
    services_offered = EXCLUDED.services_offered,
    is_active = EXCLUDED.is_active;

-- Índices y RLS para therapists
ALTER TABLE public.therapists ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Lectura publica de terapeutas activos" ON public.therapists;
CREATE POLICY "Lectura publica de terapeutas activos"
    ON public.therapists FOR SELECT
    TO anon, authenticated, service_role
    USING (is_active = true);

DROP POLICY IF EXISTS "Gestion administrativa de terapeutas" ON public.therapists;
CREATE POLICY "Gestion administrativa de terapeutas"
    ON public.therapists FOR ALL
    TO authenticated, service_role
    USING (true) WITH CHECK (true);

-- ------------------------------------------------------------------------------
-- 2. TABLA: blocked_schedules (Bloqueo de horarios por terapeutas)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.blocked_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    therapist_id VARCHAR(50) NOT NULL REFERENCES public.therapists(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    time_slot VARCHAR(10) NOT NULL, -- '09:00', '10:30', '14:30', '16:00', '17:30'
    reason VARCHAR(255) DEFAULT 'No disponible / Bloqueo administrativo',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('America/La_Paz', now()),
    UNIQUE (therapist_id, date, time_slot)
);

-- Índices de consulta rápida de disponibilidad
CREATE INDEX IF NOT EXISTS idx_blocked_schedules_lookup ON public.blocked_schedules (therapist_id, date);
CREATE INDEX IF NOT EXISTS idx_blocked_schedules_date ON public.blocked_schedules (date);

-- RLS para blocked_schedules
ALTER TABLE public.blocked_schedules ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Lectura publica de bloqueos para calculo de disponibilidad" ON public.blocked_schedules;
CREATE POLICY "Lectura publica de bloqueos para calculo de disponibilidad"
    ON public.blocked_schedules FOR SELECT
    TO anon, authenticated, service_role
    USING (true);

DROP POLICY IF EXISTS "Gestion total administrativa de bloqueos" ON public.blocked_schedules;
CREATE POLICY "Gestion total administrativa de bloqueos"
    ON public.blocked_schedules FOR ALL
    TO authenticated, service_role
    USING (true) WITH CHECK (true);

-- ------------------------------------------------------------------------------
-- 3. TABLA: bookings (Citas Clínicas y Psicoeducativas Agendadas)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_reference VARCHAR(50) UNIQUE NOT NULL, -- DP-2026-XXXX
    service_id VARCHAR(50) NOT NULL,
    modality VARCHAR(20) NOT NULL CHECK (modality IN ('presencial', 'virtual')),
    therapist_id VARCHAR(50) NOT NULL REFERENCES public.therapists(id),
    appointment_date DATE NOT NULL,
    time_slot VARCHAR(10) NOT NULL, -- HH:MM
    client_name VARCHAR(150) NOT NULL,
    client_phone VARCHAR(50) NOT NULL,
    client_email VARCHAR(255) NOT NULL,
    consultation_reason TEXT,
    consent_accepted BOOLEAN NOT NULL DEFAULT true,
    
    -- Integración Google Calendar & Meet
    google_event_id VARCHAR(255),
    google_meet_link TEXT,
    
    -- Integración WhatsApp Cloud API
    whatsapp_message_id VARCHAR(255),
    whatsapp_notification_sent BOOLEAN DEFAULT false,
    reminder_24h_sent BOOLEAN DEFAULT false,
    
    -- Estado de la Cita (Panel Admin PWA)
    status VARCHAR(30) NOT NULL DEFAULT 'confirmed' CHECK (status IN ('confirmed', 'completed', 'cancelled_by_patient', 'no_show')),
    admin_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('America/La_Paz', now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('America/La_Paz', now()),
    
    -- Restricción estricta anti-colisión a nivel motor de base de datos
    UNIQUE (therapist_id, appointment_date, time_slot)
);

-- Índices optimizados para agendamiento, filtros de agenda y búsqueda
CREATE INDEX IF NOT EXISTS idx_bookings_date_slot ON public.bookings (appointment_date, time_slot);
CREATE INDEX IF NOT EXISTS idx_bookings_therapist_date ON public.bookings (therapist_id, appointment_date);
CREATE INDEX IF NOT EXISTS idx_bookings_client_email ON public.bookings (client_email);
CREATE INDEX IF NOT EXISTS idx_bookings_reference ON public.bookings (booking_reference);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON public.bookings (status);

-- RLS para bookings
ALTER TABLE public.bookings ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Permitir insercion publica de citas" ON public.bookings;
CREATE POLICY "Permitir insercion publica de citas"
    ON public.bookings FOR INSERT TO anon, authenticated, service_role
    WITH CHECK (true);

DROP POLICY IF EXISTS "Lectura por referencia publica de cita" ON public.bookings;
CREATE POLICY "Lectura por referencia publica de cita"
    ON public.bookings FOR SELECT
    TO anon, authenticated, service_role
    USING (true);

DROP POLICY IF EXISTS "Gestion administrativa total de citas" ON public.bookings;
CREATE POLICY "Gestion administrativa total de citas"
    ON public.bookings FOR ALL TO authenticated, service_role
    USING (true) WITH CHECK (true);

-- Triggers de actualización de updated_at
DROP TRIGGER IF EXISTS tr_therapists_updated_at ON public.therapists;
CREATE TRIGGER tr_therapists_updated_at
    BEFORE UPDATE ON public.therapists
    FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();

DROP TRIGGER IF EXISTS tr_bookings_updated_at ON public.bookings;
CREATE TRIGGER tr_bookings_updated_at
    BEFORE UPDATE ON public.bookings
    FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();

-- ------------------------------------------------------------------------------
-- 4. ESQUEMA DE AUTOMATIZACIÓN pg_cron (Recordatorios 24h antes)
-- Configuración en Supabase Dashboard -> Database -> Extensions (habilitar pg_cron y pg_net)
-- ------------------------------------------------------------------------------
-- SELECT cron.schedule(
--   'recordatorio-citas-24h',
--   '0 8 * * *', -- Ejecuta cada día a las 08:00 AM hora de Bolivia
--   $$
--   SELECT net.http_post(
--       url := 'https://api.dulcepaz.com/api/v1/admin/dispatch-reminders',
--       headers := '{"Content-Type": "application/json", "Authorization": "Bearer SERVICE_ROLE_KEY"}'::jsonb
--   );
--   $$
-- );

