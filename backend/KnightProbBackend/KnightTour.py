# backend/KnightProbBackend/KnightTour.py
import random

N = 8

# All possible knight moves
move_x = [2, 1, -1, -2, -2, -1, 1, 2]
move_y = [1, 2, 2, 1, -1, -2, -2, -1]

# Shared state (resets when a new game starts)
board = [[-1 for _ in range(N)] for _ in range(N)]
path = []
current_move = 0

def is_valid(x, y, board):
    return 0 <= x < N and 0 <= y < N and board[x][y] == -1

# ----------------------------
# Start the Knight's Tour Game
# ----------------------------
def start_knight_tour(start_x, start_y):
    global board, path, current_move
    board = [[-1 for _ in range(N)] for _ in range(N)]
    path = [(start_x, start_y)]
    board[start_x][start_y] = 0
    current_move = 1
    return {"status": "started", "position": (start_x, start_y)}

# ----------------------------
# Handle Manual Move
# ----------------------------
def user_move(next_x, next_y):
    global board, path, current_move
    if not path:
        return {"status": "error", "reason": "Game not started yet"}

    last_x, last_y = path[-1]
    dx = abs(next_x - last_x)
    dy = abs(next_y - last_y)

    # Check if move is a valid knight move and unvisited
    valid_moves = list(zip(move_x, move_y))
    if is_valid(next_x, next_y, board) and (dx, dy) in valid_moves:
        board[next_x][next_y] = current_move
        path.append((next_x, next_y))
        current_move += 1

        # Check if completed
        if current_move == N * N:
            return {"status": "completed", "path": path}
        
        return {"status": "moved", "path": path, "move_count": current_move}
    else:
        return {"status": "invalid", "reason": "Illegal move or already visited", "last_position": (last_x, last_y)}


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

