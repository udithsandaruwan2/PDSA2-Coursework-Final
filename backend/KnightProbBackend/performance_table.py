import sqlite3
import os

# Create the database folder if it doesn't exist
os.makedirs("database", exist_ok=True)

# Create or connect to the SQLite database
conn = sqlite3.connect("../../database/knightstour.db")
cursor = conn.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS performance_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        backtracking_algorithm REAL ,
        warnsdoffs_algorithm REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Save changes and close the connection
conn.commit()
conn.close()

print("✅ Database and 'performance' table created successfully.")