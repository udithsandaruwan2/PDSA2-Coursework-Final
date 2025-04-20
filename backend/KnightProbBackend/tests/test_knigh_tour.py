import unittest
from KnightProbBackend.KnightTour import (
    is_knight_move,
    is_unvisited,
    validate_player_path,
    solve_knights_tour,
    validate_warnsdorff_tour,
    warnsdorff_tour
)


class TestKnightTour(unittest.TestCase):

    def test_is_knight_move(self):
        self.assertTrue(is_knight_move((0, 0), (1, 2)))
        self.assertTrue(is_knight_move((3, 3), (5, 4)))
        self.assertFalse(is_knight_move((0, 0), (0, 1)))

    def test_is_unvisited(self):
        visited = [[-1 for _ in range(8)] for _ in range(8)]
        visited[0][0] = 0
        self.assertFalse(is_unvisited(0, 0, visited))
        self.assertTrue(is_unvisited(1, 2, visited))
        self.assertFalse(is_unvisited(-1, 0, visited))  # out of bounds

    def test_validate_player_path_valid(self):
        path = [(0, 0), (1, 2), (2, 0)]
        valid, message = validate_player_path(path)
        self.assertFalse(valid)  # path is not 64 steps
        self.assertIn("Incomplete Tour", message)

    def test_validate_player_path_invalid_move(self):
        path = [(0, 0), (0, 1)]  # Not a knight move
        valid, message = validate_player_path(path)
        self.assertFalse(valid)
        self.assertIn("Invalid knight move", message)

    def test_solve_knights_tour(self):
        path = solve_knights_tour(0, 0)
        self.assertIsInstance(path, list)
        if path:  # path can be None if timeout
            self.assertEqual(len(path), 64)

    def test_warnsdorff_tour(self):
        path = warnsdorff_tour(0, 0)
        self.assertIsInstance(path, list)
        self.assertEqual(len(path), 64)

    def test_validate_warnsdorff_tour(self):
        full_path = warnsdorff_tour(0, 0)
        valid, message = validate_warnsdorff_tour(full_path)
        self.assertTrue(valid)
        self.assertIn("Tour already completed", message)


if __name__ == '__main__':
    unittest.main()
