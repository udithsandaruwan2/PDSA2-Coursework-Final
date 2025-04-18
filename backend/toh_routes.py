from flask import Blueprint, jsonify, request
import toh_db
import random
import time
import json

bp = Blueprint('toh', __name__, url_prefix='/api/toh')

# Tower of Hanoi Algorithms
def solve_toh_recursive(n, source, auxiliary, destination, moves=None):
    """Recursive solution for Tower of Hanoi."""
    if moves is None:
        moves = []
    
    if n == 1:
        moves.append((source, destination))
        return moves
    
    solve_toh_recursive(n-1, source, destination, auxiliary, moves)
    moves.append((source, destination))
    solve_toh_recursive(n-1, auxiliary, source, destination, moves)
    
    return moves

def solve_toh_iterative(n, source, auxiliary, destination):
    """Iterative solution for Tower of Hanoi."""
    moves = []
    
    # For odd number of disks
    if n % 2 == 1:
        pegs = [destination, auxiliary, source]
    # For even number of disks
    else:
        pegs = [auxiliary, destination, source]
    
    total_moves = (2 ** n) - 1
    
    for i in range(1, total_moves + 1):
        if i % 3 == 1:
            moves.append((source, pegs[0]))
        elif i % 3 == 2:
            moves.append((source, pegs[1]))
        else:
            moves.append((pegs[1], pegs[0]))
    
    # Convert to correct peg names
    named_moves = []
    peg_names = {source: 'A', auxiliary: 'B', destination: 'C'}
    for src, dst in moves:
        named_moves.append((peg_names[src], peg_names[dst]))
    
    return named_moves

def frame_stewart_algorithm(n, source, auxiliary1, auxiliary2, destination):
    """Frame-Stewart algorithm for 4 pegs Tower of Hanoi."""
    moves = []
    
    # Calculate optimal k based on Frame-Stewart algorithm
    # This is an approximation that works well in practice
    k = int(n - (2*n)**0.5)
    
    if k < 1:
        k = 1
    
    if n == 0:
        return moves
    
    if n == 1:
        moves.append((source, destination))
        return moves
    
    # Move top k disks from source to auxiliary1 using all 4 pegs
    moves.extend(frame_stewart_algorithm(k, source, auxiliary2, destination, auxiliary1))
    
    # Move remaining n-k disks from source to destination using the classic 3-peg algorithm
    # (using only source, auxiliary2, and destination)
    moves.extend(solve_toh_recursive(n-k, source, auxiliary2, destination))
    
    # Move k disks from auxiliary1 to destination using all 4 pegs
    moves.extend(frame_stewart_algorithm(k, auxiliary1, source, auxiliary2, destination))
    
    # Convert to correct peg names
    named_moves = []
    peg_names = {source: 'A', auxiliary1: 'B', auxiliary2: 'C', destination: 'D'}
    for src, dst in moves:
        named_moves.append((peg_names[src], peg_names[dst]))
    
    return named_moves

@bp.route('/new-game', methods=['GET'])
def new_game():
    """Initialize a new game with random disk count."""
    disk_count = random.randint(5, 10)
    
    # Calculate solutions with timing
    # 3-peg recursive solution
    start_time = time.time()
    recursive_solution = solve_toh_recursive(disk_count, 'A', 'B', 'C')
    recursive_time = time.time() - start_time
    
    # 3-peg iterative solution
    start_time = time.time()
    iterative_solution = solve_toh_iterative(disk_count, 'A', 'B', 'C')
    iterative_time = time.time() - start_time
    
    # 4-peg Frame-Stewart solution
    start_time = time.time()
    frame_stewart_solution = frame_stewart_algorithm(disk_count, 'A', 'B', 'C', 'D')
    frame_stewart_time = time.time() - start_time
    
    # Save algorithm performance data
    toh_db.save_algorithm_performance(disk_count, 'recursive', 3, recursive_time)
    toh_db.save_algorithm_performance(disk_count, 'iterative', 3, iterative_time)
    toh_db.save_algorithm_performance(disk_count, 'frame_stewart', 4, frame_stewart_time)
    
    return jsonify({
        'disk_count': disk_count,
        'min_moves': (2 ** disk_count) - 1,
        'solutions': {
            'recursive': {
                'moves': recursive_solution,
                'time': recursive_time
            },
            'iterative': {
                'moves': iterative_solution,
                'time': iterative_time
            },
            'frame_stewart': {
                'moves': frame_stewart_solution,
                'time': frame_stewart_time
            }
        }
    })

@bp.route('/validate-solution', methods=['POST'])
def validate_solution():
    """Validate a user's solution."""
    data = request.json
    player_name = data.get('playerName', 'Anonymous')
    disk_count = data.get('diskCount')
    moves = data.get('moves', [])
    
    # Simple validation - check if the number of moves is optimal
    optimal_moves = (2 ** disk_count) - 1
    
    # Validate the sequence of moves
    valid_solution = validate_move_sequence(disk_count, moves)
    
    if valid_solution:
        # Save to database
        toh_db.save_game_result(player_name, disk_count, len(moves), json.dumps(moves))
        
        return jsonify({
            'success': True,
            'message': f'Congratulations! You solved it in {len(moves)} moves.',
            'optimal': len(moves) == optimal_moves
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Your solution is not valid. Please check the rules and try again.'
        })

def validate_move_sequence(disk_count, moves):
    """Validate a sequence of moves for Tower of Hanoi."""
    # Initialize the towers
    towers = {
        'A': list(range(disk_count, 0, -1)),  # Largest disk at the bottom
        'B': [],
        'C': [],
        'D': []  # For 4-peg version
    }
    
    # Process each move
    for move in moves:
        source = move[0]
        destination = move[1]
        
        # Check if source tower has disks
        if not towers[source]:
            return False
        
        # Check if move is valid (smaller disk onto larger disk or empty peg)
        disk_to_move = towers[source][-1]
        if towers[destination] and towers[destination][-1] < disk_to_move:
            return False
        
        # Perform the move
        towers[destination].append(towers[source].pop())
    
    # Check if all disks are on peg C (for 3-peg) or D (for 4-peg)
    if len(towers['C']) == disk_count or (len(towers['D']) == disk_count):
        return True
    return False

@bp.route('/scores', methods=['GET'])
def get_scores():
    """Get top scores."""
    scores = toh_db.get_top_scores()
    return jsonify(scores)

@bp.route('/algorithm-comparison', methods=['GET'])
def get_algorithm_comparison():
    """Get algorithm comparison data."""
    data = toh_db.get_algorithm_comparisons()
    return jsonify(data)