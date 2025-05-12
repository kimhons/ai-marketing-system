# Service for generating Business Blueprints

import os
import json
import uuid # For generating unique blueprint IDs
from typing import Dict, Any, List, Optional
import psycopg2
from psycopg2 import pool, extras

from ..shared.data_models import BusinessIntakeData, BusinessBlueprint, LLMResponse
from ..shared.llm_service import LLMService

class BlueprintService:
    """
    Orchestrates the generation of a Business Blueprint from BusinessIntakeData.
    Uses various analysis modules and the LLMService.
    Also handles storage and retrieval of blueprints from the database.
    """
    DB_TABLE_NAME = "marketing_blueprints"

    def __init__(self, llm_service: LLMService, db_config: Optional[Dict[str, str]] = None, min_conn: int = 1, max_conn: int = 5):
        """
        Initialize the BlueprintService.
        Args:
            llm_service: An instance of the LLMService for AI-powered analysis.
            db_config: (Optional) A dictionary containing database connection parameters.
                       If not provided, uses environment variables.
            min_conn: Minimum number of connections for the pool.
            max_conn: Maximum number of connections for the pool.
        """
        self.llm_service = llm_service
        self.db_connection_pool = None
        self._db_config = None

        if db_config:
            self._db_config = db_config
        else:
            print("BlueprintService: Database configuration not provided directly, attempting to load from environment variables...")
            self._db_config = {
                "host": os.getenv("DB_HOST"),
                "port": os.getenv("DB_PORT", "5432"),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "dbname": os.getenv("DB_NAME")
            }
            if not all(val for val in [self._db_config["host"], self._db_config["user"], self._db_config["password"], self._db_config["dbname"]]):
                print("BlueprintService Warning: Critical database environment variables (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME) are not fully set. Database connection will likely fail.")
            else:
                print("BlueprintService: Database configuration loaded from environment variables.")

        if self._db_config and all(val for val in [self._db_config["host"], self._db_config["user"], self._db_config["password"], self._db_config["dbname"]]):
            try:
                print(f"BlueprintService: Initializing database connection pool for {self._db_config["dbname"]} on {self._db_config["host"]}:{self._db_config["port"]}...")
                self.db_connection_pool = psycopg2.pool.SimpleConnectionPool(
                    min_conn, 
                    max_conn,
                    host=self._db_config["host"],
                    port=self._db_config["port"],
                    user=self._db_config["user"],
                    password=self._db_config["password"],
                    dbname=self._db_config["dbname"]
                )
                # Test the connection
                conn = self.db_connection_pool.getconn()
                print("BlueprintService: Database connection pool successfully created and tested.")
                self.db_connection_pool.putconn(conn)
            except psycopg2.Error as e:
                print(f"BlueprintService Error: Error creating database connection pool: {e}")
                self.db_connection_pool = None
        else:
            print("BlueprintService: Database configuration is incomplete. Connection pool not created.")
        
        print("BlueprintService initialized.")

    def _get_db_connection(self):
        if not self.db_connection_pool:
            print("BlueprintService Error: Database connection pool is not available.")
            return None
        try:
            return self.db_connection_pool.getconn()
        except psycopg2.Error as e:
            print(f"BlueprintService Error: Error getting connection from pool: {e}")
            return None

    def _put_db_connection(self, conn):
        if self.db_connection_pool and conn:
            self.db_connection_pool.putconn(conn)

    def close_db_pool(self):
        if self.db_connection_pool:
            print("BlueprintService: Closing database connection pool...")
            self.db_connection_pool.closeall()
            print("BlueprintService: Database connection pool closed.")

    def _generate_executive_summary(self, intake_data: BusinessIntakeData, core_analysis: str) -> str:
        print("Generating Executive Summary...")
        prompt = f"""Based on the following business intake data and core analysis, write a concise and compelling executive summary (around 150-250 words) for a marketing blueprint for {intake_data.business_name}.
        Business Name: {intake_data.business_name}
        Industry: {intake_data.industry}
        Business Stage: {intake_data.business_stage}
        Key Goals: {", ".join(intake_data.goals)}
        Products/Services: {intake_data.products_services_description}
        Target Audience: {intake_data.target_audience_description}
        Core Analysis Insights: {core_analysis}

        The executive summary should highlight the primary marketing objectives and the overall strategic direction recommended in the blueprint.
        """
        response = self.llm_service.generate_text(prompt, max_tokens=300)
        return response.generated_text if response.success else "Could not generate executive summary."

    def _analyze_business_profile(self, intake_data: BusinessIntakeData) -> str:
        print("Analyzing Business Profile...")
        prompt = f"""Conduct a brief analysis of the following business profile for {intake_data.business_name}. 
        Focus on its strengths, weaknesses, opportunities, and threats (SWOT) from a marketing perspective. 
        Identify key marketing challenges and advantages.

        Business Name: {intake_data.business_name}
        Industry: {intake_data.industry}
        Business Stage: {intake_data.business_stage}
        Goals: {", ".join(intake_data.goals)}
        Target Audience: {intake_data.target_audience_description}
        Products/Services: {intake_data.products_services_description}
        Current Marketing Efforts (if any from raw_responses): {intake_data.raw_responses.get("current_marketing_efforts", "Not specified")}
        Competitor Landscape (if any from raw_responses): {intake_data.raw_responses.get("competitors", "Not specified")}

        Provide the analysis as a coherent text block (around 200-300 words).
        """
        response = self.llm_service.generate_text(prompt, max_tokens=400)
        return response.generated_text if response.success else "Could not generate business profile analysis."

    def _generate_audience_personas(self, intake_data: BusinessIntakeData) -> List[Dict[str, Any]]:
        print("Generating Audience Personas...")
        prompt = f"""Based on the target audience description for {intake_data.business_name} (Industry: {intake_data.industry}): 
        "{intake_data.target_audience_description}"

        Generate 2 detailed audience personas. For each persona, include:
        - name (e.g., "Marketing Manager Mark", "Small Business Owner Sarah")
        - demographics (e.g., age range, location, job title, education)
        - psychographics (e.g., values, interests, lifestyle, personality traits relevant to the business)
        - pain_points (challenges they face that {intake_data.business_name} can solve)
        - goals (what they want to achieve, relevant to {intake_data.business_name}"s offerings)
        - preferred_channels (how they consume information or look for solutions)

        Return the response as a JSON list of persona objects. Each object should have keys: "name", "demographics", "psychographics", "pain_points", "goals", "preferred_channels".
        Example of a single persona object in the list:
        {{ "name": "Innovative Ian", "demographics": {{"age": "30-45", "role": "CTO"}}, "psychographics": ["Early adopter", "Data-driven"], "pain_points": ["Outdated systems", "Inefficient workflows"], "goals": ["Improve team productivity", "Implement cutting-edge tech"], "preferred_channels": ["Tech blogs", "Industry conferences", "LinkedIn"] }}
        """
        response_obj = self.llm_service.generate_json_response(prompt, max_tokens=1000)
        if response_obj and isinstance(response_obj, list):
            return response_obj
        elif response_obj and isinstance(response_obj, dict) and "personas" in response_obj and isinstance(response_obj["personas"], list):
             return response_obj["personas"] # Sometimes LLM wraps it
        print(f"Failed to generate valid JSON for personas. LLM response: {response_obj}")
        return [{ "name": "Default Persona", "error": "Could not parse LLM response for personas." }]

    def _generate_strategic_marketing_plan(self, intake_data: BusinessIntakeData, personas: List[Dict[str, Any]], business_analysis: str) -> List[Dict[str, Any]]:
        print("Generating Strategic Marketing Plan...")
        personas_summary = "\n".join([f"- Persona: {p.get("name", "N/A")}, Key Pain Point: {p.get("pain_points", ["N/A"])[0] if p.get("pain_points") else "N/A"}" for p in personas])
        prompt = f"""Develop a strategic marketing plan for {intake_data.business_name} (Industry: {intake_data.industry}).
        Business Goals: {", ".join(intake_data.goals)}
        Target Audience Personas Summary:
        {personas_summary}
        Business Profile Analysis Insights: {business_analysis}

        Outline 3-4 key strategic marketing objectives. For each objective, suggest:
        - name (e.g., "Increase Brand Awareness", "Generate Qualified Leads", "Enhance Customer Engagement")
        - description (a brief explanation of the objective)
        - tactics (list of 2-3 specific actions, e.g., ["SEO optimization for local keywords", "Run targeted Facebook ad campaigns"])
        - channels (list of platforms/mediums, e.g., ["Google My Business", "Facebook", "Company Blog"])
        - kpis (list of key performance indicators to measure success, e.g., ["Website traffic from organic search", "Lead conversion rate"])

        Return the response as a JSON list of marketing strategy objects. Each object should have keys: "name", "description", "tactics", "channels", "kpis".
        """
        response_obj = self.llm_service.generate_json_response(prompt, max_tokens=1500)
        if response_obj and isinstance(response_obj, list):
            return response_obj
        elif response_obj and isinstance(response_obj, dict) and "strategies" in response_obj and isinstance(response_obj["strategies"], list):
            return response_obj["strategies"]
        print(f"Failed to generate valid JSON for strategic plan. LLM response: {response_obj}")
        return [{ "name": "Default Strategy", "error": "Could not parse LLM response for strategic plan." }]

    def _generate_channel_plan(self, strategic_plan: List[Dict[str, Any]]) -> Dict[str, str]:
        print("Generating Channel Plan...")
        all_channels = set()
        for strategy in strategic_plan:
            if isinstance(strategy.get("channels"), list):
                for channel in strategy.get("channels", []):
                    all_channels.add(channel)
        
        if not all_channels:
            return {"Default Channel": "No channels identified from strategic plan."}

        prompt = f"""Based on the following marketing channels identified in a strategic plan: {", ".join(list(all_channels))}.
        For each channel, provide a brief (1-2 sentences) recommendation on its primary role or how it should be utilized for marketing efforts.
        Return the response as a JSON object where keys are channel names and values are their recommended roles.
        Example: {{ "Company Blog": "Serve as the primary hub for thought leadership content and SEO value.", "LinkedIn": "Focus on B2B networking, professional content sharing, and direct outreach." }}
        """
        response_obj = self.llm_service.generate_json_response(prompt, max_tokens=700)
        if response_obj and isinstance(response_obj, dict):
            return response_obj
        print(f"Failed to generate valid JSON for channel plan. LLM response: {response_obj}")
        return {channel: "Could not generate role description." for channel in all_channels}

    def _generate_content_pillars(self, intake_data: BusinessIntakeData, personas: List[Dict[str, Any]]) -> List[str]:
        print("Generating Content Pillars/Themes...")
        personas_summary = "\n".join([f"- Persona: {p.get("name", "N/A")}, Key Interests/Pain Points: {p.get("pain_points", ["N/A"])[0] if p.get("pain_points") else "N/A"}, {p.get("goals", ["N/A"])[0] if p.get("goals") else "N/A"}" for p in personas])
        prompt = f"""For {intake_data.business_name} (Industry: {intake_data.industry}), which offers "{intake_data.products_services_description}", and targets the following personas:
        {personas_summary}

        Suggest 3-5 core content pillars or recurring themes that would resonate with these personas and align with the business"s offerings. These pillars should guide content creation.
        Return the response as a JSON list of strings, where each string is a content pillar/theme.
        Example: ["Solving [Common Pain Point] with [Product/Service Type]", "The Future of [Industry Trend] for [Target Audience Segment]", "Client Success Stories and Case Studies"] 
        """
        response_obj = self.llm_service.generate_json_response(prompt, max_tokens=500)
        if response_obj and isinstance(response_obj, list) and all(isinstance(item, str) for item in response_obj):
            return response_obj
        print(f"Failed to generate valid JSON list of strings for content pillars. LLM response: {response_obj}")
        return ["Default Content Pillar: Addressing customer needs effectively."]

    def _generate_lead_funnel_outline(self, intake_data: BusinessIntakeData, strategic_plan: List[Dict[str, Any]]) -> str:
        print("Generating Lead Funnel Outline...")
        plan_summary = "\n".join([f"- Strategy: {s.get("name")}, Tactics: {", ".join(s.get("tactics", []))}" for s in strategic_plan])
        prompt = f"""Outline a basic lead generation funnel for {intake_data.business_name}, considering its goals ({", ".join(intake_data.goals)}) and the following marketing strategies:
        {plan_summary}

        Describe the key stages (e.g., Awareness, Interest/Consideration, Decision, Action) and suggest 1-2 primary activities or content types for each stage, drawing from the strategic plan.
        Provide the outline as a coherent text block (around 150-200 words).
        """
        response = self.llm_service.generate_text(prompt, max_tokens=300)
        return response.generated_text if response.success else "Could not generate lead funnel outline."

    def _generate_brand_voice_guidelines(self, intake_data: BusinessIntakeData) -> str:
        print("Generating Brand Voice Guidelines...")
        prompt = f"""Based on the profile of {intake_data.business_name} (Industry: {intake_data.industry}, Stage: {intake_data.business_stage}, Target Audience: {intake_data.target_audience_description}), recommend 3-5 core attributes for its brand voice and provide a brief messaging guideline.
        For example: "Voice: Confident, Expert, Approachable. Messaging: Focus on clarity, value, and customer success. Avoid jargon."
        Provide the guidelines as a coherent text block (around 100-150 words).
        """
        response = self.llm_service.generate_text(prompt, max_tokens=200)
        return response.generated_text if response.success else "Could not generate brand voice guidelines."

    def _generate_kpi_framework(self, strategic_plan: List[Dict[str, Any]]) -> Dict[str, str]:
        print("Generating KPI Measurement Framework...")
        all_kpis = set()
        for strategy in strategic_plan:
            if isinstance(strategy.get("kpis"), list):
                for kpi in strategy.get("kpis", []):
                    all_kpis.add(kpi)
        
        if not all_kpis:
            return {"Default KPI": "No KPIs identified from strategic plan."}

        prompt = f"""For the following Key Performance Indicators (KPIs) identified in a marketing plan: {", ".join(list(all_kpis))}.
        Suggest a primary tool or method for measuring each KPI.
        Return the response as a JSON object where keys are KPI names and values are the suggested measurement tools/methods.
        Example: {{ "Website Traffic": "Google Analytics", "Lead Conversion Rate": "CRM data and campaign tracking", "Social Media Engagement": "Platform-specific analytics (e.g., Facebook Insights, LinkedIn Analytics)" }}
        """
        response_obj = self.llm_service.generate_json_response(prompt, max_tokens=500)
        if response_obj and isinstance(response_obj, dict):
            return response_obj
        print(f"Failed to generate valid JSON for KPI framework. LLM response: {response_obj}")
        return {kpi: "Could not generate measurement method." for kpi in all_kpis}

    def _generate_initial_action_plan(self, intake_data: BusinessIntakeData, strategic_plan: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        print("Generating Initial Action Plan (30-60-90 days)...")
        actions_30_day = []
        if strategic_plan and strategic_plan[0].get("tactics"):
            actions_30_day.extend(strategic_plan[0].get("tactics", [])[:2]) 
        
        prompt = f"""Based on a strategic marketing plan (first few tactics: {", ".join(actions_30_day)}) for {intake_data.business_name}, create a high-level initial action plan for the first 30, 60, and 90 days. 
        Focus on foundational activities in the first 30 days, building momentum in 60 days, and scaling/optimizing in 90 days.
        Return the response as a JSON object with keys "30-day", "60-day", and "90-day". Each key should have a list of 2-3 action items (strings).
        Example: 
        {{
            "30-day": ["Set up Google Analytics and Search Console", "Publish 2 foundational blog posts", "Optimize Google My Business profile"],
            "60-day": ["Launch initial social media ad campaign", "Develop lead magnet (e.g., ebook)", "Begin email list building"],
            "90-day": ["Analyze campaign performance and optimize ads", "Host first webinar", "Expand content production to video"]
        }}
        """
        response_obj = self.llm_service.generate_json_response(prompt, max_tokens=700)
        if response_obj and isinstance(response_obj, dict) and "30-day" in response_obj:
            return response_obj
        print(f"Failed to generate valid JSON for action plan. LLM response: {response_obj}")
        return {
            "30-day": ["Define key marketing goals", "Setup basic analytics"],
            "60-day": ["Develop initial content pieces"],
            "90-day": ["Launch first small campaign"]
        }

    def generate_blueprint(self, intake_data: BusinessIntakeData) -> Optional[BusinessBlueprint]:
        """
        Main method to generate a full business blueprint.
        """
        print(f"BlueprintService: Starting blueprint generation for: {intake_data.business_name}")

        business_profile_analysis = self._analyze_business_profile(intake_data)
        refined_target_audience_personas = self._generate_audience_personas(intake_data)
        strategic_marketing_plan_list = self._generate_strategic_marketing_plan(intake_data, refined_target_audience_personas, business_profile_analysis)
        
        executive_summary = self._generate_executive_summary(intake_data, business_profile_analysis)
        channel_plan_dict = self._generate_channel_plan(strategic_marketing_plan_list)
        content_pillars_themes_list = self._generate_content_pillars(intake_data, refined_target_audience_personas)
        lead_generation_funnel_outline_str = self._generate_lead_funnel_outline(intake_data, strategic_marketing_plan_list)
        brand_voice_messaging_guidelines_str = self._generate_brand_voice_guidelines(intake_data)
        kpi_measurement_framework_dict = self._generate_kpi_framework(strategic_marketing_plan_list)
        initial_action_plan_dict = self._generate_initial_action_plan(intake_data, strategic_marketing_plan_list)

        # Ensure business_id is present, default if not (though it should be from intake)
        business_id = str(intake_data.raw_responses.get("business_id", uuid.uuid4()))

        blueprint = BusinessBlueprint(
            blueprint_id=str(uuid.uuid4()), # Generate a new UUID for each blueprint
            business_id=business_id, 
            executive_summary=executive_summary,
            business_profile_analysis=business_profile_analysis,
            refined_target_audience_personas=refined_target_audience_personas,
            strategic_marketing_plan=strategic_marketing_plan_list,
            channel_plan=channel_plan_dict,
            content_pillars_themes=content_pillars_themes_list,
            lead_generation_funnel_outline=lead_generation_funnel_outline_str,
            brand_voice_messaging_guidelines=brand_voice_messaging_guidelines_str,
            kpi_measurement_framework=kpi_measurement_framework_dict,
            initial_action_plan=initial_action_plan_dict
        )

        print(f"BlueprintService: Blueprint generation complete for: {intake_data.business_name}")
        return blueprint

    def save_blueprint(self, blueprint: BusinessBlueprint) -> Optional[str]:
        """Saves the generated blueprint to the database."""
        conn = self._get_db_connection()
        if not conn:
            print("BlueprintService Error: Cannot save blueprint, no database connection.")
            return None
        
        insert_query = f"""INSERT INTO {self.DB_TABLE_NAME} (
            blueprint_id, business_id, executive_summary, business_profile_analysis, 
            refined_target_audience_personas, strategic_marketing_plan, channel_plan, 
            content_pillars_themes, lead_generation_funnel_outline, 
            brand_voice_messaging_guidelines, kpi_measurement_framework, initial_action_plan, version
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (blueprint_id) DO UPDATE SET
            business_id = EXCLUDED.business_id,
            executive_summary = EXCLUDED.executive_summary,
            business_profile_analysis = EXCLUDED.business_profile_analysis,
            refined_target_audience_personas = EXCLUDED.refined_target_audience_personas,
            strategic_marketing_plan = EXCLUDED.strategic_marketing_plan,
            channel_plan = EXCLUDED.channel_plan,
            content_pillars_themes = EXCLUDED.content_pillars_themes,
            lead_generation_funnel_outline = EXCLUDED.lead_generation_funnel_outline,
            brand_voice_messaging_guidelines = EXCLUDED.brand_voice_messaging_guidelines,
            kpi_measurement_framework = EXCLUDED.kpi_measurement_framework,
            initial_action_plan = EXCLUDED.initial_action_plan,
            version = {self.DB_TABLE_NAME}.version + 1,
            updated_at = CURRENT_TIMESTAMP;
        """
        try:
            with conn.cursor() as cur:
                cur.execute(insert_query, (
                    blueprint.blueprint_id,
                    blueprint.business_id,
                    blueprint.executive_summary,
                    blueprint.business_profile_analysis,
                    extras.Json(blueprint.refined_target_audience_personas),
                    extras.Json(blueprint.strategic_marketing_plan),
                    extras.Json(blueprint.channel_plan),
                    extras.Json(blueprint.content_pillars_themes),
                    blueprint.lead_generation_funnel_outline,
                    blueprint.brand_voice_messaging_guidelines,
                    extras.Json(blueprint.kpi_measurement_framework),
                    extras.Json(blueprint.initial_action_plan),
                    blueprint.version
                ))
                conn.commit()
                print(f"BlueprintService: Blueprint {blueprint.blueprint_id} for business {blueprint.business_id} saved successfully.")
                return blueprint.blueprint_id
        except psycopg2.Error as e:
            print(f"BlueprintService Error: Database error while saving blueprint {blueprint.blueprint_id}: {e}")
            conn.rollback()
            return None
        except Exception as e:
            print(f"BlueprintService Error: Unexpected error while saving blueprint {blueprint.blueprint_id}: {e}")
            conn.rollback()
            return None
        finally:
            self._put_db_connection(conn)

    def get_blueprint_by_id(self, blueprint_id: str) -> Optional[BusinessBlueprint]:
        """Retrieves a blueprint by its ID."""
        conn = self._get_db_connection()
        if not conn:
            return None
        
        query = f"SELECT * FROM {self.DB_TABLE_NAME} WHERE blueprint_id = %s;"
        try:
            with conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(query, (blueprint_id,))
                row = cur.fetchone()
                if row:
                    return BusinessBlueprint(**row)
                return None
        except psycopg2.Error as e:
            print(f"BlueprintService Error: Database error retrieving blueprint {blueprint_id}: {e}")
            return None
        finally:
            self._put_db_connection(conn)

    def get_blueprints_by_business_id(self, business_id: str, latest_only: bool = False) -> List[BusinessBlueprint]:
        """Retrieves all blueprints for a given business_id, optionally only the latest version."""
        conn = self._get_db_connection()
        if not conn:
            return []
        
        blueprints = []
        query = f"SELECT * FROM {self.DB_TABLE_NAME} WHERE business_id = %s ORDER BY version DESC, created_at DESC;"
        if latest_only:
            query = f"SELECT * FROM {self.DB_TABLE_NAME} WHERE business_id = %s ORDER BY version DESC, created_at DESC LIMIT 1;"
            
        try:
            with conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(query, (business_id,))
                rows = cur.fetchall()
                for row in rows:
                    blueprints.append(BusinessBlueprint(**row))
            return blueprints
        except psycopg2.Error as e:
            print(f"BlueprintService Error: Database error retrieving blueprints for business {business_id}: {e}")
            return []
        finally:
            self._put_db_connection(conn)

    def delete_blueprint(self, blueprint_id: str) -> bool:
        """Deletes a blueprint by its ID."""
        conn = self._get_db_connection()
        if not conn:
            return False
        
        query = f"DELETE FROM {self.DB_TABLE_NAME} WHERE blueprint_id = %s;"
        try:
            with conn.cursor() as cur:
                cur.execute(query, (blueprint_id,))
                conn.commit()
                return cur.rowcount > 0 # True if a row was deleted
        except psycopg2.Error as e:
            print(f"BlueprintService Error: Database error deleting blueprint {blueprint_id}: {e}")
            conn.rollback()
            return False
        finally:
            self._put_db_connection(conn)

# Example usage (for testing purposes)
if __name__ == "__main__":
    sample_raw_data = {
        "business_id": "biz_main_789", # Ensure this business_id is unique for testing
        "business_name": "Artisan Bakery Cafe Deluxe",
        "industry": "Food & Beverage",
        "business_stage": "Established",
        "goals": ["Increase foot traffic by 25%", "Launch catering service"],
        "target_audience_description": "Local residents, families, and young professionals aged 25-55 who appreciate high-quality baked goods, coffee, and a cozy atmosphere. They are active on Instagram and Facebook, and look for local recommendations.",
        "products_services_description": "We offer freshly baked bread, pastries, cakes, specialty coffee, and light lunch options. We use locally sourced ingredients and offer gluten-free options.",
        "current_marketing_efforts": "Local flyers, active Instagram posts, monthly newsletter.",
        "competitors": "Starbucks, Panera Bread, a few other local cafes, online cake shops."
    }
    sample_intake = BusinessIntakeData(
        business_name=sample_raw_data["business_name"],
        industry=sample_raw_data["industry"],
        business_stage=sample_raw_data["business_stage"],
        goals=sample_raw_data["goals"],
        target_audience_description=sample_raw_data["target_audience_description"],
        products_services_description=sample_raw_data["products_services_description"],
        raw_responses=sample_raw_data
    )

    print("Initializing services for BlueprintService DB example...")
    if not os.getenv("OPENAI_API_KEY"):
        print("\n** WARNING: OPENAI_API_KEY environment variable is not set. LLM calls will be simulated or fail. **\n")
    if not os.getenv("DB_HOST"):
        print("\n** WARNING: DB_HOST (and other DB_ vars) not set. DB operations will fail. **\n")
        print("Please set DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME environment variables.")
        exit()

    llm_service_instance = LLMService(model_name="gpt-3.5-turbo")
    blueprint_service_instance = BlueprintService(llm_service=llm_service_instance)

    if not blueprint_service_instance.db_connection_pool:
        print("Failed to initialize DB connection pool for BlueprintService. Exiting example.")
        exit()

    print(f"\n--- Generating Blueprint for: {sample_intake.business_name} ---")
    generated_blueprint_obj = blueprint_service_instance.generate_blueprint(sample_intake)

    if generated_blueprint_obj:
        print("\n--- Saving Generated Blueprint to Database ---")
        saved_blueprint_id = blueprint_service_instance.save_blueprint(generated_blueprint_obj)

        if saved_blueprint_id:
            print(f"Blueprint saved with ID: {saved_blueprint_id}")

            print("\n--- Retrieving Blueprint by ID from Database ---")
            retrieved_bp = blueprint_service_instance.get_blueprint_by_id(saved_blueprint_id)
            if retrieved_bp:
                print(f"Retrieved blueprint for business: {retrieved_bp.business_name} (ID: {retrieved_bp.blueprint_id})")
                # print(retrieved_bp.model_dump_json(indent=2))
            else:
                print(f"Could not retrieve blueprint with ID: {saved_blueprint_id}")

            print("\n--- Retrieving Blueprints by Business ID from Database ---")
            business_blueprints = blueprint_service_instance.get_blueprints_by_business_id(generated_blueprint_obj.business_id)
            print(f"Found {len(business_blueprints)} blueprints for business ID {generated_blueprint_obj.business_id}")
            for bp in business_blueprints:
                print(f"  - Blueprint ID: {bp.blueprint_id}, Version: {bp.version}, Created: {bp.created_at}")
            
            # print("\n--- Deleting Blueprint from Database ---")
            # if blueprint_service_instance.delete_blueprint(saved_blueprint_id):
            #     print(f"Blueprint {saved_blueprint_id} deleted successfully.")
            # else:
            #     print(f"Failed to delete blueprint {saved_blueprint_id}.")
        else:
            print("Failed to save the generated blueprint.")
    else:
        print("Blueprint generation failed.")

    blueprint_service_instance.close_db_pool()
    print("\n--- End of BlueprintService DB Example ---")

