# CustomerMatcherService: Database Integration Guide

This document outlines the database integration for the `CustomerMatcherService` within the AI Marketing System. It details the database schema, setup instructions, required environment variables, dependencies, and how the service interacts with the PostgreSQL database.

## 1. Overview

The `CustomerMatcherService` has been enhanced to retrieve business profiles from a PostgreSQL database instead of using placeholder data. This allows for a more scalable and dynamic system where business information can be managed and updated centrally.

The integration involves:
- A defined database schema for storing business profiles.
- Modifications to the `CustomerMatcherService` to connect to the database using a connection pool.
- SQL queries within the service to retrieve and filter business data.
- Updated test scripts to verify database interaction.

## 2. Database Schema (`business_profiles` table)

The core of the database integration is the `business_profiles` table. The SQL schema for this table is defined in `/home/ubuntu/ai-marketing-system-new/database/schema.sql`.

Key columns include:
- `business_id` (TEXT, PRIMARY KEY): Unique identifier for the business.
- `business_name` (TEXT, NOT NULL): Official name of the business.
- `industry` (TEXT): Primary industry.
- `business_stage` (TEXT): Current stage of the business.
- `goals` (TEXT[]): Array of business goals.
- `target_audience_description` (TEXT): Description of the target audience.
- `products_services_description` (TEXT): Description of products/services.
- `location` (TEXT): Primary operational location.
- `service_tags` (TEXT[]): Array of keywords/tags for specific services.
- `raw_data_json` (JSONB): For storing other miscellaneous structured data (e.g., ratings, certifications).
- `created_at` (TIMESTAMP WITH TIME ZONE): Timestamp of creation.
- `updated_at` (TIMESTAMP WITH TIME ZONE): Timestamp of last update (auto-updated via a trigger).

### Indexes
Appropriate GIN indexes are defined in `schema.sql` on text fields (`business_name`, `industry`, `products_services_description`, `location`) and array fields (`service_tags`, `goals`) to optimize search performance, particularly for `ILIKE` queries and array containment checks. The `pg_trgm` extension is recommended for optimal performance with GIN trigram indexes; if unavailable, alternative indexing strategies are commented in the schema file.

## 3. Setup Instructions

### 3.1. Prerequisites
- PostgreSQL server installed and running.
- Python 3.8+ environment.
- `psycopg2-binary` Python package installed: `pip install psycopg2-binary`
- (Optional but Recommended for LLM features) OpenAI API key.

### 3.2. Database Creation
1.  Create a PostgreSQL database if one doesn't already exist for this application.
    ```sql
    CREATE DATABASE ai_marketing_db;
    ```
2.  Connect to your PostgreSQL instance using a tool like `psql` or a GUI client.

### 3.3. Apply Schema
1.  Navigate to the `/home/ubuntu/ai-marketing-system-new/database/` directory in your project.
2.  Execute the `schema.sql` script against your database. For example, using `psql`:
    ```bash
    psql -U your_postgres_user -d your_database_name -a -f schema.sql
    ```
    This will create the `business_profiles` table, its indexes, and the `updated_at` trigger.
3.  (Optional, for GIN trigram indexes) Enable the `pg_trgm` extension if you intend to use `gin_trgm_ops` for better text searching performance:
    ```sql
    CREATE EXTENSION IF NOT EXISTS pg_trgm;
    ```
    Execute this command connected to your specific database as a superuser or a user with sufficient privileges.

### 3.4. Environment Variables

The `CustomerMatcherService` (and its test script) relies on environment variables for database connection details. Ensure these are set in your execution environment:

-   `DB_HOST`: Hostname or IP address of your PostgreSQL server (e.g., `localhost`).
-   `DB_PORT`: Port number for PostgreSQL (default: `5432`).
-   `DB_USER`: PostgreSQL username.
-   `DB_PASSWORD`: Password for the PostgreSQL user.
-   `DB_NAME`: Name of the database to connect to (e.g., `ai_marketing_db`).

