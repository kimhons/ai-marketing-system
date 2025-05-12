-- Consolidated Master Database Schema for AI Marketing System

-- Enable necessary extensions first
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For GIN trigram indexes

-- Define common utility functions once
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ----------------------------------------------------------------------------
-- Users Table (from schema_users.sql)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(120),
    role VARCHAR(50) DEFAULT 'user' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);

DROP TRIGGER IF EXISTS trigger_users_updated_at ON users;
CREATE TRIGGER trigger_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE users IS 'Stores user accounts for the AI Marketing System.';
COMMENT ON COLUMN users.role IS 'User role, e.g., ''user'' for standard access, ''admin'' for administrative privileges.';

-- ----------------------------------------------------------------------------
-- Business Profiles Table (from schema.sql)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS business_profiles (
    business_id TEXT PRIMARY KEY,
    business_name TEXT NOT NULL,
    industry TEXT,
    business_stage TEXT,
    goals TEXT[],
    target_audience_description TEXT,
    products_services_description TEXT,
    location TEXT,
    service_tags TEXT[],
    raw_data_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS update_business_profiles_updated_at ON business_profiles;
CREATE TRIGGER update_business_profiles_updated_at
    BEFORE UPDATE ON business_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX IF NOT EXISTS idx_business_profiles_name_gin ON business_profiles USING GIN (business_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_business_profiles_industry_gin ON business_profiles USING GIN (industry gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_business_profiles_desc_gin ON business_profiles USING GIN (products_services_description gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_business_profiles_location_gin ON business_profiles USING GIN (location gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_business_profiles_service_tags_gin ON business_profiles USING GIN (service_tags);
CREATE INDEX IF NOT EXISTS idx_business_profiles_goals_gin ON business_profiles USING GIN (goals);

COMMENT ON TABLE business_profiles IS 'Stores detailed profiles of businesses for the AI Marketing System.';
-- (Add other comments from original schema.sql if desired)

-- ----------------------------------------------------------------------------
-- Marketing Blueprints Table (from schema_blueprints.sql)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS marketing_blueprints (
    blueprint_id TEXT PRIMARY KEY,
    business_id TEXT NOT NULL,
    executive_summary TEXT,
    business_profile_analysis TEXT,
    refined_target_audience_personas JSONB,
    strategic_marketing_plan JSONB,
    channel_plan JSONB,
    content_pillars_themes JSONB,
    lead_generation_funnel_outline TEXT,
    brand_voice_messaging_guidelines TEXT,
    kpi_measurement_framework JSONB,
    initial_action_plan JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    CONSTRAINT fk_business_profile
        FOREIGN KEY(business_id)
        REFERENCES business_profiles(business_id)
        ON DELETE CASCADE
);

DROP TRIGGER IF EXISTS update_marketing_blueprints_updated_at ON marketing_blueprints;
CREATE TRIGGER update_marketing_blueprints_updated_at
    BEFORE UPDATE ON marketing_blueprints
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX IF NOT EXISTS idx_marketing_blueprints_business_id ON marketing_blueprints (business_id);
CREATE INDEX IF NOT EXISTS idx_marketing_blueprints_created_at ON marketing_blueprints (created_at DESC);

COMMENT ON TABLE marketing_blueprints IS 'Stores generated marketing blueprints for businesses.';
-- (Add other comments from original schema_blueprints.sql if desired)

-- Final notes:
-- Ensure the database user executing this script has permissions to create extensions and tables.
-- This consolidated script should be run once to set up the entire database.

