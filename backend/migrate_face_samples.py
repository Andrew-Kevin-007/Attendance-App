"""
Migration script to add face_samples table for multiple training images per employee
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "face_attendance.db")

def migrate():
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='face_samples'
        """)
        if cursor.fetchone():
            print("✓ face_samples table already exists")
            return
        
        # Create face_samples table
        print("Creating face_samples table...")
        cursor.execute("""
            CREATE TABLE face_samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                face_encoding BLOB NOT NULL,
                captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                quality_score REAL DEFAULT 0.0,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX idx_face_samples_employee 
            ON face_samples(employee_id)
        """)
        
        conn.commit()
        print("✓ Migration completed successfully!")
        print("✓ face_samples table created")
        print("\nYou can now register multiple training images per person for better accuracy!")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
