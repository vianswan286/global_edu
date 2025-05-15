import os
import sys
import argparse
import psycopg2
from psycopg2 import sql
import subprocess
from backend import create_app, db
from backend.models import Student, Course, Knowledge, Collection, Card, CourseRequiredKnowledge, CourseFinalKnowledge
from config import FLASK_CONFIG, DB_CONFIG

app = create_app()

def reset_database():
    """Drop and recreate all tables including dependent objects."""
    print("Completely resetting the database...")
    
    # Connect to the database
    conn = psycopg2.connect(
        dbname=DB_CONFIG['name'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port']
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        # Terminate all connections to the database except our own
        cursor.execute("""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = %s
          AND pid <> pg_backend_pid();
        """, (DB_CONFIG['name'],))
        
        # Close connection
        cursor.close()
        conn.close()
        
        # Drop and recreate the database
        conn = psycopg2.connect(
            dbname='postgres',  # Connect to default database
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Drop and recreate database
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_CONFIG['name']}")
        cursor.execute(f"CREATE DATABASE {DB_CONFIG['name']}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        # Now use SQLAlchemy to create all tables in the fresh database
        with app.app_context():
            db.create_all()
        
        print("Database completely recreated!")
    except Exception as e:
        print(f"Error recreating database: {str(e)}")
        print("Falling back to table recreation...")
        cursor.close()
        conn.close()
        
        # Reconnect to the original database
        conn = psycopg2.connect(
            dbname=DB_CONFIG['name'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Drop views and all tables in the right order
        cursor.execute("""
        -- Drop views first
        DROP VIEW IF EXISTS student_knowledge_progress CASCADE;
        DROP VIEW IF EXISTS course_knowledge_gap CASCADE;
        
        -- Drop all tables (this is more reliable than SQLAlchemy's drop_all for complex schemas)
        DROP SCHEMA public CASCADE;
        CREATE SCHEMA public;
        GRANT ALL ON SCHEMA public TO postgres;
        GRANT ALL ON SCHEMA public TO public;
        """)
        
        # Close the connection
        cursor.close()
        conn.close()
        
        # Now use SQLAlchemy to recreate all tables
        with app.app_context():
            db.create_all()
        
        print("Database schema reset complete.")

def apply_sql_scripts():
    """Apply SQL scripts for triggers, functions, and data."""
    # Connect to the database
    conn = psycopg2.connect(
        dbname=DB_CONFIG['name'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port']
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Create a list of all available SQL scripts
    sql_scripts = []
    
    # Get all DDL scripts
    ddl_dir = os.path.join(os.path.dirname(__file__), 'scripts', 'DDL')
    for filename in os.listdir(ddl_dir):
        if filename.endswith('.sql'):
            sql_scripts.append((os.path.join(ddl_dir, filename), 'DDL', filename))
    
    # Get all DML scripts
    dml_dir = os.path.join(os.path.dirname(__file__), 'scripts', 'DML')
    for filename in os.listdir(dml_dir):
        if filename.endswith('.sql'):
            sql_scripts.append((os.path.join(dml_dir, filename), 'DML', filename))
    
    # First, let's execute a sequence reset to avoid duplicate key issues
    print("Resetting database sequences")
    try:
        cursor.execute("""
        -- Reset all sequences to avoid duplicate key issues
        DO $$ 
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT sequencename FROM pg_sequences WHERE schemaname = 'public') LOOP
                EXECUTE 'ALTER SEQUENCE ' || r.sequencename || ' RESTART WITH 1;';
            END LOOP;
        END $$;
        """)
        print("Sequences reset successful")
    except Exception as e:
        print(f"Error resetting sequences: {str(e)}")
    
    # Process scripts in the right order
    execution_order = [
        # First execute DDL scripts (structure, functions, triggers)
        ('DDL', 'add_time_to_cards_and_course_time_fn.sql'),
        ('DDL', 'analytics_and_triggers.sql'),
        
        # Then execute DML scripts (data) in the dependency order
        ('DML', 'collections.sql'),       # First create collections
        ('DML', 'math_collections.sql'),  # Then math collections
        ('DML', 'math_knowledges.sql')    # Finally knowledge units
    ]
    
    # Execute scripts in specified order
    for script_type, script_name in execution_order:
        # Try to find the script
        for script_path, type_name, file_name in sql_scripts:
            if type_name == script_type and file_name == script_name:
                print(f"Applying SQL script: {script_name}")
                with open(script_path, 'r') as f:
                    sql_script = f.read()
                    try:
                        cursor.execute(sql_script)
                        print(f"Successfully applied: {script_name}")
                    except Exception as e:
                        print(f"Error applying {script_name}: {str(e)}")
                break
        else:
            print(f"Warning: Could not find script {script_name}")
    
    # Add a test student since it's required for login
    try:
        cursor.execute("""
        -- Add a test student if none exists
        INSERT INTO students (name, email, password_hash) VALUES
            ('Demo User', 'demo@example.com', '$pbkdf2-sha256$29000$F9JdVw1eQw2K1uV6eUoQ9A$Q9qQJYQv1QZb1JtB9k8q0eXWj1F6O1y6u5l9oZk5QhM')
        ON CONFLICT (email) DO NOTHING;
        """)
        print("Successfully added demo user")
    except Exception as e:
        print(f"Error adding demo user: {str(e)}")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Educational Platform Application')
    parser.add_argument('--reset-db', action='store_true', help='Reset the database and apply SQL scripts')
    args = parser.parse_args()
    
    if args.reset_db:
        print("Resetting database...")
        reset_database()
        apply_sql_scripts()
        print("Database reset and recreation completed successfully!")
    else:
        print("Starting Flask application...")
        app.run(
            debug=FLASK_CONFIG['debug'], 
            host=FLASK_CONFIG['host'], 
            port=FLASK_CONFIG['port']
        )
