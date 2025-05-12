"""Service for matching customers to businesses"""

import os
import re # For more sophisticated keyword extraction
import json # For parsing LLM JSON responses
import logging # For logging
from typing import List, Dict, Any, Optional
import psycopg2 # For PostgreSQL interaction
from psycopg2 import pool, extras # Added extras for DictCursor

from ..shared.data_models import CustomerQuery, MatchedBusiness, BusinessIntakeData
from ..shared.llm_service import LLMService

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class CustomerMatcherService:
    """
    Orchestrates the matching of customer queries to relevant business profiles.
    Uses keyword matching, filtering, and LLM-based semantic matching (if available).
    Integrates with a PostgreSQL database for business profile storage.
    """

    DB_TABLE_NAME = "business_profiles" # Define table name as a constant

    def __init__(self, llm_service: LLMService, db_config: Optional[Dict[str, str]] = None, min_conn: int = 1, max_conn: int = 5):
        """
        Initialize the CustomerMatcherService.
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
            logger.info("Database configuration not provided directly, attempting to load from environment variables...")
            self._db_config = {
                "host": os.getenv("DB_HOST"),
                "port": os.getenv("DB_PORT", "5432"),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "dbname": os.getenv("DB_NAME")
            }
            if not all(val for val in [self._db_config["host"], self._db_config["user"], self._db_config["password"], self._db_config["dbname"]]):
                logger.warning("Critical database environment variables (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME) are not fully set. Database connection will likely fail.")
            else:
                logger.info("Database configuration loaded from environment variables.")

        if self._db_config and all(val for val in [self._db_config["host"], self._db_config["user"], self._db_config["password"], self._db_config["dbname"]]):
            try:
                logger.info(f"Initializing database connection pool for {self._db_config['dbname']} on {self._db_config['host']}:{self._db_config['port']}...")
                self.db_connection_pool = psycopg2.pool.SimpleConnectionPool(
                    min_conn, 
                    max_conn,
                    host=self._db_config["host"],
                    port=self._db_config["port"],
                    user=self._db_config["user"],
                    password=self._db_config["password"],
                    dbname=self._db_config["dbname"]
                )
                conn = self.db_connection_pool.getconn()
                logger.info("Database connection pool successfully created and tested.")
                self.db_connection_pool.putconn(conn)
            except psycopg2.Error as e:
                logger.error(f"Error creating database connection pool: {e}")
                self.db_connection_pool = None
        else:
            logger.warning("Database configuration is incomplete. Connection pool not created.")
        
        logger.info("CustomerMatcherService initialized. Database integration setup attempted.")
        logger.info("Note: Ensure psycopg2-binary is installed (pip install psycopg2-binary).")

    def _get_db_connection(self):
        if not self.db_connection_pool:
            return None
        try:
            return self.db_connection_pool.getconn()
        except psycopg2.Error as e:
            logger.error(f"Error getting connection from pool: {e}")
            return None

    def _put_db_connection(self, conn):
        if self.db_connection_pool and conn:
            self.db_connection_pool.putconn(conn)

    def close_db_pool(self):
        if self.db_connection_pool:
            logger.info("Closing database connection pool...")
            self.db_connection_pool.closeall()
            logger.info("Database connection pool closed.")

    def _retrieve_candidate_businesses(self, processed_query: Dict[str, Any]) -> List[BusinessIntakeData]:
        """Retrieves candidate business profiles from the database based on processed query criteria."""
        conn = self._get_db_connection()
        if not conn:
            logger.error("Cannot retrieve candidates: No database connection.")
            return []

        profiles: List[BusinessIntakeData] = []
        query_keywords = processed_query.get("keywords", [])
        query_location = processed_query.get("location")

        select_columns = "business_id, business_name, industry, business_stage, goals, target_audience_description, products_services_description, location, service_tags, raw_data_json"
        sql_base = f"SELECT {select_columns} FROM {self.DB_TABLE_NAME}"
        
        where_clauses = []
        params = []

        if query_keywords:
            keyword_match_expressions = []
            for keyword in query_keywords:
                if not keyword.strip(): continue
                like_pattern = f"%{keyword.strip()}%"
                params.extend([like_pattern] * 4)
                keyword_match_expressions.append(
                    "(LOWER(business_name) ILIKE %s OR "
                    "LOWER(products_services_description) ILIKE %s OR "
                    "LOWER(industry) ILIKE %s OR "
                    "EXISTS (SELECT 1 FROM unnest(service_tags) st WHERE LOWER(st) ILIKE %s))"
                )
            if keyword_match_expressions:
                where_clauses.append(f"({' OR '.join(keyword_match_expressions)})") 

        if query_location:
            where_clauses.append("LOWER(location) = %s")
            params.append(query_location.lower())

        sql_query = sql_base
        if where_clauses:
            sql_query += " WHERE " + " AND ".join(where_clauses)
        sql_query += " LIMIT 100;"
        
        logger.debug(f"Executing candidate retrieval query: {sql_query} with params {params}")

        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql_query, tuple(params))
                rows = cur.fetchall()
                for row in rows:
                    raw_responses_data = {
                        "business_id": row["business_id"],
                        "location": row["location"],
                        "service_tags": list(row["service_tags"]) if row["service_tags"] else [],
                    }
                    if row["raw_data_json"] and isinstance(row["raw_data_json"], dict):
                        raw_responses_data.update(row["raw_data_json"])
                    elif isinstance(row["raw_data_json"], str):
                        try:
                            raw_responses_data.update(json.loads(row["raw_data_json"]))
                        except json.JSONDecodeError as json_e:
                            logger.warning(f"Could not parse raw_data_json string for business_id {row['business_id']}: {json_e}")

                    profiles.append(BusinessIntakeData(
                        business_name=row["business_name"],
                        industry=row["industry"],
                        business_stage=row["business_stage"],
                        goals=list(row["goals"]) if row["goals"] else [],
                        target_audience_description=row["target_audience_description"],
                        products_services_description=row["products_services_description"],
                        raw_responses=raw_responses_data
                    ))
            logger.debug(f"Retrieved {len(profiles)} candidate profiles from database.")
        except psycopg2.Error as e:
            logger.error(f"Database error while retrieving candidate profiles: {e}")
        finally:
            self._put_db_connection(conn)
        return profiles

    def find_matched_businesses(self, customer_query: CustomerQuery) -> List[MatchedBusiness]:
        """
        Main method to find and rank businesses matching a customer query.
        """
        logger.info(f"Starting business matching for query: {customer_query.query_text or customer_query.keywords}")

        processed_query = self._preprocess_query(customer_query)
        
        logger.info("Stage 3: Candidate Business Retrieval (from DB)...")
        candidate_businesses = self._retrieve_candidate_businesses(processed_query)

        logger.info("Stage 4: Fine-Grained Matching & Ranking...")
        matched_businesses: List[MatchedBusiness] = []
        if not candidate_businesses:
            logger.info("No candidate businesses found from database for this query.")
            return []
            
        for business_profile in candidate_businesses:
            relevance_score, match_reason_list = self._calculate_relevance(processed_query, business_profile)
            match_reason_str = "; ".join(match_reason_list)
            # Adjusted threshold, can be tuned further based on real data performance
            if relevance_score > 0.15: 
                matched_businesses.append(
                    MatchedBusiness(
                        business_id=business_profile.raw_responses.get("business_id", "unknown"), # Ensure this is reliable
                        business_name=business_profile.business_name,
                        tagline=business_profile.raw_responses.get("tagline", f"Your trusted {business_profile.industry} provider"),
                        relevant_services=self._extract_relevant_services(business_profile, processed_query),
                        location=business_profile.raw_responses.get("location"),
                        contact_info=f"Contact details for {business_profile.business_name}", # Placeholder
                        match_reason=match_reason_str,
                        relevance_score=relevance_score
                    )
                )
        
        matched_businesses.sort(key=lambda x: x.relevance_score, reverse=True)
        logger.info(f"Matching complete. Found {len(matched_businesses)} relevant businesses after ranking.")
        return matched_businesses

    def _preprocess_query(self, query: CustomerQuery) -> Dict[str, Any]:
        """Processes the customer query to extract keywords, location, and understand intent."""
        original_keywords = [k.lower().strip() for k in query.keywords if k.strip()] if query.keywords else []
        original_text = query.query_text.lower().strip() if query.query_text else ""
        
        processed = {
            "keywords": list(set(original_keywords)), 
            "original_text": original_text,
            "intent": "unknown", 
            "entities": {}
        }

        if query.service_category and query.service_category.strip():
            processed["keywords"].append(query.service_category.lower().strip())
            processed["keywords"] = list(set(processed["keywords"])) 

        if query.location and query.location.strip():
            processed["location"] = query.location.lower().strip()
        
        if original_text and not processed["keywords"]:
            # Basic keyword extraction from text if no keywords provided
            potential_keywords = [kw for kw in re.findall(r"\b[a-zA-Z]{3,}\b", original_text) if len(kw) > 2] 
            processed["keywords"].extend(potential_keywords)
            processed["keywords"] = list(set(processed["keywords"])) 

        if original_text and self.llm_service.is_api_key_available():
            logger.info("Attempting LLM-based query understanding...")
            llm_prompt = f"""Analyze the following customer query to understand their intent and extract key entities. 
