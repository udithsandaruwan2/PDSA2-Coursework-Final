import logging
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import toh_routes
from tsp_routes import tsp_bp  # Import the TSP blueprint

# Configure centralized logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the Flask app with your directory structure
app = Flask(__name__, 
            static_folder='../frontend/static',  # Path to your static folder
            template_folder='../frontend')       # Path to your templates folder

# Enable CORS for API routes (allow requests from any origin for testing)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register both blueprints
app.register_blueprint(toh_routes.bp)
app.register_blueprint(tsp_bp)

# Serve home.html as the main entry point
@app.route('/')
def home():
    return send_from_directory('../frontend', 'home.html')

# Keep the original route for Tower of Hanoi
@app.route('/tower_of_hanoi.html')
def tower_of_hanoi():
    return render_template('tower_of_hanoi.html')

# Serve other static files from the frontend directory
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('../frontend', filename)

# Main entry point for the Flask app
if __name__ == '__main__':
    logger.info("Starting the Flask application...")
    app.run(debug=True, use_reloader=False)