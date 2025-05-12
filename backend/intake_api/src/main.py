import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT' # Should be a strong, unique secret in production

# Database Configuration for PostgreSQL
DB_USERNAME = os.getenv('DB_USERNAME', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_db_password') # IMPORTANT: Use environment variables for passwords
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'ai_marketing_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) # Initialize db here

# Import models here to ensure they are registered with SQLAlchemy before create_all() is called
# It's crucial that the models are defined and imported before db.create_all() is run.
# Assuming your BusinessIntake model is in src.models.intake
from src.models.intake import BusinessIntake

# Import and register blueprints for your API routes
from src.routes.intake_routes import intake_bp
app.register_blueprint(intake_bp, url_prefix='/api/v1/intake')

# Create database tables if they don't exist
# This is suitable for development. For production, consider using migrations (e.g., Flask-Migrate).
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # This route is primarily for serving a static frontend if bundled with Flask.
    # Since we have a separate Next.js frontend, this might just return an API status.
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    elif os.path.exists(os.path.join(app.static_folder, 'index.html')):
        return send_from_directory(app.static_folder, 'index.html')
    else:
        return "Business Intake API is running. Frontend is served separately.", 200

if __name__ == '__main__':
    # Ensure this port is unique and doesn't conflict with the Next.js dev server (default 3000)
    app.run(host='0.0.0.0', port=5001, debug=True)