Customer Query: {original_text}

Identify the primary service or product the customer is looking for, any specified location, and other important details or constraints (e.g., urgency, specific features). 
Return the response as a JSON object with keys: "intent" (e.g., "find_service", "request_quote", "information_seek"), "service_keywords" (list of relevant service keywords), "location_extracted" (string, if any), and "other_details" (string summarizing other needs).
Example: For "I need an emergency plumber in London for a burst pipe", the output might be:
{{
  "intent": "find_service",
  "service_keywords": ["emergency plumber", "plumber", "burst pipe"],
  "location_extracted": "London",
  "other_details": "Urgent need due to burst pipe."
}}
"""
            try:
                llm_response_obj = self.llm_service.generate_json_response(llm_prompt, max_tokens=150)
                if llm_response_obj:
                    logger.info(f"LLM Query Understanding Response: {llm_response_obj}")
                    processed["intent"] = llm_response_obj.get("intent", processed["intent"])
                    llm_keywords = llm_response_obj.get("service_keywords", [])
                    if isinstance(llm_keywords, list):
                        processed["keywords"].extend([k.lower().strip() for k in llm_keywords if k.strip()])
                        processed["keywords"] = list(set(processed["keywords"])) 
                    
                    llm_location = llm_response_obj.get("location_extracted")
                    if llm_location and not processed.get("location"): 
                        processed["location"] = llm_location.lower().strip()
                    
                    processed["entities"]["llm_details"] = llm_response_obj.get("other_details", "")
                else:
                    logger.warning("LLM query understanding did not return a valid JSON object.")
            except Exception as e:
                logger.error(f"Error during LLM query understanding: {e}")
        else:
            if original_text:
                 logger.info("LLM API key not available or query text empty, skipping LLM query understanding.")

        logger.debug(f"Processed Query: {processed}")
        return processed

    def _calculate_relevance(self, processed_query: Dict[str, Any], business_profile: BusinessIntakeData) -> tuple[float, List[str]]:
        """Calculates a relevance score between a processed query and a business profile, potentially using LLM."""
        final_score = 0.0
        reasons: List[str] = [] # Changed to List[str]
        query_keywords = set(processed_query.get("keywords", []))
        
        # --- Component Weights (can be tuned) ---
        KEYWORD_WEIGHT = 0.4
        LOCATION_WEIGHT = 0.3
        SEMANTIC_WEIGHT = 0.3 # Only applied if LLM is used

        # --- Keyword-based scoring --- 
        keyword_score_component = 0.0
        temp_reasons_keyword = []
        desc_text = (business_profile.products_services_description or "").lower()
        # More robust word splitting, handles punctuation better
        desc_words = set(re.findall(r'\b\w+\b', desc_text))
        common_desc_keywords = query_keywords.intersection(desc_words)
        if common_desc_keywords:
            # Score based on number of common keywords, capped
            keyword_score_component += min(len(common_desc_keywords) * 0.1, 0.4) 
            temp_reasons_keyword.append(f"{len(common_desc_keywords)} keyword(s) in description: {', '.join(list(common_desc_keywords)[:3])}{'...' if len(common_desc_keywords)>3 else ''}.")

        profile_tags = business_profile.raw_responses.get("service_tags", [])
        tags = set([tag.lower() for tag in profile_tags if isinstance(tag, str)])
        common_tags_keywords = query_keywords.intersection(tags)
        if common_tags_keywords:
            keyword_score_component += min(len(common_tags_keywords) * 0.2, 0.5) # Higher weight for direct tag match
            temp_reasons_keyword.append(f"{len(common_tags_keywords)} keyword(s) in service tags: {', '.join(list(common_tags_keywords)[:3])}{'...' if len(common_tags_keywords)>3 else ''}.")

        if business_profile.industry and business_profile.industry.lower() in query_keywords:
            keyword_score_component += 0.1 # Small bonus for industry match
            temp_reasons_keyword.append(f"Industry '{business_profile.industry}' matched.")
        
        normalized_keyword_score = min(keyword_score_component, 1.0) 
        if normalized_keyword_score > 0: reasons.extend(temp_reasons_keyword)

        # --- Location scoring --- 
        location_score_component = 0.0
        profile_location = (business_profile.raw_responses.get("location") or "").lower()
        query_location = processed_query.get("location")
        if query_location and profile_location:
            if profile_location == query_location:
                location_score_component = 1.0 # Full score for exact location match
                reasons.append("Exact location match.")
            elif query_location in profile_location or profile_location in query_location: 
                location_score_component = 0.5 # Partial score for broader match
                reasons.append("Partial location match.")
        elif query_location and not profile_location:
            location_score_component = 0.0 # Query has location, profile doesn't - low match for location
        elif not query_location:
            location_score_component = 0.2 # No location in query, so don't penalize profile heavily for having one

        # --- LLM-based Semantic Similarity --- 
        semantic_score_component = 0.0
        if processed_query.get("original_text") and self.llm_service.is_api_key_available():
            logger.info(f"Attempting LLM semantic similarity for: {business_profile.business_name}")
            # Corrected and completed f-string for semantic_prompt
            semantic_prompt = f"""Assess the semantic similarity between the customer query and the business offering. 
