import sqlite3
import os
import json
from datetime import datetime
from tic_tac_toe_backend.GameEngine import games  # Assuming this is where your game sessions are stored

class TicTacToeDatabase:
    def __init__(self, db_path="database/tic_tac_toe.db"):
        # Ensure this path is persistent on your disk
        current_dir = os.path.dirname(os.path.abspath(__file__))  # get the current directory
        self.db_path = os.path.join(current_dir, db_path)  # full path to your database
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)  # create directories if needed
        self.initialize_db()

    def initialize_db(self):
        if not os.path.exists(self.db_path):  # Check if the database file already exists
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                    # Drop existing tables (for testing/reset purposes)
                    cursor.execute('DROP TABLE IF EXISTS game_sessions')
                    cursor.execute('DROP TABLE IF EXISTS correct_responses')
                    cursor.execute('DROP TABLE IF EXISTS ai_move_logs')

                    # Create game_sessions table
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS game_sessions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            session_id TEXT NOT NULL UNIQUE,
                            player_name TEXT NOT NULL,
                            algorithm TEXT NOT NULL,
                            start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                            end_time DATETIME,
                            winner TEXT
                        )
                    ''')

                    # Create correct_responses table
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS correct_responses (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            session_id TEXT NOT NULL,
                            player_name TEXT NOT NULL,
                            board_state TEXT NOT NULL,
                            winner TEXT NOT NULL,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')

                    # Create ai_move_logs table
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS ai_move_logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            session_id TEXT NOT NULL,
                            algorithm TEXT NOT NULL,
                            move TEXT NOT NULL,
                            duration_ms REAL NOT NULL,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')

                    # Create ai_move_logs table
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS user_move_logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            session_id TEXT NOT NULL,
                            name TEXT NOT NULL,
                            move TEXT NOT NULL,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')

                    conn.commit()
                    print(f"Tic-Tac-Toe database initialized at {self.db_path}.")
            except sqlite3.Error as e:
                print(f"Error initializing database: {e}")
        else:
            print(f"Database file already exists at {self.db_path}. Skipping initialization.")

    # ----------- Game Session Methods -----------

    def create_game_session(self, session_id, player_name, algorithm):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO game_sessions (session_id, player_name, algorithm)
                    VALUES (?, ?, ?)
                ''', (session_id, player_name, algorithm))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating game session: {e}")

    def end_game_session(self, session_id, winner):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE game_sessions
                    SET winner = ?, end_time = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                ''', (winner, session_id))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error ending game session: {e}")

    def get_all_game_sessions(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM game_sessions ORDER BY start_time DESC')
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching game sessions: {e}")
            return []

    # ----------- Correct Responses Methods -----------

    def log_correct_response(self, session_id, player_name, board_state, winner):
        try:
            board_json = json.dumps(board_state)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO correct_responses (session_id, player_name, board_state, winner)
                    VALUES (?, ?, ?, ?)
                ''', (session_id, player_name, board_json, winner))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error logging correct response: {e}")

    def get_all_correct_responses(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM correct_responses ORDER BY timestamp DESC')
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching correct responses: {e}")
            return []

    # ----------- AI Move Logs Methods -----------

    def log_ai_move(self, session_id, algorithm, move, duration_ms):
        try:
            move_json = json.dumps(move)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO ai_move_logs (session_id, algorithm, move, duration_ms)
                    VALUES (?, ?, ?, ?)
                ''', (session_id, algorithm, move_json, duration_ms))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error logging AI move: {e}")

    def log_user_move(self, session_id, name, move):
        if not name:
            name = "Unknown"
        try:
            move_json = json.dumps(move)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_move_logs (session_id, name, move)
                    VALUES (?, ?, ?)
                ''', (session_id, name, move_json))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error logging AI move: {e}")

    def get_ai_move_logs(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM ai_move_logs ORDER BY timestamp DESC')
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching AI move logs: {e}")
            return []

    def get_user_move_logs(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM user_move_logs ORDER BY timestamp DESC')
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching User move logs: {e}")
            return []