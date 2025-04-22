from flask import Blueprint, request, jsonify
from itertools import permutations, combinations
import math
import traceback
import time
import logging
from tsp_backend.tsp_db import TSPDatabase
import random
import json
import sqlite3

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

tsp_bp = Blueprint('tsp', __name__, url_prefix='/api')
db = TSPDatabase()



def total_path_distance(path):
    # This function calculates the total distance for a given route
    distance = 0
    for i in range(len(path)):
        a = path[i]
        b = path[(i + 1) % len(path)]  # This ensures the loop is closed
        distance += calculate_distance(a, b)
    return distance

def tsp_nearest_neighbor(cities):
    start_time = time.time()

    # Ensure home city is included in the path
    path = cities[:]  # The cities already include the home city at both ends
    logger.debug("Nearest Neighbor path:")
    for i in range(len(path)):
        a = path[i]
        b = path[(i + 1) % len(path)]
        d = calculate_distance(a, b)
        if d is None:
            logger.debug(f"NN: {a['id']} -> {b['id']}: Distance is None")
        else:
            if i == len(path) - 1:
                logger.debug(f"NN: {a['id']} -> {b['id']} (last to home): {d:.4f} km")
            else:
                logger.debug(f"NN: {a['id']} -> {b['id']}: {d:.4f} km")
    path_distance = total_path_distance(path)
    execution_time = time.time() - start_time

    return path, path_distance, execution_time
def tsp_branch_and_bound(cities):
    start_time = time.time()

    best_result = {
        'path': None,
        'distance': float('inf')
    }

    def bound(current_path, visited, current_distance):
        # A simple lower-bound estimate: current distance + minimal outgoing edge from last visited city
        if not current_path:
            return 0

        last_city = current_path[-1]
        remaining = [city for city in cities[1:] if city['id'] not in visited]

        min_estimate = float('inf')
        for city in remaining:
            dist = calculate_distance(last_city, city)
            if dist < min_estimate:
                min_estimate = dist

        return current_distance + (min_estimate if remaining else 0)

    def branch(current_path, visited, current_distance):
        # Prune if bound exceeds best found
        estimate = bound(current_path, visited, current_distance)
        if estimate >= best_result['distance']:
            return

        # If all cities visited (except home), finalize path
        if len(current_path) == len(cities) - 1:
            home = cities[0]
            last_city = current_path[-1]
            return_leg = calculate_distance(last_city, home)
            total_distance = current_distance + return_leg

            if current_path and current_path[-1]['id'] == home['id']:
                full_path = [home] + current_path  # Already ends in home
            else:
                full_path = [home] + current_path + [home]

            logger.debug("B&B candidate path:")
            for i in range(len(full_path) - 1):
                a = full_path[i]
                b = full_path[i + 1]
                logger.debug(f"BB: {a['id']} -> {b['id']}: {calculate_distance(a, b):.4f} km")

            if total_distance < best_result['distance']:
                best_result['distance'] = total_distance
                best_result['path'] = full_path
            return

        # Branch to unvisited cities
        for city in cities[1:]:  # Skip home city (assumed cities[0])
            if city['id'] not in visited:
                visited.add(city['id'])
                last_city = current_path[-1] if current_path else cities[0]
                dist = calculate_distance(last_city, city)
                current_path.append(city)

                branch(current_path, visited, current_distance + dist)

                current_path.pop()
                visited.remove(city['id'])

    branch([], set(), 0)

    execution_time = time.time() - start_time
    return best_result['path'], best_result['distance'], execution_time



