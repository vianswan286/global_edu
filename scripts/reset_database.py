"""
Database reset script for educational platform.
This script will:
1. Drop all tables in the database
2. Recreate the schema
3. Apply SQL triggers and functions
4. Load sample data
"""
import os
import sys
import psycopg2
from psycopg2 import sql
import subprocess

# Add project root to path so config can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DB_CONFIG
from backend import create_app, db

def connect_to_database():
    """Connect to PostgreSQL database."""
    conn = psycopg2.connect(
        dbname=DB_CONFIG['name'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port']
    )
    conn.autocommit = True
    return conn

def reset_database():
    """Drop and recreate all tables."""
    app = create_app()
    
    print("Dropping all tables...")
    with app.app_context():
        db.drop_all()
    
    print("Recreating tables...")
    with app.app_context():
        db.create_all()
    
    print("Database schema reset complete.")

def apply_sql_scripts():
    """Apply SQL scripts for triggers, functions, and data."""
    conn = connect_to_database()
    cursor = conn.cursor()
    
    script_directories = [
        os.path.join(os.path.dirname(__file__), 'DDL'),
        os.path.join(os.path.dirname(__file__), 'DML')
    ]
    
    # Process scripts in order
    script_order = [
        # DDL first
        'analytics_and_triggers.sql',
        'add_time_to_cards_and_course_time_fn.sql',
        
        # Then DML (data)
        'minimum_demo_data.sql',
        'math_knowledges.sql',
        'math_collections.sql',
        'collections.sql'
    ]
    
    for script_name in script_order:
        # Find the script in either directory
        script_path = None
        for directory in script_directories:
            potential_path = os.path.join(directory, script_name)
            if os.path.exists(potential_path):
                script_path = potential_path
                break
        
        if script_path:
            print(f"Applying SQL script: {script_name}")
            with open(script_path, 'r') as f:
                sql_script = f.read()
                try:
                    cursor.execute(sql_script)
                    print(f"Successfully applied: {script_name}")
                except Exception as e:
                    print(f"Error applying {script_name}: {str(e)}")
        else:
            print(f"Warning: Could not find script {script_name}")
    
    cursor.close()
    conn.close()

def main():
    """Main function to reset and recreate the database."""
    print("Starting database reset process...")
    
    # Create flask app context for SQLAlchemy operations
    reset_database()
    apply_sql_scripts()
    
    print("Database reset and recreation completed successfully!")

if __name__ == "__main__":
    main()
