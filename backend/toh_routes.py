from flask import Blueprint, jsonify, request, render_template_string
import toh_db
import random
import time
import json
import logging
import traceback
import math
import copy

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
    
    towers = {'A': list(range(n, 0, -1)), 'B': [], 'C': []}
    peg_names = {source: 'A', auxiliary: 'B', destination: 'C'}
    
    if n % 2 == 0:
        move_order = [(source, auxiliary), (source, destination), (auxiliary, destination)]
    else:
        move_order = [(source, destination), (source, auxiliary), (auxiliary, destination)]
    
    total_moves = (2 ** n) - 1
    
    for i in range(1, total_moves + 1):
        src, dst = move_order[(i - 1) % 3]
        
        src_tower = towers[peg_names[src]]
        dst_tower = towers[peg_names[dst]]
        
        if not src_tower:
            disk = dst_tower.pop()
            src_tower.append(disk)
            moves.append([disk, peg_names[dst], peg_names[src]])
        elif not dst_tower:
            disk = src_tower.pop()
            dst_tower.append(disk)
            moves.append([disk, peg_names[src], peg_names[dst]])
        elif src_tower[-1] < dst_tower[-1]:
            disk = src_tower.pop()
            dst_tower.append(disk)
            moves.append([disk, peg_names[src], peg_names[dst]])
        else:
            disk = dst_tower.pop()
            src_tower.append(disk)
            moves.append([disk, peg_names[dst], peg_names[src]])
    
    return moves

