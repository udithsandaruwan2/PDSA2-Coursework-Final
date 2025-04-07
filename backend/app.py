from flask import Flask, send_from_directory
from flask_cors import CORS
from tsp_routes import tsp_bp  # Fix the import path

app = Flask(__name__)
CORS(app)  # Enable CORS

# Register the blueprint
app.register_blueprint(tsp_bp)

@app.route('/')
def home():
    return send_from_directory('../frontend', 'home.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('../frontend', filename)

if __name__ == '__main__':
    app.run(debug=True)

