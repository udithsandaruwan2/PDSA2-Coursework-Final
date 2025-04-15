import sqlite3
import json
import os
from datetime import datetime

class TSPDatabase:
    def __init__(self, db_path="database/salesman.db"):
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(current_dir, db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        print(f"Database path: {self.db_path}")
        self.initialize_db()

    def initialize_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Store player, home city, selected cities, and distance matrix
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS game_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_name TEXT NOT NULL,
                        home_city TEXT NOT NULL,
                        selected_cities TEXT NOT NULL,     -- JSON list of selected cities
                        distance_matrix TEXT,     -- JSON 2D array, can be NULL
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Store results for each algorithm
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS algorithm_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game_session_id INTEGER,
                        algorithm_name TEXT NOT NULL,
                        route TEXT NOT NULL,             -- JSON list of city ids or coords
                        distance REAL NOT NULL,
                        execution_time REAL NOT NULL,
                        complexity_analysis TEXT,
                        FOREIGN KEY (game_session_id) REFERENCES game_sessions(id)
                    )
                ''')

                conn.commit()
            print("Database tables created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")

    def record_game_session(self, player_name, home_city, cities, distance_matrix=None):
        print(f"Recording game session for player: {player_name}, Home City: {home_city}, Cities: {cities}")
        cities_json = json.dumps(cities)
        distance_matrix_json = json.dumps(distance_matrix) if distance_matrix else None
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO game_sessions (player_name, home_city, selected_cities, distance_matrix)
                    VALUES (?, ?, ?, ?)
                ''', (player_name, home_city, cities_json, distance_matrix_json))
                conn.commit()
                print(f"Game session inserted successfully with ID {cursor.lastrowid}")
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error inserting game session: {e}")
            return None

    def record_algorithm_result(self, game_session_id, algorithm_name, route, distance, execution_time, complexity):
        try:
            route_json = json.dumps(route)
            complexity_str = json.dumps(complexity)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO algorithm_results (game_session_id, algorithm_name, route, distance, execution_time, complexity_analysis)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (game_session_id, algorithm_name, route_json, distance, execution_time, complexity_str))
                conn.commit()
                print(f"Algorithm result for {algorithm_name} inserted successfully.")
        except sqlite3.Error as e:
            print(f"Error inserting algorithm result: {e}")

    def get_all_sessions(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM game_sessions ORDER BY timestamp DESC')
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching sessions: {e}")
            return []

    def get_all_algorithm_results(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM algorithm_results ORDER BY game_session_id DESC, algorithm_name')
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching algorithm results: {e}")
            return []

    def get_algorithm_stats(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT algorithm_name,
                           AVG(execution_time),
                           MIN(execution_time),
                           MAX(execution_time),
                           AVG(distance)
                    FROM algorithm_results
                    GROUP BY algorithm_name
                ''')
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching stats: {e}")
            return []

# Algorithm complexity metadata
COMPLEXITY_INFO = {
    "nearest_neighbor": {
        "time_complexity": "O(n²)",
        "space_complexity": "O(n)",
        "description": "Greedy approach choosing nearest unvisited city at each step."
    },
    "brute_force": {
        "time_complexity": "O(n!)",
        "space_complexity": "O(n)",
        "description": "Evaluates every possible permutation to find optimal solution."
    },
    "held_karp": {
        "time_complexity": "O(n²·2ⁿ)",
        "space_complexity": "O(n·2ⁿ)",
        "description": "Dynamic programming solution using memoization and subsets."
    }
}
