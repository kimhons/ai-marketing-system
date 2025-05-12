# AI Adaptation Agent: Data Processing Pipeline Design

## 1. Introduction

This document outlines the data processing pipeline for the AI Adaptation Agent, supporting its dual roles as defined in `ai_adaptation_agent_requirements.md`:

1.  **Business Blueprint Generation:** Processing detailed business intake data to create comprehensive marketing blueprints.
2.  **Customer-to-Business Matching:** Processing customer queries to connect them with relevant businesses.

The design emphasizes modularity, scalability, and distinct data flows for each role, while leveraging shared data stores and services where appropriate.

## 2. Overall Pipeline Architecture

The AI Adaptation Agent will operate with two primary, largely independent data processing pipelines that may share underlying services like LLM integration and database access.

*   **Blueprint Generation Pipeline:** An asynchronous, in-depth analysis pipeline triggered by the submission or update of a Business Intake Form.
*   **Customer Matching Pipeline:** A synchronous, real-time pipeline triggered by a customer query via a dedicated user interface.

## 3. Pipeline for Business Blueprint Generation

This pipeline transforms raw business intake data into an actionable Business Blueprint.

**Trigger:** Submission or significant update of a Business Intake Form.
**Processing Mode:** Primarily asynchronous due to the potential for complex analysis and LLM interactions.

**Stages:**

