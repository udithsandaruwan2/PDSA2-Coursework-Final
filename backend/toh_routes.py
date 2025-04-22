from flask import Blueprint, jsonify, request, render_template_string
import toh_db
import random
import time
import json
import logging
import traceback

logger = logging.getLogger(__name__)

bp = Blueprint('toh', __name__, url_prefix='/api/toh')

def solve_toh_recursive(n, source, auxiliary, destination, moves=None):
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
    if n == 1:
        moves.append([1, source, destination])
        return moves
    if n == 2:
        moves.append([1, source, aux1])
        moves.append([2, source, destination])
        moves.append([1, aux1, destination])
        return moves
    if n == 3:
        moves.append([1, source, aux1])
        moves.append([2, source, aux2])
        moves.append([1, aux1, aux2])
        moves.append([3, source, destination])
        moves.append([1, aux2, aux1])
        moves.append([2, aux2, destination])
        moves.append([1, aux1, destination])
        return moves

    # Dynamically select k to minimize moves
    min_moves = float('inf')
    best_k = 1
    for k in range(1, n):
        # Estimate moves: 2 * moves for k disks + moves for n-k disks (3-peg)
        moves_k = len(frame_stewart_algorithm(k, source, aux2, destination, aux1))
        moves_nk = (2 ** (n - k)) - 1  # 3-peg recursive moves
        total = 2 * moves_k + moves_nk
        if total < min_moves:
            min_moves = total
            best_k = k

    k = best_k

    # Step 1: Move k smallest disks (1 to k) to aux1 using all 4 pegs
    moves.extend(frame_stewart_algorithm(k, source, aux2, destination, aux1))

    # Step 2: Move n-k largest disks (k+1 to n) to destination using 3 pegs
    sub_moves = solve_toh_recursive(n - k, source, aux2, destination)
    for disk, src, dst in sub_moves:
        moves.append([disk + k, src, dst])

    # Step 3: Move k smallest disks from aux1 to destination using all 4 pegs
    moves.extend(frame_stewart_algorithm(k, aux1, source, aux2, destination))

    # Map pegs to standard names (A, B, C, D)
    peg_names = {source: 'A', aux1: 'B', aux2: 'C', destination: 'D'}
    return [[disk, peg_names[src], peg_names[dst]] for disk, src, dst in moves]

@bp.route('/new-game', methods=['GET'])
def new_game():
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
            optimal_moves = len(frame_stewart_algorithm(disk_count, 'A', 'B', 'C', 'D')) if mode == '4peg' else (2 ** disk_count) - 1
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

@bp.route('/save-game-result', methods=['POST'])
def save_game_result():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        player_name = data.get('playerName', 'Anonymous')
        disk_count = data.get('diskCount')
        moves_count = data.get('movesCount')
        moves_json = data.get('movesJson')
        mode = data.get('mode', '3peg')
        score_amount = data.get('scoreAmount', 0)

        if not all([disk_count, moves_count, moves_json]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        try:
            disk_count = int(disk_count)
            moves_count = int(moves_count)
            score_amount = int(score_amount)
            if disk_count < 1 or moves_count < 1:
                return jsonify({'success': False, 'message': 'Disk count and moves count must be positive'}), 400
            if score_amount < 0:
                return jsonify({'success': False, 'message': 'Score amount must be non-negative'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Disk count, moves count, and score amount must be numbers'}), 400

        score_id = toh_db.save_game_result(player_name, disk_count, moves_count, moves_json, mode, score_amount)
        return jsonify({'success': True, 'message': 'Game result saved successfully', 'score_id': score_id})
    except Exception as e:
        logger.error(f"Error in save-game-result: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': 'Server error occurred while saving game result'}), 500

def validate_move_sequence(disk_count, moves):
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
    for i in range(len(towers[target_peg]) - 1):
        if towers[target_peg][i] < towers[target_peg][i + 1]:
            return False
    return True

@bp.route('/scores', methods=['GET'])
def get_scores():
    try:
        scores = toh_db.get_scores()
        return jsonify([dict(score) for score in scores])
    except Exception as e:
        logger.error(f"Error getting scores: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Server error occurred while fetching scores'}), 500

@bp.route('/all-scores', methods=['GET'])
def get_all_scores():
    try:
        scores = toh_db.get_all_scores()
        return jsonify([dict(score) for score in scores])
    except Exception as e:
        logger.error(f"Error getting all scores: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Server error occurred while fetching all scores'}), 500

@bp.route('/db-tables', methods=['GET'])
def get_db_tables():
    try:
        tables_data = toh_db.get_all_table_data()
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Database Tables</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { text-align: center; }
                h2 { margin-top: 20px; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
            </style>
        </head>
        <body>
            <h1>Database Tables</h1>
            {% for table_name, data in tables.items() %}
                <h2>{{ table_name }}</h2>
                <table>
                    <thead>
                        <tr>
                            {% for column in data['columns'] %}
                                <th>{{ column }}</th>
                            {% endfor %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in data['rows'] %}
                            <tr>
                                {% for value in row %}
                                    <td>{{ value }}</td>
                                {% endfor %}
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% endfor %}
        </body>
        </html>
        """
        return render_template_string(html, tables=tables_data)
    except Exception as e:
        logger.error(f"Error getting database tables: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Server error occurred while fetching database tables'}), 500

@bp.route('/algorithm-comparison', methods=['GET'])
def get_algorithm_comparison():
    try:
        performance_data = toh_db.get_algorithm_performance()
        return jsonify([dict(perf) for perf in performance_data])
    except Exception as e:
        logger.error(f"Error getting algorithm comparison: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Server error occurred while fetching algorithm data'}), 500

@bp.route('/algorithm-comparison-chart', methods=['GET'])
def get_algorithm_comparison_chart():
    try:
        performance_data = toh_db.get_algorithm_comparison_chart_data()
        return jsonify(performance_data)
    except Exception as e:
        logger.error(f"Error getting chart data: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Server error occurred while fetching chart data'}), 500