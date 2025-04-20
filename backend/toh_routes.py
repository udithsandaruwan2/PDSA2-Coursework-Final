from flask import Blueprint, jsonify, request  # Ensure Flask is installed in your environment
import toh_db  # Ensure toh_db is used in the code
import random  # Used for generating random disk count
import time  # Used for measuring algorithm performance
import json  # Ensure JSON is used or remove if unnecessary
import logging
import traceback  # Used for logging detailed error traces

logger = logging.getLogger(__name__)

bp = Blueprint('toh', __name__, url_prefix='/api/toh')

def solve_toh_recursive(n, source, auxiliary, destination, moves=None):
    """
    Recursive solution for Tower of Hanoi problem.
    Time complexity: O(2^n) - exponential
    Space complexity: O(n) - recursive call stack depth
    """
    if moves is None:
        moves = []
    if n <= 0:
        return moves
    if n == 1:
        moves.append([1, source, destination])
        return moves
    solve_toh_recursive(n-1, source, destination, auxiliary, moves)
    moves.append([n, source, destination])
    solve_toh_recursive(n-1, auxiliary, source, destination, moves)
    return moves

def solve_toh_iterative(n, source, auxiliary, destination):
    """
    Iterative solution for Tower of Hanoi problem.
    Time complexity: O(2^n) - exponential
    Space complexity: O(n) - to store disk positions
    """
    moves = []
    if n <= 0:
        return moves
    total_moves = (2 ** n) - 1
    towers = {'A': list(range(n, 0, -1)), 'B': [], 'C': []}
    peg_names = {source: 'A', auxiliary: 'B', destination: 'C'}

    for i in range(1, total_moves + 1):
        if i % 3 == 1:
            move_disk(towers, source, destination, moves, peg_names)
        elif i % 3 == 2:
            move_disk(towers, source, auxiliary, moves, peg_names)
        else:
            move_disk(towers, auxiliary, destination, moves, peg_names)
    return moves

def move_disk(towers, source, dest, moves, peg_names):
    """Helper function for iterative solution"""
    src_disks = towers[peg_names[source]]
    dest_disks = towers[peg_names[dest]]
    if not src_disks:
        if dest_disks:
            disk = dest_disks.pop()
            src_disks.append(disk)
            moves.append([disk, peg_names[dest], peg_names[source]])
    elif not dest_disks or src_disks[-1] < dest_disks[-1]:
        disk = src_disks.pop()
        dest_disks.append(disk)
        moves.append([disk, peg_names[source], peg_names[dest]])
    else:
        disk = dest_disks.pop()
        src_disks.append(disk)
        moves.append([disk, peg_names[dest], peg_names[source]])

def frame_stewart_algorithm(n, source, aux1, aux2, destination):
    """
    Frame-Stewart algorithm for 4-peg Tower of Hanoi.
    Time complexity: O(2^(n^0.5)) - better than standard 3-peg solution
    Space complexity: O(n) - to store disk positions
    """
    moves = []
    if n <= 0:
        return moves
    k = max(1, int((n + 1 - (2*n + 1)**0.5)))
    if n == 1:
        moves.append([1, source, destination])
        return moves

    moves.extend(frame_stewart_algorithm(k, source, aux2, destination, aux1))
    sub_moves = solve_toh_recursive(n - k, source, aux2, destination)
    for disk, src, dst in sub_moves:
        moves.append([disk + k, src, dst])
    moves.extend(frame_stewart_algorithm(k, aux1, source, aux2, destination))
    moves.extend(frame_stewart_algorithm(k, aux1, source, aux2, destination))
    peg_names = {source: 'A', aux1: 'B', aux2: 'C', destination: 'D'}
    return [[disk, peg_names[src], peg_names[dst]] for disk, src, dst in moves]

