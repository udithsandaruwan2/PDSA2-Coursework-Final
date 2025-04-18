import sqlite3
import os
import time
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Database', 'tower_of_hanoi.db')

def init_db():
    """Initialize the database with required tables if they don't exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Table for storing game results
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            disk_count INTEGER NOT NULL,
            moves_count INTEGER NOT NULL,
            moves_sequence TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Table for storing algorithm performance
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS algorithm_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disk_count INTEGER NOT NULL,
            algorithm_type TEXT NOT NULL,
            peg_count INTEGER NOT NULL,
            execution_time REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        if conn:
            conn.close()

def save_game_result(player_name, disk_count, moves_count, moves_sequence):
    """Save a player's successful game result."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO game_results (player_name, disk_count, moves_count, moves_sequence) VALUES (?, ?, ?, ?)',
            (player_name, disk_count, moves_count, moves_sequence)
        )
        conn.commit()
        return cursor.lastrowid

def save_algorithm_performance(disk_count, algorithm_type, peg_count, execution_time):
    """Save algorithm performance data."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO algorithm_performance (disk_count, algorithm_type, peg_count, execution_time) VALUES (?, ?, ?, ?)',
            (disk_count, algorithm_type, peg_count, execution_time)
        )
        conn.commit()
        return cursor.lastrowid

def get_top_scores(limit=10):
    """Get top scores based on disk count and moves."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT player_name, disk_count, moves_count 
            FROM game_results 
            ORDER BY disk_count DESC, moves_count ASC 
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]

def get_algorithm_comparisons():
    """Get algorithm comparison data."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT disk_count, algorithm_type, peg_count, AVG(execution_time) as avg_time
            FROM algorithm_performance
            GROUP BY disk_count, algorithm_type, peg_count
            ORDER BY disk_count, peg_count
        ''')
        return [dict(row) for row in cursor.fetchall()]

# Initialize database when module is loaded
init_db()