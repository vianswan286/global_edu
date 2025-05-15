from backend import create_app, db
from backend.models import Student, Course, Knowledge, Collection
from flask import Flask

app = create_app()



if __name__ == '__main__':
    # Only run the app without creating tables or seeding data
    # This ensures we only read from the existing database
    print("Starting Flask application with existing database data...")
    app.run(debug=True)
