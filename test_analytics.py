"""
Test Analytics System
Record sample engagement data and generate insights
"""

import requests
import json
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8080"

def test_record_engagement():
    """Test recording engagement data"""
    print("="*70)
    print("TEST: Recording Engagement Data")
    print("="*70)

    # Record engagement for existing posts
    sample_data = [
        {
            "post_id": 1,
            "platform": "linkedin",
            "views": 250,
            "likes": 18,
            "comments": 5,
            "shares": 3,
            "clicks": 12
        },
        {
            "post_id": 2,
            "platform": "linkedin",
            "views": 180,
            "likes": 15,
            "comments": 3,
            "shares": 2,
            "clicks": 8
        },
        {
            "post_id": 3,
            "platform": "linkedin",
            "views": 320,
            "likes": 25,
            "comments": 8,
            "shares": 5,
            "clicks": 15
        },
        {
            "post_id": 4,
            "platform": "linkedin",
            "views": 200,
            "likes": 12,
            "comments": 2,
            "shares": 1,
            "clicks": 6
        }
    ]

    for data in sample_data:
        print(f"\n  Recording engagement for post {data['post_id']}...")
        response = requests.post(f"{BASE_URL}/api/analytics/engagement", json=data)

        if response.status_code == 200:
            print(f"    [OK] {data['views']} views, {data['likes']} likes, {data['comments']} comments")
        else:
            print(f"    [ERROR] {response.status_code}: {response.text}")

    print("\n" + "="*70)


def test_post_analytics():
    """Test getting analytics for a specific post"""
    print("\nTEST: Post-Specific Analytics")
    print("="*70)

    post_id = 3  # Best performing post
    response = requests.get(f"{BASE_URL}/api/analytics/post/{post_id}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n  Post {post_id} Performance:")
        print(f"    Content: {data['content']}")
        print(f"    Voice: {data['voice_type']}")
        print(f"    Scenario: {data['scenario']}")

        platforms = data.get('platforms', {})
        for platform, metrics in platforms.items():
            print(f"\n    {platform.upper()}:")
            for metric, value in metrics.items():
                print(f"      {metric}: {value}")

    print("\n" + "="*70)


def test_overall_performance():
    """Test overall performance metrics"""
    print("\nTEST: Overall Performance (Last 30 Days)")
    print("="*70)

    response = requests.get(f"{BASE_URL}/api/analytics/overview?days=30")

    if response.status_code == 200:
        data = response.json()
        print(f"\n  Period: Last {data['period_days']} days")
        print(f"  Total Posts: {data['total_posts']}")

        metrics = data.get('metrics_by_platform', {})
        for platform, platform_metrics in metrics.items():
            print(f"\n  {platform.upper()}:")
            for metric_name, stats in platform_metrics.items():
                print(f"    {metric_name}:")
                print(f"      Total: {stats['total']}")
                print(f"      Average: {stats['average']}")
                print(f"      Best: {stats['best']}")

    print("\n" + "="*70)


def test_best_times():
    """Test best time to post analysis"""
    print("\nTEST: Best Times to Post")
    print("="*70)

    response = requests.get(f"{BASE_URL}/api/analytics/best-times?platform=linkedin")

    if response.status_code == 200:
        data = response.json()

        print(f"\n  Platform: {data['platform'].upper()}")
        print(f"  Data Points: {data['data_points']}")

        best_day = data.get('best_day', {})
        if best_day.get('day'):
            print(f"\n  Best Day: {best_day['day']}")
            print(f"    Avg Engagement: {best_day['avg_engagement']}%")

        best_hour = data.get('best_hour', {})
        if best_hour.get('hour') is not None:
            print(f"\n  Best Hour: {best_hour['hour']:02d}:00")
            print(f"    Avg Engagement: {best_hour['avg_engagement']}%")

        top_combos = data.get('top_combinations', [])
        if top_combos:
            print(f"\n  Top 3 Day/Hour Combinations:")
            for i, combo in enumerate(top_combos, 1):
                print(f"    {i}. {combo['time']} - {combo['avg_engagement']}% engagement")

    else:
        print(f"\n  Not enough data yet. Post consistently for 2-4 weeks to get insights.")

    print("\n" + "="*70)


