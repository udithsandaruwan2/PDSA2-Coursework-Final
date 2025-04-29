import unittest
import json
from flask import Flask
from eqp_backend.eqp_routes import eqp_bp
from eqp_backend.eqp_db import EightQueensDB
from datetime import datetime
import pytz

class EightQueensAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(eqp_bp)
        self.client = self.app.test_client()
        # Backup eqp_submissions
        db = EightQueensDB()
        db.execute_query("CREATE TABLE IF NOT EXISTS eqp_submissions_backup AS SELECT * FROM eqp_submissions")
        # Clear only for testing
        db.execute_query("DELETE FROM eqp_submissions")
        db.execute_query("DELETE FROM eqp_solutions")
        db.execute_query("DELETE FROM eqp_performance")
        # Populate eqp_solutions
        self.client.post('/api/eight_queens/compute_solutions')
        # Valid board matching a known solution
        self.valid_board = [
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0]
        ]
        self.valid_board_2 = [
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0]
        ]

    def tearDown(self):
        db = EightQueensDB()
        # Restore eqp_submissions from backup
        db.execute_query("DELETE FROM eqp_submissions")
        db.execute_query("INSERT INTO eqp_submissions SELECT * FROM eqp_submissions_backup")
        # Drop backup table
        db.execute_query("DROP TABLE IF EXISTS eqp_submissions_backup")

    def solution_to_board(self, solution_string):
        """Convert a 64-character solution string to an 8x8 board."""
        board = []
        for i in range(0, 64, 8):
            row = [int(c) for c in solution_string[i:i+8]]
            board.append(row)
        return board

    def board_to_string(self, board):
        return ''.join(''.join(map(str, row)) for row in board)

    def test_compute_solutions(self):
        print("Testing /api/eight_queens/compute_solutions...")
        response = self.client.post('/api/eight_queens/compute_solutions', json={'rounds': 1})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['sequential']['solutions_counts'][0], 92)
        self.assertEqual(data['parallel']['solutions_counts'][0], 92)
        print("✓ /api/eight_queens/compute_solutions works as expected.")

    def test_submit_solution_valid(self):
        print("Testing /api/eight_queens/submit_solution with valid solution...")
        payload = {'username': 'test_user', 'board': self.valid_board}
        response = self.client.post('/api/eight_queens/submit_solution', json=payload)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Solution submitted successfully!')
        self.assertEqual(data['unique_solutions'], 1)
        print("✓ /api/eight_queens/submit_solution accepts valid solution.")

    def test_submit_solution_invalid(self):
        print("Testing /api/eight_queens/submit_solution with invalid solution...")
        invalid_board = [
            [1, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0]
        ]
        payload = {'username': 'test_user', 'board': invalid_board}
        response = self.client.post('/api/eight_queens/submit_solution', json=payload)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertIn('Queens are not placed correctly', data['message'])
        print("✓ /api/eight_queens/submit_solution rejects invalid solution.")

    def test_submit_solution_duplicate_same_user(self):
        print("Testing /api/eight_queens/submit_solution with duplicate solution by same user...")
        payload = {'username': 'test_user', 'board': self.valid_board}
        self.client.post('/api/eight_queens/submit_solution', json=payload)
        response = self.client.post('/api/eight_queens/submit_solution', json=payload)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'This solution has already been submitted by you. Try a different configuration.')
        self.assertEqual(data['unique_solutions'], 1)
        print("✓ /api/eight_queens/submit_solution handles duplicate solution by same user.")

    def test_submit_solution_duplicate_different_user(self):
        print("Testing /api/eight_queens/submit_solution with duplicate solution by different user...")
        payload1 = {'username': 'test_user1', 'board': self.valid_board}
        payload2 = {'username': 'test_user2', 'board': self.valid_board}
        self.client.post('/api/eight_queens/submit_solution', json=payload1)
        response = self.client.post('/api/eight_queens/submit_solution', json=payload2)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'This solution has already been submitted by another user. Try a different configuration.')
        self.assertEqual(data['unique_solutions'], 1)
        print("✓ /api/eight_queens/submit_solution handles duplicate solution by different user.")

    def test_submit_solution_maximum_reached(self):
        print("Testing /api/eight_queens/submit_solution when maximum solutions reached...")
        db = EightQueensDB()
        db.execute_query("DELETE FROM eqp_submissions")
        solutions = db.get_solutions()
        self.assertEqual(len(solutions), 92, "Expected 92 solutions in eqp_solutions")
        for i, solution in enumerate(solutions[:91]):
            db.execute_query(
                "INSERT INTO eqp_submissions (username, solution, submitted_at) VALUES (?, ?, ?)",
                (f'test_user_{i}', solution, datetime.now(pytz.timezone('Asia/Colombo')).isoformat())
            )
        board = self.solution_to_board(solutions[91])
        payload = {'username': 'test_user', 'board': board}
        response = self.client.post('/api/eight_queens/submit_solution', json=payload)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'All 92 unique solutions have been submitted. Game reset for new submissions!')
        self.assertEqual(data['unique_solutions'], 0)
        submissions = db.get_submissions()
        self.assertEqual(len(submissions), 0)
        print("✓ /api/eight_queens/submit_solution handles maximum solutions and resets.")

    def test_get_solutions(self):
        print("Testing /api/eight_queens/get_solutions...")
        response = self.client.get('/api/eight_queens/get_solutions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['solutions']), 92)
        print("✓ /api/eight_queens/get_solutions works as expected.")

    def test_get_database(self):
        print("Testing /api/eight_queens/get_database...")
        payload = {'username': 'test_user', 'board': self.valid_board}
        self.client.post('/api/eight_queens/submit_solution', json=payload)
        response = self.client.get('/api/eight_queens/get_database')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['eqp_solutions']), 10)
        self.assertEqual(len(data['eqp_submissions']), 1)
        self.assertGreaterEqual(len(data['eqp_performance']), 2)
        print("✓ /api/eight_queens/get_database works as expected.")

    def test_reset_game(self):
        print("Testing /api/eight_queens/reset_game...")
        payload = {'username': 'test_user', 'board': self.valid_board}
        self.client.post('/api/eight_queens/submit_solution', json=payload)
        response = self.client.post('/api/eight_queens/reset_game')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Game state reset successfully')
        submissions = EightQueensDB().get_submissions()
        self.assertEqual(len(submissions), 0)
        print("✓ /api/eight_queens/reset_game works as expected.")

    def test_get_performance(self):
        print("Testing /api/eight_queens/get_performance...")
        self.client.post('/api/eight_queens/compute_solutions', json={'rounds': 1})
        response = self.client.get('/api/eight_queens/get_performance')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['performance_metrics']) >= 2)
        print("✓ /api/eight_queens/get_performance works as expected.")

    def test_submit_solution_missing_fields(self):
        print("Testing /api/eight_queens/submit_solution with missing fields...")
        payload = {'username': 'test_user'}
        response = self.client.post('/api/eight_queens/submit_solution', json=payload)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Username and board are required')
        print("✓ /api/eight_queens/submit_solution rejects missing fields.")

    def test_get_database_submissions(self):
        print("Testing /api/eight_queens/get_database for submissions...")
        payload = {'username': 'test_user', 'board': self.valid_board}
        response = self.client.post('/api/eight_queens/submit_solution', json=payload)
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/eight_queens/get_database')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['eqp_submissions']), 1)
        self.assertEqual(data['eqp_submissions'][0]['username'], 'test_user')
        print("✓ /api/eight_queens/get_database returns correct submissions data.")

    def test_run_algorithm_rounds(self):
        print("Testing /api/eight_queens/run_algorithm_rounds...")
        payload = {'rounds': 5}
        response = self.client.post('/api/eight_queens/run_algorithm_rounds', json=payload)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['rounds']), 5)
        self.assertEqual(len(data['sequential_times']), 5)
        self.assertEqual(len(data['parallel_times']), 5)
        self.assertEqual(len(data['sequential_solutions']), 5)
        self.assertEqual(len(data['parallel_solutions']), 5)
        for solutions in data['sequential_solutions']:
            self.assertEqual(solutions, 92)
        for solutions in data['parallel_solutions']:
            self.assertEqual(solutions, 92)
        print F"✓ /api/eight_queens/run_algorithm_rounds works with specified rounds.")

if __name__ == '__main__':
    unittest.main(verbosity=2)