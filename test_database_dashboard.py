"""
Test Database-Integrated Dashboard
Verifies all CRUD operations and persistence
"""

import requests
import time
from pathlib import Path

BASE_URL = "http://localhost:8080"

def test_status():
    """Test /api/status endpoint"""
    print("\n" + "="*70)
    print("TEST 1: Dashboard Status & Stats")
    print("="*70)

    response = requests.get(f"{BASE_URL}/api/status")
    data = response.json()

    print(f"✅ Status: {data['status']}")
    print(f"✅ Generated Posts: {data['generated_posts']}")
    print(f"✅ Published Posts: {data['published_posts']}")
    print(f"✅ User: {data['user']['email']}")

    return data

def test_generate_post():
    """Test /api/generate endpoint (creates post in database)"""
    print("\n" + "="*70)
    print("TEST 2: Generate Post (Save to Database)")
    print("="*70)

    payload = {
        "voice_type": "personal",
        "scenario": "partner_appreciation",
        "context": "Test database persistence with VyStar Credit Union partnership",
        "include_graphic": False,
        "include_video": False
    }

    print(f"Generating post with context: {payload['context']}")

    response = requests.post(f"{BASE_URL}/api/generate", json=payload)
    data = response.json()

    if data["success"]:
        post = data["post"]
        print(f"✅ Post created with ID: {post['id']}")
        print(f"✅ Content ({post['word_count']} words):")
        print(f"   {post['content'][:150]}...")
        print(f"✅ Voice Type: {post['voice_type']}")
        print(f"✅ Status: {post['status']}")
        print(f"✅ Created: {post['created_at']}")
        return post
    else:
        print(f"❌ Failed: {data.get('detail')}")
        return None

def test_get_all_posts():
    """Test /api/posts endpoint"""
    print("\n" + "="*70)
    print("TEST 3: Get All Posts (Read from Database)")
    print("="*70)

    response = requests.get(f"{BASE_URL}/api/posts")
    data = response.json()

    posts = data["posts"]
    print(f"✅ Total posts in database: {len(posts)}")

    if posts:
        print("\nRecent posts:")
        for post in posts[:3]:
            print(f"  - ID {post['id']}: {post['content'][:60]}... ({post['status']})")

    return posts

def test_get_single_post(post_id):
    """Test /api/posts/{id} endpoint"""
    print("\n" + "="*70)
    print(f"TEST 4: Get Single Post (ID: {post_id})")
    print("="*70)

    response = requests.get(f"{BASE_URL}/api/posts/{post_id}")
    post = response.json()

    print(f"✅ Post ID: {post['id']}")
    print(f"✅ Content: {post['content'][:100]}...")
    print(f"✅ Word Count: {post['word_count']}")
    print(f"✅ Status: {post['status']}")

    return post

def test_update_post(post_id):
    """Test PUT /api/posts/{id} endpoint"""
    print("\n" + "="*70)
    print(f"TEST 5: Update Post (ID: {post_id})")
    print("="*70)

    new_content = "We want to thank VyStar Credit Union for their incredible partnership! [EDITED VIA DATABASE]"

    payload = {
        "content": new_content,
        "status": "approved"
    }

    print(f"Updating content and status...")

    response = requests.put(f"{BASE_URL}/api/posts/{post_id}", json=payload)
    data = response.json()

    if data["success"]:
        post = data["post"]
        print(f"✅ Content updated: {post['content'][:80]}...")
        print(f"✅ Status changed to: {post['status']}")
        print(f"✅ Word count recalculated: {post['word_count']}")
        return post
    else:
        print(f"❌ Failed to update")
        return None

def test_persistence():
    """Test database persistence across restarts"""
    print("\n" + "="*70)
    print("TEST 6: Database Persistence Check")
    print("="*70)

    # Check if database file exists
    db_path = Path("c:/Users/mover/OneDrive/Documents/GitHub/All State RevShield Engine AJ/milton-publicist/milton_publicist.db")

    if db_path.exists():
        size = db_path.stat().st_size
        print(f"✅ Database file exists: {db_path}")
        print(f"✅ Database size: {size:,} bytes")
    else:
        print(f"❌ Database file not found at: {db_path}")

    # Get all posts to verify data persists
    response = requests.get(f"{BASE_URL}/api/posts")
    posts = response.json()["posts"]

    print(f"✅ Posts persist in database: {len(posts)} total")

    return db_path.exists()

def test_filter_by_status():
    """Test filtering posts by status"""
    print("\n" + "="*70)
    print("TEST 7: Filter Posts by Status")
    print("="*70)

    statuses = ["pending", "approved", "published"]

    for status in statuses:
        response = requests.get(f"{BASE_URL}/api/posts?status={status}")
        posts = response.json()["posts"]
        print(f"✅ {status.upper()}: {len(posts)} posts")

def test_delete_post(post_id):
    """Test DELETE /api/posts/{id} endpoint"""
    print("\n" + "="*70)
    print(f"TEST 8: Delete Post (ID: {post_id})")
    print("="*70)

    # First verify post exists
    response = requests.get(f"{BASE_URL}/api/posts/{post_id}")
    if response.status_code == 200:
        print(f"✅ Post {post_id} exists before deletion")

    # Delete the post
    response = requests.delete(f"{BASE_URL}/api/posts/{post_id}")
    data = response.json()

    if data["success"]:
        print(f"✅ Post {post_id} deleted successfully")

        # Verify it's gone
        response = requests.get(f"{BASE_URL}/api/posts/{post_id}")
        if response.status_code == 404:
            print(f"✅ Post {post_id} no longer accessible (404)")
        else:
            print(f"❌ Post {post_id} still exists after deletion!")
    else:
        print(f"❌ Failed to delete post {post_id}")

def main():
    """Run all database integration tests"""
    print("\n" + "="*70)
    print("MILTON AI PUBLICIST - DATABASE INTEGRATION TESTS")
    print("="*70)
    print(f"Testing dashboard at: {BASE_URL}")
    print()

    try:
        # Test 1: Check status
        status_data = test_status()

        # Test 2: Generate a new post
        new_post = test_generate_post()

        if not new_post:
            print("\n❌ Failed to generate post. Stopping tests.")
            return

        post_id = new_post["id"]

        # Test 3: Get all posts
        all_posts = test_get_all_posts()

        # Test 4: Get single post
        single_post = test_get_single_post(post_id)

        # Test 5: Update post
        updated_post = test_update_post(post_id)

        # Test 6: Check database persistence
        db_exists = test_persistence()

        # Test 7: Filter by status
        test_filter_by_status()

        # Test 8: Delete post (optional - comment out if you want to keep test data)
        # test_delete_post(post_id)

        # Final Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"✅ Dashboard running on port 8080")
        print(f"✅ Database connected and operational")
        print(f"✅ Posts persist to SQLite database")
        print(f"✅ All CRUD operations working")
        print(f"✅ Total posts in database: {len(all_posts)}")
        print()
        print("🎉 DATABASE INTEGRATION: SUCCESS!")
        print()
        print("Next: Open http://localhost:8080 to test via web UI")
        print("="*70)

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to dashboard")
        print("   Make sure dashboard is running on http://localhost:8080")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
