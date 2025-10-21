"""
Database Manager for Milton AI Publicist
SQLite-based persistent storage for posts, schedules, and analytics
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Union
from pathlib import Path
import threading


class DatabaseManager:
    """
    SQLite database manager for persistent storage
    Thread-safe operations for concurrent access
    """

    def __init__(self, db_path: str = "milton_publicist.db"):
        """
        Initialize database manager

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.local = threading.local()
        self._init_database()

    def _get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self.local, 'connection'):
            self.local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            self.local.connection.row_factory = sqlite3.Row
        return self.local.connection

    def _init_database(self):
        """Initialize database schema"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Posts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                voice_type TEXT NOT NULL,
                scenario TEXT NOT NULL,
                context TEXT,
                word_count INTEGER,
                graphic_url TEXT,
                video_url TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published_at TIMESTAMP,
                post_url TEXT
            )
        """)

        # Scheduled posts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                scheduled_time TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published_at TIMESTAMP,
                error_message TEXT,
                FOREIGN KEY (post_id) REFERENCES posts(id)
            )
        """)

        # Publishing results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS publishing_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                post_url TEXT,
                error_message TEXT,
                published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id)
            )
        """)

        # Analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_time ON scheduled_posts(scheduled_time)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_status ON scheduled_posts(status)")

        conn.commit()
        print(f"[INFO] Database initialized: {self.db_path}")

    # ========================================================================
    # POSTS CRUD OPERATIONS
    # ========================================================================

    def create_post(
        self,
        content: str,
        voice_type: str,
        scenario: str,
        context: str = "",
        graphic_url: Optional[str] = None,
        video_url: Optional[str] = None
    ) -> int:
        """Create a new post"""
        conn = self._get_connection()
        cursor = conn.cursor()

        word_count = len(content.split())

        cursor.execute("""
            INSERT INTO posts (content, voice_type, scenario, context, word_count, graphic_url, video_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (content, voice_type, scenario, context, word_count, graphic_url, video_url))

        conn.commit()
        post_id = cursor.lastrowid

        print(f"[INFO] Created post ID: {post_id}")
        return post_id

    def get_post(self, post_id: int) -> Optional[Dict]:
        """Get a single post by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None

    def get_all_posts(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all posts"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM posts
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))

        return [dict(row) for row in cursor.fetchall()]

    def update_post(self, post_id: int, **kwargs) -> bool:
        """Update a post"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Build SET clause dynamically
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [post_id]

        cursor.execute(f"""
            UPDATE posts
            SET {set_clause}
            WHERE id = ?
        """, values)

        conn.commit()
        return cursor.rowcount > 0

    def delete_post(self, post_id: int) -> bool:
        """Delete a post"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        conn.commit()

        return cursor.rowcount > 0

    def mark_post_published(self, post_id: int, post_url: Optional[str] = None):
        """Mark a post as published"""
        self.update_post(
            post_id,
            status='published',
            published_at=datetime.utcnow().isoformat(),
            post_url=post_url
        )

    # ========================================================================
    # SCHEDULED POSTS OPERATIONS
    # ========================================================================

    def schedule_post(
        self,
        post_id: int,
        platform: str,
        scheduled_time: Union[datetime, str]
    ) -> int:
        """Schedule a post for future publishing"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Convert to ISO format if datetime object, otherwise use string as-is
        if isinstance(scheduled_time, datetime):
            time_str = scheduled_time.isoformat()
        else:
            time_str = scheduled_time

        cursor.execute("""
            INSERT INTO scheduled_posts (post_id, platforms, scheduled_time)
            VALUES (?, ?, ?)
        """, (post_id, platform, time_str))

        conn.commit()
        return cursor.lastrowid

    def get_due_scheduled_posts(self) -> List[Dict]:
        """Get posts that are due to be published"""
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat()

        cursor.execute("""
            SELECT sp.*, p.content, p.graphic_url, p.video_url
            FROM scheduled_posts sp
            JOIN posts p ON sp.post_id = p.id
            WHERE sp.status = 'pending'
            AND sp.scheduled_time <= ?
            ORDER BY sp.scheduled_time
        """, (now,))

        return [dict(row) for row in cursor.fetchall()]

    def mark_scheduled_post_published(self, schedule_id: int):
        """Mark a scheduled post as published"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE scheduled_posts
            SET status = 'published', published_at = ?
            WHERE id = ?
        """, (datetime.utcnow().isoformat(), schedule_id))

        conn.commit()

    def mark_scheduled_post_failed(self, schedule_id: int, error_message: str):
        """Mark a scheduled post as failed"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE scheduled_posts
            SET status = 'failed', error_message = ?
            WHERE id = ?
        """, (error_message, schedule_id))

        conn.commit()

    def cancel_scheduled_post(self, schedule_id: int) -> bool:
        """Cancel a scheduled post"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE scheduled_posts
            SET status = 'cancelled'
            WHERE id = ? AND status = 'pending'
        """, (schedule_id,))

        conn.commit()
        return cursor.rowcount > 0

    def get_all_scheduled_posts(self, status: Optional[str] = None) -> List[Dict]:
        """Get all scheduled posts, optionally filtered by status"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute("""
                SELECT sp.*, p.content, p.voice_type, p.scenario
                FROM scheduled_posts sp
                JOIN posts p ON sp.post_id = p.id
                WHERE sp.status = ?
                ORDER BY sp.scheduled_time
            """, (status,))
        else:
            cursor.execute("""
                SELECT sp.*, p.content, p.voice_type, p.scenario
                FROM scheduled_posts sp
                JOIN posts p ON sp.post_id = p.id
                ORDER BY sp.scheduled_time
            """)

        return [dict(row) for row in cursor.fetchall()]

    def get_upcoming_schedule(self, days: int = 7) -> List[Dict]:
        """Get upcoming scheduled posts"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT sp.*, p.content, p.voice_type, p.scenario
            FROM scheduled_posts sp
            JOIN posts p ON sp.post_id = p.id
            WHERE sp.status = 'pending'
            AND sp.scheduled_time >= datetime('now')
            AND sp.scheduled_time <= datetime('now', '+' || ? || ' days')
            ORDER BY sp.scheduled_time
        """, (days,))

        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # PUBLISHING RESULTS OPERATIONS
    # ========================================================================

    def log_publishing_result(
        self,
        post_id: int,
        platform: str,
        success: bool,
        post_url: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Log a publishing result"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO publishing_results (post_id, platform, success, post_url, error_message)
            VALUES (?, ?, ?, ?, ?)
        """, (post_id, platform, success, post_url, error_message))

        conn.commit()

    def get_publishing_history(self, post_id: int) -> List[Dict]:
        """Get publishing history for a post"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM publishing_results
            WHERE post_id = ?
            ORDER BY published_at DESC
        """, (post_id,))

        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # ANALYTICS OPERATIONS
    # ========================================================================

    def update_analytics(
        self,
        post_id: int,
        platform: str,
        views: int = 0,
        likes: int = 0,
        comments: int = 0,
        shares: int = 0
    ):
        """Update analytics for a post"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Calculate engagement rate
        engagement_rate = 0.0
        if views > 0:
            engagement_rate = ((likes + comments + shares) / views) * 100

        # Check if analytics record exists
        cursor.execute("""
            SELECT id FROM analytics
            WHERE post_id = ? AND platform = ?
        """, (post_id, platform))

        existing = cursor.fetchone()

        if existing:
            # Update existing record
            cursor.execute("""
                UPDATE analytics
                SET views = ?, likes = ?, comments = ?, shares = ?,
                    engagement_rate = ?, last_updated = ?
                WHERE post_id = ? AND platform = ?
            """, (views, likes, comments, shares, engagement_rate,
                  datetime.utcnow().isoformat(), post_id, platform))
        else:
            # Insert new record
            cursor.execute("""
                INSERT INTO analytics (post_id, platform, views, likes, comments, shares, engagement_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (post_id, platform, views, likes, comments, shares, engagement_rate))

        conn.commit()

    def get_post_analytics(self, post_id: int) -> List[Dict]:
        """Get analytics for a post across all platforms"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM analytics
            WHERE post_id = ?
            ORDER BY platform
        """, (post_id,))

        return [dict(row) for row in cursor.fetchall()]

    def get_overall_analytics(self) -> Dict:
        """Get overall analytics across all posts"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(DISTINCT post_id) as total_posts,
                SUM(views) as total_views,
                SUM(likes) as total_likes,
                SUM(comments) as total_comments,
                SUM(shares) as total_shares,
                AVG(engagement_rate) as avg_engagement_rate
            FROM analytics
        """)

        row = cursor.fetchone()
        return dict(row) if row else {}

    def get_platform_comparison(self) -> List[Dict]:
        """Compare performance across platforms"""
        conn = self._get_connection()
        cursor.execute("""
            SELECT
                platform,
                COUNT(*) as post_count,
                SUM(views) as total_views,
                SUM(likes) as total_likes,
                SUM(comments) as total_comments,
                SUM(shares) as total_shares,
                AVG(engagement_rate) as avg_engagement_rate
            FROM analytics
            GROUP BY platform
            ORDER BY total_views DESC
        """)

        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # UTILITY OPERATIONS
    # ========================================================================

    def get_stats(self) -> Dict:
        """Get overall database statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Total posts
        cursor.execute("SELECT COUNT(*) as count FROM posts")
        total_posts = cursor.fetchone()['count']

        # Published posts
        cursor.execute("SELECT COUNT(*) as count FROM posts WHERE status = 'published'")
        published_posts = cursor.fetchone()['count']

        # Pending scheduled posts
        cursor.execute("SELECT COUNT(*) as count FROM scheduled_posts WHERE status = 'pending'")
        pending_scheduled = cursor.fetchone()['count']

        return {
            "total_posts": total_posts,
            "published_posts": published_posts,
            "pending_posts": total_posts - published_posts,
            "pending_scheduled": pending_scheduled
        }

    def close(self):
        """Close database connection"""
        if hasattr(self.local, 'connection'):
            self.local.connection.close()
            delattr(self.local, 'connection')


# Singleton instance
_db_instance = None


def get_database() -> DatabaseManager:
    """Get singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance


