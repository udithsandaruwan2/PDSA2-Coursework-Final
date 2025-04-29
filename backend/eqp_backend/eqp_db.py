import sqlite3
import logging
import os
from pathlib import Path
from datetime import datetime
import pytz

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class EightQueensDB:
    def __init__(self, db_path=None):
        if db_path is None:
            current_dir = Path(__file__).parent
            db_path = current_dir / ".." / "database" / "eight_queens.db"
            db_path = db_path.resolve()
        self.db_path = str(db_path)
        db_dir = os.path.dirname(self.db_path)
        os.makedirs(db_dir, exist_ok=True)
        logger.info(f"Database path: {self.db_path}")

    def init_db(self):
        """Initialize the database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Table for precomputed solutions
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS eqp_solutions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        solution TEXT NOT NULL UNIQUE CHECK (length(solution) = 64)
                    )
                ''')
                # Table for player submissions
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS eqp_submissions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL CHECK (username <> ''),
                        solution TEXT NOT NULL CHECK (length(solution) = 64),
                        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                # Table for performance metrics
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS eqp_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        algorithm_type TEXT NOT NULL CHECK (algorithm_type IN ('sequential', 'parallel')),
                        execution_time REAL NOT NULL CHECK (execution_time >= 0),
                        total_solutions INTEGER NOT NULL CHECK (total_solutions >= 0),
                        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Check if solutions table is empty and populate if necessary
                cursor.execute("SELECT COUNT(*) FROM eqp_solutions")
                count = cursor.fetchone()[0]
                if count == 0:
                    from .eqp_routes import QueensSolver
                    solver = QueensSolver()
                    solver.solve_sequential()
                    solutions = solver.get_solutions()
                    self.save_solutions(solutions)
                    logger.info("Populated eqp_solutions table with initial solutions.")
                conn.commit()
            logger.info("Eight Queens database initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def get_sri_lankan_time(self):
        """Get current time in Asia/Colombo timezone as ISO string."""
        sri_lanka_tz = pytz.timezone('Asia/Colombo')
        return datetime.now(sri_lanka_tz).isoformat()

    def execute_query(self, query, params=()):
        """Execute a query and return the results."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                return None
        except sqlite3.IntegrityError as e:
            logger.error(f"Database integrity error: {e}")
            raise ValueError(f"Invalid data: {str(e)}")
        except sqlite3.Error as e:
            logger.error(f"Database query error: {e}")
            raise

    def save_solutions(self, solutions):
        """Save precomputed solutions to the database."""
        try:
            for solution in solutions:
                self.execute_query("INSERT OR IGNORE INTO eqp_solutions (solution) VALUES (?)", (solution,))
            logger.info(f"Saved {len(solutions)} solutions to the database.")
        except sqlite3.Error as e:
            logger.error(f"Error saving solutions: {e}")
            raise

    def get_solutions(self):
        """Retrieve all precomputed solutions."""
        try:
            results = self.execute_query("SELECT solution FROM eqp_solutions ORDER BY id DESC")
            return [row[0] for row in results]
        except sqlite3.Error as e:
            logger.error(f"Error retrieving solutions: {e}")
            raise

    def save_submission(self, username, solution):
        """Save a player submission with Sri Lankan time."""
        try:
            self.execute_query(
                "INSERT INTO eqp_submissions (username, solution, submitted_at) VALUES (?, ?, ?)",
                (username, solution, self.get_sri_lankan_time())
            )
            logger.info(f"Saved submission for user {username}.")
        except sqlite3.Error as e:
            logger.error(f"Error saving submission: {e}")
            raise

    def get_submissions(self):
        """Retrieve all player submissions."""
        try:
            results = self.execute_query("SELECT username, solution FROM eqp_submissions ORDER BY submitted_at DESC")
            return [{'username': row[0], 'solution': row[1]} for row in results]
        except sqlite3.Error as e:
            logger.error(f"Error retrieving submissions: {e}")
            raise

    def clear_submissions(self):
        """Clear all player submissions."""
        try:
            self.execute_query("DELETE FROM eqp_submissions")
            logger.info("Cleared all player submissions.")
        except sqlite3.Error as e:
            logger.error(f"Error clearing submissions: {e}")
            raise

    def save_performance(self, algorithm_type, execution_time, total_solutions):
        """Save performance metrics."""
        try:
            self.execute_query(
                "INSERT INTO eqp_performance (algorithm_type, execution_time, total_solutions, recorded_at) VALUES (?, ?, ?, ?)",
                (algorithm_type, execution_time, total_solutions, self.get_sri_lankan_time())
            )
            # Keep only the last 100 records
            self.execute_query(
                "DELETE FROM eqp_performance WHERE id NOT IN (SELECT id FROM eqp_performance ORDER BY recorded_at DESC LIMIT 100)"
            )
            logger.info(f"Saved performance metrics for {algorithm_type}.")
        except sqlite3.Error as e:
            logger.error(f"Error saving performance metrics: {e}")
            raise

    def get_performance(self):
        """Retrieve all performance metrics."""
        try:
            results = self.execute_query("SELECT algorithm_type, execution_time, total_solutions, recorded_at FROM eqp_performance ORDER BY recorded_at DESC")
            return [
                {
                    'algorithm_type': row[0],
                    'execution_time': row[1],
                    'total_solutions': row[2],
                    'recorded_at': row[3]
                }
                for row in results
            ]
        except sqlite3.Error as e:
            logger.error(f"Error retrieving performance metrics: {e}")
            raise