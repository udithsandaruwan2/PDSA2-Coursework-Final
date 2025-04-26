from tic_tac_toe_backend.GameState import GameState
import numpy as np

def evaluate_heuristic(game_state: GameState):
    board = game_state.board_state
    size = game_state.size
    score = 0
    lines = []

    # Rows and columns
    for i in range(size):
        lines.append(board[i, :])       # Row
        lines.append(board[:, i])       # Column

    # Diagonals (main and anti)
    for i in range(size - 2):
        for j in range(size - 2):
            # Main diag
            main_diag = np.array([board[i + k, j + k] for k in range(3)])
            lines.append(main_diag)
            # Anti diag
            anti_diag = np.array([board[i + k, j + 2 - k] for k in range(3)])
            lines.append(anti_diag)

    for line in lines:
        zeros = np.count_nonzero(line == 0)
        if zeros < 1:
            continue
        line_sum = np.sum(line)
        # Encourage O (1), discourage X (-1)
        if line_sum > 0:
            score += line_sum ** 2
        elif line_sum < 0:
            score += line_sum ** 2
    return score


def minimax(game_state: GameState, depth: int, maximizingPlayer: bool, alpha=float('-inf'), beta=float('inf')):
    if depth == 0 or game_state.is_terminal():
        if game_state.is_terminal():
            return game_state.score(), None
        else:
            return evaluate_heuristic(game_state), None

    best_movement = None

    if maximizingPlayer:
        value = float('-inf')
        for move in game_state.get_possible_moves():
            child = game_state.get_new_state(move)
            tmp = minimax(child, depth - 1, False, alpha, beta)[0]
            if tmp > value:
                value = tmp
                best_movement = move
            alpha = max(alpha, value)
            if alpha >= beta:
                break
    else:
        value = float('inf')
        for move in game_state.get_possible_moves():
            child = game_state.get_new_state(move)
            tmp = minimax(child, depth - 1, True, alpha, beta)[0]
            if tmp < value:
                value = tmp
                best_movement = move
            beta = min(beta, value)
            if alpha >= beta:
                break

    return value, best_movement
