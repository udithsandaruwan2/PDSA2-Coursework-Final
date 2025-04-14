# KnightTour.py

def is_valid_move(x, y, board):
    return 0 <= x < 8 and 0 <= y < 8 and board[x][y] == -1

def is_knight_move(p1, p2):
    dx = abs(p1[0] - p2[0])
    dy = abs(p1[1] - p2[1])
    return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)

def validate_player_path(path):
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
        return True, "Correct Knight's Tour! Congrats You won the games. Saving winner to Database"
        ### Need to save winner name to the DB

    # Check if a solution is still possible from last move
    last_x, last_y = path[-1]
    if is_tour_possible_from(last_x, last_y, visited, len(path)):
        return False, "Incomplete Tour. But you are close! A solution is still possible from here."
    else:
        return False, "Incomplete Tour. YOU LOSE. Try again."


###Backtracking algorithm to check the whehter the player can continue from where he got stucked
move_x = [2, 1, -1, -2, -2, -1, 1, 2]
move_y = [1, 2, 2, 1, -1, -2, -2, -1]

def is_tour_possible_from(x, y, visited, step):
    if step == 64:
        return True  # Full tour completed

    for i in range(8):
        next_x = x + move_x[i]
        next_y = y + move_y[i]
        if is_valid_move(next_x, next_y, visited):
            visited[next_x][next_y] = step
            if is_tour_possible_from(next_x, next_y, visited, step + 1):
                return True
            visited[next_x][next_y] = -1  # Backtrack

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

