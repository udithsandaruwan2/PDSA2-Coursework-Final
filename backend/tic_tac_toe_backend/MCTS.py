import random
import time
from tic_tac_toe_backend.GameState import GameState

def simulate_random_game(game_state: GameState):
    current_state = game_state
    while not current_state.is_terminal():
        possible_moves = current_state.get_possible_moves()
        move = random.choice(possible_moves)
        current_state = current_state.get_new_state(move)
    return current_state.winner

def mcts(game_state: GameState, simulations=500):
    moves = game_state.get_possible_moves()

    if len(moves) == 1:
        return 1.0, moves[0]

    wins = {move: 0 for move in moves}
    plays = {move: 0 for move in moves}

    for _ in range(simulations):
        move = random.choice(moves)
        new_state = game_state.get_new_state(move)
        result = simulate_random_game(new_state)

        plays[move] += 1
        if (result == "O" and game_state.turn_O) or (result == "X" and not game_state.turn_O):
            wins[move] += 1

    best_move = max(moves, key=lambda m: wins[m] / plays[m] if plays[m] > 0 else 0)
    win_rate = wins[best_move] / plays[best_move] if plays[best_move] > 0 else 0

    return win_rate, best_move
