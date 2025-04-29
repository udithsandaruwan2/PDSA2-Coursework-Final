import requests
import random
import time
import csv

API_URL = "http://127.0.0.1:5000/api/solve_tsp"

def generate_city_list(n=10):
    return [{'id': i, 'name': chr(65 + i)} for i in range(n)]

def generate_distance_matrix(n=10, min_km=50, max_km=100):
    matrix = {}
    for i in range(n):
        matrix[i] = {}
        for j in range(n):
            if i == j:
                matrix[i][j] = None
            elif j in matrix and i in matrix[j]:
                matrix[i][j] = matrix[j][i]
            else:
                matrix[i][j] = round(random.uniform(min_km, max_km), 2)
    return matrix

def simulate_game_round(round_number):
    NUM_SELECTED_CITIES = 5  # fixed number of cities to visit (excluding home)
    all_cities = generate_city_list()
    distance_matrix = generate_distance_matrix()

    all_city_ids = list(range(10))
    home_index = random.choice(all_city_ids)

    # Select cities to visit, excluding home
    remaining_ids = [i for i in all_city_ids if i != home_index]
    selected_city_ids = random.sample(remaining_ids, NUM_SELECTED_CITIES)

    visited_chars = [chr(65 + city_id) for city_id in selected_city_ids]
    home_char = chr(65 + home_index)

    payload = {
        "player_name": f"Tester_{round_number}",
        "home_city": home_char,
        "human_route": visited_chars,
        "cities": all_cities,
        "distances": distance_matrix
    }

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return {
            "Round": round_number,
            "NumCities": NUM_SELECTED_CITIES,
            "NN_Time": round(data["nearest_neighbor"]["time"] * 1000, 2),
            "BB_Time": round(data["branch_bound"]["time"] * 1000, 2),
            "HK_Time": round(data["held_karp"]["time"] * 1000, 2),
            "NN_Distance": round(data["nearest_neighbor"]["distance"], 2),
            "BB_Distance": round(data["branch_bound"]["distance"], 2),
            "HK_Distance": round(data["held_karp"]["distance"], 2),
            "Human_Distance": round(data["human_route"]["distance"], 2),
        }
    except Exception as e:
        print(f"[ERROR] Round {round_number} failed: {e}")
        return None

def main():
    results = []
    print("Starting simulation of 10 game rounds...\n")

    for i in range(1, 11):
        print(f"Running round {i}...")
        result = simulate_game_round(i)
        if result:
            results.append(result)

    print("\nSimulation complete.\n")

    # Output results
    for row in results:
        print(row)

    # Save to CSV
    if results:
        with open("game_rounds_data.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

        print("\nSaved results to game_rounds_data.csv")

if __name__ == "__main__":
    main()