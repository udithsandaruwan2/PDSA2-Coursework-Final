from flask import Blueprint, jsonify, request
import random

knight_blueprint = Blueprint('knight', __name__, url_prefix='/api')

@knight_blueprint.route('/start', methods=['GET'])
def start_game():
    start_x = random.randint(0, 7)
    start_y = random.randint(0, 7)
    return jsonify({"start": {"x": start_x, "y": start_y}})

@knight_blueprint.route('/validate', methods=['POST'])
def validate_path():
    data = request.get_json()
    path = data.get('path', [])
    if not path or len(path) != 64:
        return jsonify({"valid": False, "message": "Path is incomplete or invalid."})

    visited = set()
    for i in range(1, len(path)):
        x1, y1 = path[i-1]
        x2, y2 = path[i]
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        if not ((dx == 2 and dy == 1) or (dx == 1 and dy == 2)) or (x2, y2) in visited:
            return jsonify({"valid": False, "message": f"Invalid move from ({x1},{y1}) to ({x2},{y2})."})
        visited.add((x1, y1))

    return jsonify({"valid": True})
