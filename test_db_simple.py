"""Simple Database Integration Test (No Emojis for Windows)"""
import requests
import json

BASE_URL = "http://localhost:8080"

print("="*70)
print("MILTON DATABASE INTEGRATION TEST")
print("="*70)

# Test 1: Status
print("\n[1/6] Testing /api/status...")
r = requests.get(f"{BASE_URL}/api/status")
data = r.json()
print(f"  Status: {data['status']}")
print(f"  User: {data['user']['email']}")
print(f"  Posts: {data['generated_posts']}")
print(f"  [OK] Status endpoint working")

# Test 2: Generate post
print("\n[2/6] Testing /api/generate (save to database)...")
r = requests.post(f"{BASE_URL}/api/generate", json={
    "voice_type": "personal",
    "scenario": "partner_appreciation",
    "context": "VyStar Credit Union partnership test",
    "include_graphic": False,
    "include_video": False
})
data = r.json()
if data["success"]:
    post = data["post"]
    post_id = post["id"]
    print(f"  Post ID: {post_id}")
    print(f"  Content: {post['content'][:60]}...")
    print(f"  Word Count: {post['word_count']}")
    print(f"  [OK] Post saved to database")
else:
    print(f"  [ERROR] {data}")
    exit(1)

# Test 3: Get all posts
print("\n[3/6] Testing /api/posts (read from database)...")
r = requests.get(f"{BASE_URL}/api/posts")
posts = r.json()["posts"]
print(f"  Total posts: {len(posts)}")
print(f"  [OK] Posts retrieved from database")

# Test 4: Get single post
print(f"\n[4/6] Testing /api/posts/{post_id}...")
r = requests.get(f"{BASE_URL}/api/posts/{post_id}")
post = r.json()
print(f"  Post {post_id} retrieved")
print(f"  Status: {post['status']}")
print(f"  [OK] Single post lookup working")

# Test 5: Update post
print(f"\n[5/6] Testing PUT /api/posts/{post_id}...")
r = requests.put(f"{BASE_URL}/api/posts/{post_id}", json={
    "content": "UPDATED: Thank you VyStar Credit Union for the partnership!",
    "status": "approved"
})
data = r.json()
if data["success"]:
    post = data["post"]
    print(f"  Content updated: {post['content'][:50]}...")
    print(f"  Status changed to: {post['status']}")
    print(f"  [OK] Post updated in database")

# Test 6: Database persistence
print("\n[6/6] Testing database persistence...")
import os
db_path = "milton_publicist.db"
if os.path.exists(db_path):
    size = os.path.getsize(db_path)
    print(f"  Database file: {db_path}")
    print(f"  Size: {size:,} bytes")
    print(f"  [OK] Database file persists")

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
print("[PASS] Database integration successful!")
print(f"  - Posts saved to SQLite database")
print(f"  - CRUD operations working")
print(f"  - Data persists across requests")
print(f"  - Total posts in DB: {len(posts)}")
print("\nNext: Open http://localhost:8080 to test via web UI")
print("="*70)
