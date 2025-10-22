-- Migration #6: Analytics Schema Enhancements
-- Created: 2025-10-22
-- Purpose: Enhance analytics_snapshots table with better tracking and constraints

-- Add unique constraint to prevent duplicate snapshots for the same period
ALTER TABLE analytics_snapshots
ADD CONSTRAINT unique_period_snapshot UNIQUE (period_type, period_start);

-- Add top-performing content tracking
ALTER TABLE analytics_snapshots
ADD COLUMN top_post_id INTEGER REFERENCES generated_content(content_id);

ALTER TABLE analytics_snapshots
ADD COLUMN top_post_platform VARCHAR(50);

ALTER TABLE analytics_snapshots
ADD COLUMN top_post_engagement_rate DECIMAL(5,2);

-- Add cross-platform aggregate metrics
ALTER TABLE analytics_snapshots
ADD COLUMN total_posts_all_platforms INTEGER DEFAULT 0;

ALTER TABLE analytics_snapshots
ADD COLUMN total_impressions_all_platforms BIGINT DEFAULT 0;

ALTER TABLE analytics_snapshots
ADD COLUMN avg_engagement_all_platforms DECIMAL(5,2);

-- Add video content metrics
ALTER TABLE analytics_snapshots
ADD COLUMN avatar_video_views INTEGER DEFAULT 0;

ALTER TABLE analytics_snapshots
ADD COLUMN avatar_video_completion_rate DECIMAL(5,2);

-- Add audience growth metrics
ALTER TABLE analytics_snapshots
ADD COLUMN total_followers_linkedin INTEGER DEFAULT 0;

ALTER TABLE analytics_snapshots
ADD COLUMN total_followers_twitter INTEGER DEFAULT 0;

ALTER TABLE analytics_snapshots
ADD COLUMN total_followers_instagram INTEGER DEFAULT 0;

-- Add content pillar performance tracking
ALTER TABLE analytics_snapshots
ADD COLUMN ai_innovation_pillar_posts INTEGER DEFAULT 0;

ALTER TABLE analytics_snapshots
ADD COLUMN leadership_pillar_posts INTEGER DEFAULT 0;

ALTER TABLE analytics_snapshots
ADD COLUMN future_sports_pillar_posts INTEGER DEFAULT 0;

ALTER TABLE analytics_snapshots
ADD COLUMN best_performing_pillar VARCHAR(100);

-- Add timing analytics
ALTER TABLE analytics_snapshots
ADD COLUMN avg_time_to_publish_minutes INTEGER;

ALTER TABLE analytics_snapshots
ADD COLUMN content_velocity DECIMAL(5,2);  -- Posts per day

-- Add quality metrics
ALTER TABLE analytics_snapshots
ADD COLUMN avg_voice_authenticity_score DECIMAL(3,2);

ALTER TABLE analytics_snapshots
ADD COLUMN avg_brand_alignment_score DECIMAL(3,2);

-- Add engagement depth metrics
ALTER TABLE analytics_snapshots
ADD COLUMN total_high_value_interactions INTEGER DEFAULT 0;

ALTER TABLE analytics_snapshots
ADD COLUMN hvt_engagement_rate DECIMAL(5,2);

ALTER TABLE analytics_snapshots
ADD COLUMN total_meaningful_conversations INTEGER DEFAULT 0;

-- Create index for faster period-based queries
CREATE INDEX idx_analytics_period_lookup ON analytics_snapshots(period_type, period_start, period_end);

-- Create index for top-performing content queries
CREATE INDEX idx_analytics_top_posts ON analytics_snapshots(top_post_engagement_rate DESC);

-- Create view for cross-platform performance comparison
CREATE OR REPLACE VIEW platform_performance_comparison AS
SELECT
    period_type,
    period_start,
    period_end,
    -- LinkedIn
    linkedin_posts_count,
    linkedin_engagement_rate,
    linkedin_impressions,
    -- Twitter
    twitter_posts_count,
    twitter_engagement_rate,
    twitter_impressions,
    -- Instagram
    instagram_posts_count,
    instagram_engagement_rate,
    instagram_impressions,
    -- Aggregates
    total_posts_all_platforms,
    total_impressions_all_platforms,
    avg_engagement_all_platforms,
    -- Growth
    linkedin_follower_growth,
    twitter_follower_growth,
    -- Quality
    avg_voice_authenticity_score,
    avg_brand_alignment_score,
    -- Top performer
    top_post_platform,
    top_post_engagement_rate
FROM analytics_snapshots
ORDER BY period_start DESC;

-- Create view for pillar performance analysis
CREATE OR REPLACE VIEW pillar_performance_analysis AS
SELECT
    period_type,
    period_start,
    period_end,
    ai_innovation_pillar_posts,
    leadership_pillar_posts,
    future_sports_pillar_posts,
    best_performing_pillar,
    total_posts_all_platforms,
    ROUND(CAST(ai_innovation_pillar_posts AS DECIMAL) / NULLIF(total_posts_all_platforms, 0) * 100, 2) as ai_pillar_percentage,
    ROUND(CAST(leadership_pillar_posts AS DECIMAL) / NULLIF(total_posts_all_platforms, 0) * 100, 2) as leadership_pillar_percentage,
    ROUND(CAST(future_sports_pillar_posts AS DECIMAL) / NULLIF(total_posts_all_platforms, 0) * 100, 2) as future_sports_pillar_percentage
FROM analytics_snapshots
WHERE total_posts_all_platforms > 0
ORDER BY period_start DESC;

-- Create view for HVT engagement tracking
CREATE OR REPLACE VIEW hvt_engagement_summary AS
SELECT
    period_type,
    period_start,
    period_end,
    total_high_value_interactions,
    hvt_engagement_rate,
    total_meaningful_conversations,
    total_posts_all_platforms,
    ROUND(CAST(total_high_value_interactions AS DECIMAL) / NULLIF(total_posts_all_platforms, 0), 2) as hvt_interactions_per_post,
    ROUND(CAST(total_meaningful_conversations AS DECIMAL) / NULLIF(total_posts_all_platforms, 0), 2) as conversations_per_post
FROM analytics_snapshots
WHERE total_posts_all_platforms > 0
ORDER BY period_start DESC;

-- Add comment for documentation
COMMENT ON COLUMN analytics_snapshots.top_post_id IS 'Reference to the best-performing post in this period';
COMMENT ON COLUMN analytics_snapshots.content_velocity IS 'Average number of posts published per day';
COMMENT ON COLUMN analytics_snapshots.hvt_engagement_rate IS 'Engagement rate specifically from high-value targets';
COMMENT ON COLUMN analytics_snapshots.total_meaningful_conversations IS 'Count of substantive comment threads (3+ exchanges)';

-- Migration completed
SELECT 'Migration #6 completed: Analytics schema enhanced with cross-platform tracking, pillar analysis, and HVT metrics' as status;