def tsp_held_karp(cities):
    start_time = time.time()
    n = len(cities)
    if n == 1:
        return cities, 0, time.time() - start_time
    dp = {}
    parent = {}
    for i in range(1, n):
        dp[(1 << i, i)] = (calculate_distance(cities[0], cities[i]), 0)
        parent[(1 << i, i)] = 0
    for subset_size in range(2, n):
        for subset in combinations(range(1, n), subset_size):
            bits = sum(1 << i for i in subset)
            for last in subset:
                prev = bits ^ (1 << last)
                min_dist = float('inf')
                min_prev = None
                for j in subset:
                    if j == last:
                        continue
                    curr_dist = dp[(prev, j)][0] + calculate_distance(cities[j], cities[last])
                    logger.debug(f"HK: {j} -> {last}: {calculate_distance(cities[j], cities[last]):.4f} km (partial sum: {curr_dist:.4f} km)")
                    if curr_dist < min_dist:
                        min_dist = curr_dist
                        min_prev = j
                dp[(bits, last)] = (min_dist, min_prev)
                parent[(bits, last)] = min_prev
    bits = (2 ** n - 1) ^ 1
    min_dist = float('inf')
    last = None
    for i in range(1, n):
        curr_dist = dp[(bits, i)][0] + calculate_distance(cities[i], cities[0])
        logger.debug(f"HK: {i} -> 0: {calculate_distance(cities[i], cities[0]):.4f} km (final leg, total: {curr_dist:.4f} km)")
        if curr_dist < min_dist:
            min_dist = curr_dist
            last = i
    path = [0]
    bits = (2 ** n - 1) ^ 1
    current = last
    for _ in range(n - 1):
        path.append(current)
        temp = parent[(bits, current)]
        bits = bits ^ (1 << current)
        current = temp
    path = path[::-1]
    path = [cities[i] for i in path]
    logger.debug("Held-Karp final path:")
    for i in range(len(path)):
        a = path[i]
        b = path[(i + 1) % len(path)]
        d = calculate_distance(a, b)
        if i == len(path) - 1:
            logger.debug(f"HK: {a['id']} -> {b['id']} (last to home): {d:.4f} km")
        else:
            logger.debug(f"HK: {a['id']} -> {b['id']}: {d:.4f} km")
    execution_time = time.time() - start_time

    return path, min_dist, execution_time


@tsp_bp.route('/solve_tsp', methods=['POST'])
def solve_tsp():
    try:
        data = request.json
        
        distance_matrix_data = data.get('distances')
        if not distance_matrix_data:
            logger.error("Distance matrix not provided!")
            return jsonify({'error': 'Distance matrix is required'}), 400

        set_distance_matrix(distance_matrix_data)



        cities = data.get('cities')  # Full list of cities
        player_name = data.get('player_name', 'Anonymous')
        home_city_char = data.get('home_city', None)  # Home city is now a character (A, B, C, ...)
        human_route_chars = data.get('human_route', [])  # Human route is now a list of characters (A, B, C, ...)

        if not cities:
            logger.error("No cities provided in the request!")
            return jsonify({'error': 'No cities provided'}), 400

        if home_city_char is None or len(home_city_char) != 1 or not home_city_char.isalpha():
            logger.error(f"Invalid home city: {home_city_char}")
            return jsonify({'error': 'Invalid home city. Please provide a single character (A-J).'}), 400

        # Convert the home city from a character (A, B, C, ...) to a numeric index
        home_city_index = ord(home_city_char.upper()) - ord('A')  # Convert 'A' -> 0, 'B' -> 1, etc.

        # Get the home city object based on the index
        home_city = next((city for city in cities if city['id'] == home_city_index), None)
        if home_city is None:
            logger.error(f"Home city with index {home_city_index} not found in cities list!")
            return jsonify({'error': f'Home city with index {home_city_index} not found in cities list!'}), 400

        # Validate that all characters in human_route are valid (A-J)
        if any(len(city) != 1 or not city.isalpha() for city in human_route_chars):
            logger.error(f"Invalid human route characters: {human_route_chars}")
            return jsonify({'error': 'Human route contains invalid characters. Please use single alphabetic characters (A-J).'}), 400

        # Convert the human route characters (A, B, C, ...) back to the city indices
        human_route_indices = [ord(city.upper()) - ord('A') for city in human_route_chars]  # Convert A -> 0, B -> 1, etc.

        # Get the selected cities (excluding the home city from human route)
        selected_cities = [city for city in cities if city['id'] in human_route_indices]

        # Ensure the home city is at both ends of the path
        selected_cities = [home_city] + selected_cities + [home_city]

        if len(selected_cities) < 2:
            return jsonify({'error': 'At least two cities must be selected for the path'}), 400

        # ✅ VALIDATE city IDs exist in the distance matrix
