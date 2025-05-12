# /home/ubuntu/ai-marketing-system-new/backend/ai_services_api/src/routes/blueprint_routes.py
import os
from flask import Blueprint, request, jsonify, current_app

# Assuming BlueprintService and BusinessIntakeData are accessible via the path adjustments in main.py
from blueprint_generator.blueprint_service import BlueprintService
from shared.data_models import BusinessIntakeData, BusinessBlueprint # For type hinting and validation
from shared.llm_service import LLMService # BlueprintService depends on LLMService

blueprint_bp = Blueprint("blueprint_bp", __name__)

# Initialize services. Ideally, these would be managed by Flask app context or a DI container
# For simplicity here, we might instantiate them per request or globally if stateless and thread-safe.
# Given they might hold db connections or LLM clients, careful instantiation is needed.

def get_blueprint_service():
    # LLMService needs an API key
    llm_service = LLMService(api_key=current_app.config.get("OPENAI_API_KEY"))
    
    # BlueprintService needs LLMService and DB config
    db_config = {
        "user": current_app.config.get("DB_USER"),
        "password": current_app.config.get("DB_PASSWORD"),
        "host": current_app.config.get("DB_HOST"),
        "port": current_app.config.get("DB_PORT"),
        "dbname": current_app.config.get("DB_NAME"),
    }
    # Note: BlueprintService was updated to accept db_config in its __init__
    blueprint_service = BlueprintService(llm_service=llm_service, db_config=db_config)
    return blueprint_service

@blueprint_bp.route("/generate", methods=["POST"])
def generate_blueprint_route():
    data = request.json
    if not data:
        return jsonify({"error": "Missing request data"}), 400

    try:
        # Validate and deserialize input data (example, actual validation might be more robust)
        intake_data_dict = data.get("intake_data")
        if not intake_data_dict:
            return jsonify({"error": "Missing intake_data in request"}), 400
        
        # Assuming BusinessIntakeData can be instantiated from a dict
        # You might need a proper deserialization method in the data model itself
        intake_data = BusinessIntakeData(**intake_data_dict)
        business_id = data.get("business_id") # Assuming business_id is provided for linking
        if not business_id:
            return jsonify({"error": "Missing business_id"}), 400

    except TypeError as e:
        return jsonify({"error": f"Invalid intake_data format: {e}"}), 400
    except Exception as e:
        return jsonify({"error": f"Error processing input: {e}"}), 400

    blueprint_service = get_blueprint_service()
    try:
        # The generate_and_save_blueprint method now takes business_id
        blueprint = blueprint_service.generate_and_save_blueprint(intake_data, business_id)
        if blueprint:
            # Convert blueprint object to dict for JSON response if it has a to_dict() method or similar
            # For Pydantic models, .model_dump() or .dict() would be used.
            # Assuming BusinessBlueprint is a Pydantic model or has a to_dict method
            return jsonify(blueprint.model_dump() if hasattr(blueprint, "model_dump") else blueprint.__dict__), 201
        else:
            return jsonify({"error": "Failed to generate or save blueprint"}), 500
    except Exception as e:
        current_app.logger.error(f"Error generating blueprint: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@blueprint_bp.route("/<string:blueprint_id>", methods=["GET"])
def get_blueprint_route(blueprint_id):
    blueprint_service = get_blueprint_service()
    try:
        blueprint = blueprint_service.get_blueprint_by_id(blueprint_id)
        if blueprint:
            return jsonify(blueprint.model_dump() if hasattr(blueprint, "model_dump") else blueprint.__dict__), 200
        else:
            return jsonify({"error": "Blueprint not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error retrieving blueprint {blueprint_id}: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@blueprint_bp.route("/business/<string:business_id>", methods=["GET"])
def get_blueprints_for_business_route(business_id):
    blueprint_service = get_blueprint_service()
    try:
        blueprints = blueprint_service.get_blueprints_by_business_id(business_id)
        # Convert list of blueprint objects to list of dicts
        blueprints_data = [bp.model_dump() if hasattr(bp, "model_dump") else bp.__dict__ for bp in blueprints]
        return jsonify(blueprints_data), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving blueprints for business {business_id}: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# Add other CRUD operations as needed (update, delete)

