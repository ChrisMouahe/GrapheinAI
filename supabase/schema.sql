-- ====================================================================
-- Supabase PostgreSQL Schema & Row Level Security (RLS) Policies
-- GrapheinAI ChartQA SaaS Enterprise Platform
-- ====================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- --------------------------------------------------------------------
-- 1. Activity Sectors Reference Table
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.activity_sectors (
    id SERIAL PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    name_fr TEXT NOT NULL,
    name_en TEXT NOT NULL
);

INSERT INTO public.activity_sectors (key, name_fr, name_en) VALUES
('finance', 'Finance', 'Finance'),
('sante', 'Santé', 'Healthcare'),
('marketing', 'Marketing', 'Marketing'),
('education', 'Éducation', 'Education'),
('telecom', 'Télécommunications', 'Telecommunications'),
('industrie', 'Industrie', 'Manufacturing'),
('banque', 'Banque', 'Banking'),
('energie', 'Énergie', 'Energy'),
('assurance', 'Assurance', 'Insurance'),
('transport', 'Transport', 'Transportation'),
('commerce', 'Commerce', 'Retail & E-commerce'),
('administration', 'Administration', 'Public Administration'),
('autre', 'Autre', 'Other')
ON CONFLICT (key) DO NOTHING;

-- --------------------------------------------------------------------
-- 2. Companies Table
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    sector TEXT,
    country TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- --------------------------------------------------------------------
-- 3. Profiles Table (Extends auth.users & UserProfile Pydantic Model)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    nom TEXT NOT NULL DEFAULT '',
    prenom TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    avatar_url TEXT,
    entreprise TEXT DEFAULT '',
    secteur_activite TEXT DEFAULT 'Finance',
    secteur_autre TEXT DEFAULT '',
    fonction TEXT DEFAULT '',
    niveau_expertise VARCHAR(30) DEFAULT 'Intermédiaire', -- Débutant, Intermédiaire, Avancé, Expert
    annees_experience INT DEFAULT 0,
    langue VARCHAR(10) DEFAULT 'fr',
    pays TEXT DEFAULT 'France',
    role VARCHAR(30) DEFAULT 'standard_user', -- admin, standard_user, guest, collaborator
    date_inscription TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    derniere_connexion TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    total_analyses INT DEFAULT 0,
    total_pdfs INT DEFAULT 0
);

