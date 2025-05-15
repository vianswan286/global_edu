# Learning Platform

Образовательная платформа, отслеживающая знания пользователя через инструмент "элементарных" знаний - маленьких кусков из которых всё состоит. Позволяет пользователям пройти курс из списка, увидев предварительно, сколько времени он займёт и какие знания даст + какие потребует от пользователя.

## Features

- User authentication (login/register)
- Course listing with prerequisites and estimated time
- Knowledge tracking system
- Knowledge shop (coming soon)

## Requirements

- Python 3.8+
- PostgreSQL
- Flask and extensions (see requirements.txt)

## Getting Started

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Make sure PostgreSQL is running with a user 'postgres' with password 'postgres'. The application will create a database called 'edu_project'
5. Run the application:
   ```
   python run.py
   ```
6. Access the application at http://localhost:5001

## Default Login

After running the setup, you will need to register a new user through the application interface. All data shown in the app is loaded directly from the database; there is no hardcoded or example data.
## Database Structure

The database structure follows a structure designed to track user knowledge. Initial data is loaded from `scripts/modified_DML.sql`.

## Technical Documentation

For more detailed technical information, please see the [TECHNICAL_INFO.md](TECHNICAL_INFO.md) file.
