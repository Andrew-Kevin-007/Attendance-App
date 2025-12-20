"""Migration script to add reset_token columns to users table"""
import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), 'task.db')

if not os.path.exists(db_path):
    print(f"Error: Database file not found at {db_path}")
    exit(1)

print(f"Migrating database: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'reset_token' not in columns:
        print("Adding reset_token column...")
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
    else:
        print("reset_token column already exists")
    
    if 'reset_token_expires' not in columns:
        print("Adding reset_token_expires column...")
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP")
    else:
        print("reset_token_expires column already exists")
    
    conn.commit()
    print("Migration completed successfully!")
    
except Exception as e:
    print(f"Error during migration: {e}")
    conn.rollback()
finally:
    conn.close()
