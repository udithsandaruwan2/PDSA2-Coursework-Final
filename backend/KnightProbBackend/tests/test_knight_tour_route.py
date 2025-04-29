import unittest
import json
from flask import Flask
import sys
import os

# Make backend accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from KnightProbBackend.KnightTourRoute import knight_blueprint

class KnightTourRouteTestCase(unittest.TestCase):
    def setUp(self):
        # Create a test Flask app and register the blueprint
        self.app = Flask(__name__)
        self.app.register_blueprint(knight_blueprint)
        self.client = self.app.test_client()

    def test_start_game(self):
        response = self.client.get('/api/start')
        data = response.get_json()
        self.assertIn('start', data)
        self.assertIn('x', data['start'])
        self.assertIn('y', data['start'])


    def test_validate_path_invalid_format(self):
        response = self.client.post('/api/validate_using_both', json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['valid'])
        self.assertEqual(data['message'], "Path not provided")

    def test_validate_backtracking_invalid(self):
        path = [[0, 0], [0, 1]]  # Not a knight move
        response = self.client.post('/api/validate_backtracking', json={"path": path})
        data = response.get_json()
        self.assertFalse(data['valid'])
        self.assertIn("Invalid knight move", data['message'])

    def test_validate_warnsdorff_invalid(self):
        path = [[0, 0], [0, 1]]
        response = self.client.post('/api/validate_warnsdorff', json={"path": path})
        data = response.get_json()
        self.assertFalse(data['valid'])

    def test_solve_from_start_position(self):
        path = [[0, 0]]
        response = self.client.post('/api/solve', json={"path": path})
        data = response.get_json()
        self.assertIn("success", data)
        if data["success"]:
            self.assertEqual(len(data["path"]), 64)

    def test_solve_from_start_position_warnsdorff(self):
        path = [[0, 0]]
        response = self.client.post('/api/warnsdorff', json={"path": path})
        data = response.get_json()
        self.assertIn("success", data)
        if data["success"]:
            self.assertEqual(len(data["path"]), 64)

    def test_submit_winner_invalid(self):
        data = {
            "name": "Knight",
            "start_x": "0",  # Invalid type (should be int)
            "start_y": 0,
            "path": [[0, 0], [1, 2]],
            "timestamp": "2025-04-19T00:00:00"
        }
        response = self.client.post('/api/submit_winner', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

if __name__ == '__main__':
    unittest.main()
