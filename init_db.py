"""
Database Initialization Script
Creates all database tables for Home IoT Guardian
"""

from app import app, db

if __name__ == '__main__':
    with app.app_context():
        # Create all tables
        db.create_all()
        print("[SUCCESS] Database tables created successfully!")
        print(f"Database location: guardian.db")

