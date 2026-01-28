-- Supabase Database Schema
-- Run this in Supabase SQL Editor

-- Usage statistics table
CREATE TABLE IF NOT EXISTS usage_stats (
  id BIGSERIAL PRIMARY KEY,
  api_key TEXT NOT NULL,
  date DATE NOT NULL,
  endpoint TEXT NOT NULL,
  count INTEGER DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(api_key, date, endpoint)
);

-- Create index for fast lookups
CREATE INDEX idx_usage_stats_api_key_date ON usage_stats(api_key, date);

-- API catalog table
CREATE TABLE IF NOT EXISTS api_catalog (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  description TEXT,
  url TEXT NOT NULL,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for category filtering
CREATE INDEX idx_api_catalog_category ON api_catalog(category);

-- User tiers table
CREATE TABLE IF NOT EXISTS user_tiers (
  api_key TEXT PRIMARY KEY,
  tier TEXT NOT NULL DEFAULT 'free',
  daily_limit INTEGER NOT NULL DEFAULT 100,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- MCP servers catalog
CREATE TABLE IF NOT EXISTS mcp_servers (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  category TEXT NOT NULL,
  endpoint TEXT NOT NULL,
  is_active BOOLEAN DEFAULT true,
  usage_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE usage_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_catalog ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_tiers ENABLE ROW LEVEL SECURITY;
ALTER TABLE mcp_servers ENABLE ROW LEVEL SECURITY;

-- Public read access for catalog
CREATE POLICY "Public read api_catalog" ON api_catalog
  FOR SELECT USING (true);

CREATE POLICY "Public read mcp_servers" ON mcp_servers
  FOR SELECT USING (true);

-- Service role can do everything
CREATE POLICY "Service role full access usage_stats" ON usage_stats
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access user_tiers" ON user_tiers
  FOR ALL USING (auth.role() = 'service_role');
