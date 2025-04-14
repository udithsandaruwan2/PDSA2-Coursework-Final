from flask import Blueprint, jsonify, request
import random
from .KnightTour import validate_player_path


knight_blueprint = Blueprint('knight', __name__, url_prefix='/api')

@knight_blueprint.route('/start', methods=['GET'])
def start_game():
    start_x = random.randint(0, 7)
    start_y = random.randint(0, 7)
    return jsonify({"start": {"x": start_x, "y": start_y}})



@knight_blueprint.route('/validate', methods=['POST'])
def validate_path():
    data = request.get_json()
    path = data.get('path')

    if not path:
        return jsonify({"valid": False, "message": "Path not provided"}), 400

    try:
        path = [(int(p[0]), int(p[1])) for p in path]
        valid, message = validate_player_path(path)
        return jsonify({"valid": valid, "message": message})
    except Exception as e:
        return jsonify({"valid": False, "message": str(e)}), 500
