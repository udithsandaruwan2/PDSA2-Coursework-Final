import unittest
import numpy as np
from unittest.mock import patch, MagicMock
from tic_tac_toe_backend.GameEngine import (
    create_game, apply_player_move, get_ai_move
)
from tic_tac_toe_backend.GameState import GameState

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def print_result(test_name, success):
    if success:
        print(f"{GREEN}✅ {test_name} PASSED{RESET}")
    else:
        print(f"{RED}❌ {test_name} FAILED{RESET}")

class TestGameEngine(unittest.TestCase):

    def runTestWithPrint(self, func):
        try:
            func()
            print_result(func.__name__, True)
        except Exception as e:
            print_result(func.__name__, False)
            raise

    def test_create_game_initial_state(self):
        game = create_game()
        self.assertIsInstance(game, GameState)
        self.assertEqual(game.board_state.shape, (5, 5))
        self.assertTrue(game.turn_O)
        self.assertTrue(np.array_equal(game.board_state, np.zeros((5, 5))))

    def test_apply_player_move_valid(self):
        game = create_game()
        new_game = apply_player_move(game, (0, 0))
        self.assertNotEqual(id(game), id(new_game))
        self.assertEqual(new_game.board_state[0, 0], 1)

    def test_apply_player_move_on_terminal_game_raises(self):
        game = create_game()
        game.is_terminal = MagicMock(return_value=True)
        with self.assertRaises(ValueError):
            apply_player_move(game, (0, 0))

    def test_apply_player_move_on_occupied_cell_raises(self):
        game = create_game()
        game.board_state[0, 0] = 1
        with self.assertRaises(ValueError):
            apply_player_move(game, (0, 0))

    @patch("tic_tac_toe_backend.GameEngine.minimax")
    def test_get_ai_move_minimax_success(self, mock_minimax):
        game = create_game()
        mock_minimax.return_value = (1, (1, 1))
        move, new_game = get_ai_move(game, algorithm="minimax")
        self.assertEqual(move, (1, 1))

    @patch("tic_tac_toe_backend.GameEngine.mcts")
    def test_get_ai_move_mcts_success(self, mock_mcts):
        game = create_game()
        mock_mcts.return_value = (1, (2, 2))
        move, new_game = get_ai_move(game, algorithm="mcts")
        self.assertEqual(move, (2, 2))

    def test_get_ai_move_on_terminal_game_raises(self):
        game = create_game()
        game.is_terminal = MagicMock(return_value=True)
        with self.assertRaises(ValueError):
            get_ai_move(game, "minimax")

    def test_get_ai_move_invalid_algorithm_raises(self):
        game = create_game()
        with self.assertRaises(ValueError):
            get_ai_move(game, algorithm="invalid_algo")

    @patch("tic_tac_toe_backend.GameEngine.minimax")
    def test_get_ai_move_returns_none_move_raises(self, mock_minimax):
        game = create_game()
        mock_minimax.return_value = (0, None)
        with self.assertRaises(ValueError):
            get_ai_move(game, algorithm="minimax")


if __name__ == "__main__":
    test_case = TestGameEngine()
    methods = [method for method in dir(test_case) if method.startswith("test_")]
    
    for method in methods:
        test_case.runTestWithPrint(getattr(test_case, method))
