import sqlite3
from datetime import datetime
import time


#  Checks if the position has not been visited yet
def is_unvisited(x, y, visited):
    return 0 <= x < 8 and 0 <= y < 8 and visited[x][y] == -1

# ♞ Validates if a move between two positions is a knight move
def is_knight_move(p1, p2):
    dx = abs(p1[0] - p2[0])
    dy = abs(p1[1] - p2[1])
    return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)

#  Validates the entire path taken by the player
def validate_player_path(path, player_name=None):
    if len(path) < 2 or not (1 <= len(path) <= 64):
        return False, "Invalid path length"

    visited = [[-1 for _ in range(8)] for _ in range(8)]
    for i, (x, y) in enumerate(path):
        if not (0 <= x < 8 and 0 <= y < 8):
            return False, f"Invalid position at index {i}"
        if visited[x][y] != -1:
            return False, f"Repeated position at index {i}"
        visited[x][y] = i

    for i in range(1, len(path)):
        if not is_knight_move(path[i-1], path[i]):
            return False, f"Invalid knight move at index {i}"

    if len(path) == 64:
        return True, "Correct Knight's Tour! Congrats You won the game. Saving winner to Database"

    #  Check if a tour is still possible from last move using backtracking
    last_x, last_y = path[-1]
    if is_tour_possible_from(last_x, last_y, visited, len(path)):
        return False, "Incomplete Tour. But you are close! A solution is still possible from here."
    else:
        return False, "Incomplete Tour. YOU LOSE. Try again."


#  Backtracking move patterns
move_x = [2, 1, -1, -2, -2, -1, 1, 2]
move_y = [1, 2, 2, 1, -1, -2, -2, -1]

# 🔄 Recursive tour possibility check using backtracking
def is_tour_possible_from(x, y, visited, step, timeout=60, start_time=None):
    if start_time is None:
        start_time = time.time()

    if time.time() - start_time > timeout:
        return False  # Timeout reached

    if step == 64:
        return True

    for i in range(8):
        next_x = x + move_x[i]
        next_y = y + move_y[i]
        if is_unvisited(next_x, next_y, visited):
            visited[next_x][next_y] = step
            if is_tour_possible_from(next_x, next_y, visited, step + 1, timeout, start_time):
                return True
            visited[next_x][next_y] = -1  # Backtrack

    return False


## Whole backtracking algorithm to visualize the knight tour problem using the user's current starting point
# Board size
N = 8

def is_valid(x, y, board):
    """Check if the knight move is inside the board and unvisited"""
    return 0 <= x < N and 0 <= y < N and board[x][y] == -1

import time

def solve_knights_tour(start_x, start_y, time_limit=60):
    print(start_x)
    print(start_y)
    start_time = time.time()
    board = [[-1 for _ in range(N)] for _ in range(N)]
    board[start_x][start_y] = 0
    path = [(start_x, start_y)]

    def backtrack(x, y, move_count):
        if time.time() - start_time > time_limit:
            return False  # Timeout

        if move_count == N * N:
            return True

        for i in range(8):
            next_x = x + move_x[i]
            next_y = y + move_y[i]

            if is_valid(next_x, next_y, board):
                board[next_x][next_y] = move_count
                path.append((next_x, next_y))

                if backtrack(next_x, next_y, move_count + 1):
                    return True

                board[next_x][next_y] = -1
                path.pop()

        return False

    if backtrack(start_x, start_y, 1):
        return path
    else:
        return None


# -----------------------
# Warnsdorff's Heuristic
# -----------------------

#Validation using Warnsdoff's Rule - Customized version
def validate_warnsdorff_tour(path):
    if not path or len(path) > 64:
        return False, "Invalid path for Warnsdorff validation"

    visited = [[-1 for _ in range(8)] for _ in range(8)]
    for i, (x, y) in enumerate(path):
        if not (0 <= x < 8 and 0 <= y < 8):
            return False, f"Invalid coordinate in path at index {i}"
        visited[x][y] = i

    # ✅ New: Check if each move is a valid knight move
    for i in range(1, len(path)):
        x1, y1 = path[i - 1]
        x2, y2 = path[i]
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        if not ((dx == 2 and dy == 1) or (dx == 1 and dy == 2)):
            return False, f"Invalid knight move from {path[i - 1]} to {path[i]}"

    step = len(path)

    if step == 64:
        return True, "Tour already completed (64 steps) — no need to validate further."

    last_x, last_y = path[-1]

    if is_tour_possible_warnsdorff(last_x, last_y, visited, step):
        return False, "Incomplete Tour. But you are close! A solution is still possible from here."
    else:
        return False, "Warnsdorff says: No complete tour is possible from your current position."


    # Knight's move offsets
move_x = [2, 1, -1, -2, -2, -1, 1, 2]
move_y = [1, 2, 2, 1, -1, -2, -2, -1]

# Checks if a position is within bounds and unvisited
def is_unvisited(x, y, visited):
    return 0 <= x < 8 and 0 <= y < 8 and visited[x][y] == -1

# Counts the number of valid onward moves from a position
def count_onward_moves(x, y, visited):
    count = 0
    for i in range(8):
        nx, ny = x + move_x[i], y + move_y[i]
        if is_unvisited(nx, ny, visited):
            count += 1
    return count

# Warnsdorff's Rule implementation (recursive)
def is_tour_possible_warnsdorff(x, y, visited, step):
    
    # Generate all possible next moves with onward move counts
    candidates = []
    for i in range(8):
        nx, ny = x + move_x[i], y + move_y[i]
        if is_unvisited(nx, ny, visited):
            onward = count_onward_moves(nx, ny, visited)
            candidates.append(((nx, ny), onward))

    # Sort moves by Warnsdorff's heuristic (least onward moves first)
    candidates.sort(key=lambda item: item[1])

    for (nx, ny), _ in candidates:
        visited[nx][ny] = step
        if is_tour_possible_warnsdorff(nx, ny, visited, step + 1):
            return True
        visited[nx][ny] = -1  # backtrack

    return False



# Complete Warnsdorff’s Rule implementation to visualize the knight tour problem using the user's current starting point
def warnsdorff_tour(start_x, start_y, board_size=8):
    knight_moves = [
        (2, 1), (1, 2), (-1, 2), (-2, 1),
        (-2, -1), (-1, -2), (1, -2), (2, -1)
    ]

    board = [[-1 for _ in range(board_size)] for _ in range(board_size)]

    def is_valid(x, y):
        return 0 <= x < board_size and 0 <= y < board_size and board[x][y] == -1

    def count_onward_moves(x, y):
        count = 0
        for dx, dy in knight_moves:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny):
                count += 1
        return count

    board[start_x][start_y] = 0
    path = [(start_x, start_y)]

    for move_num in range(1, board_size * board_size):
        current_x, current_y = path[-1] # get the last element in the path
        min_deg = 9
        next_move = None

        for dx, dy in knight_moves:
            nx, ny = current_x + dx, current_y + dy
            if is_valid(nx, ny):
                deg = count_onward_moves(nx, ny)
                if deg < min_deg:
                    min_deg = deg
                    next_move = (nx, ny)

        if next_move is None:
            return None  # No further moves possible – fail

        nx, ny = next_move
        board[nx][ny] = move_num
        path.append((nx, ny))

    return path


