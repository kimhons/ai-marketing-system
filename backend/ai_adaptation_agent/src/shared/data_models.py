# Shared data models for the AI Adaptation Agent

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# --- Business Intake and Blueprint Models (from intake_form_questions_v3.md & blueprint requirements) ---

class BusinessIntakeData(BaseModel):
    """Represents the data structure from the Business Intake Form."""
    # Define fields based on intake_form_questions_v3.md
    # Example - to be expanded significantly
    business_name: str
    industry: str
    business_stage: str
    goals: List[str]
    target_audience_description: str
    products_services_description: str
    # ... many more fields based on the 20+ questions
    raw_responses: Dict[str, Any] # To store all question-answer pairs

class AudiencePersona(BaseModel):
    name: str
    demographics: Dict[str, Any]
    psychographics: List[str]
    pain_points: List[str]
    goals: List[str]

class MarketingStrategy(BaseModel):
    name: str
    description: str
    tactics: List[str]
    channels: List[str]
    kpis: List[str]

class BusinessBlueprint(BaseModel):
    """Represents the structured Business Blueprint generated by the agent."""
    business_id: str # Link to the business intake
    executive_summary: str
    business_profile_analysis: str
    refined_target_audience_personas: List[AudiencePersona]
    strategic_marketing_plan: List[MarketingStrategy]
    channel_plan: Dict[str, str] # Channel -> Rationale/Focus
    content_pillars_themes: List[str]
    lead_generation_funnel_outline: str
    brand_voice_messaging_guidelines: str
    kpi_measurement_framework: Dict[str, str] # KPI -> How to measure
    initial_action_plan: Dict[str, List[str]] # e.g., "30-day" -> [actions]
    # ... other sections as per ai_adaptation_agent_requirements.md

# --- Customer Matching Models ---

class CustomerQuery(BaseModel):
    """Represents a customer's query for a product or service."""
    query_text: Optional[str] = None
    service_category: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    # ... other potential fields for structured queries

class MatchedBusiness(BaseModel):
    """Represents a business matched to a customer query."""
    business_id: str
    business_name: str
    tagline: Optional[str] = None
    relevant_services: List[str]
    location: Optional[str] = None
    contact_info: Optional[str] = None # Could be a link or text
    match_reason: Optional[str] = None
    relevance_score: float

# --- Shared Utility Models ---

class LLMResponse(BaseModel):
    """Generic structure for responses from LLM interactions."""
    original_prompt: str
    generated_text: str
    metadata: Optional[Dict[str, Any]] = None

# Add more models as needed for knowledge base, configurations, etc.

