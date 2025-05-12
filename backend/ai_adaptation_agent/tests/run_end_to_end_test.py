# End-to-End Test Script for CustomerMatcherService with Database Integration

import os
import sys
import psycopg2
from psycopg2 import extras

# Add the src directory to the Python path to allow imports from sibling directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.shared.data_models import CustomerQuery
from src.shared.llm_service import LLMService
from src.customer_matcher.customer_matcher_service import CustomerMatcherService

# Database connection parameters from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DB_TABLE_NAME = CustomerMatcherService.DB_TABLE_NAME

# Sample business data for testing (same as in unittest, for standalone demo)
SAMPLE_BUSINESSES_FOR_DEMO = [
    {
        "business_id": "demo_biz_001",
        "business_name": "Demo Plumbing Heroes",
        "industry": "Home Services",
        "business_stage": "Established",
        "goals": ["Increase local calls", "Emergency service leader"],
        "target_audience_description": "Homeowners in DemoCity needing urgent plumbing.",
        "products_services_description": "24/7 emergency plumbing, leak detection, drain cleaning, pipe repair, water heaters.",
        "location": "DemoCity",
        "service_tags": ["plumbing", "emergency", "leak repair", "drain cleaning", "water heater"],
        "raw_data_json": {"rating": 4.8, "years_in_service": 12, "offers_free_estimates": True}
    },
    {
        "business_id": "demo_biz_002",
        "business_name": "Demo GreenScape Designs",
        "industry": "Landscaping Services",
        "business_stage": "Growth",
        "goals": ["Attract premium clients", "Showcase design portfolio"],
        "target_audience_description": "Residents seeking high-end garden design and maintenance in DemoSuburb.",
        "products_services_description": "Custom garden design, landscape architecture, lawn care, tree services, irrigation systems.",
        "location": "DemoSuburb",
        "service_tags": ["garden design", "landscaping", "lawn care", "tree surgery", "irrigation"],
        "raw_data_json": {"eco_friendly_certified": True, "award_winner_2023": True}
    }
]