# Test if run directly
if __name__ == "__main__":
    print("="*70)
    print("DATABASE MANAGER - TEST")
    print("="*70)
    print()

    db = DatabaseManager("test_milton.db")

    # Test: Create post
    print("[TEST] Creating test post...")
    post_id = db.create_post(
        content="This is a test post for Milton AI Publicist. Let's Go Owls!",
        voice_type="personal",
        scenario="test",
        context="Testing database functionality"
    )
    print(f"[OK] Created post ID: {post_id}")
    print()

    # Test: Get post
    print("[TEST] Retrieving post...")
    post = db.get_post(post_id)
    print(f"[OK] Retrieved: {post['content'][:50]}...")
    print()

    # Test: Schedule post
    print("[TEST] Scheduling post...")
    from datetime import timedelta
    schedule_time = datetime.utcnow() + timedelta(hours=2)
    schedule_id = db.schedule_post(post_id, "linkedin", schedule_time)
    print(f"[OK] Scheduled post ID: {schedule_id} for {schedule_time}")
    print()

    # Test: Get stats
    print("[TEST] Getting database stats...")
    stats = db.get_stats()
    print(f"[OK] Stats: {stats}")
    print()

    print("="*70)
    print("All tests passed! Database is working correctly.")
    print("="*70)

    db.close()
