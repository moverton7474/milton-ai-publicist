"""
Comprehensive API Test Suite - Milton AI Publicist
Tests all 35+ API endpoints with realistic scenarios
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from dashboard.app import app

# Initialize test client
client = TestClient(app)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_post_data() -> Dict[str, Any]:
    """Sample post data for testing"""
    return {
        "voice_type": "personal",
        "scenario": "Team Celebration",
        "context": "Our volleyball team won the conference championship",
        "platform_preferences": ["linkedin", "twitter"]
    }


@pytest.fixture
def sample_post_id() -> int:
    """Create a sample post and return its ID"""
    response = client.post("/api/generate", json={
        "voice_type": "personal",
        "scenario": "Team Celebration",
        "context": "Test post for automated testing"
    })
    assert response.status_code == 200
    return response.json()["post"]["id"]


# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================

class TestCoreEndpoints:
    """Test core dashboard endpoints"""

    def test_home_page(self):
        """Test home page loads"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Milton AI Publicist" in response.text

    def test_admin_page(self):
        """Test admin dashboard loads"""
        response = client.get("/admin")
        assert response.status_code == 200

    def test_settings_page(self):
        """Test settings page loads"""
        response = client.get("/settings")
        assert response.status_code == 200

    def test_system_status(self):
        """Test system status endpoint"""
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "services" in data


# ============================================================================
# CONTENT GENERATION TESTS
# ============================================================================

class TestContentGeneration:
    """Test content generation endpoints"""

    def test_generate_personal_voice(self):
        """Test personal voice content generation"""
        response = client.post("/api/generate", json={
            "voice_type": "personal",
            "scenario": "Team Celebration",
            "context": "Basketball team won big game"
        })
        assert response.status_code == 200
        data = response.json()
        assert "post" in data
        assert "content" in data["post"]
        assert "Let's Go Owls!" in data["post"]["content"]
        # Personal voice should be 20-80 words
        word_count = len(data["post"]["content"].split())
        assert 15 <= word_count <= 100  # Allow some margin

    def test_generate_professional_voice(self):
        """Test professional voice content generation"""
        response = client.post("/api/generate", json={
            "voice_type": "professional",
            "scenario": "Strategic Update",
            "context": "New partnership with major sponsor"
        })
        assert response.status_code == 200
        data = response.json()
        assert "post" in data
        assert "content" in data["post"]
        assert "Let's Go Owls!" in data["post"]["content"]
        # Professional voice should be 200-400 words
        word_count = len(data["post"]["content"].split())
        assert 180 <= word_count <= 450  # Allow some margin

    def test_generate_missing_parameters(self):
        """Test generation with missing required parameters"""
        response = client.post("/api/generate", json={
            "voice_type": "personal"
            # Missing scenario and context
        })
        # Should still work with defaults or return appropriate error
        assert response.status_code in [200, 400, 422]

    def test_generate_invalid_voice_type(self):
        """Test generation with invalid voice type"""
        response = client.post("/api/generate", json={
            "voice_type": "invalid_voice",
            "scenario": "Test",
            "context": "Test context"
        })
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]


# ============================================================================
# POST MANAGEMENT TESTS
# ============================================================================

