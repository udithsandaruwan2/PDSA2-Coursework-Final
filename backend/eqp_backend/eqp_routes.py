import json
from flask import Blueprint, request, jsonify
import time
import logging
import threading
from eqp_backend.eqp_db import EightQueensDB
from concurrent.futures import ThreadPoolExecutor
import random

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the blueprint for Eight Queens Puzzle routes
eqp_bp = Blueprint('eqp', __name__, url_prefix='/api')

class QueensSolver:
    def __init__(self):
        self.solutions = []
        self.lock = threading.Lock()

    def is_safe(self, board, row, col):
        """Check if a queen can be placed at (row, col) without being attacked."""
        for i in range(col):
            if board[row][i] == 1:
                return False

        for i, j in zip(range(row, -1, -1), range(col, -1, -1)):
            if board[i][j] == 1:
                return False

        for i, j in zip(range(row, 8, 1), range(col, -1, -1)):
            if board[i][j] == 1:
                return False

        return True

    def validate_board(self, board):
        """Validate if the board is a correct Eight Queens solution."""
        # Check for exactly 8 queens
        queen_count = sum(row.count(1) for row in board)
        if queen_count != 8:
            logger.debug(f"Validation failed: Incorrect queen count ({queen_count})")
            return False

        # Check each row has exactly one queen
        for row in board:
            if sum(row) != 1:
                logger.debug(f"Validation failed: Row has {sum(row)} queens")
                return False

        # Check each column has exactly one queen
        for col in range(8):
            col_sum = sum(board[row][col] for row in range(8))
            if col_sum != 1:
                logger.debug(f"Validation failed: Column {col} has {col_sum} queens")
                return False

        # Collect queen positions
        queen_positions = [(r, c) for r in range(8) for c in range(8) if board[r][c] == 1]
        if len(queen_positions) != 8:
            logger.debug(f"Validation failed: Found {len(queen_positions)} queen positions")
            return False

        # Check for diagonal conflicts
        for i, (row1, col1) in enumerate(queen_positions):
            for row2, col2 in queen_positions[i + 1:]:
                if abs(row1 - row2) == abs(col1 - col2):
                    logger.debug(f"Validation failed: Diagonal conflict between ({row1}, {col1}) and ({row2}, {col2})")
                    return False

        logger.debug("Board validated successfully")
        return True

    def solve_sequential(self, board=None, col=0):
        """Solve the Eight Queens problem sequentially using backtracking."""
        if board is None:
            board = [[0 for _ in range(8)] for _ in range(8)]

        if col >= 8:
            solution = ''.join(''.join(map(str, row)) for row in board)
            with self.lock:
                if solution not in self.solutions:
                    self.solutions.append(solution)
            return

        for row in range(8):
            if self.is_safe(board, row, col):
                board[row][col] = 1
                self.solve_sequential(board, col + 1)
                board[row][col] = 0

    def solve_threaded(self, start_row):
        """Solve the Eight Queens problem for a specific starting row in the first column."""
        board = [[0 for _ in range(8)] for _ in range(8)]
        board[start_row][0] = 1
        self.solve_sequential(board, 1)

    def solve_parallel(self):
        """Solve the Eight Queens problem using parallel threads."""
        self.solutions = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(self.solve_threaded, range(8))
        with self.lock:
            self.solutions = list(set(self.solutions))
        logger.debug(f"Parallel solutions found: {len(self.solutions)}")

    def get_solutions(self):
        return self.solutions

# Lazy initialization of the solver
_solver = None

def get_solver():
    global _solver
    if _solver is None:
        _solver = QueensSolver()
        logger.info("QueensSolver initialized.")
    return _solver

