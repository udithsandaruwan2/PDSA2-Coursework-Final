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

# Calculate Euclidean distance and then convert it to kilometers
def calculate_distance(a, b):
    # Calculate Euclidean distance
    distance_in_units = math.hypot(a['x'] - b['x'], a['y'] - b['y'])
    
    # Scale by 10 if the canvas units represent 10 km each
    distance_in_km = distance_in_units / 10  # Adjust if needed
    return distance_in_km


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
    home_city = cities[0]
    unvisited = cities[1:]  # Remove home city from unvisited list
    path = [home_city]  # Start the path with the home city
    
    while unvisited:
        last = path[-1]
        next_city = min(unvisited, key=lambda c: calculate_distance(last, c))
        path.append(next_city)
        unvisited.remove(next_city)
    
    # Calculate total distance for the path, ensuring to close the loop to home city
    path_distance = total_path_distance(path + [home_city])
    execution_time = time.time() - start_time
    
    return path, path_distance, execution_time


def tsp_brute_force(cities):
    start_time = time.time()
    
    best_path = None
    best_distance = float('inf')
    print("Brute Force path calculation:")

    for perm in permutations(cities):
        distance = total_path_distance(perm)
        print(f"Permutation: {[city['id'] for city in perm]} - Distance: {distance:.2f} km")
        if distance < best_distance:
            best_path = perm
            best_distance = distance

    execution_time = time.time() - start_time
    print(f"Total Brute Force distance: {best_distance:.2f} km")
    return list(best_path), best_distance, execution_time


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
    print("Held-Karp path calculation:")
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
                    print(f"Subset {subset} - Distance from C{cities[j]['id']} to C{cities[last]['id']}: {curr_dist:.2f} km")
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
        print(f"Distance from C{cities[i]['id']} to C{cities[0]['id']}: {curr_dist:.2f} km")
        if curr_dist < min_dist:
            min_dist = curr_dist
            last = i
    # Reconstruct path
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
    execution_time = time.time() - start_time
    print(f"Total Held-Karp distance: {min_dist:.2f} km")
    return path, min_dist, execution_time


@tsp_bp.route('/solve_tsp', methods=['POST'])
def solve_tsp():
    try:
        data = request.json
        logger.debug(f"Received request data: {data}")  # Log the received data
        
        cities = data.get('cities')
        player_name = data.get('player_name', 'Anonymous')
        home_city = data.get('home_city', 'Unknown')
        human_route = data.get('human_route', [])

        if not cities:
            logger.error("No cities provided in the request!")
            return jsonify({'error': 'No cities provided'}), 400

        logger.info(f"Processing cities: {cities}")  # Log the cities being processed

        # Perform TSP calculations
        nn_path, nn_distance, nn_time = tsp_nearest_neighbor(cities)
        bf_path, bf_distance, bf_time = tsp_brute_force(cities)
        hk_path, hk_distance, hk_time = tsp_held_karp(cities)

        # Log the results
        logger.debug(f"Nearest Neighbor Result: {nn_path}, {nn_distance}, {nn_time}")
        logger.debug(f"Brute Force Result: {bf_path}, {bf_distance}, {bf_time}")
        logger.debug(f"Held-Karp Result: {hk_path}, {hk_distance}, {hk_time}")

        # Build the full human route: home -> cities -> home
        full_human_route = [cities[0], *human_route, cities[0]]
        
        # Calculate the human route distance with the return to the home city
        human_distance = total_path_distance(full_human_route)

        # Return algorithm results with human distance added
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
                'distance': human_distance  # Add human distance to the response
            }
        }

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
