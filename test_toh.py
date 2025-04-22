import unittest
import sqlite3
import os
from toh_routes import solve_toh_recursive, solve_toh_iterative, frame_stewart_algorithm, validate_move_sequence
from toh_db import init_db, save_score, save_game_result, get_scores, save_algorithm_performance, get_algorithm_performance

class TestTowerOfHanoi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up a temporary database for testing"""
        cls.db_path = 'test_toh.db'
        os.environ['TEST_DB'] = cls.db_path
        init_db()

    @classmethod
    def tearDownClass(cls):
        """Clean up the test database"""
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def setUp(self):
        """Clear the database before each test"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM scores')
            cursor.execute('DELETE FROM game_moves')
            cursor.execute('DELETE FROM algorithm_performance')
            conn.commit()

    def test_recursive_algorithm(self):
        """Test recursive algorithm for 3 disks"""
        moves = solve_toh_recursive(3, 'A', 'B', 'C')
        self.assertEqual(len(moves), 7)  # 2^3 - 1 = 7
        self.assertTrue(validate_move_sequence(3, moves))

    def test_iterative_algorithm(self):
        """Test iterative algorithm for 3 disks"""
        moves = solve_toh_iterative(3, 'A', 'B', 'C')
        self.assertEqual(len(moves), 7)
        self.assertTrue(validate_move_sequence(3, moves))

    def test_frame_stewart_algorithm(self):
        """Test Frame-Stewart algorithm for 3 disks"""
        moves = frame_stewart_algorithm(3, 'A', 'B', 'C', 'D')
        self.assertTrue(len(moves) <= 7)  # Should be efficient
        self.assertTrue(validate_move_sequence(3, moves))

    def test_validate_move_sequence_valid(self):
        """Test valid move sequence"""
        moves = [[1, 'A', 'C'], [2, 'A', 'B'], [1, 'C', 'B'], [3, 'A', 'C'], 
                 [1, 'B', 'A'], [2, 'B', 'C'], [1, 'A', 'C']]
        self.assertTrue(validate_move_sequence(3, moves))

    def test_validate_move_sequence_invalid(self):
        """Test invalid move sequence (larger disk on smaller)"""
        moves = [[1, 'A', 'C'], [2, 'A', 'C']]  # Invalid: 2 > 1
        self.assertFalse(validate_move_sequence(2, moves))

    def test_save_score(self):
        """Test saving a score"""
        score_id = save_score('TestPlayer', 5, 31, '3peg')
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT player_name, disk_count, moves_count, mode FROM scores WHERE id = ?', (score_id,))
            result = cursor.fetchone()
            self.assertEqual(result, ('TestPlayer', 5, 31, '3peg'))

    def test_save_game_result(self):
        """Test saving a game result with moves"""
        moves_json = '[[1,"A","C"],[2,"A","B"]]'
        score_id = save_game_result('TestPlayer', 5, 2, moves_json, '3peg')
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT player_name, disk_count, moves_count, mode FROM scores WHERE id = ?', (score_id,))
            score = cursor.fetchone()
            cursor.execute('SELECT moves_json FROM game_moves WHERE score_id = ?', (score_id,))
            moves = cursor.fetchone()
            self.assertEqual(score, ('TestPlayer', 5, 2, '3peg'))
            self.assertEqual(moves[0], moves_json)

    def test_get_scores(self):
        """Test retrieving high scores"""
        save_score('Player1', 5, 31, '3peg')
        save_score('Player2', 5, 32, '3peg')
        scores = get_scores(limit=10)
        self.assertEqual(len(scores), 1)  # Only the best score per disk count
        self.assertEqual(scores[0]['player_name'], 'Player1')
        self.assertEqual(scores[0]['moves_count'], 31)

    def test_save_algorithm_performance(self):
        """Test saving algorithm performance"""
        save_algorithm_performance(5, 'recursive', 3, 0.001)
        save_algorithm_performance(5, 'iterative', 3, 0.002)
        performance = get_algorithm_performance()
        self.assertEqual(len(performance), 2)
        self.assertEqual(performance[0]['disk_count'], 5)
        self.assertEqual(performance[0]['algorithm_type'], 'iterative')
        self.assertEqual(performance[0]['avg_time'], 0.002)

if __name__ == '__main__':
    unittest.main()