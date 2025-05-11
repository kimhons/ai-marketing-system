import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import firebase_admin
from firebase_admin import credentials
from flask import Flask, send_from_directory
# from src.models.user import db # Commented out as we are using Firestore
from src.routes.user import user_bp
from src.routes.campaigns import campaign_bp # Import the new campaign blueprint

# Initialize Firebase Admin SDK
try:
    # Ensure the path to your service account key is correct
    # It's often better to use an environment variable for this path in production
    key_path = os.getenv("FIREBASE_ADMIN_SDK_KEY_PATH", "/home/ubuntu/upload/ai-marketing-system-459423-c2e3533e900d.json")
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)
    print("Firebase Admin SDK initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")
    # Handle initialization error appropriately, e.g., log and exit or use a fallback

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY", "a_very_strong_default_secret_key#$!@%") # Use environment variable for secret key

# Register Blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(campaign_bp, url_prefix='/api') # Register the campaign blueprint

# SQLAlchemy database setup (commented out as we are using Firestore)
# app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)
# with app.app_context():
#     db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            # This part is usually for serving the frontend app in production
            # If you are developing, the Next.js dev server handles frontend routes.
            # For a combined build, ensure your Next.js app builds to the static folder.
            return "index.html not found in static folder. Ensure your frontend is built and placed here or Flask is not meant to serve it.", 404


if __name__ == '__main__':
    # Use environment variables for host and port for flexibility
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_RUN_PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    app.run(host=host, port=port, debug=debug_mode)

