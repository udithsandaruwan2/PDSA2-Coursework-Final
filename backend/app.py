from flask import Flask, send_from_directory, render_template
from flask_cors import CORS
from tsp_routes import tsp_bp  # Import the blueprint

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the Flask app
app = Flask(__name__)

# Enable CORS for API routes (allow requests from any origin for testing)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register the blueprint for TSP routes
app.register_blueprint(tsp_bp)

@app.route('/')
def index():
    logger.info("Serving index page")
    return render_template('tower_of_hanoi.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('../frontend/tower_of_hanoi_frontend/static', path)

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Unhandled error: {str(error)}")
    return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    try:
        toh_db.init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    logger.info("Starting Flask application")
    app.run(debug=True, use_reloader=False)