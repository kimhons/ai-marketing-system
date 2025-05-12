-- Database schema for the business_profiles table

-- Drop table if it exists to allow for re-creation during development
-- In a production environment, migrations would be handled more carefully.
DROP TABLE IF EXISTS business_profiles CASCADE;

-- Create the business_profiles table
CREATE TABLE business_profiles (
    business_id TEXT PRIMARY KEY,
    business_name TEXT NOT NULL,
    industry TEXT,
    business_stage TEXT,
    goals TEXT[],  -- Array of text for multiple goals
    target_audience_description TEXT,
    products_services_description TEXT,
    location TEXT,
    service_tags TEXT[], -- Array of text for multiple service tags
    raw_data_json JSONB, -- For storing other miscellaneous structured data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create a trigger to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_business_profiles_updated_at
    BEFORE UPDATE ON business_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Indexes for performance
-- Index on business_id is created automatically due to PRIMARY KEY constraint.

-- For text searches using ILIKE, GIN indexes with pg_trgm extension are often best.
-- If pg_trgm is not available or for simpler setup, standard GIN or BTREE on LOWER(column) can be used.
-- Assuming pg_trgm might not be universally available in all test environments, 
-- we will create GIN indexes which are generally good for text array searches and can help with text ILIKE.

-- Index for case-insensitive search on business_name
CREATE INDEX idx_business_profiles_name_gin ON business_profiles USING GIN (business_name gin_trgm_ops); -- Requires pg_trgm extension
-- If pg_trgm is not available, a simple BTREE index on lowercased text can be an alternative for some cases:
-- CREATE INDEX idx_business_profiles_name_lower ON business_profiles (LOWER(business_name) text_pattern_ops);

-- Index for case-insensitive search on industry
CREATE INDEX idx_business_profiles_industry_gin ON business_profiles USING GIN (industry gin_trgm_ops); -- Requires pg_trgm extension
-- CREATE INDEX idx_business_profiles_industry_lower ON business_profiles (LOWER(industry) text_pattern_ops);

-- Index for full-text search on products_services_description
CREATE INDEX idx_business_profiles_desc_gin ON business_profiles USING GIN (products_services_description gin_trgm_ops); -- Requires pg_trgm extension

-- Index for case-insensitive search on location
CREATE INDEX idx_business_profiles_location_gin ON business_profiles USING GIN (location gin_trgm_ops); -- Requires pg_trgm extension
-- CREATE INDEX idx_business_profiles_location_lower ON business_profiles (LOWER(location) text_pattern_ops);

-- GIN index for searching within the service_tags array
CREATE INDEX idx_business_profiles_service_tags_gin ON business_profiles USING GIN (service_tags);

-- GIN index for searching within the goals array (if frequently searched)
CREATE INDEX idx_business_profiles_goals_gin ON business_profiles USING GIN (goals);


COMMENT ON TABLE business_profiles IS 'Stores detailed profiles of businesses for the AI Marketing System.';
COMMENT ON COLUMN business_profiles.business_id IS 'Unique identifier for the business (e.g., from an external system or generated).';
COMMENT ON COLUMN business_profiles.business_name IS 'Official name of the business.';
COMMENT ON COLUMN business_profiles.industry IS 'Primary industry the business operates in (e.g., Home Services, Financial Services).';
COMMENT ON COLUMN business_profiles.business_stage IS 'Current stage of the business (e.g., Startup, Growth, Established).';
COMMENT ON COLUMN business_profiles.goals IS 'Array of business goals (e.g., Increase brand awareness, Generate leads).';
COMMENT ON COLUMN business_profiles.target_audience_description IS 'Textual description of the business''s target audience.';
COMMENT ON COLUMN business_profiles.products_services_description IS 'Detailed description of products or services offered.';
COMMENT ON COLUMN business_profiles.location IS 'Primary operational location or service area of the business.';
COMMENT ON COLUMN business_profiles.service_tags IS 'Array of keywords or tags describing specific services offered (e.g., plumbing, emergency_repair, seo_optimization).';
COMMENT ON COLUMN business_profiles.raw_data_json IS 'JSONB field for storing additional, less structured data or metadata from the intake form or other sources.';
COMMENT ON COLUMN business_profiles.created_at IS 'Timestamp of when the business profile was created.';
COMMENT ON COLUMN business_profiles.updated_at IS 'Timestamp of when the business profile was last updated.';

-- Note: To use GIN indexes with gin_trgm_ops, the pg_trgm extension must be enabled in PostgreSQL:
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- If this extension is not available, the alternative BTREE indexes on LOWER(column) with text_pattern_ops (for left-anchored ILIKE) 
-- or simple GIN indexes (for full text search capabilities) can be considered, though their performance characteristics for general ILIKE may vary.

