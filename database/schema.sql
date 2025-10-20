-- Milton Overton AI Publicist - Database Schema
-- PostgreSQL 14+

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Executive insights (Module I)
CREATE TABLE IF NOT EXISTS executive_insights (
    insight_id VARCHAR(50) PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    input_type VARCHAR(20) NOT NULL CHECK (input_type IN ('voice', 'text', 'email')),
    raw_content TEXT NOT NULL,
    transcription TEXT,
    metadata JSONB DEFAULT '{}',
    processed BOOLEAN DEFAULT FALSE,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_insights_processed ON executive_insights(processed);
CREATE INDEX idx_insights_priority ON executive_insights(priority);
CREATE INDEX idx_insights_timestamp ON executive_insights(timestamp DESC);

-- News articles (Module I)
CREATE TABLE IF NOT EXISTS news_articles (
    article_id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    url VARCHAR(1000) UNIQUE NOT NULL,
    source VARCHAR(100) NOT NULL,
    published_date TIMESTAMP WITH TIME ZONE NOT NULL,
    content TEXT,
    summary TEXT,
    categories TEXT[],
    relevance_score DECIMAL(3,2) DEFAULT 0.00,
    key_entities TEXT[],
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_articles_source ON news_articles(source);
CREATE INDEX idx_articles_relevance ON news_articles(relevance_score DESC);
CREATE INDEX idx_articles_published ON news_articles(published_date DESC);
CREATE INDEX idx_articles_processed ON news_articles(processed);

-- Content opportunities (Module I → II)
CREATE TABLE IF NOT EXISTS content_opportunities (
    opportunity_id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL CHECK (type IN ('news_reaction', 'insight_expansion', 'trend_analysis', 'avatar_video')),
    insight_id VARCHAR(50) REFERENCES executive_insights(insight_id),
    article_id INTEGER REFERENCES news_articles(article_id),
    suggested_angle TEXT NOT NULL,
    urgency VARCHAR(20) DEFAULT 'standard' CHECK (urgency IN ('immediate', 'today', 'this_week', 'standard')),
    pillar_alignment TEXT[] NOT NULL,
    target_platforms TEXT[] DEFAULT ARRAY['linkedin'],
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'rejected')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_opportunities_status ON content_opportunities(status);
CREATE INDEX idx_opportunities_urgency ON content_opportunities(urgency);
CREATE INDEX idx_opportunities_created ON content_opportunities(created_at DESC);

-- Generated content (Module II)
CREATE TABLE IF NOT EXISTS generated_content (
    content_id SERIAL PRIMARY KEY,
    opportunity_id INTEGER REFERENCES content_opportunities(opportunity_id),
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('linkedin', 'twitter', 'instagram', 'avatar_video')),
    content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('post', 'thread', 'caption', 'script')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',

    -- Quality scores
    voice_authenticity_score DECIMAL(3,2),
    brand_alignment_score DECIMAL(3,2),
    engagement_prediction_score DECIMAL(3,2),
    readability_score DECIMAL(3,2),
    overall_qa_score DECIMAL(3,2),

    -- Status
    status VARCHAR(20) DEFAULT 'pending_approval' CHECK (status IN ('pending_approval', 'approved', 'rejected', 'published', 'failed')),
    rejection_reason TEXT,

    -- Hashtags and mentions
    hashtags TEXT[],
    mentions TEXT[],

    -- Visual suggestions
    visual_suggestions JSONB,

    -- Publishing details
    optimal_post_time TIMESTAMP WITH TIME ZONE,
    scheduled_time TIMESTAMP WITH TIME ZONE,
    published_time TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_content_status ON generated_content(status);
CREATE INDEX idx_content_platform ON generated_content(platform);
CREATE INDEX idx_content_scheduled ON generated_content(scheduled_time);
CREATE INDEX idx_content_qa_score ON generated_content(overall_qa_score DESC);

-- Voice profile (Module II)
CREATE TABLE IF NOT EXISTS voice_profile (
    profile_id SERIAL PRIMARY KEY,
    version VARCHAR(20) NOT NULL,

    -- Lexical features
    vocabulary_size INTEGER,
    avg_word_length DECIMAL(4,2),
    most_common_words JSONB,
    unique_terminology TEXT[],

    -- Syntactic features
    avg_sentence_length DECIMAL(5,2),
    sentence_length_std DECIMAL(5,2),
    common_structures JSONB,
    complex_sentence_ratio DECIMAL(3,2),

    -- Semantic features
    common_themes JSONB,
    frequently_mentioned TEXT[],
    topic_distribution JSONB,

    -- Rhetorical features
    question_ratio DECIMAL(3,2),
    uses_metaphors BOOLEAN,
    data_usage_frequency DECIMAL(5,2),
    storytelling_ratio DECIMAL(3,2),
    cta_patterns TEXT[],

    -- Formatting preferences
    bullet_point_frequency DECIMAL(3,2),
    numbered_list_frequency DECIMAL(3,2),
    emoji_usage DECIMAL(3,2),
    avg_paragraph_length DECIMAL(5,2),
    line_break_pattern JSONB,

    -- Tone analysis
    primary_tone VARCHAR(100),
    tone_distribution JSONB,
    formality_level VARCHAR(50),

    -- Training metadata
    trained_on_corpus_size INTEGER,
    training_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_voice_profile_active ON voice_profile(is_active);
CREATE INDEX idx_voice_profile_version ON voice_profile(version);

-- Published posts tracking (Module III)
CREATE TABLE IF NOT EXISTS published_posts (
    post_id SERIAL PRIMARY KEY,
    content_id INTEGER REFERENCES generated_content(content_id),
    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(200),  -- External platform's ID
    platform_url VARCHAR(1000),

    -- Publishing details
    published_at TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Engagement metrics (updated periodically)
    views INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2),

    -- Analytics
    last_metrics_update TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_published_platform ON published_posts(platform);
CREATE INDEX idx_published_date ON published_posts(published_at DESC);
CREATE INDEX idx_published_engagement ON published_posts(engagement_rate DESC);

-- PR opportunities (Module IV)
CREATE TABLE IF NOT EXISTS pr_opportunities (
    opportunity_id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL CHECK (type IN ('conference_speaking', 'podcast', 'media_interview', 'panel', 'webinar')),
    title VARCHAR(500) NOT NULL,
    organization VARCHAR(200),
    url VARCHAR(1000),

    -- Opportunity details
    description TEXT,
    audience_size INTEGER,
    deadline TIMESTAMP WITH TIME ZONE,
    event_date TIMESTAMP WITH TIME ZONE,

    -- Scoring
    fit_score DECIMAL(3,2),
    audience_alignment_score DECIMAL(3,2),
    platform_credibility_score DECIMAL(3,2),
    timing_score DECIMAL(3,2),
    competition_score DECIMAL(3,2),

    -- Status tracking
    status VARCHAR(50) DEFAULT 'identified' CHECK (status IN ('identified', 'pitch_drafted', 'pitch_sent', 'follow_up', 'accepted', 'rejected', 'completed')),
    pitch_sent_date TIMESTAMP WITH TIME ZONE,
    follow_up_dates TIMESTAMP WITH TIME ZONE[],

    -- Outcome
    outcome VARCHAR(50),
    outcome_notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_pr_opps_type ON pr_opportunities(type);
CREATE INDEX idx_pr_opps_status ON pr_opportunities(status);
CREATE INDEX idx_pr_opps_fit_score ON pr_opportunities(fit_score DESC);
CREATE INDEX idx_pr_opps_deadline ON pr_opportunities(deadline);

-- Generated pitches (Module IV)
CREATE TABLE IF NOT EXISTS generated_pitches (
    pitch_id SERIAL PRIMARY KEY,
    opportunity_id INTEGER REFERENCES pr_opportunities(opportunity_id),
    pitch_type VARCHAR(50) NOT NULL,

    -- Content
    subject_line VARCHAR(200),
    pitch_content TEXT NOT NULL,

    -- Additional materials
    abstract TEXT,
    learning_objectives TEXT[],
    session_format VARCHAR(100),

    -- Status
    status VARCHAR(50) DEFAULT 'drafted' CHECK (status IN ('drafted', 'approved', 'sent', 'rejected')),

    -- Metadata
    personalization_score DECIMAL(3,2),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_pitches_opportunity ON generated_pitches(opportunity_id);
CREATE INDEX idx_pitches_status ON generated_pitches(status);

-- High-value targets (Module III - Engagement)
CREATE TABLE IF NOT EXISTS high_value_targets (
    hvt_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    title VARCHAR(200),
    organization VARCHAR(200),

    -- Platform profiles
    linkedin_url VARCHAR(500),
    twitter_handle VARCHAR(100),

    -- Category
    category VARCHAR(50) CHECK (category IN ('power_four_ad', 'ncaa_official', 'journalist', 'influencer', 'industry_leader', 'vendor')),

    -- Relationship tracking
    relationship_value_score DECIMAL(3,2),
    last_interaction_date TIMESTAMP WITH TIME ZONE,
    interaction_count INTEGER DEFAULT 0,

    -- Notes
    notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_hvt_category ON high_value_targets(category);
CREATE INDEX idx_hvt_relationship_score ON high_value_targets(relationship_value_score DESC);

-- Engagement interactions (Module III)
CREATE TABLE IF NOT EXISTS engagement_interactions (
    interaction_id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES published_posts(post_id),
    hvt_id INTEGER REFERENCES high_value_targets(hvt_id),

    -- Interaction details
    interaction_type VARCHAR(50) CHECK (interaction_type IN ('comment', 'like', 'share', 'mention', 'dm')),
    platform VARCHAR(50) NOT NULL,
    commenter_name VARCHAR(200),
    comment_text TEXT,

    -- Response
    response_drafted TEXT,
    response_sent TEXT,
    response_sent_at TIMESTAMP WITH TIME ZONE,

    -- Classification
    is_hvt BOOLEAN DEFAULT FALSE,
    requires_follow_up BOOLEAN DEFAULT FALSE,
    follow_up_action VARCHAR(200),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_interactions_post ON engagement_interactions(post_id);
CREATE INDEX idx_interactions_hvt ON engagement_interactions(hvt_id);
CREATE INDEX idx_interactions_is_hvt ON engagement_interactions(is_hvt);

-- Analytics snapshots (Module V)
CREATE TABLE IF NOT EXISTS analytics_snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    period_type VARCHAR(20) CHECK (period_type IN ('weekly', 'monthly', 'quarterly')),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    -- LinkedIn metrics
    linkedin_posts_count INTEGER DEFAULT 0,
    linkedin_impressions INTEGER DEFAULT 0,
    linkedin_engagement_rate DECIMAL(5,2),
    linkedin_reach INTEGER DEFAULT 0,
    linkedin_follower_growth INTEGER DEFAULT 0,

    -- Twitter metrics
    twitter_posts_count INTEGER DEFAULT 0,
    twitter_impressions INTEGER DEFAULT 0,
    twitter_engagement_rate DECIMAL(5,2),
    twitter_follower_growth INTEGER DEFAULT 0,

    -- Instagram metrics
    instagram_posts_count INTEGER DEFAULT 0,
    instagram_impressions INTEGER DEFAULT 0,
    instagram_engagement_rate DECIMAL(5,2),

    -- Avatar videos
    avatar_videos_count INTEGER DEFAULT 0,
    avatar_video_avg_engagement DECIMAL(5,2),

    -- Inbound opportunities
    inbound_speaking_requests INTEGER DEFAULT 0,
    inbound_podcast_requests INTEGER DEFAULT 0,
    inbound_media_requests INTEGER DEFAULT 0,

    -- PR outcomes
    pr_pitches_sent INTEGER DEFAULT 0,
    pr_pitches_accepted INTEGER DEFAULT 0,
    pr_pitch_success_rate DECIMAL(5,2),

    -- Share of Voice
    share_of_voice_score DECIMAL(5,2),
    competitor_avg_engagement DECIMAL(5,2),

    -- Growth trends
    wow_growth_rate DECIMAL(5,2),  -- Week-over-week
    momentum VARCHAR(20),  -- accelerating, maintaining, declining

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_snapshots_period ON analytics_snapshots(period_type, period_start DESC);

-- System logs
CREATE TABLE IF NOT EXISTS system_logs (
    log_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    level VARCHAR(20) CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    module VARCHAR(100),
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_logs_level ON system_logs(level);
CREATE INDEX idx_logs_timestamp ON system_logs(timestamp DESC);
CREATE INDEX idx_logs_module ON system_logs(module);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_insights_updated_at BEFORE UPDATE ON executive_insights FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON news_articles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_opportunities_updated_at BEFORE UPDATE ON content_opportunities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_content_updated_at BEFORE UPDATE ON generated_content FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_posts_updated_at BEFORE UPDATE ON published_posts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pr_opps_updated_at BEFORE UPDATE ON pr_opportunities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pitches_updated_at BEFORE UPDATE ON generated_pitches FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_hvt_updated_at BEFORE UPDATE ON high_value_targets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Approval queue view
CREATE OR REPLACE VIEW approval_queue AS
SELECT
    gc.content_id,
    gc.platform,
    gc.content_type,
    gc.content,
    gc.overall_qa_score,
    gc.voice_authenticity_score,
    gc.brand_alignment_score,
    gc.engagement_prediction_score,
    gc.hashtags,
    gc.visual_suggestions,
    gc.optimal_post_time,
    gc.created_at,
    co.type AS opportunity_type,
    co.urgency,
    co.pillar_alignment,
    ei.raw_content AS original_insight,
    na.title AS related_article_title,
    na.url AS related_article_url
FROM generated_content gc
LEFT JOIN content_opportunities co ON gc.opportunity_id = co.opportunity_id
LEFT JOIN executive_insights ei ON co.insight_id = ei.insight_id
LEFT JOIN news_articles na ON co.article_id = na.article_id
WHERE gc.status = 'pending_approval'
ORDER BY
    CASE co.urgency
        WHEN 'immediate' THEN 1
        WHEN 'today' THEN 2
        WHEN 'this_week' THEN 3
        ELSE 4
    END,
    gc.overall_qa_score DESC,
    gc.created_at ASC;

-- Performance dashboard view
CREATE OR REPLACE VIEW performance_dashboard AS
SELECT
    pp.platform,
    COUNT(*) AS total_posts,
    AVG(pp.engagement_rate) AS avg_engagement_rate,
    SUM(pp.impressions) AS total_impressions,
    SUM(pp.likes) AS total_likes,
    SUM(pp.comments) AS total_comments,
    SUM(pp.shares) AS total_shares,
    DATE_TRUNC('week', pp.published_at) AS week_start
FROM published_posts pp
WHERE pp.published_at >= NOW() - INTERVAL '90 days'
GROUP BY pp.platform, DATE_TRUNC('week', pp.published_at)
ORDER BY week_start DESC, pp.platform;

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert default voice profile (will be retrained with actual data)
INSERT INTO voice_profile (
    version,
    avg_sentence_length,
    question_ratio,
    storytelling_ratio,
    primary_tone,
    formality_level,
    is_active,
    trained_on_corpus_size
) VALUES (
    '1.0.0',
    18.0,
    0.15,
    0.20,
    'visionary_strategic_approachable',
    'professional_accessible',
    TRUE,
    0
) ON CONFLICT DO NOTHING;

-- Insert sample high-value target categories for reference
-- (Actual HVTs should be added through the application)

COMMENT ON TABLE executive_insights IS 'Milton''s raw insights captured via voice, text, or email';
COMMENT ON TABLE news_articles IS 'Monitored news articles from various sources';
COMMENT ON TABLE content_opportunities IS 'Synthesized opportunities for content creation';
COMMENT ON TABLE generated_content IS 'AI-generated content pending approval or published';
COMMENT ON TABLE voice_profile IS 'Milton''s voice profile for authentic content generation';
COMMENT ON TABLE published_posts IS 'Tracking of published posts across platforms';
COMMENT ON TABLE pr_opportunities IS 'Speaking, podcast, and media opportunities';
COMMENT ON TABLE generated_pitches IS 'Auto-generated pitches for PR opportunities';
COMMENT ON TABLE high_value_targets IS 'High-value relationship targets for engagement';
COMMENT ON TABLE engagement_interactions IS 'Tracking of interactions with HVTs';
COMMENT ON TABLE analytics_snapshots IS 'Periodic analytics snapshots for reporting';
