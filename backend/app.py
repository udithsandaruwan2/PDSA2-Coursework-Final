import logging
from flask import Flask, send_from_directory, render_template
from flask_cors import CORS
from tsp_backend.tsp_routes import tsp_bp
from tic_tac_toe_backend.tic_tac_toe_routes import tic_tac_toe_bp
from KnightProbBackend.KnightTourRoute import knight_blueprint
from toh_backend import toh_routes
from toh_backend import toh_db
from eqp_backend.eqp_routes import eqp_bp # Import the EQP blueprint
import traceback

# Configure centralized logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the Flask app
app = Flask(__name__, static_folder='../frontend/tower_of_hanoi_frontend/static', template_folder='../frontend')
CORS(app, resources={
    r"/api/*": {"origins": "*"},
    r"/tic_tac_toe/*": {"origins": "*"},
    r"/knight/*": {"origins": "*"},
    r"/api/toh/*": {"origins": "*"},
    r"/api/eight_queens/*": {"origins": "*"}
})

# Serve home.html as the main entry point
@app.route('/')
def home():
    logger.info("Serving home page")
    return send_from_directory('../frontend', 'home.html')

# Tower of Hanoi index route
@app.route('/tower_of_hanoi')
def index():
    logger.info("Serving Tower of Hanoi index page")
    return render_template('tower_of_hanoi.html')

# Eight Queens Puzzle index route
@app.route('/eight_queens')
def eight_queens_index():
    logger.info("Serving Eight Queens Puzzle index page")
    return render_template('eight_queens.html')

# Serve static files
@app.route('/static/<path:path>')
def send_static(path):
    logger.info(f"Serving static file: {path}")
    return send_from_directory('../frontend/tower_of_hanoi_frontend/static', path)

# Serve other static files from the frontend directory
@app.route('/<path:filename>')
def serve_static(filename):
    logger.info(f"Serving file: {filename}")
    return send_from_directory('../frontend', filename)

# Register blueprints
app.register_blueprint(tsp_bp, url_prefix='/api')
app.register_blueprint(tic_tac_toe_bp, url_prefix='/tic_tac_toe')
app.register_blueprint(knight_blueprint, url_prefix='/knight')
app.register_blueprint(toh_routes.bp)
app.register_blueprint(eqp_bp, url_prefix='/api')  # Consistent prefix

# Error handlers
@app.errorhandler(404)
def not_found(error):
    logger.error(f"404 error: {error}")
    return {'error': 'Not found'}, 404

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Unhandled error: {str(error)}\n{traceback.format_exc()}")
    return {'error': 'Internal server error'}, 500

# Main entry point
if __name__ == '__main__':
    try:
        toh_db.init_db()
        logger.info("Tower of Hanoi database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Tower of Hanoi database: {str(e)}")
        raise

    try:
        from eqp_backend.eqp_db import EightQueensDB
        db = EightQueensDB()
        db.init_db()
        logger.info("Eight Queens database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Eight Queens database: {str(e)}")
        raise

    logger.info("Starting the Flask application...")
    app.run(debug=True, use_reloader=False)