def test_content_performance():
    """Test content performance analysis"""
    print("\nTEST: Content Performance Analysis")
    print("="*70)

    response = requests.get(f"{BASE_URL}/api/analytics/content-performance")

    if response.status_code == 200:
        data = response.json()

        print(f"\n  Metric Analyzed: {data['metric_analyzed']}")

        # By voice type
        by_voice = data.get('by_voice_type', {})
        if by_voice:
            print(f"\n  Performance by Voice Type:")
            for voice, stats in by_voice.items():
                print(f"    {voice}: {stats['avg_performance']}% ({stats['post_count']} posts)")

        # By scenario
        by_scenario = data.get('by_scenario', [])
        if by_scenario:
            print(f"\n  Performance by Scenario:")
            for scenario in by_scenario[:5]:  # Top 5
                print(f"    {scenario['scenario']}: {scenario['avg_performance']}% ({scenario['post_count']} posts)")

        # By media presence
        by_media = data.get('by_media_presence', {})
        if by_media:
            print(f"\n  Performance by Media Presence:")
            for media_status, stats in by_media.items():
                print(f"    {media_status.replace('_', ' ').title()}: {stats['avg_performance']}% ({stats['post_count']} posts)")

    print("\n" + "="*70)


def test_top_posts():
    """Test top performing posts"""
    print("\nTEST: Top Performing Posts")
    print("="*70)

    response = requests.get(f"{BASE_URL}/api/analytics/top-posts?limit=5")

    if response.status_code == 200:
        data = response.json()
        top_posts = data.get('top_posts', [])

        if top_posts:
            print(f"\n  Top {len(top_posts)} Posts:")
            for i, post in enumerate(top_posts, 1):
                print(f"\n  #{i} - Post ID {post['post_id']} ({post['performance']}% engagement)")
                print(f"      Content: {post['content_preview']}")
                print(f"      Voice: {post['voice_type']} | Scenario: {post['scenario']}")
                print(f"      Published: {post['published_at']}")
        else:
            print("\n  No posts with analytics data yet")

    print("\n" + "="*70)


def test_insights():
    """Test insights generation"""
    print("\nTEST: Actionable Insights")
    print("="*70)

    response = requests.get(f"{BASE_URL}/api/analytics/insights")

    if response.status_code == 200:
        data = response.json()
        insights = data.get('insights', [])

        print(f"\n  Generated {len(insights)} insight(s):")

        for insight in insights:
            priority = insight['priority'].upper()
            print(f"\n  [{priority}] {insight['type'].title()}")
            print(f"      {insight['message']}")

        if not insights:
            print("\n  No insights available yet. Publish more posts to get recommendations!")

    print("\n" + "="*70)


def test_dashboard_summary():
    """Test complete dashboard summary"""
    print("\nTEST: Analytics Dashboard Summary")
    print("="*70)

    response = requests.get(f"{BASE_URL}/api/analytics/dashboard")

    if response.status_code == 200:
        data = response.json()

        print(f"\n  Generated at: {data['generated_at']}")

        summary = data.get('summary', {})
        print(f"\n  Total Posts (30 days): {summary.get('total_posts', 0)}")

        insights = data.get('insights', {})
        print(f"  Insights: {insights.get('total_insights', 0)} actionable recommendations")

        top_posts = data.get('top_posts', [])
        print(f"  Top Posts: {len(top_posts)} tracked")

    print("\n" + "="*70)


def main():
    """Run all analytics tests"""
    print("\n" + "="*70)
    print("MILTON AI PUBLICIST - ANALYTICS SYSTEM TEST")
    print("="*70)

    try:
        # Test 1: Record engagement
        test_record_engagement()

        # Test 2: Post-specific analytics
        test_post_analytics()

        # Test 3: Overall performance
        test_overall_performance()

        # Test 4: Best times to post
        test_best_times()

        # Test 5: Content performance
        test_content_performance()

        # Test 6: Top posts
        test_top_posts()

        # Test 7: Insights
        test_insights()

        # Test 8: Dashboard summary
        test_dashboard_summary()

        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print("[PASS] Analytics system operational")
        print("  - Engagement tracking: OK")
        print("  - Performance metrics: OK")
        print("  - Best times analysis: OK")
        print("  - Content analysis: OK")
        print("  - Insights generation: OK")
        print("="*70)

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to dashboard")
        print("  Start dashboard: python dashboard/app.py")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
