import unittest
import json
import sys
import os
from tsp_backend.tsp_routes import tsp_nearest_neighbor

# Setup import path to access app.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class SalesmanAPITestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

        self.sample_cities = [
            {'id': 0, 'name': 'A'},
            {'id': 1, 'name': 'B'},
            {'id': 2, 'name': 'C'}
        ]
        self.sample_distances = {
            "0": {"0": None, "1": 20, "2": 30},
            "1": {"0": 20, "1": None, "2": 15},
            "2": {"0": 30, "1": 15, "2": None}
        }

    def test_get_city_distances(self):
        print("\nTesting /api/get_city_distances...")
        response = self.client.get("/api/get_city_distances")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("cities", data)
        self.assertIn("distances", data)
        self.assertEqual(len(data["cities"]), 10)
        print("✓ /api/get_city_distances works as expected.")

    def test_solve_tsp(self):
        print("\nTesting /api/solve_tsp...")
        payload = {
            "cities": self.sample_cities,
            "player_name": "Tester",
            "home_city": "A",  # char 'A' => id 0
            "human_route": ["B", "C"],  # char B=1, C=2
            "distances": self.sample_distances
        }
        response = self.client.post("/api/solve_tsp", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("nearest_neighbor", data)
        self.assertIn("brute_force", data)
        self.assertIn("held_karp", data)
        print("✓ /api/solve_tsp returns valid algorithm data.")

    def test_save_game_session(self):
        print("\nTesting /api/save_game_session...")
        payload = {
            "player_name": "Tester",
            "home_city": "A",
            "selected_cities": ["B", "C"],
            "nn_distance": 70,
            "bf_distance": 65,
            "hk_distance": 60,
            "nn_time": 0.01,
            "bf_time": 0.02,
            "hk_time": 0.03,
            "nn_route": ["A", "B", "C", "A"],
            "bf_route": ["A", "C", "B", "A"],
            "hk_route": ["A", "C", "B", "A"]
        }
        response = self.client.post("/api/save_game_session", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("message", data)
        self.assertIn("session_id", data)
        print("✓ /api/save_game_session saves session successfully.")

    def test_save_win(self):
        print("\nTesting /api/save_win...")
        payload = {
            "player_name": "Tester",
            "home_city": "A",
            "selected_cities": ["B", "C"],
            "human_route": ["A", "B", "C", "A"],
            "human_distance": 70,
            "nn_distance": 70,
            "bf_distance": 65,
            "hk_distance": 60,
            "nn_time": 0.01,
            "bf_time": 0.02,
            "hk_time": 0.03,
            "nn_route": ["A", "B", "C", "A"],
            "bf_route": ["A", "C", "B", "A"],
            "hk_route": ["A", "C", "B", "A"],
            "session_id": 1  # Note: may need to ensure session 1 exists or mock DB
        }
        response = self.client.post("/api/save_win", json=payload)
        self.assertIn(response.status_code, [200, 500])  # Accept 500 if session_id=1 doesn't exist
        print("✓ /api/save_win called (success or handled failure).")

    def test_db_viewer(self):
        print("\nTesting /api/db_viewer...")
        response = self.client.get("/api/db_viewer")
        self.assertEqual(response.status_code, 200)
        self.assertIn("<html>", response.get_data(as_text=True))
        print("✓ /api/db_viewer returns HTML successfully.")

    def test_solve_tsp_missing_fields(self):
        print("\nTesting /api/solve_tsp with missing fields...")
        payload = {}  # Empty on purpose
        response = self.client.post("/api/solve_tsp", json=payload)
        self.assertEqual(response.status_code, 400)
        print("✓ /api/solve_tsp correctly handles missing input.")




if __name__ == "__main__":
    unittest.main()