-- Enable RLS for Profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Admins can view all profiles"
    ON public.profiles FOR SELECT
    USING (EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin'));

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- --------------------------------------------------------------------
-- 4. User Preferences Table
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.user_preferences (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    theme VARCHAR(20) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'fr',
    vlm_model TEXT DEFAULT 'gemini-3.5-flash',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own preferences"
    ON public.user_preferences FOR ALL
    USING (auth.uid() = user_id);

-- --------------------------------------------------------------------
-- 5. Analyses Table (User-scoped Chart Sessions)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    image_url TEXT,
    chart_type VARCHAR(50) DEFAULT 'bar',
    extraction JSONB,
    statistics JSONB,
    anomalies JSONB,
    insights JSONB,
    interpretation TEXT,
    execution_latency FLOAT DEFAULT 0.0,
    overall_confidence FLOAT DEFAULT 1.0,
    target_language VARCHAR(10) DEFAULT 'fr',
    has_pdf BOOLEAN DEFAULT FALSE,
    question_count INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own analyses"
    ON public.analyses FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own analyses"
    ON public.analyses FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own analyses"
    ON public.analyses FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own analyses"
    ON public.analyses FOR DELETE
    USING (auth.uid() = user_id);

-- --------------------------------------------------------------------
-- 6. Workspaces Table
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.workspaces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    description TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------------------
-- 7. Workspace Members Table
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.workspace_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(30) NOT NULL DEFAULT 'viewer', -- owner, editor, commenter, viewer
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(workspace_id, user_id)
);

ALTER TABLE public.workspace_members ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------------------
-- 8. Analysis Permissions Table (Granular Shared Session Access)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.analysis_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES public.analyses(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(30) NOT NULL DEFAULT 'viewer', -- owner, editor, commenter, viewer
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(analysis_id, user_id)
);

ALTER TABLE public.analysis_permissions ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------------------
-- 9. Invitations Table (Signed Temporary Email Invites)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID REFERENCES public.workspaces(id) ON DELETE CASCADE,
    analysis_id UUID REFERENCES public.analyses(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    inviter_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(30) NOT NULL DEFAULT 'editor',
    token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, accepted, revoked
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.invitations ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------------------
-- 10. Analysis Comments Table
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.analysis_comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES public.analyses(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES public.analysis_comments(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.analysis_comments ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------------------
-- 11. Notifications Table
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- invitation, share, comment, accepted
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    link_url TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------------------
-- 12. Activity Logs Table (Audit Trail)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID REFERENCES public.workspaces(id) ON DELETE CASCADE,
    analysis_id UUID REFERENCES public.analyses(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.activity_logs ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------------------
-- 13. Charts Table (Sub-charts detected in a single multi-chart image)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.charts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT NOT NULL,
    chart_index INT NOT NULL,
    title TEXT DEFAULT '',
    chart_type VARCHAR(50) DEFAULT 'bar',
    confidence FLOAT DEFAULT 0.95,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.charts ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------------------
-- 14. Chart Regions Table (Bounding Box Coordinates)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.chart_regions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chart_id UUID NOT NULL REFERENCES public.charts(id) ON DELETE CASCADE,
    bbox_x INT NOT NULL,
    bbox_y INT NOT NULL,
    bbox_w INT NOT NULL,
    bbox_h INT NOT NULL,
    cropped_image_path TEXT
);

ALTER TABLE public.chart_regions ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------------------
-- 15. Chart Metadata & Extracted Points
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.chart_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chart_id UUID NOT NULL REFERENCES public.charts(id) ON DELETE CASCADE,
    x_label TEXT,
    y_label TEXT,
    data_point_count INT DEFAULT 0,
    extraction_json JSONB
);

ALTER TABLE public.chart_metadata ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------------------
-- 16. Chart Relationships Table (Cross-chart Correlations)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.chart_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_chart_id UUID NOT NULL REFERENCES public.charts(id) ON DELETE CASCADE,
    target_chart_id UUID NOT NULL REFERENCES public.charts(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) DEFAULT 'correlation',
    correlation_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.chart_relationships ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------------------
-- 17. API Keys Table
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    key_prefix VARCHAR(20) NOT NULL,
    key_hash VARCHAR(128) NOT NULL,
    monthly_quota INT DEFAULT 500,
    usage_count INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE
);

ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------------------
-- 18. System Settings Table
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    maintenance_mode BOOLEAN DEFAULT FALSE,
    allow_user_signups BOOLEAN DEFAULT TRUE,
    default_user_role VARCHAR(20) DEFAULT 'viewer',
    gemini_monthly_token_budget INT DEFAULT 5000000,
    gemini_consumed_tokens INT DEFAULT 124500,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.system_settings ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------------------
-- 19. System Quotas Table
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.system_quotas (
    tier_name VARCHAR(50) PRIMARY KEY,
    max_analyses_per_month INT DEFAULT 100,
    max_file_size_mb INT DEFAULT 20,
    max_workspaces INT DEFAULT 5,
    allow_multi_chart BOOLEAN DEFAULT TRUE,
    allow_api_keys BOOLEAN DEFAULT TRUE
);

ALTER TABLE public.system_quotas ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------------------
-- Supabase Storage Buckets & Policies
-- --------------------------------------------------------------------
INSERT INTO storage.buckets (id, name, public) 
VALUES ('pdf-reports', 'pdf-reports', true), ('chart-images', 'chart-images', true)
ON CONFLICT (id) DO NOTHING;

CREATE POLICY "Allow authenticated user access to PDF storage"
    ON storage.objects FOR ALL
    USING (bucket_id = 'pdf-reports' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Allow authenticated user access to Image storage"
    ON storage.objects FOR ALL
    USING (bucket_id = 'chart-images' AND auth.uid()::text = (storage.foldername(name))[1]);
