import logging
from flask import Flask, send_from_directory
from flask_cors import CORS
from tsp_routes import tsp_bp  # Import the blueprint

# Configure centralized logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the Flask app
app = Flask(__name__)

# Enable CORS for API routes (allow requests from any origin for testing)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register the blueprint for TSP routes
app.register_blueprint(tsp_bp)

# Serve home.html as the main entry point
@app.route('/')
def home():
    return send_from_directory('../frontend', 'home.html')

# Serve other static files from the frontend directory
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('../frontend', filename)

# Main entry point for the Flask app
if __name__ == '__main__':
    logger.info("Starting the Flask application...")
    app.run(debug=True, use_reloader=False)