def setup_demo_data(conn):
    """Inserts demo data if the table is empty or demo data doesn't exist."""
    try:
        with conn.cursor() as cur:
            print(f"Checking for existing demo data in 
{DB_TABLE_NAME}
...")
            cur.execute(f"SELECT business_id FROM {DB_TABLE_NAME} WHERE business_id LIKE 'demo_biz_%';")
            existing_demo_ids = {row[0] for row in cur.fetchall()}

            inserted_count = 0
            for biz in SAMPLE_BUSINESSES_FOR_DEMO:
                if biz["business_id"] not in existing_demo_ids:
                    insert_query = f"""INSERT INTO {DB_TABLE_NAME} 
                                     (business_id, business_name, industry, business_stage, goals, 
                                      target_audience_description, products_services_description, 
                                      location, service_tags, raw_data_json) 
                                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
                    cur.execute(insert_query, (
                        biz["business_id"], biz["business_name"], biz["industry"], biz["business_stage"],
                        list(biz["goals"]), biz["target_audience_description"], biz["products_services_description"],
                        biz["location"], list(biz["service_tags"]), extras.Json(biz["raw_data_json"])
                    ))
                    inserted_count += 1
            if inserted_count > 0:
                print(f"{inserted_count} demo businesses inserted.")
            else:
                print("Demo data already seems to be present or no new demo data to insert.")
            conn.commit() # Commit after all insertions
    except psycopg2.Error as e:
        print(f"Error during demo data setup: {e}")
        conn.rollback() # Rollback on error
    except Exception as e:
        print(f"An unexpected error occurred during demo data setup: {e}")
        conn.rollback()

def run_end_to_end_customer_matching():
    """Demonstrates the end-to-end customer matching process."""
    print("--- Starting End-to-End CustomerMatcherService Demonstration ---")

    # Check for necessary DB environment variables
    if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
        print("\nERROR: Database environment variables (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME) are not set.")
        print("Please set them before running this script.")
        print("Example: export DB_HOST=localhost DB_USER=youruser DB_PASSWORD=yourpass DB_NAME=yourdb")
        return

    # Initialize LLMService (will use OpenAI API key if set)
    print("\nInitializing LLMService...")
    llm_service = LLMService(model_name="gpt-3.5-turbo") # Or your preferred model
    if not os.getenv("OPENAI_API_KEY"):
        print("** INFO: OPENAI_API_KEY environment variable is not set. **")
        print("** LLM-based query understanding and semantic matching will be skipped or use basic logic. **")
    else:
        print("OPENAI_API_KEY found. LLM features will be attempted.")

    # Initialize CustomerMatcherService
    # It will use environment variables for its DB connection pool
    print("\nInitializing CustomerMatcherService...")
    matcher_service = CustomerMatcherService(llm_service=llm_service)

    if not matcher_service.db_connection_pool:
        print("\nERROR: CustomerMatcherService failed to initialize its database connection pool.")
        print("Please check your database server, network, and environment variable settings.")
        print(f"Expected table: 
{DB_TABLE_NAME}
 in database 
{DB_NAME}
 on 
{DB_HOST}
:
{DB_PORT}
")
        return

    # Setup demo data (connect directly for this setup part)
    db_conn_for_setup = None
    try:
        db_conn_for_setup = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME)
        setup_demo_data(db_conn_for_setup)
    except psycopg2.Error as e:
        print(f"\nERROR: Could not connect to database for demo data setup: {e}")
        if db_conn_for_setup: db_conn_for_setup.close()
        matcher_service.close_db_pool()
        return
    finally:
        if db_conn_for_setup: db_conn_for_setup.close()

    # --- Define Sample Customer Queries ---
    sample_queries = [
        CustomerQuery(query_text="I need an emergency plumber for a burst pipe in DemoCity", service_category="Home Services", keywords=["plumbing", "emergency", "burst pipe"], location="DemoCity"),
        CustomerQuery(query_text="Looking for someone to design my garden in DemoSuburb, I want something modern and eco-friendly.", keywords=["garden design", "landscaping", "eco-friendly"], location="DemoSuburb"),
        CustomerQuery(query_text="Find a good coffee shop near downtown that serves breakfast.", keywords=["coffee shop", "breakfast"], location="Downtown") # Might not match demo data
    ]

    print("\n--- Processing Customer Queries ---")
    for i, customer_query in enumerate(sample_queries):
        print(f"\n--- Query {i+1} ---")
        print(f"  Text: 
{customer_query.query_text}
")
        print(f"  Category: {customer_query.service_category}")
        print(f"  Keywords: {customer_query.keywords}")
        print(f"  Location: {customer_query.location}")
        
        try:
            print("\n  Matching businesses...")
            matched_businesses = matcher_service.find_matched_businesses(customer_query)
            
            if matched_businesses:
                print(f"\n  Found {len(matched_businesses)} matched business(es):")
                for match_idx, match in enumerate(matched_businesses):
                    print(f"    --- Match {match_idx + 1} ---")
                    print(f"      Business Name: {match.business_name} (ID: {match.business_id})")
                    print(f"      Tagline: {match.tagline}")
                    print(f"      Location: {match.location}")
                    print(f"      Relevant Services: {match.relevant_services}")
                    print(f"      Relevance Score: {match.relevance_score:.3f}")
                    print(f"      Match Reason: {match.match_reason}")
            else:
                print("\n  No businesses found matching this query with the current data and algorithm.")
        
        except Exception as e:
            print(f"\n  --- An error occurred during matching for Query {i+1} --- ")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc() # Print full traceback for debugging

    # Clean up: Close the service's database connection pool
    print("\n--- End-to-End Demonstration Complete ---")
    matcher_service.close_db_pool()

if __name__ == "__main__":
    run_end_to_end_customer_matching()

