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
        ###if player_name:
            ###save_winner_to_db(player_name)
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
def is_tour_possible_from(x, y, visited, step):
    if step == 64:
        return True

    for i in range(8):
        next_x = x + move_x[i]
        next_y = y + move_y[i]
        if is_unvisited(next_x, next_y, visited):
            visited[next_x][next_y] = step
            if is_tour_possible_from(next_x, next_y, visited, step + 1):
                return True
            visited[next_x][next_y] = -1  # Backtrack

    return False

# 💾 Save winner info to local DB
"""def save_winner_to_db(name):
    try:
        conn = sqlite3.connect('database/winners.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS winners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                time TEXT NOT NULL
            )
        ''')
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO winners (name, time) VALUES (?, ?)", (name, current_time))
        conn.commit()
        conn.close()
        print(f"Winner {name} saved to DB successfully.")
    except Exception as e:
        print(f"Error saving winner to DB: {e}")"""


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

