# src/main.py
import os
import sys
from datetime import timedelta

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from dotenv import load_dotenv

# Load .env from backend/auth_service/.env
# Ensure the path to .env is correct relative to this main.py file
# __file__ is src/main.py, dirname(__file__) is src/, dirname(dirname(__file__)) is backend/auth_service/
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(env_path)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))

# Configurations
app.config["SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

if not app.config["SECRET_KEY"]:
    print("CRITICAL: JWT_SECRET_KEY environment variable not set. Using a default, insecure key. CHANGE THIS!")
    app.config["SECRET_KEY"] = "unsafe-default-jwt-secret-key-for-development-only"

if not app.config["SQLALCHEMY_DATABASE_URI"]:
    print("CRITICAL: DATABASE_URL environment variable not set. Application will likely fail to connect to DB.")
    # Consider if a fallback is truly desired or if it should fail hard.
    # For now, it will proceed and likely fail at DB operations if not set.

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", "1")))
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", "30")))

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True) # Allow all origins for /api/* routes for now

# Import and register blueprints after db and app are initialized to avoid circular imports
from src.routes.auth_routes import auth_bp 
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Remove or comment out the default user_bp from template if not used
# from src.routes.user import user_bp
# app.register_blueprint(user_bp, url_prefix='/api')

@app.route("/health") # Changed from / to /health for a more specific health check endpoint
def health_check():
    return "Authentication Service is running!", 200

# Static file serving (if you have a frontend within this Flask app, otherwise not strictly needed for an API service)
# If this is purely a backend API, these static serving routes might be removed or simplified.
@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route("/") # Serve index.html at root if it exists, otherwise a welcome message
@app.route("/<path:path>")
def serve_frontend_or_welcome(path=None):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    
    index_path = os.path.join(static_folder_path, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(static_folder_path, "index.html")
    else:
        return "Welcome to the Auth API. No UI here. Check /api/auth endpoints or /health for service status.", 200

if __name__ == "__main__":
    with app.app_context():
        from src.models.user import User # Import User model here for create_all
        db.create_all() # Create tables if they don't exist
    app.run(
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 5001)), 
        debug=(os.getenv("FLASK_ENV", "development") == "development")
    )

