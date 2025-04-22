from flask import Flask, render_template, request, jsonify, Blueprint
from tic_tac_toe_backend.GameEngine import create_game, apply_player_move, get_ai_move, games
from datetime import datetime
from tic_tac_toe_backend.tic_tac_toe_db import TicTacToeDatabase

tic_tac_toe_bp = Blueprint('tic_tac_toe_bp', __name__, url_prefix='/tic_tac_toe')

db = TicTacToeDatabase()

@tic_tac_toe_bp.route('/start', methods=['POST'])
def start_game():
    data = request.json
    session_id = data.get("session_id")
    player_name = data.get("player_name")  # Ensure player_name is included

    algorithm = data.get("algorithm", "minimax")  # Default to minimax if not provided
    
    if not session_id or not player_name:
        return jsonify({"error": "Session ID and player name are required!"}), 400
    
    # Create a new game in the database (in-memory here)
    games[session_id] = create_game()  # Initialize the game state in memory

    db.create_game_session(session_id, player_name=player_name, algorithm=algorithm)
    
    # Optionally, you could store the player_name and session_id in the database here
    return jsonify({"message": "Game started!"})

@tic_tac_toe_bp.route('/move', methods=['POST'])
def make_move():
    data = request.json
    session_id = data.get("session_id")
    x, y = data.get("move", (None, None))  # Default to None if no move is provided
    algorithm = data.get("algorithm", "minimax")
    player_name = data.get("playerName")  # Ensure player_name is included
    
    # Validate if session exists
    game = games.get(session_id)
    if not game:
        return jsonify({"error": "Session not found"}), 400
    
    if x is None or y is None:
        return jsonify({"error": "Move coordinates are required!"}), 400
    
    try:
        # Apply the player's move
        game = apply_player_move(game, (x, y))
        print(f"Player move: ({x}, {y})")
        db.log_user_move(session_id, name=player_name, move=[x, y])  # Log the user's move
        if game.is_terminal():
            return jsonify({"board": game.board_state.tolist(), "winner": game.winner})

        # AI's move logic
        start_time = datetime.now()
        move, game = get_ai_move(game, algorithm)
        end_time = datetime.now()

        # Calculate the AI move duration in milliseconds
        move_duration_ms = (end_time - start_time).total_seconds() * 1000

        print(f"AI move: {move}, Duration: {move_duration_ms} ms")
        games[session_id] = game  # Update the game state
        
        # Log an AI move with duration
        db.log_ai_move(session_id, algorithm, move, move_duration_ms)

        

        return jsonify({
            "board": game.board_state.tolist(),
            "ai_move": move,
            "winner": game.winner if game.is_terminal() else None
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    
@tic_tac_toe_bp.route('/reset', methods=['POST'])
def reset_game():
    data = request.json
    session_id = data.get("session_id")

    if not session_id or session_id not in games:
        return jsonify({"error": "Session not found"}), 400

    # Reset the game state in memory
    games[session_id] = create_game()  # Recreate the game object for a new game session
    game = games.get(session_id)
    db.end_game_session(session_id, winner=game.winner)  # End the game session in the database
    return jsonify({"message": "Game has been reset and a new session started!"})


@tic_tac_toe_bp.route("/view-database")
def view_database():
    correct_responses = db.get_all_correct_responses()
    ai_moves = db.get_ai_move_logs()
    sessions = db.get_all_game_sessions()
    user_moves = db.get_user_move_logs()

    return render_template("view_database.html", 
                           responses=correct_responses, 
                           moves=ai_moves,
                           sessions=sessions, 
                           user_moves=user_moves)
