import unittest
import sys
import os
import json
import tempfile
import sqlite3
from unittest.mock import patch, MagicMock

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the modules to test
from backend import toh_db
from backend.toh import (
    bp, solve_toh_recursive, solve_toh_iterative, 
    frame_stewart_algorithm, validate_move_sequence
)

class TestTowerOfHanoi(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment before each test"""
        # Create a temp database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        
        # Patch the db connection to use our test database
        self.db_conn_patcher = patch('backend.toh_db.get_db_connection')
        self.mock_db_conn = self.db_conn_patcher.start()
        
        # Set up the mock to return a connection to our test database
        def get_test_db_conn():
            conn = sqlite3.connect(self.temp_db_path)
            conn.row_factory = sqlite3.Row
            return conn
        
        self.mock_db_conn.side_effect = lambda: get_test_db_conn()
        
        # Initialize the test database
        toh_db.init_db()
    
    def tearDown(self):
        """Clean up after each test"""
        self.db_conn_patcher.stop()
        os.unlink(self.temp_db_path)
    
    def test_solve_toh_recursive(self):
        """Test the recursive Tower of Hanoi solution"""
        # Test with n=1
        moves = solve_toh_recursive(1, 'A', 'B', 'C')
        self.assertEqual(moves, [[1, 'A', 'C']])
        
        # Test with n=3
        moves = solve_toh_recursive(3, 'A', 'B', 'C')
        expected_moves = [
            [1, 'A', 'C'], [2, 'A', 'B'], [1, 'C', 'B'],
            [3, 'A', 'C'], [1, 'B', 'A'], [2, 'B', 'C'], [1, 'A', 'C']
        ]
        self.assertEqual(moves, expected_moves)
        
        # Verify the number of moves matches 2^n - 1
        n = 4
        moves = solve_toh_recursive(n, 'A', 'B', 'C')
        self.assertEqual(len(moves), 2**n - 1)
    
    def test_solve_toh_iterative(self):
        """Test the iterative Tower of Hanoi solution"""
        # Test with n=1
        moves = solve_toh_iterative(1, 'A', 'B', 'C')
        self.assertEqual(moves, [[1, 'A', 'C']])
        
        # Test with n=3
        moves = solve_toh_iterative(3, 'A', 'B', 'C')
        # Verify the final state would be correct (all disks on peg C)
        towers = {'A': [3, 2, 1], 'B': [], 'C': []}
        for disk, src, dst in moves:
            towers[dst].append(towers[src].pop())
        self.assertEqual(towers, {'A': [], 'B': [], 'C': [1, 2, 3]})
        
        # Verify the number of moves matches 2^n - 1
        n = 4
        moves = solve_toh_iterative(n, 'A', 'B', 'C')
        self.assertEqual(len(moves), 2**n - 1)
    
    def test_frame_stewart_algorithm(self):
        """Test the Frame-Stewart algorithm for 4-peg Tower of Hanoi"""
        # Test with n=1
        moves = frame_stewart_algorithm(1, 'A', 'B', 'C', 'D')
        self.assertEqual(moves, [[1, 'A', 'D']])
        
        # Test with n=2
        moves = frame_stewart_algorithm(2, 'A', 'B', 'C', 'D')
        self.assertEqual(len(moves), 3)  # Should take 3 moves with 4 pegs
        
        # Test with n=4 (should be more efficient than 2^n-1)
        moves = frame_stewart_algorithm(4, 'A', 'B', 'C', 'D')
        self.assertLess(len(moves), 2**4 - 1)
        
        # Test that the moves are valid
        towers = {'A': [4, 3, 2, 1], 'B': [], 'C': [], 'D': []}
        for disk, src, dst in moves:
            # Get the top disk from source
            if not towers[src]:
                self.fail(f"Invalid move: tried to move from empty peg {src}")
            top_disk = towers[src][-1]
            # Check that the disk matches what we're trying to move
            self.assertEqual(top_disk, disk)
            # Check that we're not placing a larger disk on a smaller disk
            if towers[dst] and towers[dst][-1] < disk:
                self.fail(f"Invalid move: tried to place disk {disk} on top of smaller disk {towers[dst][-1]}")
            # Perform the move
            towers[dst].append(towers[src].pop())
        
        # Verify final state - all disks should be on peg D in correct order
        self.assertEqual(towers['D'], [4, 3, 2, 1])
    
    def test_validate_move_sequence(self):
        """Test the move sequence validation function"""
        # Valid simple move sequence
        valid_sequence = [[1, 'A', 'C'], [2, 'A', 'B'], [1, 'C', 'B']]
        self.assertTrue(validate_move_sequence(2, valid_sequence))
        
        # Invalid: moving non-top disk
        invalid_sequence1 = [[2, 'A', 'B'], [1, 'A', 'C']]  # Moving disk 2 first, then disk 1
        self.assertFalse(validate_move_sequence(2, invalid_sequence1))
        
        # Invalid: placing larger disk on smaller disk
        invalid_sequence2 = [[1, 'A', 'C'], [2, 'A', 'C']]  # Moving disk 1 to C, then disk 2 to C
        self.assertFalse(validate_move_sequence(2, invalid_sequence2))
        
        # Invalid: source peg empty
        invalid_sequence3 = [[1, 'A', 'C'], [1, 'A', 'B']]  # Moving disk 1 twice from A
        self.assertFalse(validate_move_sequence(2, invalid_sequence3))
        
        # Invalid: does not end with all disks on target peg
        incomplete_sequence = [[1, 'A', 'B']]  # Only moves one disk, not both
        self.assertFalse(validate_move_sequence(2, incomplete_sequence))
    
    def test_database_operations(self):
        """Test database operations"""
        # Test save_score and get_scores
        toh_db.save_score("TestPlayer1", 5, 31, "3peg", 800)
        toh_db.save_score("TestPlayer2", 5, 30, "3peg", 850)
        
        scores = toh_db.get_scores()
        self.assertEqual(len(scores), 1)  # Should return the best score for disk_count=5
        self.assertEqual(scores[0]['player_name'], "TestPlayer2")
        self.assertEqual(scores[0]['moves_count'], 30)
        
        # Test save_game_result
        moves_json = json.dumps([[1, 'A', 'C'], [2, 'A', 'B'], [1, 'C', 'B']])
        score_id = toh_db.save_game_result("TestPlayer3", 3, 7, moves_json, "3peg", 950)
        self.assertIsNotNone(score_id)
        
        # Test get_all_scores
        all_scores = toh_db.get_all_scores()
        self.assertEqual(len(all_scores), 3)  # Should have 3 scores now
        
        # Test save_algorithm_performance
        moves = [[1, 'A', 'C'], [2, 'A', 'B']]
        toh_db.save_algorithm_performance(3, "recursive", 3, 0.5, len(moves), moves)
        
        # Test get_algorithm_performance
        performance_data = toh_db.get_algorithm_performance()
        self.assertEqual(len(performance_data), 1)
        self.assertEqual(performance_data[0]['algorithm_type'], "recursive")
        self.assertEqual(performance_data[0]['min_moves'], 2)
    
    @patch('flask.request')
    def test_new_game_endpoint(self, mock_request):
        """Test the new-game endpoint"""
        mock_request.args = {'disks': '5', 'mode': '3peg'}
        
        with patch('flask.jsonify', side_effect=lambda x: x) as mock_jsonify:
            result = bp.view_functions['toh.new_game']()
            
            # Verify the response structure
            self.assertIn('disk_count', result)
            self.assertEqual(result['disk_count'], 5)
            self.assertIn('min_moves', result)
            self.assertEqual(result['min_moves'], 31)  # 2^5 - 1 = 31
            self.assertIn('solutions', result)
            
            # Check that we have all three solutions
            solutions = result['solutions']
            self.assertIn('recursive', solutions)
            self.assertIn('iterative', solutions)
            self.assertIn('frame_stewart', solutions)
            
            # Verify the recursive solution has the correct number of moves
            self.assertEqual(len(solutions['recursive']['moves']), 31)
    
    @patch('flask.request')
    def test_validate_solution_endpoint(self, mock_request):
        """Test the validate-solution endpoint"""
        valid_moves = [[1, 'A', 'C'], [2, 'A', 'B'], [1, 'C', 'B'], [3, 'A', 'C'], 
                       [1, 'B', 'A'], [2, 'B', 'C'], [1, 'A', 'C']]
        
        mock_request.json = {
            'playerName': 'TestPlayer',
            'diskCount': 3,
            'moves': valid_moves,
            'mode': '3peg'
        }
        
        with patch('flask.jsonify', side_effect=lambda x: x) as mock_jsonify:
            result = bp.view_functions['toh.validate_solution']()
            
            # Verify that the solution is valid
            self.assertTrue(result['success'])
            self.assertEqual(result['min_moves'], 7)
            self.assertTrue(result['optimal'])
            
            # Test invalid solution
            invalid_moves = [[1, 'A', 'C'], [2, 'A', 'B']]  # Incomplete solution
            mock_request.json['moves'] = invalid_moves
            
            result = bp.view_functions['toh.validate_solution']()
            self.assertFalse(result['success'])
    
    def test_algorithm_comparison(self):
        """Test algorithm comparison functions"""
        # Setup test data
        for disk_count in [3, 4, 5]:
            recursive_time = disk_count * 0.1
            iterative_time = disk_count * 0.08
            frame_stewart_time = disk_count * 0.15
            
            toh_db.save_algorithm_performance(disk_count, "recursive", 3, recursive_time, 2**disk_count-1)
            toh_db.save_algorithm_performance(disk_count, "iterative", 3, iterative_time, 2**disk_count-1)
            toh_db.save_algorithm_performance(disk_count, "frame_stewart", 4, frame_stewart_time)
        
        # Test chart data generation
        with patch('flask.jsonify', side_effect=lambda x: x) as mock_jsonify:
            result = bp.view_functions['toh.get_algorithm_comparison_chart']()
            
            # Verify chart structure
            self.assertIn('labels', result)
            self.assertIn('datasets', result)
            self.assertEqual(len(result['datasets']), 3)  # Three algorithms
            self.assertEqual(len(result['labels']), 3)    # Three disk counts

if __name__ == '__main__':
    unittest.main()