1.  **Data Ingestion & Validation (Asynchronous Task Triggered):
    *   **Input:** Business Intake Form data (JSON/object) from the `intake_api` (presumably after it's saved to the PostgreSQL `business_intakes` table).
    *   **Action:** Retrieve the full intake record from PostgreSQL.
    *   **Validation:** Perform thorough data validation against defined schemas and business rules (e.g., completeness of critical sections, data type checks).
    *   **Error Handling:** Log validation errors. If critical data is missing/invalid, flag the record for review or notify the business user (mechanism TBD).
    *   **Output:** Validated and cleaned business intake data object.

2.  **Data Preprocessing & Feature Extraction:
    *   **Input:** Validated business intake data.
    *   **Action:** 
        *   Normalize textual data (e.g., lowercasing, removing irrelevant characters for certain analyses).
        *   Extract key entities and concepts from open-ended responses using NLP (e.g., specific pain points, unique selling propositions, brand keywords).
        *   Categorize business based on industry, size, stage, etc., using predefined rules or simple classification models.
        *   Structure data for easier consumption by downstream analysis modules.
    *   **Output:** Enriched and structured business profile data.

3.  **Core Analysis & Insight Generation (Parallelizable Sub-tasks):
    *   **Input:** Enriched business profile data.
    *   **Sub-Pipelines/Modules (can run in parallel where dependencies allow):**
        *   **Qualitative Insights (LLM):** Send open-ended responses to an LLM for summarization, sentiment analysis, and extraction of nuanced insights (e.g., unstated goals, core values).
        *   **Goal-Strategy Mapping:** Compare stated business goals against a knowledge base of marketing strategies. Use rules and potentially LLM assistance to select and prioritize relevant strategies.
        *   **Audience Persona Refinement (LLM):** Use intake data and LLM to generate more detailed target audience personas.
        *   **Competitive Analysis:** Process competitor information to identify potential gaps and differentiation opportunities. LLM can assist in summarizing competitor strengths/weaknesses.
        *   **Channel & Content Recommendation:** Based on business profile, target audience, goals, and knowledge base, recommend marketing channels and content pillars. LLM can help generate creative content ideas or themes.
    *   **Output:** A collection of analytical outputs: summarized insights, persona documents, lists of recommended strategies, channels, content themes, etc.

4.  **Blueprint Assembly & Structuring:
    *   **Input:** Collection of analytical outputs from the previous stage.
    *   **Action:** Consolidate all generated insights, recommendations, and analyses into the structured format of the Business Blueprint (as defined in `ai_adaptation_agent_requirements.md`). This involves organizing sections, ensuring coherence, and formatting for presentation.
    *   **Output:** A complete Business Blueprint object/document (e.g., JSON or structured text).

5.  **Blueprint Storage & Notification:
    *   **Input:** Complete Business Blueprint.
    *   **Action:** 
        *   Save the generated blueprint to the PostgreSQL database, linked to the respective business profile.
        *   Notify the business user (e.g., via email, in-app notification) that their blueprint is ready.
    *   **Output:** Stored blueprint and user notification.

## 4. Pipeline for Customer-to-Business Matching

This pipeline connects customers with relevant businesses in near real-time.

**Trigger:** Submission of a customer query via the customer-facing UI.
**Processing Mode:** Synchronous, optimized for low latency.

**Stages:**

1.  **Customer Query Ingestion & Validation:
    *   **Input:** Customer query data (e.g., selected categories, keywords, location from a structured form, or raw text from a natural language query).
    *   **Action:** Receive query from the customer-facing UI API endpoint.
    *   **Validation:** Basic validation (e.g., check for presence of required fields, sanitize input).
    *   **Error Handling:** Return immediate error to UI if query is malformed.
    *   **Output:** Validated customer query.

2.  **Query Preprocessing & Understanding:
    *   **Input:** Validated customer query.
    *   **Action:**
        *   **Keyword Extraction:** Identify key terms and phrases.
        *   **Intent Recognition (LLM for Natural Language Queries):** If natural language input, use LLM to understand the underlying need, disambiguate terms, and identify service categories.
        *   **Location Parsing (if applicable):** Standardize location information.
        *   **Normalization:** Normalize terms (e.g., synonyms, stemming) to improve match recall.
    *   **Output:** Processed query object with extracted entities, intent, and keywords.

3.  **Candidate Business Retrieval (Optimized Search):
    *   **Input:** Processed query object.
    *   **Action:** Query the PostgreSQL database for businesses that broadly match initial criteria (e.g., service category, location radius). This query should leverage pre-indexed fields in the business profiles (e.g., keywords, categories, location data) for speed.
    *   **Output:** A list of candidate business profiles.

4.  **Fine-Grained Matching & Ranking:
    *   **Input:** Processed query object and list of candidate business profiles.
    *   **Action (applied to each candidate):**
        *   **Detailed Keyword Matching:** Score relevance based on overlap between query keywords and business profile keywords/descriptions.
        *   **Semantic Similarity (LLM):** For more nuanced matching, use LLM to compare the semantic meaning of the customer query with business service descriptions.
        *   **Attribute Matching:** Check for matches on specific attributes (e.g., operating hours, specific certifications if available).
        *   **Scoring Algorithm:** Combine scores from different matching facets (keyword, semantic, attribute) into an overall relevance score for each candidate.
        *   **Ranking:** Sort candidate businesses by their overall relevance score.
    *   **Output:** A ranked list of matched business profiles with relevance scores.

5.  **Results Formatting & Presentation:
    *   **Input:** Ranked list of matched business profiles.
    *   **Action:** Format the results for display in the customer UI. This includes selecting key information to display (name, tagline, relevant services, contact info, why it was matched).
    *   **Output:** JSON response to the customer-facing UI containing the formatted list of matched businesses.

## 5. Shared Data Stores and Services

Both pipelines will interact with common underlying components:

*   **PostgreSQL Database:**
    *   Stores comprehensive `business_intake` data and generated `business_blueprints`.
    *   Business profiles will need optimized indexing on fields critical for matching (e.g., service categories, keywords, location).
    *   May store customer query logs for analytics and improvement (with privacy considerations).
*   **Knowledge Base:**
    *   **Structure:** Could be a combination of structured data (e.g., in database tables, configuration files) and unstructured/semi-structured documents.
    *   **Content:** Marketing strategies, industry benchmarks, service taxonomies, keyword mappings, common customer needs patterns.
    *   **Access:** Accessed by both pipelines for decision-making and enrichment.
*   **LLM Integration Service:**
    *   A centralized module/service to manage interactions with external LLM APIs (e.g., OpenAI, Anthropic).
    *   Handles API key management, prompt engineering, request/response formatting, and potentially caching of LLM responses to optimize cost and latency.
*   **Logging and Monitoring Service:** Centralized logging for both pipelines to track execution, errors, and performance metrics.

## 6. Data Flow Considerations

*   **Blueprint Generation:** Data flows from the `intake_api` to PostgreSQL, then through an asynchronous task queue (e.g., Celery with Redis/RabbitMQ) that manages the stages of preprocessing, analysis, blueprint assembly, and finally storage back in PostgreSQL.
*   **Customer Matching:** Data flows synchronously from the customer UI, through an API gateway/backend service that orchestrates query processing, database retrieval, LLM calls (if needed), ranking, and returns results directly to the UI.

## 7. Error Handling and Resilience

*   **Blueprint Pipeline:** Implement retries for transient errors (e.g., LLM API timeouts). For persistent errors, log detailed information and potentially move the task to a dead-letter queue for manual inspection. Ensure partial progress can be saved if a sub-task fails.
*   **Matching Pipeline:** Prioritize graceful degradation. If an LLM call fails or times out, fall back to simpler keyword-based matching. Implement circuit breakers for external service calls. Log all errors for analysis.

This pipeline design provides a framework for developing the AI Adaptation Agent. Specific implementation details, choice of libraries, and infrastructure will be determined in subsequent stages.
