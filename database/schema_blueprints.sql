-- Database schema for the marketing_blueprints table

-- Drop table if it exists to allow for re-creation during development
DROP TABLE IF EXISTS marketing_blueprints CASCADE;

-- Create the marketing_blueprints table
CREATE TABLE marketing_blueprints (
    blueprint_id TEXT PRIMARY KEY,
    business_id TEXT NOT NULL, -- Can be a foreign key to business_profiles.business_id if that table exists and is managed
    executive_summary TEXT,
    business_profile_analysis TEXT,
    refined_target_audience_personas JSONB, -- Stores list of persona objects
    strategic_marketing_plan JSONB, -- Stores list of strategy objects
    channel_plan JSONB, -- Stores dict of channel plans
    content_pillars_themes JSONB, -- Stores list of content pillar strings
    lead_generation_funnel_outline TEXT,
    brand_voice_messaging_guidelines TEXT,
    kpi_measurement_framework JSONB, -- Stores dict of KPI framework
    initial_action_plan JSONB, -- Stores dict of 30-60-90 day plans
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
    -- Optional: Add a foreign key constraint if business_profiles table is guaranteed
    -- CONSTRAINT fk_business_profile
    --     FOREIGN KEY(business_id)
    --     REFERENCES business_profiles(business_id)
    --     ON DELETE CASCADE
);

-- Create a trigger to automatically update the updated_at timestamp
-- (Assuming the function update_updated_at_column already exists from schema.sql for business_profiles)
-- If not, define it here:
CREATE OR REPLACE FUNCTION update_updated_at_column_for_blueprints()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_marketing_blueprints_updated_at
    BEFORE UPDATE ON marketing_blueprints
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column_for_blueprints();

-- Indexes for performance
CREATE INDEX idx_marketing_blueprints_business_id ON marketing_blueprints (business_id);
CREATE INDEX idx_marketing_blueprints_created_at ON marketing_blueprints (created_at DESC);

-- Comments for clarity
COMMENT ON TABLE marketing_blueprints IS 'Stores generated marketing blueprints for businesses.';
COMMENT ON COLUMN marketing_blueprints.blueprint_id IS 'Unique identifier for the marketing blueprint (e.g., UUID).';
COMMENT ON COLUMN marketing_blueprints.business_id IS 'Identifier for the business this blueprint belongs to.';
COMMENT ON COLUMN marketing_blueprints.executive_summary IS 'A concise overview of the marketing blueprint.';
COMMENT ON COLUMN marketing_blueprints.business_profile_analysis IS 'Analysis of the business profile, SWOT, etc.';
COMMENT ON COLUMN marketing_blueprints.refined_target_audience_personas IS 'JSONB array of detailed audience persona objects.';
COMMENT ON COLUMN marketing_blueprints.strategic_marketing_plan IS 'JSONB array of strategic marketing objectives, tactics, channels, and KPIs.';
COMMENT ON COLUMN marketing_blueprints.channel_plan IS 'JSONB object detailing the role and utilization of various marketing channels.';
COMMENT ON COLUMN marketing_blueprints.content_pillars_themes IS 'JSONB array of core content pillars or themes.';
COMMENT ON COLUMN marketing_blueprints.lead_generation_funnel_outline IS 'Textual outline of the lead generation funnel.';
COMMENT ON COLUMN marketing_blueprints.brand_voice_messaging_guidelines IS 'Guidelines for brand voice and messaging.';
COMMENT ON COLUMN marketing_blueprints.kpi_measurement_framework IS 'JSONB object mapping KPIs to measurement tools/methods.';
COMMENT ON COLUMN marketing_blueprints.initial_action_plan IS 'JSONB object for 30-60-90 day action items.';
COMMENT ON COLUMN marketing_blueprints.created_at IS 'Timestamp of when the blueprint was created.';
COMMENT ON COLUMN marketing_blueprints.updated_at IS 'Timestamp of when the blueprint was last updated.';
COMMENT ON COLUMN marketing_blueprints.version IS 'Version number of the blueprint for a given business.';

