from flask import Flask, send_from_directory
from flask_cors import CORS
import os

# Import the blueprint from your KnightTourRoute
from KnightProbBackend.KnightTourRoute import knight_blueprint

app = Flask(__name__, static_folder='../frontend')
CORS(app)  # enable CORS for all routes

# Register the knight route blueprint
app.register_blueprint(knight_blueprint)  # ✅ ADD THIS LINE

# Serve the main home.html page
@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'home.html')

# Serve any static file (CSS, JS, images, etc.)
@app.route('/<path:filename>')
def serve_static(filename):
    file_path = os.path.join(app.static_folder, filename)
    if os.path.exists(file_path):
        return send_from_directory(app.static_folder, filename)
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)
