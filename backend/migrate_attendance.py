"""Migration script to add check_in/check_out columns to attendance table"""
import sqlite3
import os

# Determine the database path
db_path = os.path.join(os.path.dirname(__file__), "face_attendance.db")
if not os.path.exists(db_path):
    # Try the root directory
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "face_attendance.db")

print(f"Using database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get existing columns
cursor.execute("PRAGMA table_info(attendance)")
existing_columns = [row[1] for row in cursor.fetchall()]
print(f"Existing columns: {existing_columns}")

# Add new columns if they don't exist
new_columns = [
    ("check_in", "DATETIME"),
    ("check_out", "DATETIME"),
    ("check_in_image", "VARCHAR(500)"),
    ("check_out_image", "VARCHAR(500)"),
    ("check_out_confidence", "FLOAT"),
]

for col_name, col_type in new_columns:
    if col_name not in existing_columns:
        print(f"Adding column: {col_name}")
        cursor.execute(f"ALTER TABLE attendance ADD COLUMN {col_name} {col_type}")
    else:
        print(f"Column already exists: {col_name}")

# Migrate existing data: copy timestamp to check_in if check_in is null
cursor.execute("""
    UPDATE attendance 
    SET check_in = timestamp 
    WHERE check_in IS NULL AND timestamp IS NOT NULL
""")
updated = cursor.rowcount
print(f"Migrated {updated} existing records (set check_in from timestamp)")

conn.commit()
conn.close()

print("Migration complete!")
