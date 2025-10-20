"""
Database Manager - SQLite database operations
Handles all database persistence for the Milton AI Publicist
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from contextlib import contextmanager

class DatabaseManager:
    """
    Manages SQLite database operations
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager

        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent / "milton_publicist.db"

        self.db_path = Path(db_path)
        self._initialize_database()

    def _initialize_database(self):
        """Initialize database with schema if it doesn't exist"""
        schema_path = Path(__file__).parent / "schema_simple.sql"

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        with self.get_connection() as conn:
            conn.executescript(schema_sql)
            conn.commit()

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections

        Yields:
            sqlite3.Connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        try:
            yield conn
        finally:
            conn.close()

    # ==================== POST OPERATIONS ====================

    def create_post(
        self,
        content: str,
        voice_type: str,
        scenario: Optional[str] = None,
        context: Optional[str] = None,
        word_count: Optional[int] = None
    ) -> int:
        """
        Create a new post

        Args:
            content: Post content
            voice_type: 'personal' or 'professional'
            scenario: Optional scenario name
            context: Optional context used for generation
            word_count: Optional word count

        Returns:
            Post ID
        """
        if word_count is None:
            word_count = len(content.split())

        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO posts (content, voice_type, scenario, context, word_count)
                VALUES (?, ?, ?, ?, ?)
                """,
                (content, voice_type, scenario, context, word_count)
            )
            conn.commit()
            return cursor.lastrowid

    def get_post(self, post_id: int) -> Optional[Dict]:
        """
        Get a post by ID

        Args:
            post_id: Post ID

        Returns:
            Post dict or None
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM posts WHERE id = ?",
                (post_id,)
            )
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

    def get_all_posts(self, status: Optional[str] = None) -> List[Dict]:
        """
        Get all posts, optionally filtered by status

        Args:
            status: Optional status filter

        Returns:
            List of post dicts
        """
        with self.get_connection() as conn:
            if status:
                cursor = conn.execute(
                    "SELECT * FROM posts WHERE status = ? ORDER BY created_at DESC",
                    (status,)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM posts ORDER BY created_at DESC"
                )

            return [dict(row) for row in cursor.fetchall()]

    def update_post(
        self,
        post_id: int,
        content: Optional[str] = None,
        status: Optional[str] = None,
        published_at: Optional[datetime] = None
    ) -> bool:
        """
        Update a post

        Args:
            post_id: Post ID
            content: Optional new content
            status: Optional new status
            published_at: Optional publication timestamp

        Returns:
            True if updated, False if not found
        """
        updates = []
        params = []

        if content is not None:
            updates.append("content = ?")
            params.append(content)
            updates.append("word_count = ?")
            params.append(len(content.split()))

        if status is not None:
            updates.append("status = ?")
            params.append(status)

        if published_at is not None:
            updates.append("published_at = ?")
            params.append(published_at.isoformat())

        if not updates:
            return False

        params.append(post_id)

        with self.get_connection() as conn:
            cursor = conn.execute(
                f"UPDATE posts SET {', '.join(updates)} WHERE id = ?",
                params
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_post(self, post_id: int) -> bool:
        """
        Delete a post

        Args:
            post_id: Post ID

        Returns:
            True if deleted, False if not found
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM posts WHERE id = ?",
                (post_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    # ==================== SCHEDULED POSTS ====================

    def schedule_post(
        self,
        post_id: int,
        platforms: List[str],
        scheduled_time: datetime,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Schedule a post for future publishing

        Args:
            post_id: Post ID
            platforms: List of platform names
            scheduled_time: When to publish
            metadata: Optional metadata

        Returns:
            Scheduled post ID
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO scheduled_posts (post_id, platforms, scheduled_time, metadata)
                VALUES (?, ?, ?, ?)
                """,
                (
                    post_id,
                    json.dumps(platforms),
                    scheduled_time.isoformat(),
                    json.dumps(metadata) if metadata else None
                )
            )
            conn.commit()
            return cursor.lastrowid

    def get_due_scheduled_posts(self) -> List[Dict]:
        """
        Get scheduled posts that are due for publishing

        Returns:
            List of scheduled post dicts
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM scheduled_posts
                WHERE status = 'scheduled'
                AND datetime(scheduled_time) <= datetime('now')
                ORDER BY scheduled_time ASC
                """
            )

            posts = []
            for row in cursor.fetchall():
                post_dict = dict(row)
                post_dict['platforms'] = json.loads(post_dict['platforms'])
                if post_dict['metadata']:
                    post_dict['metadata'] = json.loads(post_dict['metadata'])
                posts.append(post_dict)

            return posts

    def update_scheduled_post_status(
        self,
        scheduled_post_id: int,
        status: str
    ) -> bool:
        """
        Update status of a scheduled post

        Args:
            scheduled_post_id: Scheduled post ID
            status: New status

        Returns:
            True if updated
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                "UPDATE scheduled_posts SET status = ? WHERE id = ?",
                (status, scheduled_post_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    # ==================== PUBLISHING RESULTS ====================

    def record_publishing_result(
        self,
        post_id: int,
        platform: str,
        success: bool,
        platform_post_id: Optional[str] = None,
        platform_url: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> int:
        """
        Record a publishing result

        Args:
            post_id: Post ID
            platform: Platform name
            success: Whether publishing succeeded
            platform_post_id: Platform's post ID
            platform_url: URL to published post
            error_message: Error message if failed

        Returns:
            Publishing result ID
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO publishing_results
                (post_id, platform, success, platform_post_id, platform_url, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (post_id, platform, success, platform_post_id, platform_url, error_message)
            )
            conn.commit()
            return cursor.lastrowid

    def get_publishing_results(self, post_id: int) -> List[Dict]:
        """
        Get publishing results for a post

        Args:
            post_id: Post ID

        Returns:
            List of publishing result dicts
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM publishing_results WHERE post_id = ?",
                (post_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    # ==================== ANALYTICS ====================

    def record_analytics(
        self,
        post_id: int,
        platform: str,
        views: int = 0,
        likes: int = 0,
        comments: int = 0,
        shares: int = 0,
        engagement: Optional[int] = None
    ) -> int:
        """
        Record analytics for a post

        Args:
            post_id: Post ID
            platform: Platform name
            views: View count
            likes: Like count
            comments: Comment count
            shares: Share count
            engagement: Total engagement (defaults to sum)

        Returns:
            Analytics record ID
        """
        if engagement is None:
            engagement = likes + comments + shares

        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO analytics
                (post_id, platform, views, likes, comments, shares, engagement)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (post_id, platform, views, likes, comments, shares, engagement)
            )
            conn.commit()
            return cursor.lastrowid

    def get_post_analytics(self, post_id: int) -> List[Dict]:
        """
        Get analytics for a post

        Args:
            post_id: Post ID

        Returns:
            List of analytics dicts
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM analytics WHERE post_id = ? ORDER BY tracked_at DESC",
                (post_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    # ==================== VIEWS ====================

    def get_posts_with_stats(self, limit: int = 50) -> List[Dict]:
        """
        Get posts with publishing and analytics stats

        Args:
            limit: Maximum number of posts

        Returns:
            List of post dicts with stats
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                f"SELECT * FROM posts_with_stats ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_upcoming_scheduled_posts(self, limit: int = 20) -> List[Dict]:
        """
        Get upcoming scheduled posts

        Args:
            limit: Maximum number of posts

        Returns:
            List of scheduled post dicts
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                f"SELECT * FROM upcoming_scheduled_posts LIMIT ?",
                (limit,)
            )

            posts = []
            for row in cursor.fetchall():
                post_dict = dict(row)
                if post_dict.get('platforms'):
                    post_dict['platforms'] = json.loads(post_dict['platforms'])
                posts.append(post_dict)

            return posts


