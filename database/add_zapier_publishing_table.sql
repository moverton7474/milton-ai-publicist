-- Migration: Add post_publications table for tracking Zapier publishing
-- Created: 2025-10-20
-- Purpose: Track all publishing attempts via Zapier webhooks

-- Create post_publications table
CREATE TABLE IF NOT EXISTS post_publications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    platform TEXT NOT NULL,  -- linkedin, instagram, twitter, facebook
    success BOOLEAN NOT NULL DEFAULT 0,
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    post_url TEXT,  -- URL of published post (from Zapier callback)
    error_message TEXT,  -- Error details if failed
    response_data TEXT,  -- Full JSON response from Zapier (for debugging)
    retry_count INTEGER DEFAULT 0,
    webhook_url TEXT,  -- Which webhook was used

    -- Foreign key to posts table
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_post_publications_post_id
    ON post_publications(post_id);

CREATE INDEX IF NOT EXISTS idx_post_publications_platform
    ON post_publications(platform);

CREATE INDEX IF NOT EXISTS idx_post_publications_success
    ON post_publications(success);

CREATE INDEX IF NOT EXISTS idx_post_publications_published_at
    ON post_publications(published_at DESC);

CREATE INDEX IF NOT EXISTS idx_post_publications_post_platform
    ON post_publications(post_id, platform);

-- Create view for easy querying of successful publishes
CREATE VIEW IF NOT EXISTS successful_publications AS
SELECT
    pp.id,
    pp.post_id,
    p.content,
    p.voice_type,
    p.scenario,
    pp.platform,
    pp.post_url,
    pp.published_at,
    pp.response_data
FROM post_publications pp
INNER JOIN posts p ON pp.post_id = p.id
WHERE pp.success = 1
ORDER BY pp.published_at DESC;

-- Create view for failed publishes needing attention
CREATE VIEW IF NOT EXISTS failed_publications AS
SELECT
    pp.id,
    pp.post_id,
    p.content,
    pp.platform,
    pp.error_message,
    pp.retry_count,
    pp.published_at,
    pp.response_data
FROM post_publications pp
INNER JOIN posts p ON pp.post_id = p.id
WHERE pp.success = 0
ORDER BY pp.published_at DESC;

-- Create view for publishing stats by platform
CREATE VIEW IF NOT EXISTS publishing_stats_by_platform AS
SELECT
    platform,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed,
    ROUND(CAST(SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 2) as success_rate,
    MAX(published_at) as last_published
FROM post_publications
GROUP BY platform;

-- Insert sample data comment (for testing/documentation)
-- Example:
-- INSERT INTO post_publications (post_id, platform, success, post_url)
-- VALUES (1, 'linkedin', 1, 'https://linkedin.com/posts/milton-overton-12345');

-- Migration completed successfully
SELECT 'Migration completed: post_publications table created' as status;
