"""
Helper script to apply sample cards to the database
using the application's configured database connection
"""
import os
import sys
from backend import create_app, db
from config import DB_CONFIG

def apply_sample_cards():
    """Apply sample cards SQL script to the database"""
    app = create_app()
    
    with app.app_context():
        # Get DB connection from SQLAlchemy
        connection = db.engine.raw_connection()
        cursor = connection.cursor()
        
        # Read the SQL script
        script_path = os.path.join('scripts', 'DML', 'sample_cards.sql')
        with open(script_path, 'r') as f:
            sql_script = f.read()
        
        # Execute the script
        try:
            cursor.execute(sql_script)
            connection.commit()
            print("Successfully applied sample cards")
        except Exception as e:
            connection.rollback()
            print(f"Error applying sample cards: {str(e)}")
        finally:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    apply_sample_cards()