For LLM features (query understanding, semantic similarity):
-   `OPENAI_API_KEY`: Your OpenAI API key.

### 3.5. Populating with Data (Optional for Initial Setup)
For testing or initial use, you might want to populate the `business_profiles` table with some data. You can do this via SQL `INSERT` statements or by using a data seeding script if you develop one.
The test script `test_customer_matcher_service.py` includes logic to insert sample data for its own execution and cleans it up afterwards.

## 4. Service Interaction with Database

The `CustomerMatcherService` (`customer_matcher_service.py`) has been updated as follows:

-   **Initialization (`__init__`)**: 
    -   Accepts an optional `db_config` dictionary or falls back to environment variables for database connection parameters.
    -   Initializes a `psycopg2.pool.SimpleConnectionPool` for managing database connections efficiently.
    -   Includes error handling for connection pool creation.
-   **Connection Management**: 
    -   `_get_db_connection()`: Retrieves a connection from the pool.
    -   `_put_db_connection()`: Returns a connection to the pool.
    -   `close_db_pool()`: Closes all connections in the pool (should be called on service shutdown).
-   **Data Retrieval (`_retrieve_candidate_businesses`)**: 
    -   This method now constructs and executes SQL queries against the `business_profiles` table.
    -   It uses parameterized queries to prevent SQL injection vulnerabilities.
    -   It filters businesses based on keywords (searching `business_name`, `products_services_description`, `industry`, and `service_tags`) and `location`.
    -   The results are mapped from database rows to `BusinessIntakeData` objects.
-   **Main Logic (`find_matched_businesses`)**: 
    -   Calls `_retrieve_candidate_businesses` to get data from the database.
    -   The subsequent ranking and relevance calculation (`_calculate_relevance`) operate on these database-fetched profiles.
-   **LLM Integration**: 
    -   The `_preprocess_query` and `_calculate_relevance` methods now have more concrete (though still conditional on API key availability) integrations for using the `LLMService` for query understanding and semantic similarity scoring, respectively. These parts will activate if an `OPENAI_API_KEY` is provided.

## 5. Running Tests with Database Integration

The test script `/home/ubuntu/ai-marketing-system-new/backend/ai_adaptation_agent/tests/test_customer_matcher_service.py` has been updated to test the database integration.

### 5.1. Test Setup
-   The test script uses `unittest`.
-   `setUpClass` method:
    -   Connects to the test database using the environment variables.
    -   Checks if the `business_profiles` table exists.
    -   Inserts a predefined set of `SAMPLE_BUSINESSES` into the table before tests run. It uses `ON CONFLICT (business_id) DO NOTHING` to avoid errors if data already exists from a previous failed run.
-   `tearDownClass` method:
    -   Deletes the `SAMPLE_BUSINESSES` from the table to clean up.
    -   Closes the test database connection.
-   `setUp` method (for each test):
    -   Initializes `LLMService` and `CustomerMatcherService`.
    -   Skips the test if the `CustomerMatcherService` fails to initialize its DB pool.
-   `tearDown` method (for each test):
    -   Closes the `CustomerMatcherService`'s DB pool.

### 5.2. Executing Tests
1.  Ensure your PostgreSQL server is running and accessible.
2.  Ensure the database and `business_profiles` table exist (apply `schema.sql`).
3.  Set the required environment variables (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`).
4.  Navigate to the `/home/ubuntu/ai-marketing-system-new/backend/ai_adaptation_agent/tests/` directory.
5.  Run the test script:
    ```bash
    python3 test_customer_matcher_service.py
    ```
The tests will execute, interacting with the live database for fetching and matching business profiles.

## 6. Dependencies
-   `psycopg2-binary`: For PostgreSQL database interaction in Python.
-   `openai`: (Optional) For LLM-based features if an API key is provided.

This guide should provide a comprehensive overview of the database integration within the `CustomerMatcherService`. Further refinements and optimizations can be made as the system evolves and real-world usage patterns emerge.

