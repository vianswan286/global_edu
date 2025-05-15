"""
Configuration settings for the educational platform.
"""

# Database Configuration
DB_CONFIG = {
    'name': 'edu_project',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

# Flask Application Configuration
FLASK_CONFIG = {
    'debug': True,
    'host': '0.0.0.0',
    'port': 5002
}

# Security Configuration
SECURITY_CONFIG = {
    'secret_key': 'your-secret-key-here',
    'password_salt': 'your-password-salt-here'
}

