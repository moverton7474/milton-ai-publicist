"""
Database Migration System
Handles database schema migrations and version management
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import hashlib


class Migration:
    """Represents a single database migration"""

    def __init__(self, version: int, name: str, up_sql: str, down_sql: str):
        """
        Initialize migration

        Args:
            version: Migration version number
            name: Migration name/description
            up_sql: SQL to apply migration
            down_sql: SQL to rollback migration
        """
        self.version = version
        self.name = name
        self.up_sql = up_sql
        self.down_sql = down_sql
        self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate checksum of migration SQL"""
        content = f"{self.version}{self.name}{self.up_sql}{self.down_sql}"
        return hashlib.sha256(content.encode()).hexdigest()


class MigrationManager:
    """Manages database migrations"""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize migration manager

        Args:
            db_path: Path to SQLite database
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent / "milton_publicist.db"

        self.db_path = Path(db_path)
        self.migrations: List[Migration] = []
        self._ensure_migrations_table()
        self._load_migrations()

    def _ensure_migrations_table(self):
        """Create migrations tracking table if it doesn't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    rolled_back_at TIMESTAMP NULL
                )
            """)
            conn.commit()

    def _load_migrations(self):
        """Load migration definitions"""
        # Migration 001: Add OAuth tokens table
        self.migrations.append(Migration(
            version=1,
            name="add_oauth_tokens_table",
            up_sql="""
                CREATE TABLE IF NOT EXISTS oauth_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL UNIQUE,
                    access_token TEXT NOT NULL,
                    refresh_token TEXT,
                    token_type TEXT DEFAULT 'Bearer',
                    expires_at TIMESTAMP,
                    scope TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX idx_oauth_platform ON oauth_tokens(platform);
                CREATE INDEX idx_oauth_expires ON oauth_tokens(expires_at);
            """,
            down_sql="""
                DROP INDEX IF EXISTS idx_oauth_expires;
                DROP INDEX IF EXISTS idx_oauth_platform;
                DROP TABLE IF EXISTS oauth_tokens;
            """
        ))

        # Migration 002: Add API keys table
        self.migrations.append(Migration(
            version=2,
            name="add_api_keys_table",
            up_sql="""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_name TEXT NOT NULL UNIQUE,
                    api_key_encrypted TEXT NOT NULL,
                    key_type TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    last_validated_at TIMESTAMP,
                    validation_status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX idx_api_keys_service ON api_keys(service_name);
                CREATE INDEX idx_api_keys_active ON api_keys(is_active);
            """,
            down_sql="""
                DROP INDEX IF EXISTS idx_api_keys_active;
                DROP INDEX IF EXISTS idx_api_keys_service;
                DROP TABLE IF EXISTS api_keys;
            """
        ))

        # Migration 003: Add content_tags column to posts table
        self.migrations.append(Migration(
            version=3,
            name="add_content_tags_to_posts",
            up_sql="""
                ALTER TABLE posts ADD COLUMN tags TEXT;
                ALTER TABLE posts ADD COLUMN metadata TEXT;
                CREATE INDEX idx_posts_tags ON posts(tags);
            """,
            down_sql="""
                DROP INDEX IF EXISTS idx_posts_tags;
                -- Note: SQLite doesn't support DROP COLUMN, would need table recreation
            """
        ))

        # Migration 004: Add rate limiting table
        self.migrations.append(Migration(
            version=4,
            name="add_rate_limiting_table",
            up_sql="""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    limit_type TEXT NOT NULL,
                    request_count INTEGER DEFAULT 0,
                    window_start TIMESTAMP NOT NULL,
                    window_end TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX idx_rate_limits_key ON rate_limits(key, window_end);
                CREATE INDEX idx_rate_limits_window ON rate_limits(window_end);
            """,
            down_sql="""
                DROP INDEX IF EXISTS idx_rate_limits_window;
                DROP INDEX IF EXISTS idx_rate_limits_key;
                DROP TABLE IF EXISTS rate_limits;
            """
        ))

        # Migration 005: Add audit log table
        self.migrations.append(Migration(
            version=5,
            name="add_audit_log_table",
            up_sql="""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    action TEXT NOT NULL,
                    resource_type TEXT,
                    resource_id INTEGER,
                    details TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX idx_audit_user ON audit_log(user_id);
                CREATE INDEX idx_audit_action ON audit_log(action);
                CREATE INDEX idx_audit_created ON audit_log(created_at);
            """,
            down_sql="""
                DROP INDEX IF EXISTS idx_audit_created;
                DROP INDEX IF EXISTS idx_audit_action;
                DROP INDEX IF EXISTS idx_audit_user;
                DROP TABLE IF EXISTS audit_log;
            """
        ))

    def get_current_version(self) -> int:
        """Get current database version"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT MAX(version)
                FROM schema_migrations
                WHERE rolled_back_at IS NULL
            """)
            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0

    def get_pending_migrations(self) -> List[Migration]:
        """Get migrations that haven't been applied"""
        current_version = self.get_current_version()
        return [m for m in self.migrations if m.version > current_version]

    def get_applied_migrations(self) -> List[Dict]:
        """Get list of applied migrations"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT version, name, checksum, applied_at, rolled_back_at
                FROM schema_migrations
                ORDER BY version
            """)
            return [dict(row) for row in cursor.fetchall()]

    def migrate_up(self, target_version: Optional[int] = None) -> List[int]:
        """
        Apply pending migrations

        Args:
            target_version: Target version to migrate to (None = latest)

        Returns:
            List of applied migration versions
        """
        current_version = self.get_current_version()
        pending = self.get_pending_migrations()

        if target_version is not None:
            pending = [m for m in pending if m.version <= target_version]

        applied = []

        with sqlite3.connect(self.db_path) as conn:
            for migration in pending:
                try:
                    print(f"Applying migration {migration.version}: {migration.name}")

                    # Execute migration SQL
                    conn.executescript(migration.up_sql)

                    # Record migration
                    conn.execute("""
                        INSERT INTO schema_migrations (version, name, checksum)
                        VALUES (?, ?, ?)
                    """, (migration.version, migration.name, migration.checksum))

                    conn.commit()
                    applied.append(migration.version)

                    print(f"  [OK] Migration {migration.version} applied successfully")

                except Exception as e:
                    print(f"  [ERROR] Migration {migration.version} failed: {e}")
                    conn.rollback()
                    raise

        return applied

    def migrate_down(self, target_version: int) -> List[int]:
        """
        Rollback migrations to target version

        Args:
            target_version: Version to rollback to

        Returns:
            List of rolled back migration versions
        """
        current_version = self.get_current_version()

        if target_version >= current_version:
            print(f"Already at or below version {target_version}")
            return []

        # Get migrations to rollback (in reverse order)
        to_rollback = [
            m for m in reversed(self.migrations)
            if target_version < m.version <= current_version
        ]

        rolled_back = []

        with sqlite3.connect(self.db_path) as conn:
            for migration in to_rollback:
                try:
                    print(f"Rolling back migration {migration.version}: {migration.name}")

                    # Execute rollback SQL
                    conn.executescript(migration.down_sql)

                    # Mark as rolled back
                    conn.execute("""
                        UPDATE schema_migrations
                        SET rolled_back_at = CURRENT_TIMESTAMP
                        WHERE version = ?
                    """, (migration.version,))

                    conn.commit()
                    rolled_back.append(migration.version)

                    print(f"  [OK] Migration {migration.version} rolled back successfully")

                except Exception as e:
                    print(f"  [ERROR] Rollback {migration.version} failed: {e}")
                    conn.rollback()
                    raise

        return rolled_back

    def status(self) -> Dict:
        """Get migration status"""
        current_version = self.get_current_version()
        pending = self.get_pending_migrations()
        applied = self.get_applied_migrations()

        return {
            "current_version": current_version,
            "latest_version": max([m.version for m in self.migrations]),
            "pending_count": len(pending),
            "applied_count": len([m for m in applied if m["rolled_back_at"] is None]),
            "pending_migrations": [
                {"version": m.version, "name": m.name}
                for m in pending
            ],
            "applied_migrations": applied
        }

    def validate_checksums(self) -> List[Dict]:
        """Validate checksums of applied migrations"""
        issues = []

        applied = self.get_applied_migrations()

        for applied_migration in applied:
            if applied_migration["rolled_back_at"]:
                continue  # Skip rolled back migrations

            # Find corresponding migration definition
            migration_def = next(
                (m for m in self.migrations if m.version == applied_migration["version"]),
                None
            )

            if not migration_def:
                issues.append({
                    "version": applied_migration["version"],
                    "issue": "migration_not_found",
                    "message": "Applied migration not found in migration definitions"
                })
                continue

            if migration_def.checksum != applied_migration["checksum"]:
                issues.append({
                    "version": applied_migration["version"],
                    "issue": "checksum_mismatch",
                    "message": "Migration checksum doesn't match applied version",
                    "expected": migration_def.checksum,
                    "actual": applied_migration["checksum"]
                })

        return issues


