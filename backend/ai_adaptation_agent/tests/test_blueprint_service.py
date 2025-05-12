# Test script for the BlueprintService

import os
import sys

# Add the src directory to the Python path to allow imports from sibling directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.shared.data_models import BusinessIntakeData
from src.shared.llm_service import LLMService
from src.blueprint_generator.blueprint_service import BlueprintService

def run_blueprint_service_test():
    """Tests the BlueprintService functionality."""
    print("--- Starting BlueprintService Test ---")

    # 1. Prepare sample BusinessIntakeData
    sample_raw_data = {
        "business_id": "test_biz_001",
        "business_name": "Artisan Coffee Roasters",
        "industry": "Food & Beverage",
        "business_stage": "Startup",
        "goals": ["Build brand awareness", "Attract local customers"],
        "target_audience_description": "Coffee enthusiasts aged 25-55, living locally, appreciate quality and ethical sourcing.",
        "products_services_description": "Specialty roasted coffee beans, brewed coffee, pastries. Focus on unique single-origin beans.",
        "current_marketing_efforts": "None, just opened.",
        "brand_identity_voice": "Artisanal, friendly, knowledgeable, passionate."
        # ... add more fields as per BusinessIntakeData model if needed for deeper testing
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
    print(f"Sample Intake Data Prepared for: {sample_intake.business_name}")

    # 2. Initialize LLMService
    # The LLMService will attempt to use OPENAI_API_KEY from environment variables
    # If not set, it will print a warning and simulated/error responses will occur.
    print("\nInitializing LLMService...")
    llm_service = LLMService(model_name="gpt-3.5-turbo") # Using a common, cost-effective model for testing
    if not os.getenv("OPENAI_API_KEY"):
        print("** WARNING: OPENAI_API_KEY environment variable is not set. **")
        print("** LLM calls will be simulated or will return an error from the LLMService. **")
        print("** To run with live OpenAI API, set the OPENAI_API_KEY environment variable. **")
    else:
        print("OPENAI_API_KEY found. Attempting live LLM calls.")

    # 3. Initialize BlueprintService
    print("\nInitializing BlueprintService...")
    blueprint_service = BlueprintService(llm_service=llm_service)

    # 4. Call generate_blueprint method
    print("\nCalling generate_blueprint...")
    try:
        generated_blueprint = blueprint_service.generate_blueprint(sample_intake)

        # 5. Print results
        print("\n--- Generated Blueprint Results ---")
        if generated_blueprint:
            print(f"Business ID: {generated_blueprint.business_id}")
            print(f"Executive Summary (first 100 chars): {generated_blueprint.executive_summary[:100]}...")
            
            print("\nAudience Personas (first persona if exists):")
            if generated_blueprint.refined_target_audience_personas:
                print(generated_blueprint.refined_target_audience_personas[0])
            else:
                print("No personas generated (or parsing failed in placeholder).")

            print("\nLLM Interaction Details (from Business Profile Analysis metadata, if available from LLMService):")
            # The blueprint_service.py currently puts the LLM response text directly into business_profile_analysis
            # To get metadata, we would need to adjust blueprint_service to store/return the LLMResponse object
            # For now, we check if the LLMService itself indicated simulation/error during its calls
            # This requires inspecting the LLMResponse object that would have been returned by llm_service.generate_text
            # The current BlueprintService doesn't directly expose this, so we rely on LLMService's own print statements for now.
            # A more robust test would mock LLMService or capture its output.
            print("(Refer to LLMService print statements during execution for live/simulated status)")
            
            print("\nFull Blueprint (JSON representation - snippet):")
            # Using model_dump_json for Pydantic models
            blueprint_json_snippet = generated_blueprint.model_dump_json(indent=2)[:1000]
            print(blueprint_json_snippet + "...")

        else:
            print("Blueprint generation failed or returned None.")
            
    except Exception as e:
        print(f"\n--- An error occurred during blueprint generation test --- ")
        print(f"Error: {e}")

    print("\n--- BlueprintService Test Complete ---")

if __name__ == "__main__":
    run_blueprint_service_test()

