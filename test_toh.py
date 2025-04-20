import unittest
import requests
import json

class TestTowerOfHanoi(unittest.TestCase):
    BASE_URL = "http://localhost:5000"

    def test_new_game(self):
        response = requests.get(f"{self.BASE_URL}/api/toh/new-game?disks=5")
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['disk_count'], 5)
        self.assertIn('min_moves', data)
        self.assertIn('solutions', data)

    def test_move_counter(self):
        # Start a new game
        response = requests.get(f"{self.BASE_URL}/api/toh/new-game?disks=5")
        self.assertEqual(response.status_code, 200)

        # Simulate a single move
        move = [[1, 'A', 'C']]
        response = requests.post(
            f"{self.BASE_URL}/api/toh/validate-solution",
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'playerName': 'Test', 'diskCount': 5, 'moves': move})
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(data['success'])  # Single move won't solve
        self.assertEqual(len(move), 1)

    def test_solution_submission(self):
        # 5-disk, 31-move solution
        moves = [
            [1, 'A', 'C'], [2, 'A', 'B'], [1, 'C', 'B'], [3, 'A', 'C'], [1, 'B', 'A'],
            [2, 'B', 'C'], [1, 'A', 'C'], [4, 'A', 'B'], [1, 'C', 'B'], [2, 'C', 'A'],
            [1, 'B', 'A'], [3, 'C', 'B'], [1, 'A', 'C'], [2, 'A', 'B'], [1, 'C', 'B'],
            [5, 'A', 'C'], [1, 'B', 'A'], [2, 'B', 'C'], [1, 'A', 'C'], [3, 'B', 'A'],
            [1, 'C', 'B'], [2, 'C', 'A'], [1, 'B', 'A'], [4, 'B', 'C'], [1, 'A', 'C'],
            [2, 'A', 'B'], [1, 'C', 'B'], [3, 'A', 'C'], [1, 'B', 'A'], [2, 'B', 'C'],
            [1, 'A', 'C']
        ]
        response = requests.post(
            f"{self.BASE_URL}/api/toh/validate-solution",
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'playerName': 'Test', 'diskCount': 5, 'moves': moves})
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(moves), 31)

if __name__ == '__main__':
    unittest.main()