@eqp_bp.route('/eight_queens/compute_solutions', methods=['POST'])
def compute_solutions():
    """Compute solutions using both sequential and parallel approaches."""
    try:
        db = EightQueensDB()  # Create instance here
        solver = get_solver()
        
        # Sequential computation
        start_time = time.time()
        solver.solutions = []
        logger.debug("Starting sequential solving...")
        solver.solve_sequential()
        seq_time = time.time() - start_time
        seq_solutions = solver.get_solutions()
        seq_count = len(seq_solutions)
        logger.debug(f"Sequential solving completed. Found {seq_count} solutions in {seq_time} seconds.")

        # Save sequential solutions to the database
        logger.debug("Saving sequential solutions to database...")
        db.save_solutions(seq_solutions)
        logger.debug("Sequential solutions saved.")

        # Record sequential performance
        logger.debug("Recording sequential performance...")
        db.save_performance('sequential', seq_time, seq_count)
        logger.debug("Sequential performance recorded.")

        # Parallel computation
        start_time = time.time()
        solver.solutions = []
        logger.debug("Starting parallel solving...")
        solver.solve_parallel()
        par_time = time.time() - start_time
        par_solutions = solver.get_solutions()
        par_count = len(par_solutions)
        logger.debug(f"Parallel solving completed. Found {par_count} solutions in {par_time} seconds.")

        # Save parallel solutions to the database
        logger.debug("Saving parallel solutions to database...")
        db.save_solutions(par_solutions)
        logger.debug("Parallel solutions saved.")

        # Record parallel performance
        logger.debug("Recording parallel performance...")
        db.save_performance('parallel', par_time, par_count)
        logger.debug("Parallel performance recorded.")

        return jsonify({
            'success': True,
            'sequential': {
                'time': seq_time,
                'solutions_count': seq_count
            },
            'parallel': {
                'time': par_time,
                'solutions_count': par_count
            }
        })
    except Exception as e:
        logger.error(f"Error computing solutions: {str(e)}")
        return jsonify({'success': False, 'message': f"Error computing solutions: {str(e)}"}), 500

