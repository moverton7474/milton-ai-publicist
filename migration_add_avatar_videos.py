# migration_add_avatar_videos.py

import sqlite3
from datetime import datetime

def migrate_database(db_path='milton_publicist.db'):
    """Add avatar_videos table to existing database"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"[{datetime.now()}] Starting database migration...")

    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS avatar_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                post_id INTEGER REFERENCES posts(id),
                script TEXT NOT NULL,
                scenario VARCHAR(100),
                voice_type VARCHAR(50) CHECK(voice_type IN ('personal', 'professional')),
                context TEXT,
                heygen_video_id TEXT,
                heygen_job_id TEXT,
                avatar_id TEXT DEFAULT 'YOUR_HEYGEN_AVATAR_ID',
                voice_id TEXT,
                video_url TEXT,
                thumbnail_url TEXT,
                duration_seconds INTEGER,
                dimensions VARCHAR(20) DEFAULT 'square' CHECK(dimensions IN ('square', 'vertical', 'horizontal')),
                status VARCHAR(50) DEFAULT 'generating' CHECK(status IN ('generating', 'processing', 'ready', 'failed', 'published')),
                error_message TEXT,
                generation_time_seconds INTEGER,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                engagement_rate DECIMAL(5,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                published_at TIMESTAMP,
                estimated_reach INTEGER DEFAULT 0,
                platform VARCHAR(50)
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_avatar_videos_user_id ON avatar_videos(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_avatar_videos_status ON avatar_videos(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_avatar_videos_created_at ON avatar_videos(created_at DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_avatar_videos_heygen_video_id ON avatar_videos(heygen_video_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_avatar_videos_post_id ON avatar_videos(post_id)')

        conn.commit()
        print(f"[{datetime.now()}] SUCCESS: Migration completed successfully!")

        # Verify
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='avatar_videos'")
        if cursor.fetchone():
            print(f"[{datetime.now()}] SUCCESS: Table 'avatar_videos' verified")

        # Check table structure
        cursor.execute("PRAGMA table_info(avatar_videos)")
        columns = cursor.fetchall()
        print(f"[{datetime.now()}] SUCCESS: Table has {len(columns)} columns")

    except Exception as e:
        print(f"[{datetime.now()}] ERROR: Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
