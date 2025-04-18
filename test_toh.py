import pytest
import json
import toh_routes
import toh_db
import os
import sys
import sqlite3
import time

# Add backend directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

# Test the algorithms
def test_recursive_solution():
    """Test that recursive solution generates correct number of moves."""
    for n in range(1, 11):
        moves = toh_routes.solve_toh_recursive(n, 'A', 'B', 'C')
        assert len(moves) == (2**n - 1), f"Recursive solution for {n} disks should have {2**n - 1} moves"

def test_iterative_solution():
    """Test that iterative solution generates correct number of moves."""
    for n in range(1, 11):
        moves = toh_routes.solve_toh_iterative(n, 'A', 'B', 'C')
        assert len(moves) == (2**n - 1), f"Iterative solution for {n} disks should have {2**n - 1} moves"

def test_frame_stewart_algorithm():
    """Test Frame-Stewart algorithm for 4 pegs."""
    # For small values, Frame-Stewart should generate fewer moves than classic 3-peg solution
    for n in range(4, 8):
        classic_moves = toh_routes.solve_toh_recursive(n, 'A', 'B', 'C')
        frame_stewart_moves = toh_routes.frame_stewart_algorithm(n, 'A', 'B', 'C', 'D')
        
        assert len(frame_stewart_moves) <= len(classic_moves), f"Frame-Stewart should be more efficient than classic for {n} disks"

def test_solution_validation():
    """Test the validation of move sequences."""
    # Test with a simple valid solution for 3 disks
    valid_moves = [('A', 'C'), ('A', 'B'), ('C', 'B'), ('A', 'C'), ('B', 'A'), ('B', 'C'), ('A', 'C')]
    assert toh_routes.validate_move_sequence(3, valid_moves) == True
    
    # Test with an invalid solution (placing larger disk on smaller)
    invalid_moves = [('A', 'C'), ('A', 'B'), ('C', 'B'), ('A', 'B')]  # This would place a larger disk on a smaller one
    assert toh_routes.validate_move_sequence(3, invalid_moves) == False
    
    # Test with incomplete solution
    incomplete_moves = [('A', 'C'), ('A', 'B')]
    assert toh_routes.validate_move_sequence(3, incomplete_moves) == False

def test_algorithm_performance():
    """Test performance comparison of algorithms."""
    disk_count = 8
    
    # Test recursive algorithm
    start_time = time.time()
    toh_routes.solve_toh_recursive(disk_count, 'A', 'B', 'C')
    recursive_time = time.time() - start_time
    
    # Test iterative algorithm
    start_time = time.time()
    toh_routes.solve_toh_iterative(disk_count, 'A', 'B', 'C')
    iterative_time = time.time() - start_time
    
    # Test Frame-Stewart algorithm
    start_time = time.time()
    toh_routes.frame_stewart_algorithm(disk_count, 'A', 'B', 'C', 'D')
    frame_stewart_time = time.time() - start_time
    
    # Log performance data
    print(f"Algorithm performance for {disk_count} disks:")
    print(f"Recursive: {recursive_time:.6f} seconds")
    print(f"Iterative: {iterative_time:.6f} seconds")
    print(f"Frame-Stewart: {frame_stewart_time:.6f} seconds")
    
    # We're not strictly asserting times here as they can vary by system,
    # but we're logging them for manual review

# Test database operations
@pytest.fixture
def temp_db():
    """Create a temporary in-memory database for testing."""
    # Store the original DB_PATH
    original_db_path = toh_db.DB_PATH
    
    # Set to use an in-memory database
    toh_db.DB_PATH = ":memory:"
    
    # Initialize the database
    toh_db.init_db()
    
    yield
    
    # Restore original DB_PATH
    toh_db.DB_PATH = original_db_path

def test_save_game_result(temp_db):
    """Test saving game results to database."""
    player_name = "Test Player"
    disk_count = 5
    moves_count = 31
    moves_sequence = json.dumps([('A', 'C'), ('A', 'B'), ('C', 'B')])
    
    # Save the result
    result_id = toh_db.save_game_result(player_name, disk_count, moves_count, moves_sequence)
    
    # Verify it was saved
    assert result_id is not None, "Result ID should not be None"
    assert result_id > 0, "Result ID should be positive"

def test_save_algorithm_performance(temp_db):
    """Test saving algorithm performance data."""
    disk_count = 6
    algorithm_type = "recursive"
    peg_count = 3
    execution_time = 0.001234
    
    # Save the performance data
    perf_id = toh_db.save_algorithm_performance(disk_count, algorithm_type, peg_count, execution_time)
    
    # Verify it was saved
    assert perf_id is not None, "Performance ID should not be None"
    assert perf_id > 0, "Performance ID should be positive"

def test_get_top_scores(temp_db):
    """Test retrieving top scores."""
    # Add some test scores
    toh_db.save_game_result("Player 1", 5, 31, "[]")
    toh_db.save_game_result("Player 2", 6, 63, "[]")
    toh_db.save_game_result("Player 3", 7, 127, "[]")
    
    # Get top scores
    scores = toh_db.get_top_scores(limit=2)
    
    # Verify we got the expected number of scores
    assert len(scores) == 2, "Should return 2 scores"
    
    # Verify they're sorted by disk count (desc) and moves (asc)
    assert scores[0]['disk_count'] >= scores[1]['disk_count'], "Scores should be sorted by disk count (desc)"
    if scores[0]['disk_count'] == scores[1]['disk_count']:
        assert scores[0]['moves_count'] <= scores[1]['moves_count'], "For same disk count, should sort by moves (asc)"

def test_get_algorithm_comparisons(temp_db):
    """Test retrieving algorithm comparison data."""
    # Add some test performance data
    toh_db.save_algorithm_performance(5, "recursive", 3, 0.001)
    toh_db.save_algorithm_performance(5, "recursive", 3, 0.002)  # Same parameters, different execution time
    toh_db.save_algorithm_performance(5, "iterative", 3, 0.0005)
    toh_db.save_algorithm_performance(6, "frame_stewart", 4, 0.003)
    
    # Get comparisons
    comparisons = toh_db.get_algorithm_comparisons()
    
    # Verify we have the expected data points
    assert len(comparisons) == 3, "Should have 3 distinct algorithm/disk count combinations"
    
    # Check that we have all the expected algorithm types
    algorithm_types = [comp['algorithm_type'] for comp in comparisons]
    assert "recursive" in algorithm_types, "Should have recursive algorithm"
    assert "iterative" in algorithm_types, "Should have iterative algorithm"
    assert "frame_stewart" in algorithm_types, "Should have frame_stewart algorithm"
    
    # Check that the averages are calculated correctly
    for comp in comparisons:
        if comp['algorithm_type'] == 'recursive' and comp['disk_count'] == 5:
            # Average of 0.001 and 0.002 should be 0.0015
            assert abs(comp['avg_time'] - 0.0015) < 0.00001, "Average time calculation is incorrect for recursive"

if __name__ == "__main__":
    pytest.main()