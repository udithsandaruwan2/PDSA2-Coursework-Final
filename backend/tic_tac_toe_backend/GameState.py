import numpy as np

class GameState:

    def __init__(self, board_state, turn_O, win_length=5):
        self.board_state = board_state
        self.turn_O = turn_O
        self.winner = ""
        self.size = board_state.shape[0]
        self.win_length = win_length

    def is_terminal(self):
        # Check all directions for win_length in a row
        for i in range(self.size):
            for j in range(self.size - self.win_length + 1):
                # Check rows
                row = self.board_state[i, j:j+self.win_length]
                if np.all(row == 1):
                    self.winner = "O"
                    return True
                elif np.all(row == -1):
                    self.winner = "X"
                    return True

                # Check columns
                col = self.board_state[j:j+self.win_length, i]
                if np.all(col == 1):
                    self.winner = "O"
                    return True
                elif np.all(col == -1):
                    self.winner = "X"
                    return True

        # Check diagonals
        for i in range(self.size - self.win_length + 1):
            for j in range(self.size - self.win_length + 1):
                # Main diagonal
                main_diag = [self.board_state[i+k, j+k] for k in range(self.win_length)]
                if all(val == 1 for val in main_diag):
                    self.winner = "O"
                    return True
                elif all(val == -1 for val in main_diag):
                    self.winner = "X"
                    return True

                # Anti-diagonal
                anti_diag = [self.board_state[i+k, j+self.win_length-1-k] for k in range(self.win_length)]
                if all(val == 1 for val in anti_diag):
                    self.winner = "O"
                    return True
                elif all(val == -1 for val in anti_diag):
                    self.winner = "X"
                    return True

        # Check draw
        if not np.any(self.board_state == 0):
            self.winner = "Draw"
            return True

        self.winner = ""
        return False

    def score(self):
        # Similar to is_terminal but returns score
        for i in range(self.size):
            for j in range(self.size - self.win_length + 1):
                row = self.board_state[i, j:j+self.win_length]
                col = self.board_state[j:j+self.win_length, i]
                if np.all(row == 1) or np.all(col == 1):
                    return 1
                elif np.all(row == -1) or np.all(col == -1):
                    return -1

        for i in range(self.size - self.win_length + 1):
            for j in range(self.size - self.win_length + 1):
                main_diag = [self.board_state[i+k, j+k] for k in range(self.win_length)]
                anti_diag = [self.board_state[i+k, j+self.win_length-1-k] for k in range(self.win_length)]
                if all(val == 1 for val in main_diag) or all(val == 1 for val in anti_diag):
                    return 1
                elif all(val == -1 for val in main_diag) or all(val == -1 for val in anti_diag):
                    return -1

        return 0  # draw or ongoing

    def get_possible_moves(self):
        return [(x, y) for x in range(self.size) for y in range(self.size) if self.board_state[x, y] == 0]

    def get_new_state(self, move):
        new_board = self.board_state.copy()
        x, y = move
        new_board[x, y] = 1 if self.turn_O else -1
        return GameState(new_board, not self.turn_O, self.win_length)