def migrate_database(db_path: Optional[str] = None, target_version: Optional[int] = None):
    """
    Convenience function to run migrations

    Args:
        db_path: Path to database
        target_version: Target version (None = latest)
    """
    manager = MigrationManager(db_path)

    print("=" * 60)
    print("DATABASE MIGRATION")
    print("=" * 60)
    print()

    # Show current status
    status = manager.status()
    print(f"Current Version: {status['current_version']}")
    print(f"Latest Version: {status['latest_version']}")
    print(f"Pending Migrations: {status['pending_count']}")
    print()

    if status['pending_count'] == 0:
        print("[OK] Database is up to date")
        return

    # Apply migrations
    print("Applying migrations...")
    print()

    applied = manager.migrate_up(target_version)

    print()
    print("=" * 60)
    print(f"[OK] Applied {len(applied)} migration(s)")
    print("=" * 60)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        manager = MigrationManager()

        if command == "status":
            status = manager.status()
            print(f"Current Version: {status['current_version']}")
            print(f"Pending Migrations: {status['pending_count']}")

        elif command == "up":
            migrate_database()

        elif command == "down":
            if len(sys.argv) < 3:
                print("Usage: python migrations.py down <version>")
                sys.exit(1)

            target_version = int(sys.argv[2])
            manager.migrate_down(target_version)

        elif command == "validate":
            issues = manager.validate_checksums()
            if not issues:
                print("[OK] All checksums valid")
            else:
                print("[ERROR] Checksum validation failed:")
                for issue in issues:
                    print(f"  Version {issue['version']}: {issue['message']}")

        else:
            print("Unknown command. Use: status, up, down, or validate")
    else:
        migrate_database()
