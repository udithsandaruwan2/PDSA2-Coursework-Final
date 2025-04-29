import sqlite3
import os
import json
from datetime import datetime
from tic_tac_toe_backend.GameEngine import games  # Assuming this is where your game sessions are stored

class TicTacToeDatabase:
    def __init__(self, db_path="../database/tic_tac_toe.db"):
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
        
    def get_tictactoe_performance(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                performance = {'minimax': [], 'mcts': []}

                # Get last 10 moves for minimax
                cursor.execute('''
                    SELECT algorithm, duration_ms, timestamp
                    FROM ai_move_logs
                    WHERE algorithm = 'minimax'
                    ORDER BY timestamp DESC
                    LIMIT 10
                ''')
                performance['minimax'] = [
                    {'duration_ms': row['duration_ms'], 'timestamp': row['timestamp']}
                    for row in cursor.fetchall()
                ][::-1]

                # Get last 10 moves for mcts
                cursor.execute('''
                    SELECT algorithm, duration_ms, timestamp
                    FROM ai_move_logs
                    WHERE algorithm = 'mcts'
                    ORDER BY timestamp DESC
                    LIMIT 10
                ''')
                performance['mcts'] = [
                    {'duration_ms': row['duration_ms'], 'timestamp': row['timestamp']}
                    for row in cursor.fetchall()
                ][::-1]

                return {'success': True, 'metrics': performance}

        except Exception as e:
            print("DB Error:", e)
            return {'success': False, 'metrics': {}}
        
    def get_tictactoe_performance_rounds(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                performance = {'minimax': [], 'mcts': []}

                for algo in ['minimax', 'mcts']:
                    # Step 1: Get latest 10 session_ids for this algorithm
                    cursor.execute('''
                        SELECT DISTINCT session_id
                        FROM ai_move_logs
                        WHERE LOWER(algorithm) = ?
                        ORDER BY timestamp DESC
                        LIMIT 10
                    ''', (algo,))
                    sessions = [row['session_id'] for row in cursor.fetchall()]
                    sessions.reverse()  # oldest to newest

                    # Step 2: For each session, get average move duration
                    for session_id in sessions:
                        cursor.execute('''
                            SELECT AVG(duration_ms) as avg_duration
                            FROM ai_move_logs
                            WHERE session_id = ? AND LOWER(algorithm) = ?
                        ''', (session_id, algo))
                        row = cursor.fetchone()
                        if row and row['avg_duration'] is not None:
                            performance[algo].append(round(row['avg_duration'], 2))

                return {'success': True, 'metrics': performance}

        except Exception as e:
            print("DB Error:", e)
            return {'success': False, 'metrics': {}}
