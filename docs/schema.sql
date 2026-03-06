-- Database Schema for Webhook Tracking Pipeline

CREATE TABLE IF NOT EXISTS messages (
    idx SERIAL PRIMARY KEY,
    id UUID UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL, -- assistant, user
    content TEXT NOT NULL,
    cliente_id INTEGER,
    metdado JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    lead_id INTEGER,
    type VARCHAR(20), -- disparo, followup, conversation
    canal_uuid VARCHAR(255),
    status VARCHAR(20), -- sent, error, etc.
    read BOOLEAN DEFAULT FALSE,
    other_hash VARCHAR(255),
    has_media BOOLEAN DEFAULT FALSE,
    media_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS meta_erros (
    idx SERIAL PRIMARY KEY,
    id INTEGER UNIQUE,
    erro INTEGER,
    detalhes TEXT,
    solucoes TEXT,
    code_requests VARCHAR(50),
    critical_template BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS black_leads (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER,
    strategy INTEGER NOT NULL DEFAULT 0,
    phone_number VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    erro_code BIGINT REFERENCES meta_erros(erro),
    service_send VARCHAR(20)  -- disparo, followup, conversation
);

CREATE INDEX IF NOT EXISTS idx_black_leads_conversation_id ON black_leads(conversation_id);
CREATE INDEX IF NOT EXISTS idx_black_leads_phone ON black_leads(phone_number);
