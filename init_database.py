"""
Database Initialization Script
Creates and initializes the Milton AI Publicist database
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from database.database_manager import DatabaseManager

def main():
    """Initialize the database"""
    print("Initializing Milton AI Publicist Database...")
    print("-" * 50)

    try:
        # Initialize database (will create if doesn't exist)
        db = DatabaseManager()

        print(f"[OK] Database created at: {db.db_path}")
        print(f"[OK] Schema applied successfully")

        # Verify tables were created
        with db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in cursor.fetchall()]

        print(f"\n[OK] Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table}")

        print("\n" + "=" * 50)
        print("DATABASE INITIALIZATION COMPLETE!")
        print("=" * 50)

        return 0

    except Exception as e:
        print(f"\n[ERROR] Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