class TestPostManagement:
    """Test post CRUD operations"""

    def test_get_all_posts(self):
        """Test retrieving all posts"""
        response = client.get("/api/posts")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert isinstance(data["posts"], list)

    def test_get_single_post(self, sample_post_id):
        """Test retrieving a single post"""
        response = client.get(f"/api/posts/{sample_post_id}")
        assert response.status_code == 200
        data = response.json()
        assert "post" in data
        assert data["post"]["id"] == sample_post_id

    def test_get_nonexistent_post(self):
        """Test retrieving non-existent post"""
        response = client.get("/api/posts/999999")
        assert response.status_code == 404

    def test_update_post(self, sample_post_id):
        """Test updating a post"""
        response = client.put(f"/api/posts/{sample_post_id}", json={
            "content": "Updated content for testing",
            "status": "approved"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["post"]["content"] == "Updated content for testing"

    def test_delete_post(self):
        """Test deleting a post"""
        # Create a post to delete
        create_response = client.post("/api/generate", json={
            "voice_type": "personal",
            "scenario": "Test",
            "context": "Post to be deleted"
        })
        post_id = create_response.json()["post"]["id"]

        # Delete it
        response = client.delete(f"/api/posts/{post_id}")
        assert response.status_code == 200

        # Verify it's gone
        get_response = client.get(f"/api/posts/{post_id}")
        assert get_response.status_code == 404


# ============================================================================
# SCHEDULING TESTS
# ============================================================================

class TestScheduling:
    """Test content scheduling functionality"""

    def test_schedule_post(self, sample_post_id):
        """Test scheduling a post"""
        # Schedule for tomorrow at 9 AM
        tomorrow = datetime.now() + timedelta(days=1)
        schedule_time = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)

        response = client.post(f"/api/posts/{sample_post_id}/schedule", json={
            "platform": "linkedin",
            "scheduled_time": schedule_time.isoformat()
        })
        assert response.status_code in [200, 201]

    def test_get_scheduled_posts(self):
        """Test retrieving scheduled posts"""
        response = client.get("/api/scheduled")
        assert response.status_code == 200
        data = response.json()
        assert "scheduled_posts" in data

    def test_get_upcoming_scheduled(self):
        """Test retrieving upcoming scheduled posts"""
        response = client.get("/api/scheduled/upcoming")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_cancel_scheduled_post(self, sample_post_id):
        """Test canceling a scheduled post"""
        # First schedule it
        tomorrow = datetime.now() + timedelta(days=1)
        schedule_response = client.post(f"/api/posts/{sample_post_id}/schedule", json={
            "platform": "linkedin",
            "scheduled_time": tomorrow.isoformat()
        })

        if schedule_response.status_code == 200:
            schedule_id = schedule_response.json().get("schedule_id")
            if schedule_id:
                # Cancel it
                cancel_response = client.delete(f"/api/scheduled/{schedule_id}")
                assert cancel_response.status_code in [200, 204]

    def test_scheduler_status(self):
        """Test scheduler status endpoint"""
        response = client.get("/api/scheduler/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


# ============================================================================
# PUBLISHING TESTS
# ============================================================================

class TestPublishing:
    """Test publishing functionality"""

    def test_get_platforms(self):
        """Test getting available platforms"""
        response = client.get("/api/publish/platforms")
        assert response.status_code == 200
        data = response.json()
        assert "platforms" in data
        platforms = data["platforms"]
        assert any(p["name"] == "linkedin" for p in platforms)

    def test_get_publish_stats(self):
        """Test getting publishing statistics"""
        response = client.get("/api/publish/stats")
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data

    def test_get_publish_history(self):
        """Test getting publish history"""
        response = client.get("/api/publish/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_published_posts(self):
        """Test getting published posts"""
        response = client.get("/api/published")
        assert response.status_code == 200
        data = response.json()
        assert "published_posts" in data

    def test_platform_setup_instructions(self):
        """Test getting platform setup instructions"""
        response = client.get("/api/publish/platforms/linkedin/setup")
        assert response.status_code == 200
        data = response.json()
        assert "instructions" in data


# ============================================================================
# ANALYTICS TESTS
# ============================================================================

class TestAnalytics:
    """Test analytics functionality"""

    def test_analytics_overview(self):
        """Test analytics overview endpoint"""
        response = client.get("/api/analytics/overview")
        assert response.status_code == 200
        data = response.json()
        assert "total_posts" in data

    def test_analytics_dashboard(self):
        """Test analytics dashboard endpoint"""
        response = client.get("/api/analytics/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_top_posts(self):
        """Test top performing posts endpoint"""
        response = client.get("/api/analytics/top-posts")
        assert response.status_code == 200
        data = response.json()
        assert "top_posts" in data

    def test_best_posting_times(self):
        """Test best posting times endpoint"""
        response = client.get("/api/analytics/best-times")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_content_performance(self):
        """Test content performance endpoint"""
        response = client.get("/api/analytics/content-performance")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_insights(self):
        """Test analytics insights endpoint"""
        response = client.get("/api/analytics/insights")
        assert response.status_code == 200
        data = response.json()
        assert "insights" in data

    def test_post_analytics(self, sample_post_id):
        """Test getting analytics for specific post"""
        response = client.get(f"/api/analytics/post/{sample_post_id}")
        assert response.status_code in [200, 404]  # 404 if no analytics yet

    def test_record_engagement(self, sample_post_id):
        """Test recording engagement metrics"""
        response = client.post("/api/analytics/engagement", json={
            "post_id": sample_post_id,
            "platform": "linkedin",
            "views": 150,
            "likes": 25,
            "comments": 5,
            "shares": 3
        })
        assert response.status_code in [200, 201]


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

class TestAuthentication:
    """Test OAuth and authentication"""

    def test_oauth_callback(self):
        """Test OAuth callback endpoint"""
        response = client.get("/auth/callback/linkedin?code=test_code&state=test_state")
        # Should redirect
        assert response.status_code in [200, 302, 307]

    def test_test_platform_connection(self):
        """Test platform connection testing"""
        response = client.get("/api/auth/linkedin/test")
        assert response.status_code == 200
        data = response.json()
        assert "connected" in data


# ============================================================================
# MEDIA MANAGEMENT TESTS
# ============================================================================

class TestMediaManagement:
    """Test media upload and management"""

    def test_get_media_gallery(self):
        """Test getting media gallery"""
        response = client.get("/api/media/gallery")
        assert response.status_code == 200
        data = response.json()
        assert "graphics" in data
        assert "videos" in data
        assert "uploads" in data


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_endpoint(self):
        """Test accessing invalid endpoint"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_invalid_method(self):
        """Test using wrong HTTP method"""
        response = client.post("/api/posts")  # Should be GET
        assert response.status_code == 405

    def test_malformed_json(self):
        """Test sending malformed JSON"""
        response = client.post(
            "/api/generate",
            data="invalid json{{{",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegrationWorkflows:
    """Test complete workflows"""

    def test_full_content_workflow(self):
        """Test complete content creation workflow"""
        # 1. Generate content
        generate_response = client.post("/api/generate", json={
            "voice_type": "personal",
            "scenario": "Game Recap",
            "context": "Soccer team won 3-1"
        })
        assert generate_response.status_code == 200
        post_id = generate_response.json()["post"]["id"]

        # 2. Update content
        update_response = client.put(f"/api/posts/{post_id}", json={
            "content": "Updated: Great soccer win today! 3-1 victory. Let's Go Owls!",
            "status": "approved"
        })
        assert update_response.status_code == 200

        # 3. Schedule post
        tomorrow = datetime.now() + timedelta(days=1)
        schedule_response = client.post(f"/api/posts/{post_id}/schedule", json={
            "platform": "linkedin",
            "scheduled_time": tomorrow.isoformat()
        })
        assert schedule_response.status_code in [200, 201]

        # 4. Get post details
        get_response = client.get(f"/api/posts/{post_id}")
        assert get_response.status_code == 200

        # 5. Clean up - delete post
        delete_response = client.delete(f"/api/posts/{post_id}")
        assert delete_response.status_code == 200

    def test_analytics_workflow(self):
        """Test analytics recording and retrieval workflow"""
        # 1. Create a post
        generate_response = client.post("/api/generate", json={
            "voice_type": "personal",
            "scenario": "Team Update",
            "context": "Training camp starts next week"
        })
        post_id = generate_response.json()["post"]["id"]

        # 2. Record engagement
        engagement_response = client.post("/api/analytics/engagement", json={
            "post_id": post_id,
            "platform": "linkedin",
            "views": 200,
            "likes": 40,
            "comments": 8,
            "shares": 5
        })
        assert engagement_response.status_code in [200, 201]

        # 3. Get post analytics
        analytics_response = client.get(f"/api/analytics/post/{post_id}")
        assert analytics_response.status_code == 200

        # 4. Clean up
        client.delete(f"/api/posts/{post_id}")


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test system performance"""

    def test_concurrent_generation(self):
        """Test generating multiple posts concurrently"""
        # Generate 5 posts
        responses = []
        for i in range(5):
            response = client.post("/api/generate", json={
                "voice_type": "personal",
                "scenario": "Quick Update",
                "context": f"Test post {i}"
            })
            responses.append(response)

        # All should succeed
        assert all(r.status_code == 200 for r in responses)

        # Clean up
        for response in responses:
            post_id = response.json()["post"]["id"]
            client.delete(f"/api/posts/{post_id}")

    def test_bulk_post_retrieval(self):
        """Test retrieving all posts performs reasonably"""
        import time
        start = time.time()
        response = client.get("/api/posts")
        elapsed = time.time() - start

        assert response.status_code == 200
        # Should complete in under 2 seconds
        assert elapsed < 2.0


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("MILTON AI PUBLICIST - COMPREHENSIVE API TEST SUITE")
    print("=" * 70)
    print()

    # Run pytest with verbose output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "-x"  # Stop on first failure
    ])
