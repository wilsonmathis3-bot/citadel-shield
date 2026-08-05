-- ============================================================
-- BOS CS LLC — UNIFIED RAILWAY DATABASE SCHEMA
-- Version: 1.0.0 | Date: 2026-08-05
-- Platform: PostgreSQL 15+ on Railway
-- ============================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- -----------------------------------------------------------
-- CORE IDENTITY & TENANCY
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS workspaces (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    slug            VARCHAR(100) UNIQUE NOT NULL,
    owner_id        UUID NOT NULL,
    plan_tier       VARCHAR(50) DEFAULT 'free',
    settings        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255),
    role            VARCHAR(50) DEFAULT 'member',
    profile         JSONB DEFAULT '{}',
    mfa_enabled     BOOLEAN DEFAULT FALSE,
    last_login      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS api_keys (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
    name            VARCHAR(255) NOT NULL,
    key_hash        VARCHAR(255) NOT NULL,
    key_prefix      VARCHAR(20) NOT NULL,
    scopes          JSONB DEFAULT '["read"]',
    expires_at      TIMESTAMPTZ,
    last_used_at    TIMESTAMPTZ,
    revoked_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------
-- PROJECT REGISTRY (All 28+ Projects)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS projects (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    code            VARCHAR(50) UNIQUE NOT NULL,
    name            VARCHAR(255) NOT NULL,
    category        VARCHAR(50) NOT NULL,
    description     TEXT,
    status          VARCHAR(50) DEFAULT 'planning',
    config          JSONB DEFAULT '{}',
    repo_url        VARCHAR(500),
    deploy_url      VARCHAR(500),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO projects (code, name, category, description, status) VALUES
('bos_crm', 'BOS CRM + PDF Auto-Population', 'webapp', 'Contact/lead tracking with PDF generation', 'planning'),
('railway_memory', 'Railway SQL Memory System', 'ai', 'Persistent conversation memory architecture', 'planning'),
('bmw_diag', 'BMW AI Diagnostic Web App', 'automotive', 'OBD-II based BMW fault diagnosis', 'planning'),
('stolen_tracker', 'Stolen Vehicle Tracker', 'automotive', 'Passive OBD-II trip signature logging', 'planning'),
('mazda_parts', 'Mazda 3 Parts Compatibility API', 'automotive', 'Parts interchange database', 'planning'),
('citadel', 'CITADEL Zero-Knowledge Vault', 'cybersecurity', 'Device-encrypted vault with server-side blobs', 'planning'),
('privacy_summarizer', 'Privacy Policy Summarizer', 'cybersecurity', 'Plain-language privacy policy analysis', 'planning'),
('privacy_search', 'Custom Privacy Search Engine', 'cybersecurity', 'Tracking-free personalized search', 'planning'),
('metatron', 'Metatron Cube Multi-Agent', 'ai', '13-node sacred geometry agent orchestration', 'planning'),
('tesla_369', 'Tesla 3-6-9 Swarm Research', 'ai', 'Numerology-constrained swarm research', 'planning'),
('hydra', 'Hydra Survival AI', 'ai', 'Autonomous resource-acquisition AI', 'planning'),
('offline_ai', 'Offline AI Stack', 'ai', 'llama.cpp + Whisper on AMD/CPU', 'planning'),
('viral_scraper', 'Foreign Viral Creator Scraper', 'scraping', 'Douyin/foreign platform creator scraping', 'planning'),
('unclaimed_funds', 'Unclaimed Funds Recovery Scraper', 'scraping', 'State/federal unclaimed property scraper', 'planning'),
('same_day_income', 'Same-Day Income Scraper', 'scraping', 'Gig/job filter for immediate pay', 'planning'),
('keystudio_midi', 'KeyStudio 25 Linux MIDI Bridge', 'audio', 'MIDI routing and mapping for KeyStudio 25', 'planning'),
('wave_player', 'Linux Wave Player Utility', 'audio', 'CLI .wav player for Linux/Termux', 'planning'),
('linkedin_auto', 'LinkedIn Campaign Automation', 'marketing', 'Outreach and pitch sequences for BOS CS', 'planning'),
('pitch_deck', 'Million-Dollar Pitch Deck Generator', 'marketing', 'AI-powered investor slide deck creator', 'planning'),
('console_clean', 'Console Cleaning Marketing Site', 'marketing', 'Landing page for console repair/cleaning', 'planning'),
('ghost_sensor', 'In-Home Radar / Ghost Sensor', 'scientific', 'DIY radar and environmental anomaly detection', 'planning'),
('em_rail', 'Homemade Electromagnetic Rail', 'scientific', 'Linear induction projectile launcher', 'planning'),
('fft_ecosystem', 'FFT Ecosystem (GPS Spoof Defense)', 'scientific', 'SDR-based signal analysis and spoof detection', 'planning'),
('elk_template', 'ELK Stack Template', 'devops', 'Pre-configured logging and monitoring stack', 'planning'),
('sop_generator', 'Automated Procedures Generator', 'devops', 'AI-generated standard operating procedures', 'planning'),
('vscode_guide', 'VS Code Workspace Guide', 'devops', 'Setup scripts and file type documentation', 'planning'),
('gumroad_tracker', 'Gumroad License Tracker', 'webapp', 'License key management for Gumroad products', 'planning'),
('sentinel', 'Sentinel Secretary', 'webapp', 'AI executive assistant with voice commands', 'planning')
ON CONFLICT (code) DO NOTHING;

-- -----------------------------------------------------------
-- UNIFIED AI / MEMORY / AGENT SYSTEM
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS ai_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    project_id      UUID REFERENCES projects(id) ON DELETE SET NULL,
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
    session_type    VARCHAR(50) NOT NULL,
    title           VARCHAR(255),
    context_window  JSONB DEFAULT '[]',
    metadata        JSONB DEFAULT '{}',
    archived_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ai_memories (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID REFERENCES ai_sessions(id) ON DELETE CASCADE,
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    memory_type     VARCHAR(50) NOT NULL,
    content         TEXT NOT NULL,
    tags            JSONB DEFAULT '[]',
    priority        INTEGER DEFAULT 5,
    confidence      DECIMAL(3,2) DEFAULT 1.00,
    source          VARCHAR(255),
    verified        BOOLEAN DEFAULT FALSE,
    verified_at     TIMESTAMPTZ,
    verified_by     UUID REFERENCES users(id) ON DELETE SET NULL,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ai_agents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    project_id      UUID REFERENCES projects(id) ON DELETE SET NULL,
    agent_code      VARCHAR(50) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    role_desc       TEXT NOT NULL,
    model_config    JSONB DEFAULT '{}',
    geometry_node   VARCHAR(50),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID REFERENCES ai_sessions(id) ON DELETE CASCADE,
    agent_id        UUID REFERENCES ai_agents(id) ON DELETE SET NULL,
    input_payload   JSONB NOT NULL,
    output_payload JSONB NOT NULL,
    confidence      DECIMAL(3,2),
    dissent_notes   TEXT,
    latency_ms      INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------
-- CRM / CONTACTS / OUTREACH
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS contacts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    project_id      UUID REFERENCES projects(id) ON DELETE SET NULL,
    contact_type    VARCHAR(50) NOT NULL,
    first_name      VARCHAR(255),
    last_name       VARCHAR(255),
    email           VARCHAR(255),
    phone           VARCHAR(50),
    company         VARCHAR(255),
    title           VARCHAR(255),
    linkedin_url    VARCHAR(500),
    source          VARCHAR(255),
    tags            JSONB DEFAULT '[]',
    custom_fields   JSONB DEFAULT '{}',
    status          VARCHAR(50) DEFAULT 'new',
    assigned_to     UUID REFERENCES users(id) ON DELETE SET NULL,
    last_contact_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS outreach_sequences (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    project_id      UUID REFERENCES projects(id) ON DELETE SET NULL,
    name            VARCHAR(255) NOT NULL,
    target_vertical VARCHAR(100),
    sequence_steps  JSONB NOT NULL,
    is_active       BOOLEAN DEFAULT TRUE,
    metrics         JSONB DEFAULT '{"sent":0,"replied":0,"meetings":0}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS outreach_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sequence_id     UUID REFERENCES outreach_sequences(id) ON DELETE CASCADE,
    contact_id      UUID REFERENCES contacts(id) ON DELETE CASCADE,
    step_number     INTEGER NOT NULL,
    action          VARCHAR(50) NOT NULL,
    content         TEXT,
    status          VARCHAR(50) DEFAULT 'pending',
    replied_at      TIMESTAMPTZ,
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------
-- AUTOMOTIVE
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS vehicles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    project_id      UUID REFERENCES projects(id) ON DELETE SET NULL,
    vin             VARCHAR(50),
    make            VARCHAR(100) NOT NULL,
    model           VARCHAR(100) NOT NULL,
    year            INTEGER,
    trim            VARCHAR(100),
    engine_code     VARCHAR(50),
    owner_id        UUID REFERENCES users(id) ON DELETE SET NULL,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS obd_readings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id      UUID REFERENCES vehicles(id) ON DELETE CASCADE,
    reading_type    VARCHAR(50) NOT NULL,
    code            VARCHAR(50),
    description     TEXT,
    severity        VARCHAR(50),
    raw_data        JSONB NOT NULL,
    ai_diagnosis    JSONB,
    recorded_at     TIMESTAMPTZ DEFAULT NOW(),
    location        GEOGRAPHY(POINT,4326)
);

CREATE TABLE IF NOT EXISTS trip_signatures (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id      UUID REFERENCES vehicles(id) ON DELETE CASCADE,
    signature_hash  VARCHAR(255) NOT NULL,
    start_time      TIMESTAMPTZ NOT NULL,
    end_time        TIMESTAMPTZ,
    distance_km     DECIMAL(10,2),
    avg_speed       DECIMAL(5,2),
    max_speed       DECIMAL(5,2),
    fuel_used_l     DECIMAL(5,2),
    is_authorized   BOOLEAN DEFAULT TRUE,
    alert_sent      BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS parts_catalog (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    part_number     VARCHAR(100) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    category        VARCHAR(100) NOT NULL,
    make            VARCHAR(100),
    model           VARCHAR(100),
    year_start      INTEGER,
    year_end        INTEGER,
    interchange_ids JSONB DEFAULT '[]',
    specs           JSONB DEFAULT '{}',
    price_range     JSONB,
    source_urls     JSONB DEFAULT '[]',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------
-- CYBERSECURITY
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS vaults (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    vault_name      VARCHAR(255) NOT NULL,
    blob_id         VARCHAR(255) NOT NULL,
    blob_size       BIGINT,
    blob_checksum   VARCHAR(255),
    encryption_meta JSONB NOT NULL,
    last_sync_at    TIMESTAMPTZ,
    device_count    INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vault_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vault_id        UUID REFERENCES vaults(id) ON DELETE CASCADE,
    item_type       VARCHAR(50) NOT NULL,
    encrypted_data  BYTEA NOT NULL,
    encrypted_title BYTEA,
    version         INTEGER DEFAULT 1,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS threat_iocs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    ioc_type        VARCHAR(50) NOT NULL,
    value           VARCHAR(255) NOT NULL,
    threat_level    VARCHAR(50) DEFAULT 'medium',
    source          VARCHAR(255),
    first_seen      TIMESTAMPTZ DEFAULT NOW(),
    last_seen       TIMESTAMPTZ,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS privacy_policies (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    url             VARCHAR(500) NOT NULL,
    domain          VARCHAR(255) NOT NULL,
    raw_text        TEXT,
    summary         TEXT,
    risk_score      INTEGER,
    data_practices  JSONB DEFAULT '{}',
    reading_level   VARCHAR(50),
    analyzed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------
-- SCRAPING
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS scrape_jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    project_id      UUID REFERENCES projects(id) ON DELETE SET NULL,
    job_name        VARCHAR(255) NOT NULL,
    source_platform VARCHAR(100) NOT NULL,
    target_url      VARCHAR(500),
    schedule        VARCHAR(100),
    status          VARCHAR(50) DEFAULT 'idle',
    last_run_at     TIMESTAMPTZ,
    next_run_at     TIMESTAMPTZ,
    config          JSONB DEFAULT '{}',
    error_log       TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS scraped_data (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id          UUID REFERENCES scrape_jobs(id) ON DELETE CASCADE,
    source_id       VARCHAR(255),
    raw_data        JSONB NOT NULL,
    normalized_data JSONB NOT NULL,
    match_score     DECIMAL(3,2),
    is_processed    BOOLEAN DEFAULT FALSE,
    processed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------
-- AUDIO / MIDI
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS midi_devices (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    device_name     VARCHAR(255) NOT NULL,
    device_id       VARCHAR(255) NOT NULL,
    vendor_id       VARCHAR(10),
    product_id      VARCHAR(10),
    is_connected    BOOLEAN DEFAULT FALSE,
    last_seen_at    TIMESTAMPTZ,
    config          JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS midi_mappings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id       UUID REFERENCES midi_devices(id) ON DELETE CASCADE,
    mapping_name    VARCHAR(255) NOT NULL,
    mapping_type    VARCHAR(50) NOT NULL,
    source_cc       INTEGER,
    source_note     INTEGER,
    target_action   VARCHAR(255),
    target_channel  INTEGER DEFAULT 1,
    min_value       INTEGER DEFAULT 0,
    max_value       INTEGER DEFAULT 127,
    curve           VARCHAR(50) DEFAULT 'linear',
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audio_playlists (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    tracks          JSONB DEFAULT '[]',
    shuffle         BOOLEAN DEFAULT FALSE,
    loop            BOOLEAN DEFAULT FALSE,
    volume          DECIMAL(3,2) DEFAULT 1.00,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------
-- SCIENTIFIC / HARDWARE
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS sensors (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    project_id      UUID REFERENCES projects(id) ON DELETE SET NULL,
    sensor_name     VARCHAR(255) NOT NULL,
    sensor_type     VARCHAR(50) NOT NULL,
    hardware_id     VARCHAR(255),
    location        GEOGRAPHY(POINT,4326),
    config          JSONB DEFAULT '{}',
    is_active       BOOLEAN DEFAULT TRUE,
    last_reading_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sensor_readings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sensor_id       UUID REFERENCES sensors(id) ON DELETE CASCADE,
    reading_type    VARCHAR(50) NOT NULL,
    value           JSONB NOT NULL,
    anomaly_score   DECIMAL(5,4) DEFAULT 0.0000,
    classified_as   VARCHAR(100),
    raw_bytes       BYTEA,
    recorded_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS em_rail_tests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    test_number     INTEGER NOT NULL,
    capacitor_voltage DECIMAL(6,2),
    projectile_mass_g INTEGER,
    projectile_material VARCHAR(100),
    velocity_ms     DECIMAL(6,2),
    energy_joules   DECIMAL(8,4),
    efficiency_pct  DECIMAL(5,2),
    safety_check    JSONB DEFAULT '{}',
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------
-- DEVOPS / SOP / ELK
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS procedures (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    project_id      UUID REFERENCES projects(id) ON DELETE SET NULL,
    title           VARCHAR(255) NOT NULL,
    category        VARCHAR(100) NOT NULL,
    version         INTEGER DEFAULT 1,
    status          VARCHAR(50) DEFAULT 'draft',
    steps           JSONB NOT NULL,
    risk_assessment JSONB DEFAULT '{}',
    compliance_tags JSONB DEFAULT '[]',
    approved_by     UUID REFERENCES users(id) ON DELETE SET NULL,
    approved_at     TIMESTAMPTZ,
    created_by      UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS procedure_revisions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    procedure_id    UUID REFERENCES procedures(id) ON DELETE CASCADE,
    version         INTEGER NOT NULL,
    diff            JSONB NOT NULL,
    changed_by      UUID REFERENCES users(id) ON DELETE SET NULL,
    change_reason   TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS elk_configs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    config_name     VARCHAR(255) NOT NULL,
    stack_version   VARCHAR(50),
    docker_compose  TEXT,
    log_pipelines   JSONB DEFAULT '[]',
    alert_rules     JSONB DEFAULT '[]',
    index_lifecycle JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------
-- WEB APPS / SAAS
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    project_id      UUID REFERENCES projects(id) ON DELETE SET NULL,
    gumroad_id      VARCHAR(255),
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    price           DECIMAL(10,2),
    currency        VARCHAR(3) DEFAULT 'USD',
    status          VARCHAR(50) DEFAULT 'draft',
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS licenses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id      UUID REFERENCES products(id) ON DELETE CASCADE,
    license_key     VARCHAR(255) UNIQUE NOT NULL,
    customer_email  VARCHAR(255),
    customer_id     VARCHAR(255),
    activation_limit INTEGER DEFAULT 1,
    activation_count INTEGER DEFAULT 0,
    activations     JSONB DEFAULT '[]',
    revoked_at      TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pitch_decks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    project_id      UUID REFERENCES projects(id) ON DELETE SET NULL,
    title           VARCHAR(255) NOT NULL,
    template        VARCHAR(50) DEFAULT 'yc',
    business_idea   TEXT,
    target_market   TEXT,
    financials      JSONB DEFAULT '{}',
    team            JSONB DEFAULT '[]',
    slides          JSONB NOT NULL,
    ai_enhancements JSONB DEFAULT '{}',
    export_formats  JSONB DEFAULT '["pdf","html"]',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bookings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    project_id      UUID REFERENCES projects(id) ON DELETE SET NULL,
    contact_id      UUID REFERENCES contacts(id) ON DELETE SET NULL,
    service_type    VARCHAR(100) NOT NULL,
    scheduled_at    TIMESTAMPTZ NOT NULL,
    duration_min    INTEGER DEFAULT 60,
    status          VARCHAR(50) DEFAULT 'pending',
    price           DECIMAL(10,2),
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------
-- FINANCIAL / STRIPE / TRANSACTIONS
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS transactions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    project_id      UUID REFERENCES projects(id) ON DELETE SET NULL,
    transaction_type VARCHAR(50) NOT NULL,
    amount          DECIMAL(12,2) NOT NULL,
    currency        VARCHAR(3) DEFAULT 'USD',
    source          VARCHAR(255),
    source_id       VARCHAR(255),
    description     TEXT,
    category        VARCHAR(100),
    status          VARCHAR(50) DEFAULT 'pending',
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------
-- UNIFIED AUDIT / LOGGING
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS event_log (
    id              BIGSERIAL PRIMARY KEY,
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    project_id      UUID REFERENCES projects(id) ON DELETE SET NULL,
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type      VARCHAR(100) NOT NULL,
    severity        VARCHAR(50) DEFAULT 'info',
    message         TEXT NOT NULL,
    payload         JSONB DEFAULT '{}',
    ip_address      INET,
    user_agent      VARCHAR(500),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_event_log_workspace ON event_log(workspace_id);
CREATE INDEX IF NOT EXISTS idx_event_log_project ON event_log(project_id);
CREATE INDEX IF NOT EXISTS idx_event_log_created ON event_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_event_log_type ON event_log(event_type);

-- -----------------------------------------------------------
-- INDEXES FOR PERFORMANCE
-- -----------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_users_workspace ON users(workspace_id);
CREATE INDEX IF NOT EXISTS idx_contacts_workspace ON contacts(workspace_id);
CREATE INDEX IF NOT EXISTS idx_contacts_status ON contacts(status);
CREATE INDEX IF NOT EXISTS idx_ai_memories_session ON ai_memories(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_memories_type ON ai_memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_scraped_data_job ON scraped_data(job_id);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_sensor ON sensor_readings(sensor_id);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_time ON sensor_readings(recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_obd_vehicle ON obd_readings(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_parts_number ON parts_catalog(part_number);
CREATE INDEX IF NOT EXISTS idx_licenses_product ON licenses(product_id);
CREATE INDEX IF NOT EXISTS idx_vaults_user ON vaults(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_workspace ON transactions(workspace_id);

-- -----------------------------------------------------------
-- ROW LEVEL SECURITY (RLS)
-- -----------------------------------------------------------
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE vaults ENABLE ROW LEVEL SECURITY;
ALTER TABLE vault_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE vehicles ENABLE ROW LEVEL SECURITY;
ALTER TABLE sensors ENABLE ROW LEVEL SECURITY;
ALTER TABLE sensor_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE event_log ENABLE ROW LEVEL SECURITY;

-- -----------------------------------------------------------
-- COMMENTS FOR DOCUMENTATION
-- -----------------------------------------------------------
COMMENT ON TABLE projects IS 'Master registry of all BOS CS LLC projects. Each project maps to a specific table group.';
COMMENT ON TABLE ai_memories IS 'Persistent memory store for AI agents. Server never sees plaintext for encrypted vaults.';
COMMENT ON TABLE vault_items IS 'Zero-knowledge: server stores only encrypted blobs. Keys never leave user devices.';
COMMENT ON TABLE event_log IS 'Unified audit trail. All projects write here for observability and compliance.';
