"""Migration script to add notes and updated_at columns to tasks table"""
import sqlite3
import os

# Determine the database path
db_path = os.path.join(os.path.dirname(__file__), "task.db")
if not os.path.exists(db_path):
    print(f"Database not found at: {db_path}")
    exit(1)

print(f"Using database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get existing columns
cursor.execute("PRAGMA table_info(tasks)")
existing_columns = [row[1] for row in cursor.fetchall()]
print(f"Existing columns: {existing_columns}")

# Add new columns if they don't exist
new_columns = [
    ("notes", "TEXT"),
    ("updated_at", "DATETIME"),
]

for col_name, col_type in new_columns:
    if col_name not in existing_columns:
        print(f"Adding column: {col_name}")
        cursor.execute(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_type}")
    else:
        print(f"Column already exists: {col_name}")

conn.commit()
conn.close()

print("Migration complete!")
