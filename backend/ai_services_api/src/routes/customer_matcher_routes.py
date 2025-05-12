# /home/ubuntu/ai-marketing-system-new/backend/ai_services_api/src/routes/customer_matcher_routes.py
import os
from flask import Blueprint, request, jsonify, current_app

# Assuming CustomerMatcherService and CustomerQuery are accessible via path adjustments in main.py
from customer_matcher.customer_matcher_service import CustomerMatcherService
from shared.data_models import CustomerQuery # For type hinting and validation
from shared.llm_service import LLMService # CustomerMatcherService depends on LLMService

customer_matcher_bp = Blueprint("customer_matcher_bp", __name__)

def get_customer_matcher_service():
    # LLMService needs an API key
    llm_service = LLMService(api_key=current_app.config.get("OPENAI_API_KEY"))
    
    # CustomerMatcherService needs LLMService and DB config
    db_config = {
        "user": current_app.config.get("DB_USER"),
        "password": current_app.config.get("DB_PASSWORD"),
        "host": current_app.config.get("DB_HOST"),
        "port": current_app.config.get("DB_PORT"),
        "dbname": current_app.config.get("DB_NAME"),
    }
    # Note: CustomerMatcherService was updated to accept db_config in its __init__
    customer_matcher_service = CustomerMatcherService(llm_service=llm_service, db_config=db_config)
    return customer_matcher_service

@customer_matcher_bp.route("/match", methods=["POST"])
def match_customer_route():
    data = request.json
    if not data:
        return jsonify({"error": "Missing request data"}), 400

    try:
        # Validate and deserialize input data
        query_text = data.get("query_text")
        service_category = data.get("service_category")
        keywords = data.get("keywords", [])
        location = data.get("location")
        # user_id = data.get("user_id") # Optional, if you want to associate queries with users

        if not query_text or not service_category:
            return jsonify({"error": "Missing required fields: query_text, service_category"}), 400

        customer_query = CustomerQuery(
            query_text=query_text,
            service_category=service_category,
            keywords=keywords,
            location=location
        )
    except TypeError as e:
        return jsonify({"error": f"Invalid customer query format: {e}"}), 400
    except Exception as e:
        return jsonify({"error": f"Error processing input: {e}"}), 400

    matcher_service = get_customer_matcher_service()
    try:
        matched_businesses = matcher_service.find_matched_businesses(customer_query)
        
        # Convert list of MatchedBusinessProfile objects to list of dicts
        # Assuming MatchedBusinessProfile has a to_dict() or is Pydantic model
        results = []
        for mbp in matched_businesses:
            business_dict = mbp.business_profile.model_dump() if hasattr(mbp.business_profile, "model_dump") else mbp.business_profile.__dict__
            results.append({
                "business_profile": business_dict,
                "relevance_score": mbp.relevance_score,
                "matching_reasons": mbp.matching_reasons
            })
            
        return jsonify(results), 200
    except Exception as e:
        current_app.logger.error(f"Error matching customer query: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# Potential future endpoint to get business profile details if not fully returned by match
# @customer_matcher_bp.route("/business/<string:business_id>", methods=["GET"])
# def get_business_profile_route(business_id):
#     # This might involve a direct DB lookup or a call to a dedicated business profile service
#     pass

