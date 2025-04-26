import logging
from flask import Flask, send_from_directory
from flask_cors import CORS
from tsp_backend.tsp_routes import tsp_bp  # Import the blueprint
from tic_tac_toe_backend.tic_tac_toe_routes import tic_tac_toe_bp
from KnightProbBackend.KnightTourRoute import knight_blueprint

# Configure centralized logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the Flask app
app = Flask(__name__)
app = Flask(__name__, template_folder='../frontend')

app.register_blueprint(tsp_bp, url_prefix='/api')
app.register_blueprint(tic_tac_toe_bp, url_prefix='/tic_tac_toe')
app.register_blueprint(knight_blueprint, url_prefix='/knight')

CORS(app, resources={r"/api/*": {"origins": "*"}, r"/tic_tac_toe/*": {"origins": "*"}, r"/knight/*": {"origins": "*"}})

print(app.url_map)

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