Customer Query: {processed_query["original_text"]}

Business Name: {business_profile.business_name}
Business Description: {business_profile.products_services_description}
Business Industry: {business_profile.industry}
Service Tags: {', '.join(business_profile.raw_responses.get("service_tags", []))}

Provide a semantic similarity score as a float between 0.0 (not similar) and 1.0 (highly similar). 
Also provide a brief justification for the score. 
Return the response as a JSON object with keys: "semantic_score" (float) and "semantic_justification" (string).
Example JSON response: {{"semantic_score": 0.75, "semantic_justification": "The business offers services that closely match the customer's stated needs for X and Y."}}
"""
            try:
                llm_response_obj = self.llm_service.generate_json_response(semantic_prompt, max_tokens=200)
                if llm_response_obj and isinstance(llm_response_obj, dict):
                    score = llm_response_obj.get("semantic_score")
                    justification = llm_response_obj.get("semantic_justification")
                    if isinstance(score, (float, int)) and 0.0 <= score <= 1.0:
                        semantic_score_component = float(score)
                        if justification and isinstance(justification, str):
                            reasons.append(f"LLM Semantic Match: {justification} (Score: {semantic_score_component:.2f})")
                        else:
                            reasons.append(f"LLM Semantic Score: {semantic_score_component:.2f}")
                    else:
                        logger.warning(f"LLM returned invalid semantic_score: {score} for business {business_profile.business_name}")
                else:
                    logger.warning(f"LLM semantic similarity did not return a valid JSON object for business {business_profile.business_name}. Response: {llm_response_obj}")
            except Exception as e:
                logger.error(f"Error during LLM semantic similarity assessment for {business_profile.business_name}: {e}")
        else:
            if processed_query.get("original_text"):
                logger.info(f"LLM API key not available, skipping semantic similarity for {business_profile.business_name}.")

        # --- Combine scores --- 
        # If LLM was used and provided a score, it contributes; otherwise, its weight is redistributed or ignored.
        if semantic_score_component > 0 and self.llm_service.is_api_key_available():
            final_score = (normalized_keyword_score * KEYWORD_WEIGHT) + \
                          (location_score_component * LOCATION_WEIGHT) + \
                          (semantic_score_component * SEMANTIC_WEIGHT)
        else:
            # Redistribute semantic weight if not used, or simply use other components
            # For simplicity, let's normalize based on available components if semantic is missing
            total_weight_used = KEYWORD_WEIGHT + LOCATION_WEIGHT
            if total_weight_used > 0:
                final_score = ((normalized_keyword_score * KEYWORD_WEIGHT) + 
                               (location_score_component * LOCATION_WEIGHT)) / total_weight_used
            else: # Should not happen if keywords or location always have some score potential
                final_score = 0.0

        return min(max(final_score, 0.0), 1.0), reasons # Ensure score is between 0 and 1

    def _extract_relevant_services(self, business_profile: BusinessIntakeData, processed_query: Dict[str, Any]) -> List[str]:
        """Extracts a list of relevant services from the business profile based on the query."""
        relevant_services_found: List[str] = []
        query_keywords = set(processed_query.get("keywords", []))

        # 1. Check service tags
        profile_tags = business_profile.raw_responses.get("service_tags", [])
        if profile_tags:
            for tag in profile_tags:
                if isinstance(tag, str) and tag.lower() in query_keywords:
                    relevant_services_found.append(tag)
        
        # 2. Check products_services_description for keywords
        desc_text = (business_profile.products_services_description or "").lower()
        if desc_text:
            # Simple check: if a query keyword is in the description, consider the business's primary industry/service type relevant
            # This could be made more sophisticated by extracting specific service phrases from the description that match keywords.
            for keyword in query_keywords:
                if keyword in desc_text:
                    # Add the keyword itself if it seems like a service, or a more general service category
                    # For now, we'll add matched keywords from description if they are not already from tags
                    if keyword not in [s.lower() for s in relevant_services_found]:
                         # Attempt to find a phrase around the keyword in description
                        try:
                            match_pos = desc_text.find(keyword)
                            start_phrase = max(0, match_pos - 15)
                            end_phrase = min(len(desc_text), match_pos + len(keyword) + 15)
                            phrase = desc_text[start_phrase:end_phrase]
                            # Basic cleanup of the phrase
                            phrase = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', phrase) # trim non-alphanum edges
                            relevant_services_found.append(f"...{phrase}...") 
                        except:
                             relevant_services_found.append(keyword) # Fallback to keyword

        # Deduplicate while preserving order (roughly)
        final_relevant_services = []
        for service in relevant_services_found:
            is_present = False
            for existing_service in final_relevant_services:
                if service.strip().lower() in existing_service.strip().lower() or existing_service.strip().lower() in service.strip().lower():
                    is_present = True
                    break
            if not is_present:
                 final_relevant_services.append(service.strip().capitalize()) # Capitalize for display
        
        if not final_relevant_services and business_profile.industry:
             final_relevant_services.append(business_profile.industry.capitalize() + " (General Category)")

        return list(set(final_relevant_services))[:5] # Return unique, capitalized, and limit to 5 for brevity

