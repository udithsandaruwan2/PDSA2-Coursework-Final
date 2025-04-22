import numpy as np
from tic_tac_toe_backend.GameState import GameState
from tic_tac_toe_backend.MinMax import minimax
from tic_tac_toe_backend.MCTS import mcts

games = {}

def create_game():
    board = np.zeros((5, 5), dtype=int)
    return GameState(board, turn_O=True)

def apply_player_move(game, move):
    if game.is_terminal():
        raise ValueError("Game is already over.")
    if game.board_state[move] != 0:
        raise ValueError("Invalid move.")
    return game.get_new_state(move)

def get_ai_move(game, algorithm="minimax"):
    if game.is_terminal():
        raise ValueError("Game is already over.")
    if algorithm == "minimax":
        _, move = minimax(game, depth=4, maximizingPlayer=not game.turn_O)
    elif algorithm == "mcts":
        _, move = mcts(game, simulations=1000)
    else:
        raise ValueError("Unknown algorithm.")
    if move is None:
        raise ValueError("AI could not determine a move.")
    return move, game.get_new_state(move)
