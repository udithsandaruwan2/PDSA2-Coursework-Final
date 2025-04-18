from flask import Blueprint, request, jsonify
from itertools import permutations, combinations
import math
import traceback
import time
import logging
from tsp_db import TSPDatabase
import random
import json
import sqlite3

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

tsp_bp = Blueprint('tsp', __name__, url_prefix='/api')
db = TSPDatabase()

def calculate_distance(a, b):
    # Calculate Euclidean distance
    distance_in_units = math.hypot(a['x'] - b['x'], a['y'] - b['y'])
    # Scale by 10 if the canvas units represent 10 km each
    distance_in_km = distance_in_units / 10  # Adjust if needed
    return distance_in_km

# Update total_path_distance to scale the distance properly
def total_path_distance(path):
    # This function calculates the total distance for a given route
    distance = 0
    for i in range(len(path)):
        a = path[i]
        b = path[(i + 1) % len(path)]  # This ensures the loop is closed (return to home)
        distance += calculate_distance(a, b)
    return distance



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
        if i == len(path) - 1:
            logger.debug(f"NN: {a['id']} -> {b['id']} (last to home): {d:.4f} km")
        else:
            logger.debug(f"NN: {a['id']} -> {b['id']}: {d:.4f} km")
    path_distance = total_path_distance(path)
    execution_time = time.time() - start_time

    return path, path_distance, execution_time


def tsp_brute_force(cities):
    start_time = time.time()

    best_path = None
    best_distance = float('inf')

    # Brute force all permutations of cities (including the home city at both ends)
    for perm in permutations(cities[1:-1]):  # Exclude the home city from permutations
        full_perm = [cities[0]] + list(perm) + [cities[0]]  # Add home city at both ends
        logger.debug("Brute Force candidate path:")
        for i in range(len(full_perm)):
            a = full_perm[i]
            b = full_perm[(i + 1) % len(full_perm)]
            d = calculate_distance(a, b)
            if i == len(full_perm) - 1:
                logger.debug(f"BF: {a['id']} -> {b['id']} (last to home): {d:.4f} km")
            else:
                logger.debug(f"BF: {a['id']} -> {b['id']}: {d:.4f} km")
        distance = total_path_distance(full_perm)
        if distance < best_distance:
            best_path = full_perm
            best_distance = distance

    execution_time = time.time() - start_time

    return best_path, best_distance, execution_time


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
        logger.debug(f"Received request data: {data}")

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

        # Perform TSP calculations only on selected cities (which include home city at both ends)
        nn_path, nn_distance, nn_time = tsp_nearest_neighbor(selected_cities)
        bf_path, bf_distance, bf_time = tsp_brute_force(selected_cities)
        hk_path, hk_distance, hk_time = tsp_held_karp(selected_cities)

        # Check if human route matches the best algorithm route
        best_algorithm_distance = min(nn_distance, bf_distance, hk_distance)
        human_distance = total_path_distance(selected_cities)

        response_data = {
            'nearest_neighbor': {
                'route': json.dumps(nn_path),
                'distance': nn_distance,
                'time': nn_time
            },
            'brute_force': {
                'route': json.dumps(bf_path),
                'distance': bf_distance,
                'time': bf_time
            },
            'held_karp': {
                'route': json.dumps(hk_path),
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
        return jsonify({'error': f"Error in solve_tsp: {str(e)}"}), 500



@tsp_bp.route('/save_game_session', methods=['POST'])
def save_game_session():
    try:
        data = request.json
        logger.debug(f"Received game session data: {data}")

        # Extract data from the request
        player_name = data.get('player_name')
        home_city_char = data.get('home_city')  # Now home city is passed as a character (A, B, C)
        selected_cities = data.get('selected_cities')  # Selected cities are passed as alphabetic chars
        nn_distance = round(float(data.get('nn_distance')), 1)
        bf_distance = round(float(data.get('bf_distance')), 1)
        hk_distance = round(float(data.get('hk_distance')), 1)
        nn_time = round(float(data.get('nn_time')), 1)
        bf_time = round(float(data.get('bf_time')), 1)
        hk_time = round(float(data.get('hk_time')), 1)


        # Record the game session
        game_session_id = db.record_game_session(
            player_name,
            home_city_char,
            selected_cities,
            nn_distance,
            bf_distance,
            hk_distance,
            nn_time,
            bf_time,
            hk_time
        )

        # Return success message
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
        bf_distance = round(float(data.get('bf_distance')), 1)
        hk_distance = round(float(data.get('hk_distance')), 1)
        nn_time = round(float(data.get('nn_time')), 1)
        bf_time = round(float(data.get('bf_time')), 1)
        hk_time = round(float(data.get('hk_time')), 1)

        session_id = data.get('session_id')

        # Insert the game session data into the database
        game_session_id = db.record_game_session(
            player_name,
            home_city,
            human_route,
            nn_distance,
            bf_distance,
            hk_distance,
            nn_time,
            bf_time,
            hk_time
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
        
        # Prepare HTML for displaying sessions
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
                    <th>BF Distance</th>
                    <th>HK Distance</th>
                    <th>NN Time</th>
                    <th>BF Time</th>
                    <th>HK Time</th>
                    <th>Timestamp</th>
                </tr>
        """
        
        # Display game sessions
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
        
        # Display win players
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