# Example usage
def main():
    """Example usage of DatabaseManager"""
    print("="*70)
    print("DATABASE MANAGER - DEMO")
    print("="*70)
    print()

    db = DatabaseManager()

    # Create a post
    print("[INFO] Creating sample post...")
    post_id = db.create_post(
        content="Excited to share our AI innovation! Let's Go Owls!",
        voice_type="personal",
        scenario="Team Celebration",
        context="AI innovation announcement"
    )
    print(f"       Post created with ID: {post_id}")
    print()

    # Get the post
    print("[INFO] Retrieving post...")
    post = db.get_post(post_id)
    print(f"       Content: {post['content'][:50]}...")
    print(f"       Status: {post['status']}")
    print()

    # Schedule the post
    print("[INFO] Scheduling post for tomorrow at 9 AM...")
    from datetime import timedelta
    tomorrow_9am = datetime.now() + timedelta(days=1)
    tomorrow_9am = tomorrow_9am.replace(hour=9, minute=0, second=0, microsecond=0)

    schedule_id = db.schedule_post(
        post_id=post_id,
        platforms=["linkedin", "twitter"],
        scheduled_time=tomorrow_9am
    )
    print(f"       Scheduled with ID: {schedule_id}")
    print()

    # Get all posts
    print("[INFO] All posts:")
    all_posts = db.get_all_posts()
    print(f"       Total posts: {len(all_posts)}")
    print()

    print("="*70)
    print("Database created at:", db.db_path)
    print("="*70)

if __name__ == "__main__":
    main()
