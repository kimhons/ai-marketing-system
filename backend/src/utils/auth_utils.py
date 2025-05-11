from functools import wraps
from flask import request, jsonify
import firebase_admin
from firebase_admin import auth

def verify_firebase_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        id_token = None
        if "Authorization" in request.headers:
            auth_header = request.headers.get("Authorization")
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                id_token = parts[1]

        if not id_token:
            return jsonify({"error": "Unauthorized: No token provided"}), 401

        try:
            decoded_token = auth.verify_id_token(id_token)
            request.user = decoded_token  # Add user info to request context
        except firebase_admin.auth.InvalidIdTokenError:
            return jsonify({"error": "Unauthorized: Invalid token"}), 401
        except Exception as e:
            print(f"Error verifying token: {e}")
            return jsonify({"error": "Unauthorized: Token verification failed"}), 401

        return f(*args, **kwargs)
    return decorated_function