@eqp_bp.route('/eight_queens/submit_solution', methods=['POST'])
def submit_solution():
    try:
        db = EightQueensDB()  # Create instance here
        data = request.get_json()
        username = data.get('username')
        board = data.get('board')

        # Check for missing fields
        if not username or not board:
            logger.error("Missing username or board")
            return jsonify({'success': False, 'message': 'Username and board are required'}), 400

        # Validate username
        if not isinstance(username, str) or len(username.strip()) == 0:
            logger.error("Invalid username")
            return jsonify({'success': False, 'message': 'Username must be a non-empty string.'}), 400

        # Validate board structure
        if not isinstance(board, list) or len(board) != 8 or any(len(row) != 8 for row in board):
            logger.error("Invalid board format")
            return jsonify({'success': False, 'message': 'Board must be an 8x8 array.'}), 400

        # Validate board values
        if not all(all(cell in (0, 1) for cell in row) for row in board):
            logger.error("Invalid board values")
            return jsonify({'success': False, 'message': 'Board must contain only 0s and 1s.'}), 400

        # Validate queen placement
        solver = get_solver()
        if not solver.validate_board(board):
            logger.error("Board validation failed")
            return jsonify({'success': False, 'message': 'Invalid solution: Queens are not placed correctly.'}), 400

        # Convert board to 64-character string
        board_string = ''.join(''.join(map(str, row)) for row in board)
        logger.debug(f"Submitted board string: {board_string}")

        # Check if solution exists in precomputed solutions
        precomputed_solutions = db.get_solutions()
        if board_string not in precomputed_solutions:
            logger.error(f"Solution not in precomputed solutions: {board_string}")
            return jsonify({
                'success': False,
                'message': 'Invalid solution: Not one of the 92 precomputed solutions.'
            }), 400

        # Check for duplicate submission by the same user
        existing_submissions = db.execute_query(
            "SELECT username FROM eqp_submissions WHERE solution = ? AND username = ?",
            (board_string, username)
        )
        if existing_submissions:
            unique_solutions = db.execute_query("SELECT COUNT(DISTINCT solution) FROM eqp_submissions")
            unique_solution_count = unique_solutions[0][0] if unique_solutions else 0
            logger.info(f"Duplicate solution by same user: {username}")
            return jsonify({
                'success': True,
                'message': 'This solution has already been submitted by you. Try a different configuration.',
                'unique_solutions': unique_solution_count
            }), 200
        
        # Check for duplicate submission by a different user
        existing_solution = db.execute_query(
            "SELECT username FROM eqp_submissions WHERE solution = ?",
            (board_string,)
        )
        if existing_solution and existing_solution[0][0] != username:
            unique_solutions = db.execute_query("SELECT COUNT(DISTINCT solution) FROM eqp_submissions")
            unique_solution_count = unique_solutions[0][0] if unique_solutions else 0
            logger.info(f"Duplicate solution by different user: {username}")
            return jsonify({
                'success': True,
                'message': 'This solution has already been submitted by another user. Try a different configuration.',
                'unique_solutions': unique_solution_count
            }), 200

        # Store valid solution
        logger.debug(f"Saving submission for user: {username}")
        db.save_submission(username, board_string)

        # Check unique solutions count after saving
        unique_solutions = db.execute_query("SELECT COUNT(DISTINCT solution) FROM eqp_submissions")
        unique_solution_count = unique_solutions[0][0] if unique_solutions else 0

        # Reset submissions if exactly 92 unique solutions are reached
        if unique_solution_count >= 92:
            logger.info("Maximum solutions reached, resetting submissions")
            db.clear_submissions()
            return jsonify({
                'success': True,
                'message': 'All 92 unique solutions have been submitted. Game reset for new submissions!',
                'unique_solutions': 0
            }), 200

        logger.info(f"Solution submitted successfully by {username}")
        return jsonify({
            'success': True,
            'message': 'Solution submitted successfully!',
            'unique_solutions': unique_solution_count
        }), 200

    except Exception as e:
        logger.error(f"Error submitting solution: {str(e)}")
        return jsonify({'success': False, 'message': f"Error submitting solution: {str(e)}"}), 500

@eqp_bp.route('/eight_queens/get_solutions', methods=['GET'])
def get_solutions():
    """Retrieve all stored solutions."""
    try:
        db = EightQueensDB()  # Create instance here
        solutions_db = db.get_solutions()
        player_submissions = db.get_submissions()
        return jsonify({
            'success': True,
            'solutions': solutions_db,
            'submitted_solutions': player_submissions
        })
    except Exception as e:
        logger.error(f"Error retrieving solutions: {str(e)}")
        return jsonify({'success': False, 'message': f"Error retrieving solutions: {str(e)}"}), 500

@eqp_bp.route('/eight_queens/get_performance', methods=['GET'])
def get_performance():
    """Retrieve performance metrics."""
    try:
        db = EightQueensDB()  # Create instance here
        performance_metrics = db.get_performance()
        return jsonify({
            'success': True,
            'performance_metrics': performance_metrics
        })
    except Exception as e:
        logger.error(f"Error retrieving performance metrics: {str(e)}")
        return jsonify({'success': False, 'message': f"Error retrieving performance metrics: {str(e)}"}), 500

@eqp_bp.route('/eight_queens/reset_game', methods=['POST'])
def reset_game():
    """Reset the game state."""
    try:
        db = EightQueensDB()  # Create instance here
        db.clear_submissions()
        return jsonify({'success': True, 'message': 'Game state reset successfully'})
    except Exception as e:
        logger.error(f"Error resetting game state: {str(e)}")
        return jsonify({'success': False, 'message': f"Error resetting game state: {str(e)}"}), 500

