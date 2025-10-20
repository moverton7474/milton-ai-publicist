"""
Apply Zapier Publishing Database Migration
Applies the add_zapier_publishing_table.sql migration to the database
"""

import sqlite3
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Paths
db_path = os.path.join(script_dir, 'milton_publicist.db')
migration_path = os.path.join(script_dir, 'database', 'add_zapier_publishing_table.sql')

print("=" * 70)
print("ZAPIER PUBLISHING MIGRATION")
print("=" * 70)
print()
print(f"Database: {db_path}")
print(f"Migration: {migration_path}")
print()

# Check if files exist
if not os.path.exists(db_path):
    print(f"ERROR: Database file not found at {db_path}")
    print("Creating new database...")

if not os.path.exists(migration_path):
    print(f"ERROR: Migration file not found at {migration_path}")
    exit(1)

# Read migration SQL
print("Reading migration SQL...")
with open(migration_path, 'r', encoding='utf-8') as f:
    migration_sql = f.read()

print(f"Migration SQL loaded ({len(migration_sql)} characters)")
print()

# Apply migration
print("Applying migration to database...")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute migration SQL
    cursor.executescript(migration_sql)

    # Commit changes
    conn.commit()

    print("✓ Migration applied successfully!")
    print()

    # Verify table was created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='post_publications'")
    table_exists = cursor.fetchone()

    if table_exists:
        print("✓ Table 'post_publications' verified")

        # Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='post_publications'")
        indexes = cursor.fetchall()
        print(f"✓ Created {len(indexes)} indexes")

        # Check views
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        views = cursor.fetchall()
        print(f"✓ Created {len([v for v in views if 'publication' in v[0].lower()])} views")

    else:
        print("✗ ERROR: Table 'post_publications' not found after migration!")

    conn.close()
    print()
    print("=" * 70)
    print("MIGRATION COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Configure Zapier webhooks in your .env file")
    print("2. Restart the dashboard: python dashboard/app.py")
    print("3. Test publishing: http://localhost:8080/api/publish/platforms")
    print()

except sqlite3.Error as e:
    print(f"✗ ERROR applying migration: {e}")
    exit(1)
