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

                #Delete existing tables if they exist
                cursor.execute('DROP TABLE IF EXISTS game_sessions')
                cursor.execute('DROP TABLE IF EXISTS win_players')

                # Create game_sessions table
                # Update this inside CREATE TABLE IF NOT EXISTS game_sessions:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS game_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_name TEXT NOT NULL,
                        home_city TEXT NOT NULL,
                        selected_cities TEXT NOT NULL,
                        nn_distance REAL NOT NULL,
                        bf_distance REAL NOT NULL,
                        hk_distance REAL NOT NULL,
                        nn_time REAL NOT NULL,
                        bf_time REAL NOT NULL,
                        hk_time REAL NOT NULL,
                        nn_route TEXT,  -- NEW
                        bf_route TEXT,  -- NEW
                        hk_route TEXT,  -- NEW
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Create win_players table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS win_players (
                        player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_name TEXT,
                        session_id INTEGER,
                        human_route TEXT NOT NULL,
                        human_distance REAL NOT NULL,
                        FOREIGN KEY (session_id) REFERENCES game_sessions(id)
                    )
                ''')

                conn.commit()
            print("Database tables created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")

    def record_game_session(
        self, player_name, home_city, selected_cities,
        nn_distance, bf_distance, hk_distance,
        nn_time, bf_time, hk_time,
        nn_route=None, bf_route=None, hk_route=None
    ):
        try:
            selected_cities_json = json.dumps(selected_cities)
            nn_route_json = json.dumps(nn_route or [])
            bf_route_json = json.dumps(bf_route or [])
            hk_route_json = json.dumps(hk_route or [])

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO game_sessions (
                        player_name, home_city, selected_cities,
                        nn_distance, bf_distance, hk_distance,
                        nn_time, bf_time, hk_time,
                        nn_route, bf_route, hk_route
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    player_name, home_city, selected_cities_json,
                    nn_distance, bf_distance, hk_distance,
                    nn_time, bf_time, hk_time,
                    nn_route_json, bf_route_json, hk_route_json
                ))
                conn.commit()
                print(f"Game session inserted successfully with ID {cursor.lastrowid}")
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error inserting game session: {e}")
            return None


    def record_win_player(self, player_name, session_id, human_route, human_distance):
        try:
            human_route_json = json.dumps(human_route)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO win_players (player_name, session_id, human_route, human_distance)
                    VALUES (?, ?, ?, ?)
                ''', (player_name, session_id, human_route_json, human_distance))
                conn.commit()
                print(f"Win player data inserted successfully for player {player_name}.")
        except sqlite3.Error as e:
            print(f"Error inserting win player data: {e}")

    def get_all_sessions(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM game_sessions ORDER BY timestamp DESC')
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching sessions: {e}")
            return []

    def get_all_win_players(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT wp.player_name, wp.human_route, wp.human_distance, wp.session_id
                    FROM win_players wp
                ''')
                rows = cursor.fetchall()

                # Debug: Print out rows for inspection
                print(f"Fetched rows from win_players: {rows}")

                # Make sure rows are not empty
                if not rows:
                    print("No win players found in the database.")
                    return []

                # Ensure that every row contains exactly 4 elements
                cleaned_rows = []
                for row in rows:
                    if len(row) == 4:  # Expected number of columns
                        cleaned_rows.append(row)
                    else:
                        print(f"Skipping malformed row (incorrect number of columns): {row}")

                return cleaned_rows
        except sqlite3.Error as e:
            print(f"Error fetching win players data: {e}")
            return []
