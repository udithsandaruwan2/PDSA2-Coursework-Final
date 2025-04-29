import pytest
import numpy as np
from tic_tac_toe_backend.GameState import GameState
from tic_tac_toe_backend.GameEngine import create_game, apply_player_move, get_ai_move, games
from tic_tac_toe_backend.MinMax import minimax, evaluate_heuristic
from tic_tac_toe_backend.MCTS import mcts, simulate_random_game
from tic_tac_toe_backend.tic_tac_toe_db import TicTacToeDatabase
from flask import Flask

# --- Tests for GameState ---
class TestGameState:
    def test_is_terminal_empty(self):
        state = GameState(np.zeros((5,5), dtype=int), turn_O=True)
        assert not state.is_terminal()
        assert state.winner == ""

    def test_is_terminal_row_win(self):
        board = np.zeros((5,5), dtype=int)
        board[2, :] = 1  # O wins on row
        state = GameState(board, turn_O=False)
        assert state.is_terminal()
        assert state.winner == "O"

    def test_is_terminal_col_win(self):
        board = np.zeros((5,5), dtype=int)
        board[:, 1] = -1  # X wins on column
        state = GameState(board, turn_O=True)
        assert state.is_terminal()
        assert state.winner == "X"

    def test_is_terminal_diagonal_win(self):
        board = np.zeros((5,5), dtype=int)
        for i in range(5): board[i, i] = 1
        state = GameState(board, turn_O=False)
        assert state.is_terminal()
        assert state.winner == "O"

    def test_is_terminal_draw(self):
        board = np.ones((5,5), dtype=int)
        board[0,0] = -1  # mix values but no winner
        state = GameState(board, turn_O=True)
        assert state.is_terminal()
        assert state.winner == "Draw"

    def test_score(self):
        board = np.zeros((5,5), dtype=int)
        board[0,0:5] = 1
        assert GameState(board, True).score() == 1
        board *= 0
        board[0:5,0] = -1
        assert GameState(board, False).score() == -1
        # no win
        board *= 0
        assert GameState(board, True).score() == 0

    def test_get_possible_moves(self):
        board = np.zeros((5,5), dtype=int)
        board[0,0] = 1
        state = GameState(board, True)
        moves = state.get_possible_moves()
        assert (0,0) not in moves
        assert len(moves) == 24

    def test_get_new_state_immutability(self):
        board = np.zeros((5,5), dtype=int)
        state = GameState(board, True)
        new_state = state.get_new_state((1,1))
        assert state.board_state[1,1] == 0
        assert new_state.board_state[1,1] == 1

# --- Tests for GameEngine ---
class TestGameEngine:
    def test_create_game(self):
        state = create_game()
        assert isinstance(state, GameState)
        assert np.all(state.board_state == 0)
        assert state.turn_O is True

    def test_apply_player_move_valid(self):
        state = create_game()
        new_state = apply_player_move(state, (0,0))
        assert new_state.board_state[0,0] == 1

    def test_apply_player_move_invalid_occupied(self):
        state = create_game()
        state = apply_player_move(state, (0,0))
        with pytest.raises(ValueError):
            apply_player_move(state, (0,0))

    def test_apply_player_move_after_terminal(self):
        board = np.ones((5,5), dtype=int)
        state = GameState(board, True)
        with pytest.raises(ValueError):
            apply_player_move(state, (4,4))

    def test_get_ai_move_unknown_algo(self):
        state = create_game()
        with pytest.raises(ValueError):
            get_ai_move(state, algorithm="unknown")

# --- Tests for Minimax and MCTS ---
class TestAIAlgorithms:
    def test_minimax_depth_zero(self):
        state = create_game()
        # empty board: heuristic score is zero
        val, move = minimax(state, depth=0, maximizingPlayer=True)
        assert isinstance(val, (int, float))
        assert move is None

    def test_evaluate_heuristic_nonzero(self):
        state = create_game()
        # create a 3-length line for heuristic
        board = np.zeros((5,5), dtype=int)
        board[0,0:3] = 1
        state = GameState(board, True)
        h = evaluate_heuristic(state)
        assert h > 0

    def test_mcts_single_move(self):
        # board with one empty cell
        board = np.ones((5,5), dtype=int)
        board[0,0] = 0
        state = GameState(board, True)
        win_rate, move = mcts(state, simulations=10)
        assert move == (0,0)
        assert 0.0 <= win_rate <= 1.0

    def test_simulate_random_game(self):
        state = create_game()
        winner = simulate_random_game(state)
        assert winner in ("O", "X", "Draw")

# --- Tests for Database Layer ---
class TestDatabase:
    @pytest.fixture(autouse=True)
    def db(self, tmp_path):
        # Use a temporary file for the database
        db_file = tmp_path / "test_ttt.db"
        db = TicTacToeDatabase(db_path=str(db_file))
        return db

    def test_empty_sessions(self, db):
        sessions = db.get_all_game_sessions()
        assert sessions == []

    def test_log_and_fetch_session(self, db):
        db.create_game_session("s1", "Alice", "minimax")
        sessions = db.get_all_game_sessions()
        assert len(sessions) == 1
        assert sessions[0][1] == "s1"
        assert sessions[0][2] == "Alice"

# --- Example: Running Flask Endpoint Tests ---
# To test Flask routes, you can create an app instance and register the blueprint:
#
#     app = Flask(__name__)
#     from tic_tac_toe_backend.your_flask_module import tic_tac_toe_bp
#     app.register_blueprint(tic_tac_toe_bp)
#     client = app.test_client()
#
# Then use `client.post('/tic_tac_toe/start', json={...})` to verify responses.