# ✅ VALIDATE city IDs exist in the distance matrix
        for city in selected_cities:
            city_id_str = str(city['id'])
            if city_id_str not in distance_matrix:
                logger.error(f"City ID {city_id_str} not found in distance_matrix keys!")
                logger.debug(f"Available keys in distance_matrix: {list(distance_matrix.keys())}")
                return jsonify({'error': f"City ID {city_id_str} not in distance matrix"}), 400


        # Perform TSP calculations only on selected cities (which include home city at both ends)
        nn_path, nn_distance, nn_time = tsp_nearest_neighbor(selected_cities)
        bb_path, bb_distance, bb_time = tsp_branch_and_bound(selected_cities)
        hk_path, hk_distance, hk_time = tsp_held_karp(selected_cities)

        # Check if human route matches the best algorithm route
        best_algorithm_distance = min(nn_distance, bb_distance, hk_distance)
        human_distance = total_path_distance(selected_cities)

        response_data = {
            'nearest_neighbor': {
                'route': nn_path,
                'distance': nn_distance,
                'time': nn_time
            },
            'branch_bound': {
                'route': bb_path,
                'distance': bb_distance,
                'time': bb_time
            },
            'held_karp': {
                'route': hk_path,
                'distance': hk_distance,
                'time': hk_time
            },
            'human_route': {
                'distance': human_distance  # Now including home at both ends
            },
            'message': ""  # Placeholder for a message if the human matches the best algorithm
        }

        if human_distance <= best_algorithm_distance:
            response_data['message'] = "Congratulations! You matched the best algorithm's route!"
        else:
            response_data['message'] = "Nice try! The algorithm found a shorter route."

        logger.debug("Human route distances:")
        for i in range(len(selected_cities)):
            a = selected_cities[i]
            b = selected_cities[(i + 1) % len(selected_cities)]
            d = calculate_distance(a, b)
            logger.debug(f"Human: {a['id']} -> {b['id']}: {d:.4f} km")

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Error in solve_tsp: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f"Error in solve_tsp: {str(e)}"}), 500


@tsp_bp.route('/save_game_session', methods=['POST'])
def save_game_session():
    try:
        data = request.json
        logger.debug(f"Received game session data: {data}")

        player_name = data.get('player_name')
        home_city_char = data.get('home_city')
        selected_cities = data.get('selected_cities')
        nn_distance = round(float(data.get('nn_distance')), 1)
        bb_distance = round(float(data.get('bb_distance')), 1)
        hk_distance = round(float(data.get('hk_distance')), 1)
        nn_time = round(float(data.get('nn_time')), 1)
        bb_time = round(float(data.get('bb_time')), 1)
        hk_time = round(float(data.get('hk_time')), 1)

        # 🆕 Extract the routes
        nn_route = data.get('nn_route', [])
        bb_route = data.get('bb_route', [])
        hk_route = data.get('hk_route', [])

        # Save to DB including routes
        game_session_id = db.record_game_session(
            player_name,
            home_city_char,
            selected_cities,
            nn_distance,
            bb_distance,
            hk_distance,
            nn_time,
            bb_time,
            hk_time,
            nn_route,
            bb_route,
            hk_route
        )

        return jsonify({"message": "Game session saved successfully!", "session_id": game_session_id}), 200

    except Exception as e:
        logger.error(f"Error saving game session: {str(e)}")
        return jsonify({"error": "Error saving game session"}), 500



@tsp_bp.route('/save_win', methods=['POST'])
def save_win():
    try:
        data = request.json
        logger.debug(f"Received win data: {data}")

        # Extract data from the request
        player_name = data.get('player_name')
        home_city = data.get('home_city')
        selected_cities = data.get('selected_cities')
        human_route = data.get('human_route')
        human_distance = round(float(data.get('human_distance')), 1)
        nn_distance = round(float(data.get('nn_distance')), 1)
        bb_distance = round(float(data.get('bb_distance')), 1)
        hk_distance = round(float(data.get('hk_distance')), 1)
        nn_time = round(float(data.get('nn_time')), 1)
        bb_time = round(float(data.get('bb_time')), 1)
        hk_time = round(float(data.get('hk_time')), 1)

        nn_route = data.get('nn_route', [])
        bb_route = data.get('bb_route', [])
        hk_route = data.get('hk_route', [])

        session_id = data.get('session_id')

        # Insert the game session data into the database
        game_session_id = db.record_game_session(
            player_name,
            home_city,
            human_route,
            nn_distance,
            bb_distance,
            hk_distance,
            nn_time,
            bb_time,
            hk_time,
            nn_route,
            bb_route,
            hk_route
        )

        # Insert the win player data into the win_players table
        db.record_win_player(
            player_name,
            game_session_id,  # The ID of the session saved above
            human_route,
            human_distance
        )

        logger.debug(f"Player {player_name} win data saved successfully.")
        return jsonify({"message": "Player win saved successfully!"}), 200

    except Exception as e:
        logger.error(f"Error saving win data: {str(e)}")
        return jsonify({"error": f"Error saving win data: {str(e)}"}), 500



