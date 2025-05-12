# Test script for the CustomerMatcherService with Database Integration

import os
import sys
import unittest
import psycopg2
from psycopg2 import extras

# Add the src directory to the Python path to allow imports from sibling directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.shared.data_models import CustomerQuery, BusinessIntakeData # MatchedBusiness is also used by service
from src.shared.llm_service import LLMService
from src.customer_matcher.customer_matcher_service import CustomerMatcherService

# Database connection parameters from environment variables
# These are needed for the test script to manage test data directly.
# The CustomerMatcherService itself also uses these (or a passed config) for its pool.
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Table name from the service
DB_TABLE_NAME = CustomerMatcherService.DB_TABLE_NAME

# Sample business data for testing
# Note: The service expects business_id, location, service_tags to be in raw_responses 
# when creating BusinessIntakeData from DB. The DB schema has these as direct columns.
# The _retrieve_candidate_businesses method maps these correctly.
SAMPLE_BUSINESSES = [
    {
        "business_id": "test_biz_001",
        "business_name": "Test Plumbing Experts",
        "industry": "Home Services",
        "business_stage": "Established",
        "goals": ["Increase local calls", "Emergency service leader"],
        "target_audience_description": "Homeowners in TestCity needing urgent plumbing.",
        "products_services_description": "24/7 emergency plumbing, leak detection, drain cleaning, pipe repair.",
        "location": "TestCity",
        "service_tags": ["plumbing", "emergency", "leak repair", "drain cleaning"],
        "raw_data_json": {"rating": 4.5, "years_in_service": 10}
    },
    {
        "business_id": "test_biz_002",
        "business_name": "Green Test Gardens",
        "industry": "Landscaping Services",
        "business_stage": "Growth",
        "goals": ["Attract premium clients", "Showcase design portfolio"],
        "target_audience_description": "Residents seeking high-end garden design and maintenance.",
        "products_services_description": "Custom garden design, landscape architecture, lawn care, tree services.",
        "location": "TestSuburb",
        "service_tags": ["garden design", "landscaping", "lawn care", "tree surgery"],
        "raw_data_json": {"eco_friendly_certified": True}
    },
    {
        "business_id": "test_biz_003",
        "business_name": "Test Secure Finance",
        "industry": "Financial Services",
        "business_stage": "Established",
        "goals": ["Expand insurance products"],
        "target_audience_description": "Individuals and families looking for insurance.",
        "products_services_description": "Home insurance, auto insurance, life insurance, investment advice.",
        "location": "TestCity",
        "service_tags": ["insurance", "home insurance", "auto insurance", "financial planning"],
        "raw_data_json": {"branch_count": 3}
    }
]

class TestCustomerMatcherServiceDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up for all tests in this class."""
        if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
            raise unittest.SkipTest("Database environment variables (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME) not set. Skipping DB integration tests.")
        
        cls.conn = None
        try:
            cls.conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME)
            cls.conn.autocommit = True # Easier for test setup/teardown
            with cls.conn.cursor() as cur:
                # Ensure table exists (schema.sql should be applied beforehand)
                cur.execute(f"SELECT to_regclass(\'{DB_TABLE_NAME}\');")
                if cur.fetchone()[0] is None:
                    raise unittest.SkipTest(f"Database table 
{DB_TABLE_NAME}
 does not exist. Apply schema.sql first. Skipping DB tests.")

                # Insert sample data
                print(f"\nSetting up test data in 
{DB_TABLE_NAME}
...")
                for biz in SAMPLE_BUSINESSES:
                    # Ensure goals and service_tags are lists, raw_data_json is a dict (for psycopg2.extras.Json)
                    insert_query = f"""INSERT INTO {DB_TABLE_NAME} 
                                     (business_id, business_name, industry, business_stage, goals, 
                                      target_audience_description, products_services_description, 
                                      location, service_tags, raw_data_json) 
                                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (business_id) DO NOTHING;"""
                    cur.execute(insert_query, (
                        biz["business_id"], biz["business_name"], biz["industry"], biz["business_stage"],
                        list(biz["goals"]), biz["target_audience_description"], biz["products_services_description"],
                        biz["location"], list(biz["service_tags"]), extras.Json(biz["raw_data_json"])
                    ))
                print(f"{len(SAMPLE_BUSINESSES)} sample businesses inserted/ensured.")

        except psycopg2.Error as e:
            if cls.conn: cls.conn.close()
            raise unittest.SkipTest(f"Database connection or setup failed: {e}. Skipping DB integration tests.")
        except Exception as e:
             if cls.conn: cls.conn.close()
             raise unittest.SkipTest(f"An unexpected error occurred during setUpClass: {e}. Skipping DB tests.")

    @classmethod
    def tearDownClass(cls):
        """Tear down after all tests in this class."""
        if hasattr(cls, "conn") and cls.conn:
            try:
                with cls.conn.cursor() as cur:
                    print(f"\nCleaning up test data from 
{DB_TABLE_NAME}
...")
                    for biz in SAMPLE_BUSINESSES:
                        cur.execute(f"DELETE FROM {DB_TABLE_NAME} WHERE business_id = %s;", (biz["business_id"],))
                    print("Test data cleaned up.")
            except psycopg2.Error as e:
                print(f"Error during test data cleanup: {e}")
            finally:
                cls.conn.close()
                print("Test database connection closed.")

    def setUp(self):
        """Set up for each test method."""
        self.llm_service = LLMService(model_name="gpt-3.5-turbo") # Mocked or real based on OPENAI_API_KEY
        # The service will use its own pool based on env vars or passed config
        self.matcher_service = CustomerMatcherService(llm_service=self.llm_service)
        if not self.matcher_service.db_connection_pool:
             self.skipTest("CustomerMatcherService failed to initialize its DB connection pool. Check service logs and DB env vars.")

    def tearDown(self):
        """Tear down after each test method."""
        if self.matcher_service:
            self.matcher_service.close_db_pool()

    def test_plumbing_query_exact_match(self):
        """Test a query that should find an exact plumbing match."""
        query = CustomerQuery(query_text="emergency plumbing in TestCity", service_category="Home Services", keywords=["plumbing", "emergency"], location="TestCity")
        matches = self.matcher_service.find_matched_businesses(query)
        self.assertGreater(len(matches), 0, "Should find at least one plumbing match")
        self.assertEqual(matches[0].business_id, "test_biz_001")
        self.assertIn("plumbing", matches[0].relevant_services)
        self.assertIn("TestCity", matches[0].location)

    def test_landscaping_query(self):
        """Test a query for landscaping services."""
        query = CustomerQuery(query_text="garden design TestSuburb", keywords=["garden design", "landscaping"], location="TestSuburb")
        matches = self.matcher_service.find_matched_businesses(query)
        self.assertGreater(len(matches), 0, "Should find at least one landscaping match")
        self.assertEqual(matches[0].business_id, "test_biz_002")
        self.assertIn("garden design", matches[0].relevant_services)

    def test_financial_query_broad_location_ignored(self):
        """Test a financial services query without specific location, should still match based on keywords."""
        query = CustomerQuery(service_category="Financial Services", keywords=["home insurance", "investment"], location=None)
        matches = self.matcher_service.find_matched_businesses(query)
        self.assertGreater(len(matches), 0, "Should find financial services match")
        self.assertEqual(matches[0].business_id, "test_biz_003")

    def test_no_match_query(self):
        """Test a query that should not find any matches."""
        query = CustomerQuery(query_text="alien pet grooming services in Mars", keywords=["alien", "pets", "grooming"], location="Mars")
        matches = self.matcher_service.find_matched_businesses(query)
        self.assertEqual(len(matches), 0, "Should find no matches for an obscure query")

    def test_keyword_in_description(self):
        """Test matching based on a keyword in the products_services_description."""
        query = CustomerQuery(keywords=["pipe repair"], location="TestCity")
        matches = self.matcher_service.find_matched_businesses(query)
        self.assertTrue(any(m.business_id == "test_biz_001" for m in matches), "Should find Test Plumbing Experts by description keyword")

    def test_service_tag_match(self):
        """Test matching based on a service tag."""
        query = CustomerQuery(keywords=["lawn care"], location="TestSuburb")
        matches = self.matcher_service.find_matched_businesses(query)
        self.assertTrue(any(m.business_id == "test_biz_002" for m in matches), "Should find Green Test Gardens by service tag")

if __name__ == "__main__":
    print("--- Running CustomerMatcherService Database Integration Tests ---")
    print("This test requires a running PostgreSQL database configured with environment variables:")
    print("DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME")
    print(f"It also expects the table 
{DB_TABLE_NAME}
 to exist (apply schema.sql from ai-marketing-system-new/database/)")
    print("The test will attempt to insert and delete its own sample data.")
    
    # Check for OPENAI_API_KEY for LLMService info, though not critical for these DB tests
    if not os.getenv("OPENAI_API_KEY"):
        print("\n** INFO: OPENAI_API_KEY environment variable is not set. **")
        print("** LLMService calls (if any were active in CustomerMatcherService) would be simulated or error out. **")
    else:
        print("\nOPENAI_API_KEY found. LLMService could make live calls if used by CustomerMatcherService.")
    
    unittest.main()

