"""Database configuration and connection management"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from urllib.parse import urlparse
from contextlib import contextmanager

# Database configuration
# You can use either a DATABASE_URL or individual components
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/secref')

# Parse DATABASE_URL if provided
if DATABASE_URL.startswith('postgresql://'):
    result = urlparse(DATABASE_URL)
    DB_CONFIG = {
        'dbname': result.path[1:],
        'user': result.username or 'postgres',
        'password': result.password,
        'host': result.hostname or 'localhost',
        'port': result.port or 5432
    }
else:
    # Local development defaults
    DB_CONFIG = {
        'dbname': 'secref',
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', 5432)
    }

@contextmanager
def get_db_connection():
    """Get a database connection with automatic cleanup"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def create_database():
    """Create the database if it doesn't exist"""
    # Connect to postgres database to create our database
    conn_config = DB_CONFIG.copy()
    conn_config['dbname'] = 'postgres'
    
    try:
        conn = psycopg2.connect(**conn_config)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_CONFIG['dbname'],)
        )
        
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['dbname']}")
            print(f"Created database: {DB_CONFIG['dbname']}")
        else:
            print(f"Database already exists: {DB_CONFIG['dbname']}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        raise

def init_schema(schema_file='database/schema.sql'):
    """Initialize the database schema"""
    create_database()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Read and execute schema file
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        cursor.execute(schema_sql)
        print("Schema initialized successfully")
        
        cursor.close()

if __name__ == '__main__':
    # Test connection
    print(f"Testing connection to database: {DB_CONFIG['dbname']}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            print(f"Connected successfully! PostgreSQL version: {version['version']}")
    except Exception as e:
        print(f"Connection failed: {e}")