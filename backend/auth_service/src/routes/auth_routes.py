# src/routes/auth_routes.py
import os
from flask import Blueprint, request, jsonify
from src.models.user import User
from src.main import db, bcrypt # Import db and bcrypt from main.py
import jwt
from datetime import datetime, timedelta, timezone

auth_bp = Blueprint("auth_bp", __name__)

# Helper function to generate tokens
def _create_tokens(user_id):
    access_token_payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", "1")))
    }
    refresh_token_payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", "30")))
    }
    secret_key = os.getenv("JWT_SECRET_KEY")
    if not secret_key:
        raise ValueError("JWT_SECRET_KEY not configured")

    access_token = jwt.encode(access_token_payload, secret_key, algorithm="HS256")
    refresh_token = jwt.encode(refresh_token_payload, secret_key, algorithm="HS256")
    return access_token, refresh_token

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Missing username, email, or password"}), 400

    username = data["username"]
    email = data["email"]
    password = data["password"]

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"error": "User with this username or email already exists"}), 409

    try:
        new_user = User(username=username, email=email, password=password, full_name=data.get("full_name"))
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or (not data.get("username") and not data.get("email")) or not data.get("password"):
        return jsonify({"error": "Missing username/email or password"}), 400

    identifier = data.get("username") or data.get("email")
    password = data["password"]

    user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()

    if user and user.check_password(password):
        if not user.is_active:
            return jsonify({"error": "User account is inactive"}), 403
        try:
            access_token, refresh_token = _create_tokens(user.id)
            return jsonify({
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.to_dict()
            }), 200
        except ValueError as ve:
             return jsonify({"error": str(ve)}), 500 # For JWT_SECRET_KEY not configured
        except Exception as e:
            return jsonify({"error": f"Token generation failed: {str(e)}"}), 500
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route("/refresh", methods=["POST"])
def refresh_token():
    data = request.get_json()
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        return jsonify({"error": "Refresh token is missing"}), 400

    secret_key = os.getenv("JWT_SECRET_KEY")
    if not secret_key:
        return jsonify({"error": "JWT_SECRET_KEY not configured"}), 500

    try:
        payload = jwt.decode(refresh_token, secret_key, algorithms=["HS256"])
        user_id = payload["user_id"]
        # Optionally, check if user still exists and is active
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return jsonify({"error": "Invalid refresh token or inactive user"}), 401
        
        new_access_token, new_refresh_token = _create_tokens(user_id)
        return jsonify({
            "access_token": new_access_token,
            "refresh_token": new_refresh_token # Optionally, issue a new refresh token or re-use
        }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid refresh token"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Example of a protected route (to be created if needed)
# from functools import wraps
# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#         if "Authorization" in request.headers:
#             auth_header = request.headers["Authorization"]
#             if auth_header.startswith("Bearer "):
#                 token = auth_header.split(" ")[1]
#         if not token:
#             return jsonify({"message": "Token is missing!"}), 401
#         try:
#             secret_key = os.getenv("JWT_SECRET_KEY")
#             data = jwt.decode(token, secret_key, algorithms=["HS256"])
#             current_user = User.query.get(data["user_id"])
#             if not current_user or not current_user.is_active:
#                 return jsonify({"message": "Token is invalid or user inactive!"}), 401
#         except jwt.ExpiredSignatureError:
#             return jsonify({"message": "Token has expired!"}), 401
#         except jwt.InvalidTokenError:
#             return jsonify({"message": "Token is invalid!"}), 401
#         except Exception as e:
#             return jsonify({"message": f"Token validation error: {str(e)}"}), 500
#         return f(current_user, *args, **kwargs)
#     return decorated

# @auth_bp.route("/me", methods=["GET"])
# @token_required
# def get_current_user(current_user):
#     return jsonify(current_user.to_dict()), 200

