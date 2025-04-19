from flask import Blueprint, jsonify, request
import random
import sqlite3
import os
from .KnightTour import validate_player_path, solve_knights_tour, warnsdorff_tour, validate_warnsdorff_tour

knight_blueprint = Blueprint('knight', __name__, url_prefix='/api')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, '../../database/knightstour.db'))

@knight_blueprint.route('/start', methods=['GET'])
def start_game():
    start_x = random.randint(0, 7)
    start_y = random.randint(0, 7)
    return jsonify({"start": {"x": start_x, "y": start_y}})

"""@knight_blueprint.route('/validate', methods=['POST'])
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
        return jsonify({"valid": False, "message": str(e)}), 500"""


"""@knight_blueprint.route('/validate', methods=['POST'])
def validate_path():
    data = request.get_json()
    path = data.get('path')

    if not path:
        return jsonify({"valid": False, "message": "Path not provided"}), 400

    try:
        # Convert path to tuples
        path = [(int(p[0]), int(p[1])) for p in path]

        # Validate with both approaches
        valid_bt, msg_bt = validate_player_path(path)
        valid_warn, msg_warn = validate_warnsdorff_tour(path)

        # If any of the algorithms validate the path as a full correct tour
        if valid_bt or valid_warn:
            return jsonify({
                "valid": True,
                "message": "Correct Knight's Tour! 🎉 Congrats, you won the game. Saving winner to Database."
            })

        # If neither validates the tour
        return jsonify({
            "valid": False,
            "message": msg_warn if msg_warn else msg_bt
        })

    except Exception as e:
        return jsonify({"valid": False, "message": str(e)}), 500"""

@knight_blueprint.route('/validate_backtracking', methods=['POST'])
def validate_backtracking_path():
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


@knight_blueprint.route('/validate_warnsdorff', methods=['POST'])
def validate_warnsdorff_path():
    data = request.get_json()
    path = data.get('path')

    if not path:
        return jsonify({"valid": False, "message": "Path not provided"}), 400

    try:
        path = [(int(p[0]), int(p[1])) for p in path]
        valid, message = validate_warnsdorff_tour(path)

        return jsonify({"valid": valid, "message": message})
    except Exception as e:
        return jsonify({"valid": False, "message": str(e)}), 500



# 🔁 Backtrack Visualization
@knight_blueprint.route('/solve', methods=['POST'])
def solve_from_start_position():
    data = request.get_json()
    print("Received solve request with data:", data)

    path = data.get('path')

    if not path or len(path) == 0 or not isinstance(path[0], list) or len(path[0]) != 2:
        print("Invalid or missing start position")
        return jsonify({"success": False, "message": "Invalid or missing start position"}), 400

    try:
        start_x, start_y = int(path[0][0]), int(path[0][1])
    except (ValueError, TypeError):
        print("Start position format error")
        return jsonify({"success": False, "message": "Start position must contain integers"}), 400

    solution = solve_knights_tour(start_x, start_y)
    print("Backtracking solution found:", solution)

    if solution:
        return jsonify({"success": True, "path": solution})
    else:
        return jsonify({"success": False, "message": "No solution possible from this position"})


### Submit winner to db
@knight_blueprint.route('/submit_winner', methods=['POST'])
def submit_winner():
    data = request.get_json()
    name = data.get('name')
    start_x = data.get('start_x')
    start_y = data.get('start_y')
    path = data.get('path')
    currentTimestamp = data.get('timestamp')

    # 🔍 Debug output
    print("🔍 Received data:")
    print("Name:", name)
    print("Start X:", start_x)
    print("Start Y:", start_y)
    print("Path:", path)
    print("Timestamp:", currentTimestamp)

    if not all([name, isinstance(start_x, int), isinstance(start_y, int)]):
        return jsonify({"error": "Missing or invalid data."}), 400

    if path:
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('''
                INSERT INTO winners (name, start_x, start_y, path, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, start_x, start_y, str(path), currentTimestamp))
            conn.commit()
            conn.close()
            return jsonify({"message": "Winner saved successfully!"}), 200
        except Exception as e:
            print("❌ Database error:", str(e))  # Print actual DB error!
            return jsonify({"error": f"Database error: {str(e)}"}), 500
    else:
        return jsonify({"error": "Could not solve Knight's Tour from given start position."}), 400


    # 🔁 Warndoff's Rule Visualization
@knight_blueprint.route('/warnsdorff', methods=['POST'])
def solve_from_start_position_warnsdoff():
    data = request.get_json()
    print("Received solve request with data:", data)

    path = data.get('path')

    if not path or len(path) == 0 or not isinstance(path[0], list) or len(path[0]) != 2:
        print("Invalid or missing start position")
        return jsonify({"success": False, "message": "Invalid or missing start position"}), 400

    try:
        start_x, start_y = int(path[0][0]), int(path[0][1])
    except (ValueError, TypeError):
        print("Start position format error")
        return jsonify({"success": False, "message": "Start position must contain integers"}), 400

    solution = warnsdorff_tour(start_x, start_y)
    print("Warndoff'Rule solution found:", solution)

    if solution:
        return jsonify({"success": True, "path": solution})
    else:
        return jsonify({"success": False, "message": "No solution possible from this position"})