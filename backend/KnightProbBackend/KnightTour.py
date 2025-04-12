 # backend/KnightProbBackend/KnightTour.py
import random

N = 8

# All possible knight moves
move_x = [2, 1, -1, -2, -2, -1, 1, 2]
move_y = [1, 2, 2, 1, -1, -2, -2, -1]

def is_valid(x, y, board):
    return 0 <= x < N and 0 <= y < N and board[x][y] == -1

# -----------------------
# Backtracking Algorithm
# -----------------------
def solve_knight_tour_backtracking(start_x, start_y):
    board = [[-1 for _ in range(N)] for _ in range(N)]
    board[start_x][start_y] = 0
    path = [(start_x, start_y)]

    if not backtrack(board, start_x, start_y, 1, path):
        return None
    return path

def backtrack(board, curr_x, curr_y, move_i, path):
    if move_i == N * N:
        return True

    for k in range(8):
        next_x = curr_x + move_x[k]
        next_y = curr_y + move_y[k]
        if is_valid(next_x, next_y, board):
            board[next_x][next_y] = move_i
            path.append((next_x, next_y))

            if backtrack(board, next_x, next_y, move_i + 1, path):
                return True

            # Backtrack
            board[next_x][next_y] = -1
            path.pop()

    return False

# -----------------------
# Warnsdorff's Heuristic
# -----------------------
def count_onward_moves(x, y, board):
    count = 0
    for i in range(8):
        nx = x + move_x[i]
        ny = y + move_y[i]
        if is_valid(nx, ny, board):
            count += 1
    return count

def solve_knight_tour_warnsdorff(start_x, start_y):
    board = [[-1 for _ in range(N)] for _ in range(N)]
    board[start_x][start_y] = 0
    pos = 1
    curr_x, curr_y = start_x, start_y
    path = [(curr_x, curr_y)]

    while pos < N * N:
        min_deg = 9
        next_move = None

        for i in range(8):
            nx = curr_x + move_x[i]
            ny = curr_y + move_y[i]
            if is_valid(nx, ny, board):
                c = count_onward_moves(nx, ny, board)
                if c < min_deg:
                    min_deg = c
                    next_move = (nx, ny)

        if not next_move:
            return None

        curr_x, curr_y = next_move
        board[curr_x][curr_y] = pos
        path.append((curr_x, curr_y))
        pos += 1

    return path