@eqp_bp.route('/eight_queens/get_database', methods=['GET'])
def get_database():
    """Retrieve database contents."""
    try:
        db = EightQueensDB()  # Create instance here
        solutions = db.execute_query("SELECT * FROM eqp_solutions")
        solutions_data = [{'id': row[0], 'solution': row[1]} for row in solutions] if solutions else []

        submissions = db.execute_query("SELECT * FROM eqp_submissions ORDER BY id DESC LIMIT 10")
        submissions_data = [
            {'id': row[0], 'username': row[1], 'solution': row[2], 'submitted_at': row[3]}
            for row in submissions
        ] if submissions else []

        performance = db.execute_query("SELECT * FROM eqp_performance ORDER BY id DESC LIMIT 10")
        performance_data = [
            {
                'id': row[0],
                'algorithm_type': row[1],
                'execution_time': row[2],
                'total_solutions': row[3],
                'recorded_at': row[4]
            }
            for row in performance
        ] if performance else []

        return jsonify({
            'success': True,
            'eqp_solutions': solutions_data,
            'eqp_submissions': submissions_data,
            'eqp_performance': performance_data
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving database data: {str(e)}")
        return jsonify({'success': False, 'message': f"Error retrieving database data: {str(e)}"}), 500
    
@eqp_bp.route('/eight_queens/get_full_table', methods=['GET'])
def get_full_table():
    """Retrieve all rows from a specified database table."""
    try:
        db = EightQueensDB()  # Create instance here
        table_name = request.args.get('table')
        if table_name not in ['eqp_solutions', 'eqp_submissions', 'eqp_performance']:
            return jsonify({'success': False, 'message': 'Invalid table name'}), 400

        if table_name == 'eqp_solutions':
            data = db.execute_query("SELECT * FROM eqp_solutions")
            data_rows = [{'id': row[0], 'solution': row[1]} for row in data] if data else []
        elif table_name == 'eqp_submissions':
            data = db.execute_query("SELECT * FROM eqp_submissions")
            data_rows = [
                {'id': row[0], 'username': row[1], 'solution': row[2], 'submitted_at': row[3]}
                for row in data
            ] if data else []
        else:  # eqp_performance
            data = db.execute_query("SELECT * FROM eqp_performance")
            data_rows = [
                {
                    'id': row[0],
                    'algorithm_type': row[1],
                    'execution_time': row[2],
                    'total_solutions': row[3],
                    'recorded_at': row[4]
                }
                for row in data
            ] if data else []

        return jsonify({
            'success': True,
            'data': data_rows
        })
    except Exception as e:
        logger.error(f"Error retrieving table data: {str(e)}")
        return jsonify({'success': False, 'message': f"Error retrieving table data: {str(e)}"}), 500
    
@eqp_bp.route('/eight_queens/get_performance_stats', methods=['GET'])
def get_performance_stats():
    """Retrieve performance statistics for the last 10 runs."""
    try:
        db = EightQueensDB()  # Create instance here
        performance = db.execute_query(
            "SELECT id, algorithm_type, execution_time, total_solutions FROM eqp_performance "
            "ORDER BY id DESC LIMIT 30"
        )
        sequential_times = []
        parallel_times = []
        validation_times = []
        sequential_solutions = []
        parallel_solutions = []
        validation_solutions = []
        rounds = []

        run_count = 0
        i = 0
        while i < len(performance) and run_count < 10:
            if i + 2 < len(performance):
                # Assume sequential, parallel, and validation records are in groups
                for record in performance[i:i+3]:
                    if record[1] == 'sequential':
                        sequential_times.append(record[2])
                        sequential_solutions.append(record[3])
                    elif record[1] == 'parallel':
                        parallel_times.append(record[2])
                        parallel_solutions.append(record[3])
                    elif record[1] == 'validation':
                        validation_times.append(record[2])
                        validation_solutions.append(record[3])
                if sequential_times and parallel_times and validation_times:
                    rounds.append(str(run_count + 1))
                    run_count += 1
                i += 3
            else:
                break

        sequential_times.reverse()
        parallel_times.reverse()
        validation_times.reverse()
        sequential_solutions.reverse()
        parallel_solutions.reverse()
        validation_solutions.reverse()
        rounds.reverse()

        # Calculate speedup (sequential_time / parallel_time)
        speedup = [seq / par if par > 0 else 0 for seq, par in zip(sequential_times, parallel_times)]

        return jsonify({
            'success': True,
            'rounds': rounds,
            'sequential_times': sequential_times,
            'parallel_times': parallel_times,
            'validation_times': validation_times,
            'sequential_solutions': sequential_solutions,
            'parallel_solutions': parallel_solutions,
            'validation_solutions': validation_solutions,
            'speedup': speedup
        })
    except Exception as e:
        logger.error(f"Error retrieving performance stats: {str(e)}")
        return jsonify({'success': False, 'message': f"Error retrieving performance stats: {str(e)}"}), 500   
    
@eqp_bp.route('/eight_queens/get_player_stats', methods=['GET'])
def get_player_stats():
    """Retrieve player submission statistics."""
    try:
        db = EightQueensDB()  # Create instance here
        submissions = db.execute_query("SELECT username, COUNT(*) as solution_count FROM eqp_submissions GROUP BY username ORDER BY solution_count DESC LIMIT 10")
        players = [row[0] for row in submissions]
        solution_counts = [row[1] for row in submissions]

        return jsonify({
            'success': True,
            'players': players,
            'solution_counts': solution_counts
        })
    except Exception as e:
        logger.error(f"Error retrieving player stats: {str(e)}")
        return jsonify({'success': False, 'message': f"Error retrieving player stats: {str(e)}"}), 500
    
@eqp_bp.route('/eight_queens/run_algorithm_rounds', methods=['POST'])
def run_algorithm_rounds():
    """Run sequential and parallel algorithms for a specified number of rounds and record performance."""
    try:
        db = EightQueensDB()  # Create instance here
        data = request.get_json()
        rounds = data.get('rounds', 10)  # Default to 10 if not provided
        if not isinstance(rounds, int) or rounds < 1:
            return jsonify({'success': False, 'message': 'Rounds must be a positive integer'}), 400

        solver = get_solver()
        sequential_times = []
        parallel_times = []
        sequential_solutions = []
        parallel_solutions = []

        for round_num in range(rounds):
            logger.debug(f"Running round {round_num + 1}...")

            # Sequential computation
            start_time = time.time()
            solver.solutions = []
            solver.solve_sequential()
            seq_time = time.time() - start_time
            seq_solutions = solver.get_solutions()
            seq_count = len(seq_solutions)
            sequential_times.append(seq_time)
            sequential_solutions.append(seq_count)
            logger.debug(f"Sequential round {round_num + 1}: {seq_count} solutions in {seq_time} seconds.")

            # Record sequential performance
            db.save_performance('sequential', seq_time, seq_count)

            # Parallel computation
            start_time = time.time()
            solver.solutions = []
            solver.solve_parallel()
            par_time = time.time() - start_time
            par_solutions = solver.get_solutions()
            par_count = len(par_solutions)
            parallel_times.append(par_time)
            parallel_solutions.append(par_count)
            logger.debug(f"Parallel round {round_num + 1}: {par_count} solutions in {par_time} seconds.")

            # Record parallel performance
            db.save_performance('parallel', par_time, par_count)

        return jsonify({
            'success': True,
            'rounds': [str(i + 1) for i in range(rounds)],
            'sequential_times': sequential_times,
            'parallel_times': parallel_times,
            'sequential_solutions': sequential_solutions,
            'parallel_solutions': parallel_solutions,
            'speedup': [seq / par if par > 0 else 0 for seq, par in zip(sequential_times, parallel_times)]
        }), 200

    except Exception as e:
        logger.error(f"Error running algorithm rounds: {str(e)}")
        return jsonify({'success': False, 'message': f"Error running algorithm rounds: {str(e)}"}), 500