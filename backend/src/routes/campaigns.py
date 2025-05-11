# backend/src/routes/campaigns.py
from flask import Blueprint, jsonify, request
import firebase_admin
from firebase_admin import firestore
from src.utils.auth_utils import verify_firebase_token # Import the decorator

campaign_bp = Blueprint("campaign_bp", __name__)
db = firestore.client()

@campaign_bp.route("/campaigns", methods=["POST"])
@verify_firebase_token
def create_campaign():
    data = request.json
    user_uid = request.user.get("uid")

    if not data or not data.get("name"):
        return jsonify({"error": "Campaign name is required"}), 400

    campaign_data = {
        "name": data.get("name"),
        "description": data.get("description", ""),
        "status": data.get("status", "draft"), # e.g., draft, active, paused, completed
        "created_by": user_uid,
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
        # Add other campaign-specific fields here, e.g., target_audience, budget, etc.
    }

    try:
        campaign_ref = db.collection("users").document(user_uid).collection("campaigns").document()
        campaign_ref.set(campaign_data)
        new_campaign = campaign_ref.get().to_dict()
        if new_campaign:
            new_campaign["id"] = campaign_ref.id
            return jsonify(new_campaign), 201
        else:
            return jsonify({"error": "Failed to create campaign after saving"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@campaign_bp.route("/campaigns", methods=["GET"])
@verify_firebase_token
def get_campaigns():
    user_uid = request.user.get("uid")
    try:
        campaigns_ref = db.collection("users").document(user_uid).collection("campaigns").order_by("created_at", direction=firestore.Query.DESCENDING)
        campaigns = []
        for doc in campaigns_ref.stream():
            campaign_data = doc.to_dict()
            campaign_data["id"] = doc.id
            campaigns.append(campaign_data)
        return jsonify(campaigns), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@campaign_bp.route("/campaigns/<string:campaign_id>", methods=["GET"])
@verify_firebase_token
def get_campaign(campaign_id):
    user_uid = request.user.get("uid")
    try:
        campaign_ref = db.collection("users").document(user_uid).collection("campaigns").document(campaign_id)
        campaign_doc = campaign_ref.get()
        if campaign_doc.exists:
            campaign_data = campaign_doc.to_dict()
            campaign_data["id"] = campaign_doc.id
            return jsonify(campaign_data), 200
        else:
            return jsonify({"error": "Campaign not found"}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@campaign_bp.route("/campaigns/<string:campaign_id>", methods=["PUT"])
@verify_firebase_token
def update_campaign(campaign_id):
    user_uid = request.user.get("uid")
    data = request.json
    try:
        campaign_ref = db.collection("users").document(user_uid).collection("campaigns").document(campaign_id)
        campaign_doc = campaign_ref.get()

        if not campaign_doc.exists:
            return jsonify({"error": "Campaign not found"}), 404

        update_data = {}
        if "name" in data:
            update_data["name"] = data["name"]
        if "description" in data:
            update_data["description"] = data["description"]
        if "status" in data:
            update_data["status"] = data["status"]
        # Add other updatable fields

        if not update_data:
            return jsonify({"error": "No update fields provided"}), 400
        
        update_data["updated_at"] = firestore.SERVER_TIMESTAMP
        campaign_ref.update(update_data)
        
        updated_campaign_doc = campaign_ref.get()
        updated_campaign_data = updated_campaign_doc.to_dict()
        if updated_campaign_data:
            updated_campaign_data["id"] = updated_campaign_doc.id
            return jsonify(updated_campaign_data), 200
        else:
            return jsonify({"error": "Failed to update campaign"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@campaign_bp.route("/campaigns/<string:campaign_id>", methods=["DELETE"])
@verify_firebase_token
def delete_campaign(campaign_id):
    user_uid = request.user.get("uid")
    try:
        campaign_ref = db.collection("users").document(user_uid).collection("campaigns").document(campaign_id)
        campaign_doc = campaign_ref.get()

        if not campaign_doc.exists:
            return jsonify({"error": "Campaign not found"}), 404

        campaign_ref.delete()
        return "", 204
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