@tsp_bp.route('/db_viewer', methods=['GET'])
def db_viewer():
    try:
        # Get game sessions and win players data
        game_sessions = db.get_all_sessions()
        win_players = db.get_all_win_players()

        # ✅ Initialize the HTML string before appending
        html = """
        <html>
        <head>
            <style>
                table { border-collapse: collapse; margin: 20px 0; width: 100%; }
                th, td { border: 1px solid black; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h2>Game Sessions</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Player</th>
                    <th>Home City</th>
                    <th>Selected Cities</th>
                    <th>NN Distance</th>
                    <th>BB Distance</th>
                    <th>HK Distance</th>
                    <th>NN Time</th>
                    <th>BB Time</th>
                    <th>HK Time</th>
                    <th>NN Route</th>
                    <th>BB Route</th>
                    <th>HK Route</th>
                    <th>Timestamp</th>
                </tr>
        """

        for session in game_sessions:
            html += f"""
                <tr>
                    <td>{session[0]}</td>
                    <td>{session[1]}</td>
                    <td>{session[2]}</td>
                    <td>{session[3]}</td>
                    <td>{session[4]}</td>
                    <td>{session[5]}</td>
                    <td>{session[6]}</td>
                    <td>{session[7]}</td>
                    <td>{session[8]}</td>
                    <td>{session[9]}</td>
                    <td>{session[10]}</td>
                    <td>{session[11]}</td>
                    <td>{session[12]}</td>
                    <td>{session[13]}</td>
                </tr>
            """

        html += """
            </table>
            <h2>Win Players</h2>
            <table>
                <tr>
                    <th>Player Name</th>
                    <th>Human Route</th>
                    <th>Human Distance</th>
                    <th>Session ID</th>
                </tr>
        """

        for win_player in win_players:
            html += f"""
                <tr>
                    <td>{win_player[0]}</td>
                    <td>{win_player[1]}</td>
                    <td>{win_player[2]}</td>
                    <td>{win_player[3]}</td>
                </tr>
            """

        html += """
            </table>
        </body>
        </html>
        """

        return html

    except Exception as e:
        return f"Error viewing database: {str(e)}", 500


# Global holder (in memory for now)
distance_matrix = {}

def set_distance_matrix(matrix):
    global distance_matrix
    distance_matrix = {
        str(k): {str(sub_k): v for sub_k, v in sub.items()}
        for k, sub in matrix.items()
    }



def calculate_distance(a, b):
    global distance_matrix

    a_id = str(a['id'])
    b_id = str(b['id'])

    try:
        d = distance_matrix[a_id][b_id]
        if d is None:
            logger.warning(f"Distance between {a_id} and {b_id} is None (possibly same city)")
            return 0.0
        return d
    except KeyError as e:
        logger.error(f"City ID {e} not found in distance_matrix keys!")
        logger.debug(f"Available keys in distance_matrix: {list(distance_matrix.keys())}")
        raise


def generate_city_list():
    return [{'id': i, 'name': chr(65 + i), 'x': 0, 'y': 0} for i in range(10)]



def generate_random_distance_matrix(num_cities=10, min_km=50, max_km=100):
    matrix = {}
    for i in range(num_cities):
        matrix[i] = {}
        for j in range(num_cities):
            if i == j:
                matrix[i][j] = None
            elif j in matrix and i in matrix[j]:
                # Mirror the upper triangle to lower (symmetric)
                matrix[i][j] = matrix[j][i]
            else:
                matrix[i][j] = round(random.uniform(min_km, max_km), 2)
    return matrix

@tsp_bp.route('/get_city_distances', methods=['GET'])
def get_city_distances():
    try:
        cities = generate_city_list()
        matrix = generate_random_distance_matrix()
        set_distance_matrix(matrix)  # <- This sets the global matrix

        return jsonify({
            'cities': cities,
            'distances': matrix
        })
    except Exception as e:
        logger.error(f"Error generating random city distances: {str(e)}")
        return jsonify({'error': 'Failed to generate distances'}), 500
