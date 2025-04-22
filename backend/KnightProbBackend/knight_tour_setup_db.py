import sqlite3
import os

# Create the database folder if it doesn't exist
os.makedirs("database", exist_ok=True)

# Create or connect to the SQLite database
conn = sqlite3.connect("../../database/knightstour.db")
cursor = conn.cursor()

# Create the winners table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS winners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        start_x INTEGER NOT NULL,
        start_y INTEGER NOT NULL,
        path TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Save changes and close the connection
conn.commit()
conn.close()

print("✅ Database and 'winners' table created successfully.")
