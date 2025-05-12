# /home/ubuntu/ai-marketing-system-new/backend/ai_services_api/src/main.py
import os
import sys
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Add the parent directory of 'ai_adaptation_agent' to sys.path
# to allow importing BlueprintService and CustomerMatcherService
# The ai_services_api is in backend/ai_services_api/, and ai_adaptation_agent is in backend/ai_adaptation_agent/
# So, we need to go up one level from ai_services_api (to backend/) and then into ai_adaptation_agent/src
# Or, more robustly, add the root of the ai_adaptation_agent module if it's structured as a package.
# Assuming ai_adaptation_agent is a sibling directory to ai_services_api within the backend directory.
# The services themselves are in ai_adaptation_agent/src/

# Correct path adjustment assuming backend/ is the common root for ai_services_api and ai_adaptation_agent
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../ai_adaptation_agent/src")))
# A simpler way if both ai_services_api and ai_adaptation_agent are installable packages or PYTHONPATH is set:
# For direct script execution, relative paths can be tricky. Let's assume a structure where
# ai_marketing_system-new/backend/ is on PYTHONPATH or we adjust path carefully.

# Let's make the path adjustment more explicit and robust
# Current file: /home/ubuntu/ai-marketing-system-new/backend/ai_services_api/src/main.py
# Target for import: /home/ubuntu/ai-marketing-system-new/backend/ai_adaptation_agent/src/
AI_ADAPTATION_AGENT_SRC_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), # .../ai_services_api/src
        "..",                     # .../ai_services_api/
        "..",                     # .../backend/
        "ai_adaptation_agent",    # .../backend/ai_adaptation_agent/
        "src"                     # .../backend/ai_adaptation_agent/src
    )
)
if AI_ADAPTATION_AGENT_SRC_PATH not in sys.path:
    sys.path.insert(0, AI_ADAPTATION_AGENT_SRC_PATH)

# Load environment variables from .env file
# Assuming .env file is in the root of ai_services_api directory
DOTENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(DOTENV_PATH):
    load_dotenv(DOTENV_PATH)
else:
    # Fallback if .env is in the src directory (less common for Flask apps)
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Import routes after path adjustment
from .routes.blueprint_routes import blueprint_bp
from .routes.customer_matcher_routes import customer_matcher_bp

app = Flask(__name__)

# Configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your-default-jwt-secret-key") # Should be same as auth_service if validating its tokens
app.config["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Database configuration (passed to services)
app.config["DB_USER"] = os.getenv("DB_USER", "postgres")
app.config["DB_PASSWORD"] = os.getenv("DB_PASSWORD", "password")
app.config["DB_HOST"] = os.getenv("DB_HOST", "localhost") # Or your Cloud SQL proxy address
app.config["DB_PORT"] = os.getenv("DB_PORT", "5432")
app.config["DB_NAME"] = os.getenv("DB_NAME", "ai_marketing_db") # Ensure this is the correct DB name

# Enable CORS for all routes and origins (adjust for production)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register Blueprints
app.register_blueprint(blueprint_bp, url_prefix="/api/blueprint")
app.register_blueprint(customer_matcher_bp, url_prefix="/api/matcher")

@app.route("/api/health", methods=["GET"])
def health_check():
    return {"status": "healthy", "service": "AI Services API"}, 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5002)) # Different port from auth_service
    app.run(host="0.0.0.0", port=port, debug=True) # Debug should be False in production

