"""
Analytics Tracker - Track post performance and engagement metrics
Provides insights and recommendations for content optimization
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from collections import defaultdict

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class AnalyticsTracker:
    """
    Tracks and analyzes post performance across platforms
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize analytics tracker

        Args:
            storage_path: Path to store analytics data (JSON file)
        """
        if storage_path is None:
            storage_path = Path(__file__).parent.parent / "data" / "analytics.json"

        self.storage_path = Path(storage_path)
        self.analytics_data: Dict = {
            "posts": [],
            "summary": {}
        }

        # Load existing data if available
        self._load_data()

    def _load_data(self):
        """Load analytics data from file"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self.analytics_data = json.load(f)
            except Exception as e:
                print(f"[WARN] Could not load analytics data: {e}")

    def _save_data(self):
        """Save analytics data to file"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.analytics_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Could not save analytics data: {e}")

    def track_post(
        self,
        post_id: str,
        platform: str,
        content: str,
        published_at: datetime,
        metrics: Optional[Dict] = None
    ):
        """
        Track a published post

        Args:
            post_id: Unique post identifier
            platform: Platform name (linkedin, twitter, instagram)
            content: Post content
            published_at: Publication datetime
            metrics: Initial metrics (views, likes, etc.)
        """
        post_data = {
            "id": post_id,
            "platform": platform.lower(),
            "content": content,
            "published_at": published_at.isoformat(),
            "metrics": metrics or {},
            "tracked_at": datetime.now().isoformat()
        }

        self.analytics_data["posts"].append(post_data)
        self._save_data()

    def update_post_metrics(
        self,
        post_id: str,
        metrics: Dict
    ):
        """
        Update metrics for a tracked post

        Args:
            post_id: Post identifier
            metrics: Updated metrics dict
        """
        for post in self.analytics_data["posts"]:
            if post["id"] == post_id:
                post["metrics"].update(metrics)
                post["last_updated"] = datetime.now().isoformat()
                self._save_data()
                return

        print(f"[WARN] Post {post_id} not found in analytics data")

    def get_post_metrics(self, post_id: str) -> Optional[Dict]:
        """
        Get metrics for a specific post

        Args:
            post_id: Post identifier

        Returns:
            Metrics dict or None if not found
        """
        for post in self.analytics_data["posts"]:
            if post["id"] == post_id:
                return post.get("metrics", {})

        return None

    def get_platform_performance(
        self,
        platform: str,
        days: int = 30
    ) -> Dict:
        """
        Get performance summary for a platform

        Args:
            platform: Platform name
            days: Number of days to analyze

        Returns:
            Performance summary dict
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        platform_posts = [
            p for p in self.analytics_data["posts"]
            if p["platform"] == platform.lower()
            and datetime.fromisoformat(p["published_at"]) >= cutoff_date
        ]

        if not platform_posts:
            return {
                "platform": platform,
                "period_days": days,
                "total_posts": 0,
                "metrics": {}
            }

        # Aggregate metrics
        total_metrics = defaultdict(int)
        for post in platform_posts:
            for metric, value in post.get("metrics", {}).items():
                if isinstance(value, (int, float)):
                    total_metrics[metric] += value

        avg_metrics = {
            f"avg_{k}": v / len(platform_posts)
            for k, v in total_metrics.items()
        }

        return {
            "platform": platform,
            "period_days": days,
            "total_posts": len(platform_posts),
            "total_metrics": dict(total_metrics),
            "average_metrics": avg_metrics
        }

    def get_best_performing_posts(
        self,
        platform: Optional[str] = None,
        metric: str = "engagement",
        limit: int = 10
    ) -> List[Dict]:
        """
        Get best performing posts

        Args:
            platform: Filter by platform (None = all)
            metric: Metric to sort by
            limit: Number of posts to return

        Returns:
            List of top posts
        """
        posts = self.analytics_data["posts"]

        if platform:
            posts = [p for p in posts if p["platform"] == platform.lower()]

        # Sort by metric
        sorted_posts = sorted(
            posts,
            key=lambda p: p.get("metrics", {}).get(metric, 0),
            reverse=True
        )

        return sorted_posts[:limit]

    def get_posting_time_analysis(
        self,
        platform: str,
        days: int = 30
    ) -> Dict:
        """
        Analyze best posting times based on historical performance

        Args:
            platform: Platform name
            days: Number of days to analyze

        Returns:
            Posting time analysis
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        platform_posts = [
            p for p in self.analytics_data["posts"]
            if p["platform"] == platform.lower()
            and datetime.fromisoformat(p["published_at"]) >= cutoff_date
        ]

        if not platform_posts:
            return {
                "platform": platform,
                "analysis": "Not enough data"
            }

        # Group by hour
        hourly_performance = defaultdict(list)

        for post in platform_posts:
            published_at = datetime.fromisoformat(post["published_at"])
            hour = published_at.hour

            engagement = post.get("metrics", {}).get("engagement", 0)
            hourly_performance[hour].append(engagement)

        # Calculate average engagement per hour
        avg_by_hour = {
            hour: sum(engagements) / len(engagements)
            for hour, engagements in hourly_performance.items()
        }

        # Find top 3 hours
        top_hours = sorted(
            avg_by_hour.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        return {
            "platform": platform,
            "period_days": days,
            "best_hours": [
                {
                    "hour": hour,
                    "time": f"{hour}:00",
                    "avg_engagement": engagement
                }
                for hour, engagement in top_hours
            ],
            "hourly_performance": avg_by_hour
        }

    def get_content_insights(
        self,
        platform: Optional[str] = None,
        days: int = 30
    ) -> Dict:
        """
        Get insights about content performance

        Args:
            platform: Filter by platform (None = all)
            days: Number of days to analyze

        Returns:
            Content insights dict
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        posts = [
            p for p in self.analytics_data["posts"]
            if datetime.fromisoformat(p["published_at"]) >= cutoff_date
        ]

        if platform:
            posts = [p for p in posts if p["platform"] == platform.lower()]

        if not posts:
            return {"error": "Not enough data"}

        # Analyze content length vs engagement
        length_engagement = []
        for post in posts:
            content_length = len(post.get("content", "").split())
            engagement = post.get("metrics", {}).get("engagement", 0)
            length_engagement.append((content_length, engagement))

        # Calculate average engagement by length category
        short_posts = [e for l, e in length_engagement if l < 50]
        medium_posts = [e for l, e in length_engagement if 50 <= l < 200]
        long_posts = [e for l, e in length_engagement if l >= 200]

        insights = {
            "period_days": days,
            "total_posts_analyzed": len(posts)
        }

        if platform:
            insights["platform"] = platform

        if short_posts:
            insights["short_posts_avg_engagement"] = sum(short_posts) / len(short_posts)

        if medium_posts:
            insights["medium_posts_avg_engagement"] = sum(medium_posts) / len(medium_posts)

        if long_posts:
            insights["long_posts_avg_engagement"] = sum(long_posts) / len(long_posts)

        # Identify signature phrases in top posts
        top_posts = self.get_best_performing_posts(platform, limit=10)
        signature_phrases = []

        for post in top_posts:
            content = post.get("content", "")
            if "Let's Go Owls!" in content:
                signature_phrases.append("Let's Go Owls!")
            if "I am so proud" in content:
                signature_phrases.append("I am so proud")
            if "We want to thank" in content:
                signature_phrases.append("We want to thank")

        if signature_phrases:
            insights["top_signature_phrases"] = list(set(signature_phrases))

        return insights

    def generate_weekly_report(self) -> Dict:
        """
        Generate a weekly performance report

        Returns:
            Weekly report dict
        """
        report = {
            "report_date": datetime.now().isoformat(),
            "period": "Last 7 days",
            "platforms": {}
        }

        for platform in ["linkedin", "twitter", "instagram"]:
            performance = self.get_platform_performance(platform, days=7)
            report["platforms"][platform] = performance

        return report

    def get_growth_metrics(self, days: int = 30) -> Dict:
        """
        Calculate growth metrics over time

        Args:
            days: Number of days to analyze

        Returns:
            Growth metrics dict
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        recent_posts = [
            p for p in self.analytics_data["posts"]
            if datetime.fromisoformat(p["published_at"]) >= cutoff_date
        ]

        if len(recent_posts) < 2:
            return {"error": "Not enough data"}

        # Split into first half and second half
        midpoint = len(recent_posts) // 2
        first_half = recent_posts[:midpoint]
        second_half = recent_posts[midpoint:]

        def avg_engagement(posts):
            total = sum(p.get("metrics", {}).get("engagement", 0) for p in posts)
            return total / len(posts) if posts else 0

        first_avg = avg_engagement(first_half)
        second_avg = avg_engagement(second_half)

        growth_rate = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0

        return {
            "period_days": days,
            "first_half_avg_engagement": first_avg,
            "second_half_avg_engagement": second_avg,
            "growth_rate_percent": growth_rate,
            "trend": "Growing" if growth_rate > 0 else "Declining" if growth_rate < 0 else "Stable"
        }


# Example usage
def main():
    """Example usage of AnalyticsTracker"""
    print("="*70)
    print("ANALYTICS TRACKER - DEMO")
    print("="*70)
    print()

    tracker = AnalyticsTracker()

    # Example 1: Track a post
    print("[INFO] Tracking sample posts...")

    tracker.track_post(
        post_id="post_001",
        platform="linkedin",
        content="Excited to share our new AI innovation! Let's Go Owls!",
        published_at=datetime.now() - timedelta(days=5),
        metrics={"views": 1250, "likes": 87, "comments": 12, "shares": 8, "engagement": 107}
    )

    tracker.track_post(
        post_id="post_002",
        platform="linkedin",
        content="Great meeting with partners today. We want to thank everyone! Let's Go Owls!",
        published_at=datetime.now() - timedelta(days=3),
        metrics={"views": 980, "likes": 65, "comments": 8, "shares": 5, "engagement": 78}
    )

    print("       2 posts tracked")
    print()

    # Example 2: Get platform performance
    print("[INFO] LinkedIn performance (last 30 days):")
    performance = tracker.get_platform_performance("linkedin", days=30)
    print(f"       Total posts: {performance['total_posts']}")
    print(f"       Average metrics: {performance.get('average_metrics', {})}")
    print()

    # Example 3: Get best performing posts
    print("[INFO] Best performing posts:")
    top_posts = tracker.get_best_performing_posts(platform="linkedin", limit=5)
    for i, post in enumerate(top_posts, 1):
        engagement = post.get("metrics", {}).get("engagement", 0)
        print(f"       {i}. Post {post['id']}: {engagement} engagement")
    print()

    # Example 4: Get content insights
    print("[INFO] Content insights:")
    insights = tracker.get_content_insights(platform="linkedin", days=30)
    print(f"       Posts analyzed: {insights.get('total_posts_analyzed', 0)}")
    if "top_signature_phrases" in insights:
        print(f"       Top phrases: {', '.join(insights['top_signature_phrases'])}")
    print()

    print("="*70)
    print("Analytics data saved to:", tracker.storage_path)
    print("="*70)

if __name__ == "__main__":
    main()
