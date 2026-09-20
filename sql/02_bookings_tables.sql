-- ==============================================================================
-- DULCE PAZ - SISTEMA DE SALUD MENTAL Y BIENESTAR INTEGRAL
-- 02_bookings_tables.sql: Tablas y Automatizaciones asignadas al Colaborador 2
-- (Terapeutas, Bloqueos de Horario, Citas y pg_cron)
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
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('America/La_Paz', now())
);

-- Seed de terapeutas institucionales
INSERT INTO public.therapists (id, name, email, role, specialty, quote, services_offered, avatar_url, is_active)
VALUES
('nikki-paz', 'Lic. Nikki Paz', 'nikki@dulcepaz.com', 'Coordinadora General / Psicóloga Clínica', 'Terapia de pareja, ansiedad, duelo y terapia intercultural bilingüe (Español/Inglés)', 'Nuestra prioridad es guiarte hacia un espacio de paz interna en medio de las complejidades cotidianas de la vida.', ARRAY['individual', 'pareja', 'familiar', 'talleres'], '/team/nikki.jpg', true),
('keila-vilar', 'Lic. Keila Vilar', 'keila@dulcepaz.com', 'Especialista Psicopedagógica', 'Acompañamiento infanto-juvenil, hábitos de estudio y orientación vocacional', 'El aprendizaje florece cuando las niñas, niños y jóvenes se sienten escuchados, validados y acompañados con paciencia.', ARRAY['vocacional', 'adolescentes', 'talleres'], '/team/keila.jpg', true),
('william-mendoza', 'Lic. William Mendoza', 'william@dulcepaz.com', 'Psicólogo Organizacional', 'Salud ocupacional, clima corporativo, consultoría y selección de talento', 'Organizaciones sanas y humanas logran resultados extraordinarios y sostenibles en el tiempo.', ARRAY['organizacional', 'talleres'], '/team/william.jpg', true)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    role = EXCLUDED.role,
    specialty = EXCLUDED.specialty,
    services_offered = EXCLUDED.services_offered;

-- ------------------------------------------------------------------------------
-- 2. TABLA: blocked_schedules (Bloqueo de horarios por terapeutas)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.blocked_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    therapist_id VARCHAR(50) NOT NULL REFERENCES public.therapists(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    time_slot VARCHAR(10) NOT NULL, -- '09:00', '10:30', '14:30', '16:00', '17:30'
    reason VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('America/La_Paz', now()),
    UNIQUE (therapist_id, date, time_slot)
);

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
    
    -- Evitar citas duplicadas en el mismo horario con el mismo terapeuta
    UNIQUE (therapist_id, appointment_date, time_slot)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_bookings_date ON public.bookings (appointment_date, time_slot);
CREATE INDEX IF NOT EXISTS idx_bookings_therapist ON public.bookings (therapist_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON public.bookings (status);

-- RLS
ALTER TABLE public.bookings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Permitir insercion publica de citas"
    ON public.bookings FOR INSERT TO anon, authenticated, service_role
    WITH CHECK (true);

CREATE POLICY "Gestion administrativa de citas"
    ON public.bookings FOR ALL TO authenticated, service_role
    USING (true) WITH CHECK (true);

-- ------------------------------------------------------------------------------
-- 4. ESQUEMA DE AUTOMATIZACIÓN pg_cron (Recordatorios 24h antes)
-- [Colaborador 2 configurará la extensión en Supabase Dashboard -> Database -> Extensions]
-- ------------------------------------------------------------------------------
-- SELECT cron.schedule(
--   'recordatorio-citas-24h',
--   '0 8 * * *', -- Cada día a las 08:00 AM hora Bolivia
--   $$
--   SELECT net.http_post(
--       url := 'https://api.dulcepaz.com/api/v1/admin/dispatch-reminders',
--       headers := '{"Content-Type": "application/json", "Authorization": "Bearer SERVICE_ROLE_KEY"}'::jsonb
--   );
--   $$
-- );
