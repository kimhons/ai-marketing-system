from flask import Blueprint, jsonify, request
import firebase_admin
from firebase_admin import firestore

user_bp = Blueprint(
    "user_bp", __name__
)  # Changed blueprint name to avoid conflict if you have another user.py

# Get a Firestore client
db = firestore.client()

@user_bp.route("/users", methods=["GET"])
def get_users():
    users_ref = db.collection("users")
    users = []
    for doc in users_ref.stream():
        user_data = doc.to_dict()
        user_data["id"] = doc.id  # Add document ID to the user data
        users.append(user_data)
    return jsonify(users), 200

@user_bp.route("/users", methods=["POST"])
def create_user():
    data = request.json
    if not data or not data.get("email"):
        return jsonify({"error": "Missing email in request body"}), 400

    # You might want to use the email or a generated UID as the document ID
    # For simplicity, letting Firestore auto-generate ID here.
    # Or, if using Firebase Auth, the UID from auth would be the document ID.
    user_ref = db.collection("users").document()
    user_data = {
        "username": data.get("username"),
        "email": data.get("email"),
        # Add other fields as necessary
    }
    user_ref.set(user_data)
    created_user = user_ref.get().to_dict()
    if created_user:
        created_user["id"] = user_ref.id
        return jsonify(created_user), 201
    else:
        return jsonify({"error": "Failed to create user"}), 500

@user_bp.route("/users/<string:user_id>", methods=["GET"])
def get_user(user_id):
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        user_data["id"] = user_doc.id
        return jsonify(user_data), 200
    else:
        return jsonify({"error": "User not found"}), 404

@user_bp.route("/users/<string:user_id>", methods=["PUT"])
def update_user(user_id):
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    if not user_doc.exists:
        return jsonify({"error": "User not found"}), 404

    data = request.json
    update_data = {}
    if "username" in data:
        update_data["username"] = data["username"]
    if "email" in data:
        update_data["email"] = data["email"]
    # Add other updatable fields

    if not update_data:
        return jsonify({"error": "No update fields provided"}), 400

    user_ref.update(update_data)
    updated_user_doc = user_ref.get()
    updated_user_data = updated_user_doc.to_dict()
    if updated_user_data:
        updated_user_data["id"] = updated_user_doc.id
        return jsonify(updated_user_data), 200
    else:
        return jsonify({"error": "Failed to update user"}), 500

@user_bp.route("/users/<string:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    if not user_doc.exists:
        return jsonify({"error": "User not found"}), 404

    user_ref.delete()
    return "", 204

