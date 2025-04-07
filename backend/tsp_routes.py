from itertools import permutations, combinations
import math

def calculate_distance(a, b):
    return math.hypot(a['x'] - b['x'], a['y'] - b['y'])

def total_path_distance(path):
    distance = 0
    for i in range(len(path)):
        a = path[i]
        b = path[(i + 1) % len(path)]  # loop back to start
        distance += calculate_distance(a, b)
    return distance

def tsp_nearest_neighbor(cities):
    unvisited = cities[:]
    path = [unvisited.pop(0)]
    while unvisited:
        last = path[-1]
        next_city = min(unvisited, key=lambda c: calculate_distance(last, c))
        path.append(next_city)
        unvisited.remove(next_city)
    return path, total_path_distance(path)

def tsp_brute_force(cities):
    best_path = None
    best_distance = float('inf')

    for perm in permutations(cities):
        distance = total_path_distance(perm)
        if distance < best_distance:
            best_path = perm
            best_distance = distance

    return list(best_path), best_distance

def tsp_held_karp(cities):
    n = len(cities)
    # If we have only one city, return it
    if n == 1:
        return cities[0], 0
        
    # Initialize the dynamic programming table
    dp = {}
    parent = {}  # To reconstruct the path
    
    # Initialize distances for subsets of size 2 (from the home city)
    for i in range(1, n):
        dp[(1 << i, i)] = (calculate_distance(cities[0], cities[i]), 0)
        parent[(1 << i, i)] = 0

    # Process subsets of increasing size
    for subset_size in range(2, n):
        for subset in combinations(range(1, n), subset_size):
            bits = sum(1 << i for i in subset)
            for last in subset:
                prev = bits ^ (1 << last)
                min_dist = float('inf')
                min_prev = None
                
                # Find the best previous state
                for j in subset:
                    if j == last:
                        continue
                    curr_dist = dp[(prev, j)][0] + calculate_distance(cities[j], cities[last])
                    if curr_dist < min_dist:
                        min_dist = curr_dist
                        min_prev = j
                        
                dp[(bits, last)] = (min_dist, min_prev)
                parent[(bits, last)] = min_prev

    # Find the optimal tour length
    bits = (2 ** n - 1) ^ 1  # All cities except 0
    min_dist = float('inf')
    last = None
    
    for i in range(1, n):
        curr_dist = dp[(bits, i)][0] + calculate_distance(cities[i], cities[0])
        if curr_dist < min_dist:
            min_dist = curr_dist
            last = i

    # Reconstruct the path
    path = []
    curr = last
    curr_bits = bits
    while curr != 0:
        path.append(cities[curr])
        temp = curr
        curr = parent[(curr_bits, curr)]
        curr_bits = curr_bits ^ (1 << temp)
    
    path.append(cities[0])
    path.reverse()
    
    return path, min_dist

# Example Flask endpoint update
from flask import Blueprint, request, jsonify
import traceback

tsp_bp = Blueprint('tsp', __name__, url_prefix='/api')  # Add url_prefix for better organization

@tsp_bp.route('/solve_tsp', methods=['POST'])  # Ensure POST method is allowed
def solve_tsp():
    try:
        print("Received solve_tsp request")
        data = request.json
        cities = data.get('cities')
        
        if not cities:
            print("No cities provided in request")
            return jsonify({'error': 'No cities provided'}), 400

        print(f"Processing {len(cities)} cities")
        
        try:
            print("Running Nearest Neighbor algorithm...")
            nn_path, nn_distance = tsp_nearest_neighbor(cities)
            print(f"NN complete: distance = {nn_distance}")
        except Exception as e:
            print(f"Error in nearest neighbor: {str(e)}")
            raise

        try:
            print("Running Brute Force algorithm...")
            bf_path, bf_distance = tsp_brute_force(cities)
            print(f"BF complete: distance = {bf_distance}")
        except Exception as e:
            print(f"Error in brute force: {str(e)}")
            raise

        try:
            print("Running Held-Karp algorithm...")
            hk_path, hk_distance = tsp_held_karp(cities)
            print(f"HK complete: distance = {hk_distance}")
        except Exception as e:
            print(f"Error in Held-Karp: {str(e)}")
            raise

        response_data = {
            'nearest_neighbor': {
                'route': nn_path,
                'distance': nn_distance
            },
            'brute_force': {
                'route': bf_path,
                'distance': bf_distance
            },
            'held_karp': {
                'route': hk_path,
                'distance': hk_distance
            }
        }
        print("Sending response:", response_data)
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in solve_tsp: {str(e)}")
        print(f"Error traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
