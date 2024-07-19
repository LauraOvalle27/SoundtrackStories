import sqlite3
import os



try:
    conn = sqlite3.connect("app.db")
    print("Database connected successfully.")
    conn.close()
except Exception as e:
    print(f"Failed to connect to the database: {e}")
