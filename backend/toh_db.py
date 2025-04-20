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
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            logger.info("Scores table created or already exists")
            
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

def save_score(player_name, disk_count, moves_count, mode):
    """Save player score to database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO scores (player_name, disk_count, moves_count, mode) VALUES (?, ?, ?, ?)',
                (player_name, disk_count, moves_count, mode)
            )
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Error saving score: {e}")
        raise

def save_game_result(player_name, disk_count, moves_count, moves_json, mode="3peg"):
    """Save complete game result including moves"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO scores (player_name, disk_count, moves_count, mode) VALUES (?, ?, ?, ?)',
                (player_name, disk_count, moves_count, mode)
            )
            score_id = cursor.lastrowid
            
            cursor.execute(
                'INSERT INTO game_moves (score_id, moves_json) VALUES (?, ?)',
                (score_id, moves_json)
            )
            conn.commit()
            return score_id
    except sqlite3.Error as e:
        logger.error(f"Error saving game result: {e}")
        raise

def get_scores(limit=20):
    """Get high scores, ordered by best moves count for each disk count"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.id, s.player_name, s.disk_count, s.moves_count, s.mode, s.timestamp
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
    except sqlite3.Error as e:
        logger.error(f"Error saving algorithm performance: {e}")
        raise

def get_algorithm_performance():
    """Get average performance data for each algorithm and disk count"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    disk_count, 
                    algorithm_type, 
                    peg_count, 
                    AVG(avg_time) as avg_time
                FROM algorithm_performance
                GROUP BY disk_count, algorithm_type, peg_count
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
                    AVG(avg_time) * 1000 as avg_time_ms
                FROM algorithm_performance
                GROUP BY disk_count, algorithm_type
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