"""
Enhanced Analytics Engine - Milton AI Publicist
Track engagement, analyze performance, and provide insights
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import json
from .database import get_database


class AnalyticsEngine:
    """
    Advanced analytics engine for social media performance

    Features:
    - Engagement tracking (views, likes, comments, shares)
    - Performance metrics and trends
    - Best time to post suggestions
    - Content performance analysis
    - Scenario effectiveness tracking
    - Voice type comparison
    """

    def __init__(self):
        """Initialize analytics engine"""
        self.db = get_database()

    # ========================================================================
    # ENGAGEMENT TRACKING
    # ========================================================================

    def record_engagement(
        self,
        post_id: int,
        platform: str,
        views: int = 0,
        likes: int = 0,
        comments: int = 0,
        shares: int = 0,
        clicks: int = 0
    ) -> bool:
        """
        Record engagement metrics for a post

        Args:
            post_id: Post ID
            platform: 'linkedin', 'twitter', 'instagram'
            views: Number of views/impressions
            likes: Number of likes/reactions
            comments: Number of comments
            shares: Number of shares/retweets
            clicks: Number of link clicks

        Returns:
            bool: Success status
        """
        try:
            # Calculate engagement rate
            engagement_rate = 0.0
            if views > 0:
                total_engagement = likes + comments + shares + clicks
                engagement_rate = (total_engagement / views) * 100

            # Record metrics using flat schema
            conn = self.db._get_connection()
            cursor = conn.cursor()

            # Check if record exists
            cursor.execute("""
                SELECT id FROM analytics WHERE post_id = ? AND platform = ?
            """, (post_id, platform))

            existing = cursor.fetchone()

            if existing:
                # Update existing record
                cursor.execute("""
                    UPDATE analytics
                    SET views = ?, likes = ?, comments = ?, shares = ?,
                        engagement_rate = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE post_id = ? AND platform = ?
                """, (views, likes, comments, shares, engagement_rate, post_id, platform))
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO analytics (post_id, platform, views, likes, comments, shares, engagement_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (post_id, platform, views, likes, comments, shares, engagement_rate))

            conn.commit()
            return True

        except Exception as e:
            print(f"[ERROR] Failed to record engagement: {e}")
            return False

    # ========================================================================
    # PERFORMANCE METRICS
    # ========================================================================

    def get_post_performance(self, post_id: int) -> Dict:
        """Get complete performance data for a specific post"""
        post = self.db.get_post(post_id)

        if not post:
            return {"error": "Post not found"}

        # Get analytics data (adapted for flat schema)
        conn = self.db._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT platform, views, likes, comments, shares, engagement_rate, last_updated
            FROM analytics
            WHERE post_id = ?
            ORDER BY last_updated DESC
        """, (post_id,))

        analytics = cursor.fetchall()

        # Organize by platform
        by_platform = {}
        for row in analytics:
            platform = row['platform']
            by_platform[platform] = {
                'views': row['views'],
                'likes': row['likes'],
                'comments': row['comments'],
                'shares': row['shares'],
                'engagement_rate': round(row['engagement_rate'], 2) if row['engagement_rate'] else 0
            }

        return {
            "post_id": post_id,
            "content": post['content'][:100] + "...",
            "voice_type": post['voice_type'],
            "scenario": post['scenario'],
            "published_at": post['published_at'],
            "platforms": by_platform
        }

    def get_overall_performance(self, days: int = 30) -> Dict:
        """Get overall performance metrics for the last N days"""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        conn = self.db._get_connection()
        cursor = conn.cursor()

        # Get all published posts in date range
        cursor.execute("""
            SELECT COUNT(*) as total_posts
            FROM posts
            WHERE status = 'published'
            AND published_at >= ?
        """, (cutoff_date,))

        total_posts = cursor.fetchone()['total_posts']

        # Get aggregated metrics (adapted for flat schema)
        cursor.execute("""
            SELECT
                platform,
                SUM(views) as total_views,
                AVG(views) as avg_views,
                MAX(views) as best_views,
                SUM(likes) as total_likes,
                AVG(likes) as avg_likes,
                MAX(likes) as best_likes,
                SUM(comments) as total_comments,
                AVG(comments) as avg_comments,
                MAX(comments) as best_comments,
                SUM(shares) as total_shares,
                AVG(shares) as avg_shares,
                MAX(shares) as best_shares,
                AVG(engagement_rate) as avg_engagement
            FROM analytics a
            JOIN posts p ON a.post_id = p.id
            WHERE p.published_at >= ?
            GROUP BY platform
        """, (cutoff_date,))

        metrics = defaultdict(lambda: defaultdict(dict))

        for row in cursor.fetchall():
            platform = row['platform']

            # Convert flat schema to metric dict
            metrics[platform]['views'] = {
                'total': row['total_views'] or 0,
                'average': round(row['avg_views'] or 0, 2),
                'best': row['best_views'] or 0
            }
            metrics[platform]['likes'] = {
                'total': row['total_likes'] or 0,
                'average': round(row['avg_likes'] or 0, 2),
                'best': row['best_likes'] or 0
            }
            metrics[platform]['comments'] = {
                'total': row['total_comments'] or 0,
                'average': round(row['avg_comments'] or 0, 2),
                'best': row['best_comments'] or 0
            }
            metrics[platform]['shares'] = {
                'total': row['total_shares'] or 0,
                'average': round(row['avg_shares'] or 0, 2),
                'best': row['best_shares'] or 0
            }
            metrics[platform]['engagement_rate'] = {
                'average': round(row['avg_engagement'] or 0, 2)
            }

        return {
            "period_days": days,
            "total_posts": total_posts,
            "metrics_by_platform": dict(metrics)
        }

    # ========================================================================
    # BEST TIME TO POST
    # ========================================================================

    def analyze_best_times(self, platform: str = "linkedin") -> Dict:
        """
        Analyze posting times to determine optimal posting schedule

        Returns best times by:
        - Day of week
        - Hour of day
        - Day/hour combination
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        # Get all posts with their engagement (adapted for flat schema)
        cursor.execute("""
            SELECT
                p.id,
                p.published_at,
                COALESCE(a.engagement_rate, 0) as avg_engagement
            FROM posts p
            LEFT JOIN analytics a ON p.id = a.post_id AND a.platform = ?
            WHERE p.status = 'published'
            AND p.published_at IS NOT NULL
            AND a.engagement_rate > 0
        """, (platform,))

        posts = cursor.fetchall()

        if not posts:
            return {
                "message": "Not enough data yet",
                "recommendation": "Post consistently for 2-4 weeks to get insights"
            }

        # Analyze by day of week
        by_day = defaultdict(list)
        by_hour = defaultdict(list)
        by_day_hour = defaultdict(list)

        for post in posts:
            try:
                dt = datetime.fromisoformat(post['published_at'].replace('Z', '+00:00'))
                day_name = dt.strftime('%A')
                hour = dt.hour
                engagement = post['avg_engagement']

                by_day[day_name].append(engagement)
                by_hour[hour].append(engagement)
                by_day_hour[(day_name, hour)].append(engagement)

            except Exception as e:
                continue

        # Calculate averages
        day_averages = {
            day: round(statistics.mean(engagements), 2)
            for day, engagements in by_day.items()
        }

        hour_averages = {
            hour: round(statistics.mean(engagements), 2)
            for hour, engagements in by_hour.items()
        }

        # Find best times
        best_day = max(day_averages.items(), key=lambda x: x[1]) if day_averages else None
        best_hour = max(hour_averages.items(), key=lambda x: x[1]) if hour_averages else None

        # Top 3 day/hour combinations
        combo_averages = {
            f"{day} at {hour:02d}:00": round(statistics.mean(engagements), 2)
            for (day, hour), engagements in by_day_hour.items()
        }

        top_combos = sorted(combo_averages.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            "platform": platform,
            "data_points": len(posts),
            "best_day": {
                "day": best_day[0] if best_day else None,
                "avg_engagement": best_day[1] if best_day else 0
            },
            "best_hour": {
                "hour": best_hour[0] if best_hour else None,
                "avg_engagement": best_hour[1] if best_hour else 0
            },
            "top_combinations": [
                {"time": combo[0], "avg_engagement": combo[1]}
                for combo in top_combos
            ],
            "all_days": day_averages,
            "all_hours": {f"{h:02d}:00": v for h, v in hour_averages.items()}
        }

    # ========================================================================
    # CONTENT ANALYSIS
    # ========================================================================

    def analyze_content_performance(self, metric: str = "engagement_rate") -> Dict:
        """
        Analyze which content types perform best

        Compares:
        - Voice types (personal vs coach vs professional)
        - Scenarios (game highlights, recruiting, etc.)
        - Media presence (with graphics vs without)
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        # Performance by voice type (adapted for flat schema)
        cursor.execute("""
            SELECT
                p.voice_type,
                COUNT(DISTINCT p.id) as post_count,
                AVG(a.engagement_rate) as avg_metric
            FROM posts p
            LEFT JOIN analytics a ON p.id = a.post_id
            WHERE p.status = 'published'
            GROUP BY p.voice_type
            HAVING avg_metric IS NOT NULL
        """)

        by_voice = {
            row['voice_type']: {
                'post_count': row['post_count'],
                'avg_performance': round(row['avg_metric'], 2)
            }
            for row in cursor.fetchall()
        }

        # Performance by scenario (adapted for flat schema)
        cursor.execute("""
            SELECT
                p.scenario,
                COUNT(DISTINCT p.id) as post_count,
                AVG(a.engagement_rate) as avg_metric
            FROM posts p
            LEFT JOIN analytics a ON p.id = a.post_id
            WHERE p.status = 'published'
            GROUP BY p.scenario
            HAVING avg_metric IS NOT NULL
            ORDER BY avg_metric DESC
        """)

        by_scenario = [
            {
                'scenario': row['scenario'],
                'post_count': row['post_count'],
                'avg_performance': round(row['avg_metric'], 2)
            }
            for row in cursor.fetchall()
        ]

        # Performance with vs without media (adapted for flat schema)
        cursor.execute("""
            SELECT
                CASE
                    WHEN p.graphic_url IS NOT NULL OR p.video_url IS NOT NULL THEN 'with_media'
                    ELSE 'without_media'
                END as media_status,
                COUNT(DISTINCT p.id) as post_count,
                AVG(a.engagement_rate) as avg_metric
            FROM posts p
            LEFT JOIN analytics a ON p.id = a.post_id
            WHERE p.status = 'published'
            GROUP BY media_status
            HAVING avg_metric IS NOT NULL
        """)

        by_media = {
            row['media_status']: {
                'post_count': row['post_count'],
                'avg_performance': round(row['avg_metric'], 2)
            }
            for row in cursor.fetchall()
        }

        return {
            "metric_analyzed": metric,
            "by_voice_type": by_voice,
            "by_scenario": by_scenario,
            "by_media_presence": by_media
        }

    def get_top_performing_posts(self, limit: int = 10, metric: str = "engagement_rate") -> List[Dict]:
        """Get top performing posts (adapted for flat schema)"""
        conn = self.db._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                p.id,
                p.content,
                p.voice_type,
                p.scenario,
                p.published_at,
                AVG(a.engagement_rate) as performance
            FROM posts p
            JOIN analytics a ON p.id = a.post_id
            WHERE p.status = 'published'
            GROUP BY p.id, p.content, p.voice_type, p.scenario, p.published_at
            HAVING performance IS NOT NULL
            ORDER BY performance DESC
            LIMIT ?
        """, (limit,))

        return [
            {
                'post_id': row['id'],
                'content_preview': row['content'][:100] + "...",
                'voice_type': row['voice_type'],
                'scenario': row['scenario'],
                'published_at': row['published_at'],
                'performance': round(row['performance'], 2)
            }
            for row in cursor.fetchall()
        ]

    # ========================================================================
    # INSIGHTS & RECOMMENDATIONS
    # ========================================================================

    def generate_insights(self) -> Dict:
        """Generate actionable insights from analytics data"""
        insights = []

        # Check posting frequency
        posts_last_7days = len(self.db.get_all_posts(limit=1000))
        if posts_last_7days < 3:
            insights.append({
                "type": "frequency",
                "priority": "high",
                "message": f"Only {posts_last_7days} posts in last 7 days. Aim for 3-5 posts per week for optimal engagement."
            })

        # Best time analysis
        best_times = self.analyze_best_times()
        if best_times.get('best_day'):
            insights.append({
                "type": "timing",
                "priority": "medium",
                "message": f"Your best performing day is {best_times['best_day']['day']}. Schedule more posts on this day."
            })

        # Content performance
        content_analysis = self.analyze_content_performance()
        scenarios = content_analysis.get('by_scenario', [])
        if scenarios:
            best_scenario = scenarios[0]
            insights.append({
                "type": "content",
                "priority": "medium",
                "message": f"'{best_scenario['scenario']}' posts perform best (avg: {best_scenario['avg_performance']}% engagement). Create more of this content."
            })

        # Media impact
        media_analysis = content_analysis.get('by_media_presence', {})
        if 'with_media' in media_analysis and 'without_media' in media_analysis:
            with_media = media_analysis['with_media']['avg_performance']
            without_media = media_analysis['without_media']['avg_performance']

            if with_media > without_media * 1.2:  # 20% better
                insights.append({
                    "type": "media",
                    "priority": "high",
                    "message": f"Posts with media perform {((with_media/without_media - 1) * 100):.0f}% better. Always include graphics or video!"
                })

        return {
            "insights": insights,
            "total_insights": len(insights)
        }

    # ========================================================================
    # DASHBOARD SUMMARY
    # ========================================================================

    def get_dashboard_summary(self) -> Dict:
        """Get complete analytics summary for dashboard"""
        overall = self.get_overall_performance(days=30)
        best_times = self.analyze_best_times()
        content = self.analyze_content_performance()
        top_posts = self.get_top_performing_posts(limit=5)
        insights = self.generate_insights()

        return {
            "summary": overall,
            "best_times": best_times,
            "content_performance": content,
            "top_posts": top_posts,
            "insights": insights,
            "generated_at": datetime.now().isoformat()
        }


def main():
    """Test analytics engine"""
    analytics = AnalyticsEngine()

    print("="*70)
    print("ANALYTICS ENGINE - TEST")
    print("="*70)

    # Test with sample data
    print("\n[1/3] Recording sample engagement...")
    analytics.record_engagement(
        post_id=1,
        platform="linkedin",
        views=150,
        likes=12,
        comments=3,
        shares=2
    )
    print("  Sample engagement recorded")

    print("\n[2/3] Getting overall performance...")
    performance = analytics.get_overall_performance(days=30)
    print(f"  Total posts: {performance['total_posts']}")

    print("\n[3/3] Generating insights...")
    insights = analytics.generate_insights()
    print(f"  Generated {insights['total_insights']} insights")

    for insight in insights['insights']:
        print(f"    - [{insight['priority'].upper()}] {insight['message']}")

    print("\n" + "="*70)


if __name__ == "__main__":
    main()