@bp.route('/new-game', methods=['GET'])
def new_game():
    """Start a new Tower of Hanoi game with random number of disks"""
    try:
        disk_count = int(request.args.get('disks', random.randint(5, 10)))
        mode = request.args.get('mode', '3peg')
        
        if not 5 <= disk_count <= 10:
            return jsonify({'error': 'Disk count must be between 5 and 10'}), 400

        logger.info(f"Starting new game with {disk_count} disks, mode: {mode}")

        start_time = time.time()
        recursive_solution = solve_toh_recursive(disk_count, 'A', 'B', 'C')
        recursive_time = time.time() - start_time

        start_time = time.time()
        iterative_solution = solve_toh_iterative(disk_count, 'A', 'B', 'C')
        iterative_time = time.time() - start_time

        start_time = time.time()
        frame_stewart_solution = frame_stewart_algorithm(disk_count, 'A', 'B', 'C', 'D')
        frame_stewart_time = time.time() - start_time

        toh_db.save_algorithm_performance(disk_count, 'recursive', 3, recursive_time)
        toh_db.save_algorithm_performance(disk_count, 'iterative', 3, iterative_time)
        toh_db.save_algorithm_performance(disk_count, 'frame_stewart', 4, frame_stewart_time)

        # Set minimum moves based on mode
        min_moves = len(frame_stewart_solution) if mode == '4peg' else (2 ** disk_count) - 1

        return jsonify({
            'disk_count': disk_count,
            'min_moves': min_moves,
            'solutions': {
                'recursive': {'moves': recursive_solution, 'time': recursive_time},
                'iterative': {'moves': iterative_solution, 'time': iterative_time},
                'frame_stewart': {'moves': frame_stewart_solution, 'time': frame_stewart_time}
            }
        })
    except ValueError as e:
        logger.error(f"Value error in new-game: {str(e)}")
        return jsonify({'error': 'Invalid input: disk count must be a number'}), 400
    except Exception as e:
        logger.error(f"Error in new-game: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Server error occurred while starting new game'}), 500

@bp.route('/validate-solution', methods=['POST'])
def validate_solution():
    """Validate user's solution to Tower of Hanoi problem"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
            
        player_name = data.get('playerName', 'Anonymous')
        disk_count = data.get('diskCount')
        moves = data.get('moves', [])
        mode = data.get('mode', '3peg')
        
        if not disk_count:
            return jsonify({'success': False, 'message': 'Disk count is required'}), 400
        if not moves:
            return jsonify({'success': False, 'message': 'Moves sequence is required'}), 400
            
        try:
            disk_count = int(disk_count)
            if disk_count < 1:
                return jsonify({'success': False, 'message': 'Disk count must be positive'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Disk count must be a number'}), 400

        valid_solution = validate_move_sequence(disk_count, moves)
        if valid_solution:
            toh_db.save_score(player_name, disk_count, len(moves), mode)
            optimal_moves = (2 ** disk_count) - 1
            is_optimal = len(moves) == optimal_moves
            
            return jsonify({
                'success': True,
                'message': f'Solution valid! Completed in {len(moves)} moves.',
                'optimal': is_optimal,
                'min_moves': optimal_moves
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid solution. Ensure all disks are moved correctly.'
            })
    except Exception as e:
        logger.error(f"Error in validate-solution: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': 'Server error occurred while validating solution'}), 500

def validate_move_sequence(disk_count, moves):
    """
    Validate if a sequence of moves correctly solves the Tower of Hanoi problem.
    Returns True if valid, False otherwise.
    """
    towers = {'A': list(range(disk_count, 0, -1)), 'B': [], 'C': [], 'D': []}
    
    for disk, source, dest in moves:
        if source not in towers or dest not in towers or not towers[source]:
            return False
            
        top_disk = towers[source][-1]
        if top_disk != disk:
            return False
            
        if towers[dest] and towers[dest][-1] < disk:
            return False
            
        towers[dest].append(towers[source].pop())
    
    target_peg = 'D' if len(towers['D']) > 0 else 'C'
    if len(towers[target_peg]) != disk_count:
        return False
        
    for i in range(len(towers[target_peg])-1):
        if towers[target_peg][i] < towers[target_peg][i+1]:
            return False
            
    return True

@bp.route('/scores', methods=['GET'])
def get_scores():
    """Get high scores from database"""
    try:
        scores = toh_db.get_scores()
        return jsonify([dict(score) for score in scores])
    except Exception as e:
        logger.error(f"Error getting scores: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Server error occurred while fetching scores'}), 500

@bp.route('/algorithm-comparison', methods=['GET'])
def get_algorithm_comparison():
    """Get algorithm performance comparison data"""
    try:
        performance_data = toh_db.get_algorithm_performance()
        return jsonify([dict(perf) for perf in performance_data])
    except Exception as e:
        logger.error(f"Error getting algorithm comparison: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Server error occurred while fetching algorithm data'}), 500