from flask import Blueprint, jsonify, request
import firebase_admin
from firebase_admin import firestore
from src.utils.auth_utils import verify_firebase_token # Import the decorator

user_bp = Blueprint(
    "user_bp", __name__
)

db = firestore.client()

@user_bp.route("/users", methods=["GET"])
@verify_firebase_token # Protect this route
def get_users():
    # Access user info from request.user if needed (added by the decorator)
    # print(f"Authenticated user UID: {request.user.get('uid')}")
    users_ref = db.collection("users")
    users = []
    for doc in users_ref.stream():
        user_data = doc.to_dict()
        user_data["id"] = doc.id
        users.append(user_data)
    return jsonify(users), 200

@user_bp.route("/users", methods=["POST"])
@verify_firebase_token # Protect this route
def create_user():
    data = request.json
    if not data or not data.get("email"):
        return jsonify({"error": "Missing email in request body"}), 400
    
    # Use Firebase Auth UID as the document ID if available and appropriate
    auth_user_uid = request.user.get("uid")
    # For example, you might want to ensure the user being created matches the authenticated user
    # or that only admins can create users. For now, we'll use the UID for the document ID.

    doc_id_to_use = auth_user_uid if auth_user_uid else data.get("email") # Fallback if UID not present (e.g. admin creating user)
    
    user_ref = db.collection("users").document(doc_id_to_use)
    
    # Check if user already exists if using email or other non-UID as ID
    if user_ref.get().exists and not auth_user_uid: # Only check if not using auth UID, as that should be unique
        return jsonify({"error": f"User with ID {doc_id_to_use} already exists"}), 409

    user_data = {
        "username": data.get("username"),
        "email": data.get("email"),
        "auth_uid": auth_user_uid # Store the Firebase Auth UID
        # Add other fields as necessary
    }
    user_ref.set(user_data) # Use set() which can create or overwrite
    
    created_user_doc = user_ref.get()
    if created_user_doc.exists:
        created_user = created_user_doc.to_dict()
        created_user["id"] = created_user_doc.id
        return jsonify(created_user), 201
    else:
        return jsonify({"error": "Failed to create or retrieve user after creation"}), 500

@user_bp.route("/users/<string:user_id>", methods=["GET"])
@verify_firebase_token # Protect this route
def get_user(user_id):
    # Add logic here to ensure the authenticated user is authorized to get this user's details
    # For example, request.user.get('uid') == user_id or admin check
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        user_data["id"] = user_doc.id
        return jsonify(user_data), 200
    else:
        return jsonify({"error": "User not found"}), 404

@user_bp.route("/users/<string:user_id>", methods=["PUT"])
@verify_firebase_token # Protect this route
def update_user(user_id):
    # Add logic here to ensure the authenticated user is authorized to update this user
    # For example, request.user.get('uid') == user_id
    if request.user.get("uid") != user_id:
        return jsonify({"error": "Forbidden: You can only update your own profile."}), 403

    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    if not user_doc.exists:
        return jsonify({"error": "User not found"}), 404

    data = request.json
    update_data = {}
    if "username" in data:
        update_data["username"] = data["username"]
    # Email update might need re-verification, handle carefully or disallow direct update here
    # if "email" in data:
    #     update_data["email"] = data["email"]

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
@verify_firebase_token # Protect this route
def delete_user(user_id):
    # Add logic here to ensure the authenticated user is authorized to delete this user
    # For example, request.user.get('uid') == user_id or admin check
    if request.user.get("uid") != user_id:
         return jsonify({"error": "Forbidden: You can only delete your own profile."}), 403

    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    if not user_doc.exists:
        return jsonify({"error": "User not found"}), 404

    user_ref.delete()
    # Optionally, you might want to delete the user from Firebase Authentication as well
    # auth.delete_user(user_id) # Be careful with this, ensure it's the Firebase Auth UID
    return "", 204

# Example of a public route (no token needed)
@user_bp.route("/public_info", methods=["GET"])
def public_info():
    return jsonify({"message": "This is public information."}), 200

# Example of a protected route that uses the user info from token
@user_bp.route("/me", methods=["GET"])
@verify_firebase_token
def get_my_profile():
    user_uid = request.user.get("uid")
    email = request.user.get("email")
    # Here you would typically fetch the user's profile from Firestore using user_uid
    user_profile_ref = db.collection("users").document(user_uid)
    user_profile_doc = user_profile_ref.get()
    if user_profile_doc.exists:
        return jsonify(user_profile_doc.to_dict()), 200
    else:
        # Optionally create a profile if it doesn't exist, or return 404
        return jsonify({"uid": user_uid, "email": email, "message": "Profile not yet created in Firestore, but authenticated."}), 200

