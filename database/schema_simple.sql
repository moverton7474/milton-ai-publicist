-- Simple SQLite Schema for Milton AI Publicist
-- Production-ready database schema for content management

-- Posts table - stores all generated content
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    voice_type TEXT NOT NULL CHECK(voice_type IN ('personal', 'professional')),
    scenario TEXT,
    context TEXT,
    word_count INTEGER,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'published', 'rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP
);

-- Scheduled posts table - for future publishing
CREATE TABLE IF NOT EXISTS scheduled_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    platforms TEXT NOT NULL, -- JSON array
    scheduled_time TIMESTAMP NOT NULL,
    status TEXT NOT NULL DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'published', 'cancelled', 'failed')),
    metadata TEXT, -- JSON object
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

-- Publishing results table - tracks where posts were published
CREATE TABLE IF NOT EXISTS publishing_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    platform TEXT NOT NULL,
    platform_post_id TEXT,
    platform_url TEXT,
    success BOOLEAN NOT NULL DEFAULT 0,
    error_message TEXT,
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

-- Analytics table - stores performance metrics
CREATE TABLE IF NOT EXISTS analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    platform TEXT NOT NULL,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    engagement INTEGER DEFAULT 0,
    tracked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_time ON scheduled_posts(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_status ON scheduled_posts(status);
CREATE INDEX IF NOT EXISTS idx_publishing_results_post ON publishing_results(post_id);
CREATE INDEX IF NOT EXISTS idx_analytics_post ON analytics(post_id);

-- Trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_posts_timestamp
AFTER UPDATE ON posts
FOR EACH ROW
BEGIN
    UPDATE posts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Views for common queries
CREATE VIEW IF NOT EXISTS posts_with_stats AS
SELECT
    p.id,
    p.content,
    p.voice_type,
    p.scenario,
    p.word_count,
    p.status,
    p.created_at,
    p.published_at,
    COUNT(DISTINCT pr.id) as publish_count,
    GROUP_CONCAT(DISTINCT pr.platform) as platforms,
    COALESCE(SUM(a.views), 0) as total_views,
    COALESCE(SUM(a.engagement), 0) as total_engagement
FROM posts p
LEFT JOIN publishing_results pr ON p.id = pr.post_id AND pr.success = 1
LEFT JOIN analytics a ON p.id = a.post_id
GROUP BY p.id;

CREATE VIEW IF NOT EXISTS upcoming_scheduled_posts AS
SELECT
    sp.id,
    sp.post_id,
    p.content,
    sp.platforms,
    sp.scheduled_time,
    sp.status,
    (julianday(sp.scheduled_time) - julianday('now')) * 24 as hours_until_publish
FROM scheduled_posts sp
JOIN posts p ON sp.post_id = p.id
WHERE sp.status = 'scheduled'
AND sp.scheduled_time > datetime('now')
ORDER BY sp.scheduled_time ASC;
