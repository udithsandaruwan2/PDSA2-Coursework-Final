import sqlite3
from contextlib import contextmanager
import logging
import os

logger = logging.getLogger(__name__)

# Ensure the database directory exists
os.makedirs('../database', exist_ok=True)

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        db_path = os.path.abspath('../database/tower_of_hanoi.db')
        logger.debug(f"Connecting to database at: {db_path}")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def init_db():
    """Initialize the database tables if they don't exist"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    disk_count INTEGER NOT NULL,
                    moves_count INTEGER NOT NULL,
                    mode TEXT NOT NULL,
                    score_amount INTEGER NOT NULL DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            logger.info("Scores table created or already exists")

            cursor.execute("PRAGMA table_info(scores)")
            columns = [col['name'] for col in cursor.fetchall()]
            if 'score_amount' not in columns:
                cursor.execute('ALTER TABLE scores ADD COLUMN score_amount INTEGER NOT NULL DEFAULT 0')
                logger.info("Added score_amount column to scores table")
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS algorithm_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    disk_count INTEGER NOT NULL,
                    algorithm_type TEXT NOT NULL,
                    peg_count INTEGER NOT NULL,
                    avg_time REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            logger.info("Algorithm_performance table created or already exists")
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_moves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    score_id INTEGER NOT NULL,
                    moves_json TEXT NOT NULL,
                    FOREIGN KEY (score_id) REFERENCES scores (id)
                )
            ''')
            logger.info("Game_moves table created or already exists")
            
            conn.commit()
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def save_score(player_name, disk_count, moves_count, mode, score_amount=0):
    """Save player score to database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO scores (player_name, disk_count, moves_count, mode, score_amount) VALUES (?, ?, ?, ?, ?)',
                (player_name, disk_count, moves_count, mode, score_amount)
            )
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Error saving score: {e}")
        raise

def save_game_result(player_name, disk_count, moves_count, moves_json, mode="3peg", score_amount=0):
    """Save complete game result including moves and score amount"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO scores (player_name, disk_count, moves_count, mode, score_amount) VALUES (?, ?, ?, ?, ?)',
                (player_name, disk_count, moves_count, mode, score_amount)
            )
            score_id = cursor.lastrowid
            
            cursor.execute(
                'INSERT INTO game_moves (score_id, moves_json) VALUES (?, ?)',
                (score_id, moves_json)
            )
            conn.commit()
            logger.info(f"Saved game result with score_id: {score_id}, score_amount: {score_amount}")
            return score_id
    except sqlite3.Error as e:
        logger.error(f"Error saving game result: {e}")
        raise

def save_algorithm_performance(disk_count, algorithm_type, peg_count, avg_time):
    """Save algorithm performance metrics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO algorithm_performance (disk_count, algorithm_type, peg_count, avg_time) VALUES (?, ?, ?, ?)',
                (disk_count, algorithm_type, peg_count, avg_time)
            )
            conn.commit()
            logger.debug(f"Saved algorithm performance: disk_count={disk_count}, type={algorithm_type}, time={avg_time:.6f} ms")
    except sqlite3.Error as e:
        logger.error(f"Error saving algorithm performance: {e}")
        raise

def get_scores(limit=20):
    """Get high scores, ordered by best moves count for each disk count"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.id, s.player_name, s.disk_count, s.moves_count, s.mode, s.score_amount, s.timestamp
                FROM scores s
                JOIN (
                    SELECT disk_count, MIN(moves_count) as min_moves
                    FROM scores
                    GROUP BY disk_count
                ) m ON s.disk_count = m.disk_count AND s.moves_count = m.min_moves
                ORDER BY s.disk_count DESC, s.moves_count ASC, s.timestamp DESC
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Error getting scores: {e}")
        raise

def get_all_scores():
    """Get all scores, ordered by timestamp"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, player_name, disk_count, moves_count, mode, score_amount, timestamp
                FROM scores
                ORDER BY timestamp DESC
            ''')
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Error getting all scores: {e}")
        raise

def get_all_table_data():
    """Get data from all database tables"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            tables = {
                'scores': {
                    'columns': ['id', 'player_name', 'disk_count', 'moves_count', 'mode', 'score_amount', 'timestamp'],
                    'rows': []
                },
                'algorithm_performance': {
                    'columns': ['id', 'disk_count', 'algorithm_type', 'peg_count', 'avg_time', 'timestamp'],
                    'rows': []
                },
                'game_moves': {
                    'columns': ['id', 'score_id', 'moves_json'],
                    'rows': []
                }
            }

            cursor.execute('SELECT * FROM scores')
            for row in cursor.fetchall():
                tables['scores']['rows'].append([row['id'], row['player_name'], row['disk_count'], row['moves_count'], row['mode'], row['score_amount'], row['timestamp']])

            cursor.execute('SELECT * FROM algorithm_performance')
            for row in cursor.fetchall():
                tables['algorithm_performance']['rows'].append([row['id'], row['disk_count'], row['algorithm_type'], row['peg_count'], row['avg_time'], row['timestamp']])

            cursor.execute('SELECT * FROM game_moves')
            for row in cursor.fetchall():
                tables['game_moves']['rows'].append([row['id'], row['score_id'], row['moves_json']])

            return tables
    except sqlite3.Error as e:
        logger.error(f"Error getting all table data: {e}")
        raise

def get_algorithm_performance():
    """Get latest performance data for each algorithm and disk count"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    disk_count, 
                    algorithm_type, 
                    peg_count, 
                    avg_time,
                    timestamp
                FROM algorithm_performance
                WHERE (disk_count, algorithm_type, timestamp) IN (
                    SELECT disk_count, algorithm_type, MAX(timestamp)
                    FROM algorithm_performance
                    GROUP BY disk_count, algorithm_type
                )
                ORDER BY disk_count, algorithm_type, peg_count
            ''')
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Error getting algorithm performance: {e}")
        raise

def get_algorithm_comparison_chart_data():
    """Get data formatted for charting algorithm performance"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    disk_count, 
                    algorithm_type, 
                    avg_time as avg_time_ms
                FROM algorithm_performance
                WHERE (disk_count, algorithm_type, timestamp) IN (
                    SELECT disk_count, algorithm_type, MAX(timestamp)
                    FROM algorithm_performance
                    GROUP BY disk_count, algorithm_type
                )
                ORDER BY disk_count, algorithm_type
            ''')
            rows = cursor.fetchall()
            
            disk_counts = sorted(set(row['disk_count'] for row in rows))
            algorithms = sorted(set(row['algorithm_type'] for row in rows))
            
            result = {
                'labels': disk_counts,
                'datasets': []
            }
            
            colors = {
                'recursive': 'rgba(255, 99, 132, 0.8)',
                'iterative': 'rgba(54, 162, 235, 0.8)',
                'frame_stewart': 'rgba(75, 192, 192, 0.8)'
            }
            
            for algorithm in algorithms:
                dataset = {
                    'label': algorithm.capitalize(),
                    'backgroundColor': colors.get(algorithm, 'rgba(0, 0, 0, 0.8)'),
                    'data': []
                }
                
                for disk in disk_counts:
                    time_value = next((row['avg_time_ms'] for row in rows 
                                     if row['disk_count'] == disk and row['algorithm_type'] == algorithm), 0)
                    dataset['data'].append(time_value)
                
                result['datasets'].append(dataset)
            
            return result
    except sqlite3.Error as e:
        logger.error(f"Error getting chart data: {e}")
        raise