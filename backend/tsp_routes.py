from flask import Blueprint, request, jsonify
from itertools import permutations, combinations
import math
import traceback
import time
import logging
from tsp_db import TSPDatabase, COMPLEXITY_INFO
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
        home_city_id = data.get('home_city', None)
        human_route = data.get('human_route', [])

        if not cities:
            logger.error("No cities provided in the request!")
            return jsonify({'error': 'No cities provided'}), 400

        if home_city_id is None:
            logger.error("Home city ID is missing!")
            return jsonify({'error': 'Home city ID is missing'}), 400

        # Get the home city object
        home_city = next((city for city in cities if city['id'] == home_city_id), None)
        if home_city is None:
            logger.error(f"Home city with id {home_city_id} not found in cities list!")
            return jsonify({'error': f'Home city with id {home_city_id} not found in cities list!'}), 400

        # Get only the user-selected cities
        selected_cities = [city for city in cities if city['id'] in human_route]

        # Ensure the home city is at both ends of the path
        selected_cities = [home_city] + selected_cities + [home_city]

        if len(selected_cities) < 2:
            return jsonify({'error': 'At least two cities must be selected for the path'}), 400

        # Perform TSP calculations only on selected cities (which include home city at both ends)
        nn_path, nn_distance, nn_time = tsp_nearest_neighbor(selected_cities)
        bf_path, bf_distance, bf_time = tsp_brute_force(selected_cities)
        hk_path, hk_distance, hk_time = tsp_held_karp(selected_cities)

        # Return the results as JSON
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
                'distance': total_path_distance(selected_cities)  # Now including home at both ends
            }
        }
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


@tsp_bp.route('/db_viewer', methods=['GET'])
def db_viewer():
    """View database contents in a simple HTML format"""
    try:
        sessions = db.get_all_sessions()
        results = db.get_all_algorithm_results()
        
        html = """
        <html>
        <head>
            <style>
                table { border-collapse: collapse; margin: 20px 0; }
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
                    <th>Timestamp</th>
                </tr>
        """
        
        for session in sessions:
            html += f"<tr><td>{session[0]}</td><td>{session[1]}</td><td>{session[2]}</td><td>{session[4]}</td></tr>"
            
        html += """
            </table>
            <h2>Algorithm Results</h2>
            <table>
                <tr>
                    <th>Session ID</th>
                    <th>Algorithm</th>
                    <th>Distance</th>
                    <th>Time (ms)</th>
                </tr>
        """
        
        for result in results:
            html += f"<tr><td>{result[1]}</td><td>{result[2]}</td><td>{result[4]:.2f}</td><td>{result[5]*1000:.2f}</td></tr>"
            
        html += """
            </table>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        return f"Error viewing database: {str(e)}", 500