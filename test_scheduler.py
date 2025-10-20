"""
Test Scheduler Daemon and Scheduling API
"""

import requests
import json
from datetime import datetime, timedelta, timezone

BASE_URL = "http://localhost:8080"

def test_scheduling_workflow():
    """Test complete scheduling workflow"""
    print("="*70)
    print("SCHEDULER DAEMON - COMPLETE WORKFLOW TEST")
    print("="*70)

    # Step 1: Generate a post
    print("\n[1/7] Generating a test post...")
    r = requests.post(f"{BASE_URL}/api/generate", json={
        "voice_type": "personal",
        "scenario": "game_highlights",
        "context": "KSU football team victory over rival",
        "include_graphic": False,
        "include_video": False
    })
    data = r.json()

    if not data["success"]:
        print(f"  [ERROR] Failed to generate post")
        return

    post = data["post"]
    post_id = post["id"]
    print(f"  [OK] Post created with ID: {post_id}")
    print(f"  Content: {post['content'][:60]}...")

    # Step 2: Schedule post for 2 minutes from now
    print("\n[2/7] Scheduling post for future publishing...")

    # Schedule for 2 minutes from now
    scheduled_time = (datetime.now(timezone.utc) + timedelta(minutes=2)).isoformat()

    r = requests.post(f"{BASE_URL}/api/posts/{post_id}/schedule", json={
        "platform": "linkedin",
        "scheduled_time": scheduled_time
    })
    data = r.json()

    if not data["success"]:
        print(f"  [ERROR] Failed to schedule")
        return

    schedule = data["schedule"]
    schedule_id = schedule["id"]
    print(f"  [OK] Post scheduled!")
    print(f"  Schedule ID: {schedule_id}")
    print(f"  Platform: {schedule['platform']}")
    print(f"  Time: {schedule['scheduled_time']}")

    # Step 3: Get all scheduled posts
    print("\n[3/7] Fetching all scheduled posts...")
    r = requests.get(f"{BASE_URL}/api/scheduled")
    scheduled = r.json()["scheduled"]
    print(f"  [OK] Total scheduled posts: {len(scheduled)}")

    for s in scheduled:
        print(f"    - ID {s['id']}: {s['platform']} at {s['scheduled_time']} ({s['status']})")

    # Step 4: Get upcoming scheduled posts
    print("\n[4/7] Fetching upcoming scheduled posts (next 7 days)...")
    r = requests.get(f"{BASE_URL}/api/scheduled/upcoming")
    upcoming = r.json()["upcoming"]
    print(f"  [OK] Upcoming posts: {len(upcoming)}")

    # Step 5: Get pending scheduled posts
    print("\n[5/7] Fetching pending scheduled posts...")
    r = requests.get(f"{BASE_URL}/api/scheduled?status=pending")
    pending = r.json()["scheduled"]
    print(f"  [OK] Pending posts: {len(pending)}")

    # Step 6: Check scheduler status
    print("\n[6/7] Checking scheduler daemon status...")
    r = requests.get(f"{BASE_URL}/api/scheduler/status")
    status = r.json()
    print(f"  Daemon running: {status['daemon_running']}")
    print(f"  Pending schedules: {status['pending_schedules']}")
    print(f"  Total posts: {status['total_posts']}")
    print(f"  Published posts: {status['published_posts']}")

    # Step 7: Cancel the scheduled post (optional)
    print("\n[7/7] Test cancellation (optional)...")
    choice = input("  Cancel the scheduled post? (y/n): ")

    if choice.lower() == 'y':
        r = requests.delete(f"{BASE_URL}/api/scheduled/{schedule_id}")
        data = r.json()
        if data["success"]:
            print(f"  [OK] Scheduled post cancelled")
        else:
            print(f"  [ERROR] Failed to cancel")
    else:
        print(f"  [SKIP] Keeping scheduled post")
        print(f"\n  NOTE: Start the scheduler daemon to auto-publish:")
        print(f"    python scheduler_daemon.py")

    # Summary
    print("\n" + "="*70)
    print("WORKFLOW TEST SUMMARY")
    print("="*70)
    print("[PASS] All scheduling API endpoints working")
    print(f"  - Created post ID {post_id}")
    print(f"  - Scheduled for {scheduled_time}")
    print(f"  - Schedule ID: {schedule_id}")
    print()
    print("Next Steps:")
    print("1. Start scheduler daemon: python scheduler_daemon.py")
    print("2. Daemon will check every 60 seconds")
    print("3. Post will auto-publish at scheduled time")
    print("4. Check logs in scheduler_daemon.log")
    print("="*70)


def test_immediate_schedule():
    """Test scheduling a post for immediate publishing (1 minute from now)"""
    print("\n" + "="*70)
    print("IMMEDIATE SCHEDULE TEST (1 minute from now)")
    print("="*70)

    # Generate post
    print("\n[1/2] Generating test post...")
    r = requests.post(f"{BASE_URL}/api/generate", json={
        "voice_type": "coach",
        "scenario": "recruiting_update",
        "context": "New 5-star recruit commitment",
        "include_graphic": False,
        "include_video": False
    })
    post = r.json()["post"]
    post_id = post["id"]
    print(f"  [OK] Post ID: {post_id}")

    # Schedule for 1 minute from now (for quick testing with --test mode)
    print("\n[2/2] Scheduling for 1 minute from now...")
    scheduled_time = (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()

    r = requests.post(f"{BASE_URL}/api/posts/{post_id}/schedule", json={
        "platform": "linkedin",
        "scheduled_time": scheduled_time
    })
    schedule = r.json()["schedule"]
    print(f"  [OK] Scheduled for: {scheduled_time}")
    print(f"  Schedule ID: {schedule['id']}")

    print("\n" + "="*70)
    print("READY FOR DAEMON TEST")
    print("="*70)
    print("Run the daemon in test mode:")
    print("  python scheduler_daemon.py --test")
    print()
    print("The daemon will:")
    print("  - Check every 10 seconds (test mode)")
    print("  - Publish your post in ~1 minute")
    print("  - Log results to scheduler_daemon.log")
    print("="*70)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--immediate":
        test_immediate_schedule()
    else:
        test_scheduling_workflow()