def frame_stewart_algorithm(n, source, aux1, aux2, destination):
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

    def is_valid_move(disk, src, dst, towers):
        """Check if moving disk from src to dst is valid."""
        if src not in towers or dst not in towers:
            return False
        if not towers[src] or towers[src][-1] != disk:
            return False
        if towers[dst] and towers[dst][-1] < disk:
            return False
        return True

    def add_move(disk, src, dst, towers, moves_list):
        """Add a move if valid and update tower state."""
        if is_valid_move(disk, src, dst, towers):
            towers[src].pop()
            towers[dst].append(disk)
            moves_list.append([disk, src, dst])
            return True
        logger.error(f"Invalid move: {disk} from {src} to {dst}")
        return False

    def solve_4peg(n, src, a1, a2, dst, base_disk, towers, moves_list):
        """Recursive 4-peg solver with base_disk tracking."""
        if n <= 0:
            return
        if n == 1:
            add_move(base_disk, src, dst, towers, moves_list)
            return
        if n == 2:
            add_move(base_disk, src, a1, towers, moves_list)
            add_move(base_disk + 1, src, dst, towers, moves_list)
            add_move(base_disk, a1, dst, towers, moves_list)
            return

        # Choose k: number of disks to move to a1 in first step
        k_overrides = {3: 1, 4: 2, 5: 2, 6: 3, 7: 3, 8: 4, 9: 5, 10: 5}
        k = k_overrides.get(n, max(1, n - int(math.ceil(math.sqrt(n)))))
        if k >= n:
            k = n - 1

        # Stage 1: Move k disks from src to a1 using all four pegs
        solve_4peg(k, src, a2, dst, a1, base_disk, towers, moves_list)

        # Stage 2: Move n-k disks from src to dst using 3 pegs (a2 as auxiliary)
        sub_moves = solve_toh_recursive(n - k, src, a2, dst)
        for disk, s, d in sub_moves:
            actual_disk = base_disk + k + disk - 1  # Adjust disk number
            if not add_move(actual_disk, s, d, towers, moves_list):
                logger.error(f"Failed to add move: {actual_disk} from {s} to {d}")

        # Stage 3: Move k disks from a1 to dst using all four pegs
        solve_4peg(k, a1, src, a2, dst, base_disk, towers, moves_list)

    # Initialize tower state
    towers = {
        source: list(range(n, 0, -1)),
        aux1: [],
        aux2: [],
        destination: []
    }

    # Execute the 4-peg solver with base_disk=1
    solve_4peg(n, source, aux1, aux2, destination, 1, towers, moves)

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

        start_time = time.perf_counter()
        recursive_solution = solve_toh_recursive(disk_count, 'A', 'B', 'C')
        recursive_time = (time.perf_counter() - start_time) * 1000
        logger.debug(f"Recursive time: {recursive_time:.6f} ms")

        start_time = time.perf_counter()
        iterative_solution = solve_toh_iterative(disk_count, 'A', 'B', 'C')
        iterative_time = (time.perf_counter() - start_time) * 1000
        logger.debug(f"Iterative time: {iterative_time:.6f} ms")

        start_time = time.perf_counter()
        frame_stewart_solution = frame_stewart_algorithm(disk_count, 'A', 'B', 'C', 'D')
        frame_stewart_time = (time.perf_counter() - start_time) * 1000
        logger.debug(f"Frame-Stewart time: {frame_stewart_time:.6f} ms")

        toh_db.save_algorithm_performance(
            disk_count, 'recursive', 3, recursive_time, len(recursive_solution), recursive_solution
        )
        toh_db.save_algorithm_performance(
            disk_count, 'iterative', 3, iterative_time, len(iterative_solution), iterative_solution
        )
        toh_db.save_algorithm_performance(
            disk_count, 'frame_stewart', 4, frame_stewart_time, len(frame_stewart_solution), frame_stewart_solution
        )

        min_moves = len(frame_stewart_solution) if mode == '4peg' else (2 ** disk_count) - 1
        logger.info(f"Computed min_moves for disk_count={disk_count}, mode={mode}: {min_moves}")

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
            if mode == '4peg':
                optimal_moves = len(frame_stewart_algorithm(disk_count, 'A', 'B', 'C', 'D'))
            else:
                optimal_moves = (2 ** disk_count) - 1
                
            is_optimal = len(moves) == optimal_moves
            
            penalty_factor = min(100, 100 * (len(moves) - optimal_moves) / optimal_moves) if optimal_moves > 0 else 100
            score_amount = int(max(0, 1000 - (penalty_factor * 10)))

            return jsonify({
                'success': True,
                'message': f'Solution valid! Completed in {len(moves)} moves.',
                'optimal': is_optimal,
                'min_moves': optimal_moves,
                'score_amount': score_amount
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

        if not all([disk_count, moves_count, moves_json]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        try:
            disk_count = int(disk_count)
            moves_count = int(moves_count)
            if disk_count < 1 or moves_count < 1:
                return jsonify({'success': False, 'message': 'Disk count and moves count must be positive'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Disk count and moves count must be numbers'}), 400

        moves = json.loads(moves_json)
        valid_solution = validate_move_sequence(disk_count, moves)
        if not valid_solution:
            return jsonify({'success': False, 'message': 'Invalid move sequence'}), 400

        if mode == '4peg':
            optimal_moves = len(frame_stewart_algorithm(disk_count, 'A', 'B', 'C', 'D'))
        else:
            optimal_moves = (2 ** disk_count) - 1
            
        penalty_factor = min(100, 100 * (moves_count - optimal_moves) / optimal_moves) if optimal_moves > 0 else 100
        score_amount = int(max(0, 1000 - (penalty_factor * 10)))
        
        logger.info(f"Calculated score_amount: {score_amount} for {moves_count} moves (optimal: {optimal_moves})")

        score_id = toh_db.save_game_result(player_name, disk_count, moves_count, moves_json, mode, score_amount)
        return jsonify({
            'success': True, 
            'message': 'Game result saved successfully', 
            'score_id': score_id, 
            'score_amount': score_amount,
            'optimal_moves': optimal_moves
        })
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
                * {
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }

                body {
                    background: linear-gradient(135deg, #e0e7ff 0%, #f0f4ff 100%);
                    color: #1e293b;
                    min-height: 100vh;
                    padding: 20px;
                }

                h1 {
                    text-align: center;
                    margin-bottom: 40px;
                    font-size: 2.5rem;
                    font-weight: 700;
                    color: #1e293b;
                    letter-spacing: -0.5px;
                }

                h2 {
                    margin: 30px 0 20px;
                    font-size: 1.8rem;
                    font-weight: 600;
                    color: #334155;
                    text-align: center;
                }

                .table-container {
                    max-width: 100%;
                    margin: 0 auto;
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 12px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    backdrop-filter: blur(8px);
                    padding: 20px;
                    margin-bottom: 30px;
                }

                table {
                    width: 100%;
                    max-width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                    border-radius: 8px;
                    overflow: hidden;
                }

                th, td {
                    border: 1px solid #e2e8f0;
                    padding: 12px;
                    text-align: left;
                    font-size: 1rem;
                    color: #334155;
                }

                th {
                    background: linear-gradient(45deg, #3b82f6, #60a5fa);
                    color: #fff;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }

                td {
                    background: rgba(255, 255, 255, 0.9);
                }

                tr:nth-child(even) td {
                    background: rgba(241, 245, 249, 0.9);
                }

                tr:hover td {
                    background: rgba(203, 213, 225, 0.9);
                    transition: background 0.2s ease;
                }

                nav {
                    position: sticky;
                    top: 0;
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(8px);
                    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
                    padding: 10px 20px;
                    z-index: 1000;
                    margin-bottom: 20px;
                    border-radius: 8px;
                }

                .nav-list {
                    display: flex;
                    flex-wrap: wrap;
                    justify: center;
                    gap: 10px;
                    list-style: none;
                }

                .nav-item a {
                    display: inline-block;
                    padding: 8px 16px;
                    background: linear-gradient(45deg, #3b82f6, #60a5fa);
                    color: #fff;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 500;
                    font-size: 0.9rem;
                    transition: transform 0.2s, box-shadow 0.2s, background 0.3s;
                }

                .nav-item a:hover {
                    background: linear-gradient(45deg, #2563eb, #3b82f6);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                }

                @media (max-width: 768px) {
                    body {
                        padding: 10px;
                    }

                    h1 {
                        font-size: 2rem;
                    }

                    h2 {
                        font-size: 1.5rem;
                    }

                    .table-container {
                        padding: 15px;
                    }

                    table {
                        display: block;
                        overflow-x: auto;
                        -webkit-overflow-scrolling: touch;
                    }

                    th, td {
                        padding: 10px;
                        font-size: 0.9rem;
                    }

                    .nav-list {
                        flex-direction: column;
                        align-items: center;
                    }

                    .nav-item a {
                        width: 100%;
                        text-align: center;
                        padding: 10px;
                    }
                }

                @media (max-width: 480px) {
                    h1 {
                        font-size: 1.8rem;
                    }

                    h2 {
                        font-size: 1.3rem;
                    }

                    th, td {
                        padding: 8px;
                        font-size: 0.85rem;
                    }

                    .nav-item a {
                        font-size: 0.8rem;
                    }
                }
            </style>
        </head>
        <body>
            <h1>Database Tables</h1>
            <nav>
                <ul class="nav-list">
                    {% for table_name, data in tables.items() %}
                        <li class="nav-item"><a href="#{{ table_name }}">{{ table_name }}</a></li>
                    {% endfor %}
                </ul>
            </nav>
            {% for table_name, data in tables.items() %}
                <h2 id="{{ table_name }}">{{ table_name }}</h2>
                <div class="table-container">
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
                </div>
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
        logger.debug(f"Algorithm comparison data: {[dict(perf) for perf in performance_data]}")
        return jsonify([dict(perf) for perf in performance_data])
    except Exception as e:
        logger.error(f"Error getting algorithm comparison: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Server error occurred while fetching algorithm data'}), 500

@bp.route('/algorithm-comparison-chart', methods=['GET'])
def get_algorithm_comparison_chart():
    try:
        performance_data = toh_db.get_algorithm_performance()
        algorithms = sorted(set(perf['algorithm_type'] for perf in performance_data))
        disk_counts = sorted(set(perf['disk_count'] for perf in performance_data))
        
        result = {
            'labels': disk_counts,
            'datasets': []
        }
        
        colors = {
            'recursive': 'rgba(255, 99, 132, 0.8)',
            'iterative': 'rgba(54, 162, 235, 0.8)',
            'frame_stewart': 'rgba(75, 192, 192, 0.8)'
        }
        
        for algorithm in algorithms:
            dataset = {
                'label': algorithm.capitalize(),
                'backgroundColor': colors.get(algorithm, 'rgba(0, 0, 0, 0.8)'),
                'data': []
            }
            
            for disk_count in disk_counts:
                time_value = next((perf['avg_time'] for perf in performance_data 
                                 if perf['algorithm_type'] == algorithm and perf['disk_count'] == disk_count), 0)
                dataset['data'].append(time_value)
            
            result['datasets'].append(dataset)
        
        logger.debug(f"Algorithm comparison chart data: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting chart data: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Server error occurred while fetching chart data'}), 500

@bp.route('/rounds-comparison', methods=['GET'])
def get_rounds_comparison():
    try:
        performance_data = toh_db.get_last_10_rounds_performance()
        logger.debug(f"Rounds comparison data: {[dict(perf) for perf in performance_data]}")
        return jsonify([dict(perf) for perf in performance_data])
    except Exception as e:
        logger.error(f"Error getting rounds comparison: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Server error occurred while fetching rounds data'}), 500

@bp.route('/rounds-comparison-chart', methods=['GET'])
def get_rounds_comparison_chart():
    try:
        chart_data = toh_db.get_rounds_comparison_chart_data()
        logger.debug(f"Rounds comparison chart data: {chart_data}")
        return jsonify(chart_data)
    except Exception as e:
        logger.error(f"Error getting rounds chart data: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Server error occurred while fetching rounds chart data'}), 500