"""
Milton AI Publicist - Dashboard Testing Script
Automated tests for the approval dashboard
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, List

# Dashboard URL
BASE_URL = "http://localhost:8080"

class DashboardTester:
    def __init__(self):
        self.session = None
        self.tests_passed = 0
        self.tests_failed = 0

    async def initialize(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()

    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    def print_test(self, name: str, passed: bool, details: str = ""):
        """Print test result"""
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")
        if details:
            print(f"       {details}")

        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1

    async def test_server_running(self) -> bool:
        """Test 1: Check if dashboard server is running"""
        try:
            async with self.session.get(f"{BASE_URL}/", timeout=5) as response:
                passed = response.status == 200
                self.print_test(
                    "Dashboard server is running",
                    passed,
                    f"Status: {response.status}"
                )
                return passed
        except Exception as e:
            self.print_test(
                "Dashboard server is running",
                False,
                f"Error: {str(e)}"
            )
            return False

    async def test_status_endpoint(self) -> bool:
        """Test 2: Check /api/status endpoint"""
        try:
            async with self.session.get(f"{BASE_URL}/api/status") as response:
                if response.status != 200:
                    self.print_test("Status endpoint", False, f"Status: {response.status}")
                    return False

                data = await response.json()

                # Check required fields
                required_fields = ["status", "connections", "stats"]
                missing = [f for f in required_fields if f not in data]

                if missing:
                    self.print_test(
                        "Status endpoint",
                        False,
                        f"Missing fields: {', '.join(missing)}"
                    )
                    return False

                self.print_test(
                    "Status endpoint",
                    True,
                    f"Status: {data.get('status')}, LinkedIn: {data['connections'].get('linkedin')}"
                )
                return True

        except Exception as e:
            self.print_test("Status endpoint", False, f"Error: {str(e)}")
            return False

    async def test_generate_personal_voice(self) -> Dict:
        """Test 3: Generate content in personal voice"""
        try:
            payload = {
                "voice_type": "personal",
                "scenario": "Partner Appreciation",
                "context": "Thank GameChanger Analytics for partnership"
            }

            async with self.session.post(
                f"{BASE_URL}/api/generate",
                json=payload
            ) as response:
                if response.status != 200:
                    self.print_test(
                        "Generate personal voice content",
                        False,
                        f"Status: {response.status}"
                    )
                    return None

                data = await response.json()

                if not data.get("success"):
                    self.print_test(
                        "Generate personal voice content",
                        False,
                        f"Generation failed: {data.get('error')}"
                    )
                    return None

                post = data.get("post", {})
                content = post.get("content", "")
                word_count = post.get("word_count", 0)

                # Check word count (should be 20-80 words)
                word_count_ok = 20 <= word_count <= 80

                # Check for signature phrase
                has_signature = "Let's Go Owls!" in content

                passed = word_count_ok and has_signature

                self.print_test(
                    "Generate personal voice content",
                    passed,
                    f"Words: {word_count}, Signature: {has_signature}"
                )

                return post if passed else None

        except Exception as e:
            self.print_test(
                "Generate personal voice content",
                False,
                f"Error: {str(e)}"
            )
            return None

    async def test_generate_professional_voice(self) -> Dict:
        """Test 4: Generate content in professional voice"""
        try:
            payload = {
                "voice_type": "professional",
                "scenario": "Coaching Announcement",
                "context": "Hiring Sarah Mitchell as Assistant Women's Basketball Coach"
            }

            async with self.session.post(
                f"{BASE_URL}/api/generate",
                json=payload
            ) as response:
                if response.status != 200:
                    self.print_test(
                        "Generate professional voice content",
                        False,
                        f"Status: {response.status}"
                    )
                    return None

                data = await response.json()

                if not data.get("success"):
                    self.print_test(
                        "Generate professional voice content",
                        False,
                        f"Generation failed: {data.get('error')}"
                    )
                    return None

                post = data.get("post", {})
                content = post.get("content", "")
                word_count = post.get("word_count", 0)

                # Check word count (should be 200-400 words)
                word_count_ok = 200 <= word_count <= 400

                # Check for signature phrase (lowercase in professional)
                has_signature = "Let's go Owls!" in content

                passed = word_count_ok and has_signature

                self.print_test(
                    "Generate professional voice content",
                    passed,
                    f"Words: {word_count}, Signature: {has_signature}"
                )

                return post if passed else None

        except Exception as e:
            self.print_test(
                "Generate professional voice content",
                False,
                f"Error: {str(e)}"
            )
            return None

    async def test_get_posts(self) -> bool:
        """Test 5: Get all posts"""
        try:
            async with self.session.get(f"{BASE_URL}/api/posts") as response:
                if response.status != 200:
                    self.print_test("Get posts endpoint", False, f"Status: {response.status}")
                    return False

                data = await response.json()
                posts = data.get("posts", [])

                # Should have at least the posts we just generated
                passed = len(posts) >= 2

                self.print_test(
                    "Get posts endpoint",
                    passed,
                    f"Posts returned: {len(posts)}"
                )

                return passed

        except Exception as e:
            self.print_test("Get posts endpoint", False, f"Error: {str(e)}")
            return False

    async def test_edit_post(self, post_id: int) -> bool:
        """Test 6: Edit a post"""
        try:
            new_content = "This is edited test content. Let's Go Owls!"

            async with self.session.put(
                f"{BASE_URL}/api/posts/{post_id}",
                json={"content": new_content}
            ) as response:
                if response.status != 200:
                    self.print_test("Edit post endpoint", False, f"Status: {response.status}")
                    return False

                data = await response.json()

                if not data.get("success"):
                    self.print_test(
                        "Edit post endpoint",
                        False,
                        f"Edit failed: {data.get('error')}"
                    )
                    return False

                updated_post = data.get("post", {})
                updated_content = updated_post.get("content", "")

                passed = updated_content == new_content

                self.print_test(
                    "Edit post endpoint",
                    passed,
                    f"Content updated: {passed}"
                )

                return passed

        except Exception as e:
            self.print_test("Edit post endpoint", False, f"Error: {str(e)}")
            return False

    async def test_delete_post(self, post_id: int) -> bool:
        """Test 7: Delete a post"""
        try:
            async with self.session.delete(f"{BASE_URL}/api/posts/{post_id}") as response:
                if response.status != 200:
                    self.print_test("Delete post endpoint", False, f"Status: {response.status}")
                    return False

                data = await response.json()
                passed = data.get("success", False)

                self.print_test(
                    "Delete post endpoint",
                    passed,
                    f"Post deleted: {passed}"
                )

                return passed

        except Exception as e:
            self.print_test("Delete post endpoint", False, f"Error: {str(e)}")
            return False

    async def run_all_tests(self):
        """Run all dashboard tests"""
        print("="*70)
        print("MILTON AI PUBLICIST - DASHBOARD TESTING")
        print("="*70)
        print()

        # Test 1: Server running
        server_ok = await self.test_server_running()
        if not server_ok:
            print()
            print("[ERROR] Dashboard server is not running!")
            print("        Start it with: python start_dashboard.py")
            return

        print()

        # Test 2: Status endpoint
        await self.test_status_endpoint()

        print()

        # Test 3: Generate personal voice
        personal_post = await self.test_generate_personal_voice()

        print()

        # Test 4: Generate professional voice
        professional_post = await self.test_generate_professional_voice()

        print()

        # Test 5: Get all posts
        await self.test_get_posts()

        print()

        # Test 6: Edit post (if we have a post ID)
        if personal_post:
            await self.test_edit_post(personal_post.get("id"))
            print()

        # Test 7: Delete post (if we have a post ID)
        if professional_post:
            await self.test_delete_post(professional_post.get("id"))
            print()

        # Print summary
        print("="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"Total:  {self.tests_passed + self.tests_failed}")
        print()

        if self.tests_failed == 0:
            print("[SUCCESS] All tests passed!")
            print()
            print("Next steps:")
            print("1. Complete LinkedIn OAuth setup (15-20 min)")
            print("2. Test publishing to LinkedIn")
            print("3. Generate and publish real content")
        else:
            print(f"[WARNING] {self.tests_failed} test(s) failed")
            print()
            print("Check the errors above and:")
            print("1. Verify .env file has ANTHROPIC_API_KEY")
            print("2. Ensure dashboard server is running")
            print("3. Check console for error messages")

        print()
        print("="*70)

async def main():
    """Main test runner"""
    tester = DashboardTester()

    try:
        await tester.initialize()
        await tester.run_all_tests()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] Testing interrupted by user")
        sys.exit(0)
