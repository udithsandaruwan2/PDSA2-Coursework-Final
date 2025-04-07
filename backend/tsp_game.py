from itertools import permutations
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

    
