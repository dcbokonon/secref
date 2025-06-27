"""SQLite database configuration and connection management"""

import os
import sqlite3
import json
from contextlib import contextmanager
from pathlib import Path

# Database file location
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'secref.db')

def dict_factory(cursor, row):
    """Convert SQLite rows to dictionaries"""
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

@contextmanager
def get_db_connection():
    """Get a database connection with automatic cleanup"""
    conn = None
    try:
        # Ensure database directory exists
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = dict_factory
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def init_schema(schema_file='database/schema_sqlite.sql'):
    """Initialize the database schema"""
    print(f"Initializing SQLite database at: {DB_PATH}")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Read and execute schema file
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # SQLite requires executing statements one at a time
        conn.executescript(schema_sql)
        print("Schema initialized successfully")

def test_connection():
    """Test database connection"""
    print(f"Testing connection to SQLite database: {DB_PATH}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()
            print(f"Connected successfully! SQLite version: {version['sqlite_version()']}")
            
            # Show tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = cursor.fetchall()
            print(f"Tables: {[t['name'] for t in tables]}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == '__main__':
    test_connection()