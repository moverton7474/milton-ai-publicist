"""
System Testing Script
Tests the complete Milton Overton AI Publicist workflow
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Import our modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from module_i.insight_synthesis import InsightSynthesizer
from module_ii.voice_modeling import VoiceProfileModeler
from module_ii.content_generator import ContentGenerator
from module_ii.quality_assurance import QualityAssurance


class SystemTester:
    """End-to-end system testing"""

    def __init__(self):
        load_dotenv()
        self.db_url = os.getenv("DATABASE_URL")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.db_url or not self.anthropic_key:
            raise ValueError("Missing DATABASE_URL or ANTHROPIC_API_KEY in .env file")

    async def test_database_connection(self):
        """Test 1: Database connectivity"""
        print("\n" + "="*60)
        print("TEST 1: Database Connection")
        print("="*60)

        try:
            conn = await asyncpg.connect(self.db_url)

            # Check if tables exist
            tables = await conn.fetch("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """)

            print(f"✅ Connected to database")
            print(f"✅ Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table['tablename']}")

            await conn.close()
            return True

        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

    async def test_voice_profile(self):
        """Test 2: Voice profile training"""
        print("\n" + "="*60)
        print("TEST 2: Voice Profile Training")
        print("="*60)

        corpus_dir = "data/milton_content"

        # Check if corpus exists
        if not os.path.exists(corpus_dir):
            print(f"⚠️  Corpus directory not found: {corpus_dir}")
            print(f"Creating sample content for testing...")

            # Create sample content
            os.makedirs(f"{corpus_dir}/linkedin_posts", exist_ok=True)

            sample_posts = [
                """The future of college athletics isn't about bigger budgets—it's about smarter strategy.

At Keuka College, we're proving that innovation doesn't require massive resources. Our AI-driven donor engagement system has increased response rates by 40% in just three months.

The key? Personalization at scale. Instead of generic outreach, we're using data to understand what matters to each donor, then crafting messages that resonate.

This isn't science fiction. It's practical application of available technology that any athletic department can implement.

What's stopping your department from taking the first step toward AI-assisted operations?

#CollegeSports #AIInnovation #AthleticDirector #DonorEngagement""",

                """Leadership in college athletics today requires a different mindset than it did five years ago.

NIL, conference realignment, declining enrollment—these aren't problems to solve in isolation. They're interconnected challenges that demand strategic thinking.

Here's what I've learned as an AD at a Division III program:
• Data beats gut feeling every time
• Technology is your competitive advantage
• Your team is your greatest asset
• Donors want to see innovation, not just tradition

The athletic directors who thrive in the next decade won't be the ones with the biggest budgets. They'll be the ones who adapt fastest.

Are you building systems or fighting fires?

#Leadership #HigherEd #AthleticLeadership #Strategy""",

                """I'm often asked: "Why use an AI avatar for donor outreach?"

The answer is simple: because it works.

Our Synthesia avatar allows me to send personalized video messages to 100+ donors per week—something I physically couldn't do. Each donor gets a genuine message addressing their specific interests and history with our program.

The response? Overwhelming. Donors appreciate the personal touch, and engagement metrics are through the roof.

This isn't about replacing human connection. It's about scaling it.

Technology should amplify what makes us human, not replace it.

#AIInnovation #DonorRelations #CollegeSports #Leadership""",

                """Conference realignment is dominating the headlines, but Division III programs face a different reality.

While Power Five schools negotiate billion-dollar media deals, we're focused on sustainable growth, student-athlete experience, and community impact.

Our competitive advantage? Agility.

We can implement new technologies faster, experiment with innovative approaches, and build deeper relationships with our supporters.

At Keuka, we've turned this into an opportunity. Our AI-first approach to athletics administration is attracting attention from larger programs asking how we do more with less.

The future of college sports isn't just Power Five vs. Group of Five. It's about which programs—at every level—can innovate fastest.

What innovations are you implementing at your institution?

#DivisionIII #CollegeSports #Innovation #Strategy"""
            ]

            for i, post in enumerate(sample_posts, 1):
                with open(f"{corpus_dir}/linkedin_posts/sample_post_{i:03d}.txt", 'w') as f:
                    f.write(post)

            print(f"✅ Created {len(sample_posts)} sample posts")

        try:
            modeler = VoiceProfileModeler(db_url=self.db_url)
            await modeler.initialize()

            profile = await modeler.train_on_corpus(corpus_dir, version="test-1.0.0")

            print(f"✅ Voice profile trained successfully")
            print(f"   - Corpus size: {profile['trained_on_corpus_size']} documents")
            print(f"   - Avg sentence length: {profile['syntactic']['avg_sentence_length']} words")
            print(f"   - Question ratio: {profile['rhetorical']['question_ratio']}")
            print(f"   - Primary tone: {profile['emotional_tone']['primary_tone']}")

            await modeler.close()
            return True

        except Exception as e:
            print(f"❌ Voice profile training failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def test_content_generation(self):
        """Test 3: Content generation"""
        print("\n" + "="*60)
        print("TEST 3: Content Generation")
        print("="*60)

        try:
            # First, create a test content opportunity
            conn = await asyncpg.connect(self.db_url)

            # Create a test insight
            insight_id = await conn.fetchval("""
                INSERT INTO executive_insights (
                    insight_id, input_type, raw_content, priority, processed
                ) VALUES ($1, $2, $3, $4, $5)
                RETURNING insight_id
            """,
                f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "text",
                "AI technology is revolutionizing how we engage with donors in college athletics",
                "high",
                True
            )

            print(f"✅ Created test insight: {insight_id}")

            # Create a test content opportunity
            opportunity_id = await conn.fetchval("""
                INSERT INTO content_opportunities (
                    type, insight_id, suggested_angle, urgency,
                    pillar_alignment, target_platforms, status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING opportunity_id
            """,
                "insight_expansion",
                insight_id,
                "Explore how AI-driven donor engagement creates sustainable athletic programs",
                "today",
                ["AI Innovation in Sports Business", "Leadership & Vision"],
                ["linkedin"],
                "pending"
            )

            print(f"✅ Created test opportunity: {opportunity_id}")

            await conn.close()

            # Generate content
            generator = ContentGenerator(
                anthropic_api_key=self.anthropic_key,
                db_url=self.db_url
            )
            await generator.initialize()

            print(f"⏳ Generating LinkedIn post (this may take 10-15 seconds)...")

            result = await generator.generate_linkedin_post(
                opportunity_id=opportunity_id,
                target_pillar="AI Innovation in Sports Business",
                include_personal_story=False
            )

            print(f"\n✅ LinkedIn post generated!")
            print(f"   - Content ID: {result['content_id']}")
            print(f"   - Word count: {result['word_count']}")
            print(f"   - Character count: {result['character_count']}")
            print(f"   - Hashtags: {', '.join(result['hashtags'])}")

            print(f"\n📝 Generated Content Preview:")
            print(f"{'-'*60}")
            preview = result['content'][:500] + "..." if len(result['content']) > 500 else result['content']
            print(preview)
            print(f"{'-'*60}")

            await generator.close()

            return result['content_id']

        except Exception as e:
            print(f"❌ Content generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def test_quality_assurance(self, content_id: int):
        """Test 4: Quality assurance"""
        print("\n" + "="*60)
        print("TEST 4: Quality Assurance")
        print("="*60)

        try:
            qa = QualityAssurance(
                anthropic_api_key=self.anthropic_key,
                db_url=self.db_url
            )
            await qa.initialize()

            print(f"⏳ Running QA checks on content {content_id} (this may take 10-15 seconds)...")

            result = await qa.full_qa_check(content_id)

            print(f"\n✅ QA check complete!")
            print(f"   - Overall score: {result['overall_score']:.2%}")
            print(f"   - Passed: {'✅ YES' if result['passed'] else '❌ NO'}")
            print(f"   - Ready for approval: {'✅ YES' if result['ready_for_approval'] else '❌ NO'}")

            print(f"\n📊 Individual Check Scores:")
            for check_name, check_data in result['checks'].items():
                score = check_data.get('score', 0)
                status = "✅" if score >= 0.70 else "⚠️"
                print(f"   {status} {check_name.replace('_', ' ').title()}: {score:.2%}")

            if result['recommendations']:
                print(f"\n💡 Recommendations:")
                for rec in result['recommendations'][:3]:
                    print(f"   - {rec}")

            await qa.close()
            return result['passed']

        except Exception as e:
            print(f"❌ QA check failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def test_approval_dashboard_data(self):
        """Test 5: Approval dashboard data"""
        print("\n" + "="*60)
        print("TEST 5: Approval Dashboard Data")
        print("="*60)

        try:
            conn = await asyncpg.connect(self.db_url)

            # Get approval queue
            queue = await conn.fetch("""
                SELECT
                    gc.content_id,
                    gc.platform,
                    gc.overall_qa_score,
                    gc.status,
                    co.urgency,
                    co.pillar_alignment
                FROM generated_content gc
                LEFT JOIN content_opportunities co ON gc.opportunity_id = co.opportunity_id
                WHERE gc.status = 'pending_approval'
                ORDER BY gc.created_at DESC
                LIMIT 5
            """)

            print(f"✅ Found {len(queue)} items in approval queue")

            for item in queue:
                print(f"\n   Content ID: {item['content_id']}")
                print(f"   Platform: {item['platform']}")
                print(f"   QA Score: {float(item['overall_qa_score']):.2%}")
                print(f"   Urgency: {item['urgency']}")
                print(f"   Pillars: {', '.join(item['pillar_alignment'] or [])}")

            # Get stats
            stats = await conn.fetchrow("""
                SELECT
                    COUNT(*) FILTER (WHERE status = 'pending_approval') as pending,
                    COUNT(*) FILTER (WHERE status = 'approved') as approved,
                    COUNT(*) FILTER (WHERE status = 'rejected') as rejected
                FROM generated_content
            """)

            print(f"\n📊 Dashboard Statistics:")
            print(f"   - Pending: {stats['pending']}")
            print(f"   - Approved: {stats['approved']}")
            print(f"   - Rejected: {stats['rejected']}")

            await conn.close()
            return True

        except Exception as e:
            print(f"❌ Dashboard data check failed: {e}")
            return False

    async def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*60)
        print("MILTON OVERTON AI PUBLICIST - SYSTEM TEST")
        print("="*60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        results = []

        # Test 1: Database
        results.append(("Database Connection", await self.test_database_connection()))

        # Test 2: Voice Profile
        results.append(("Voice Profile Training", await self.test_voice_profile()))

        # Test 3: Content Generation
        content_id = await self.test_content_generation()
        results.append(("Content Generation", content_id is not None))

        # Test 4: QA (only if content was generated)
        if content_id:
            results.append(("Quality Assurance", await self.test_quality_assurance(content_id)))

        # Test 5: Dashboard Data
        results.append(("Approval Dashboard", await self.test_approval_dashboard_data()))

        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} - {test_name}")

        print(f"\n{'='*60}")
        print(f"OVERALL: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
        print(f"{'='*60}")

        if passed == total:
            print("\n🎉 ALL TESTS PASSED! System is ready to use.")
            print("\nNext steps:")
            print("1. Collect Milton's real LinkedIn posts")
            print("2. Retrain voice profile with real data")
            print("3. Start the approval dashboard: python dashboard/approval_dashboard.py")
            print("4. Open http://localhost:8080 to review generated content")
        else:
            print("\n⚠️  Some tests failed. Please review the errors above.")
            print("\nCommon issues:")
            print("- Missing .env file or API keys")
            print("- Database not initialized (run: psql < database/schema.sql)")
            print("- Network issues with Anthropic API")

        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


async def main():
    """Main entry point"""
    try:
        tester = SystemTester()
        await tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
