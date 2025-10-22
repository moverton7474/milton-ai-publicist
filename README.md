# Milton Overton AI Publicist Agent

**Version:** 2.0
**Author:** AI Development Team
**Date:** October 2025

## Overview

An autonomous AI publicist agent system that positions Milton Overton (Athletic Director at Keuka College) as the definitive AI Technology Innovator in college sports through automated content generation, strategic distribution, and intelligent opportunity identification.

## System Architecture

The system consists of 5 core modules:

1. **Module I: Insight Capture & Curation** - Voice transcription, news monitoring, insight synthesis
2. **Module II: Content Generation & Voice Emulation** - Voice-authentic multi-platform content creation
3. **Module III: Strategic Distribution & Automation** - Optimal scheduling, multi-platform publishing, engagement management
4. **Module IV: PR & Opportunity Scoring** - Conference/podcast scanning, pitch generation
5. **Module V: Analytics & Self-Correction** - KPI tracking, trend analysis, continuous improvement

## Technology Stack

- **LLM**: Claude (Anthropic API) - Sonnet 4.5 (claude-sonnet-4-5-20250929)
- **Language**: Python 3.11+
- **Framework**: FastAPI + uvicorn
- **Database**: PostgreSQL 14+
- **Cache/Queue**: Redis 7+
- **NLP**: OpenAI Whisper, spaCy, Sentence Transformers
- **Social Publishing**: Zapier webhooks for LinkedIn, Twitter/X, Instagram
- **AI Avatar**: HeyGen integration
- **Security**: HashiCorp Vault / AWS Secrets Manager
- **Monitoring**: Prometheus + Grafana

## Quick Start

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 14+
- Redis 7+
- API Keys: Anthropic, HeyGen, LinkedIn, Twitter/X

### Installation

```bash
# Clone and navigate to directory
cd milton-publicist

# Run setup script
bash scripts/setup.sh

# Configure credentials
cp .env.template .env
# Edit .env with your API keys

# Initialize database
python scripts/migrate_database.py

# Train voice profile (requires Milton's existing content)
python scripts/train_voice_profile.py --corpus-dir data/milton_content/

# Start MCP server
python mcp_server/milton_publicist_mcp.py
```

### Running the System

```bash
# Start approval dashboard
python dashboard/approval_dashboard.py

# Start media monitoring (separate terminal)
python module_i/media_monitor.py --daemon

# Start content scheduler (separate terminal)
python module_iii/scheduler.py --daemon
```

## Features

### Core Capabilities

- **Voice-Authentic Content**: NLP-based voice modeling maintains Milton's unique tone across all platforms
- **Multi-Platform Publishing**: LinkedIn (primary), Twitter/X threads, Instagram captions via Zapier webhooks
- **AI Avatar Videos**: HeyGen integration for video content showcasing AI innovation (Creator plan: $24/month)
- **Real-Time News Monitoring**: 8+ sources continuously scanned for content opportunities
- **Intelligent Scheduling**: Platform-specific optimal posting times with conflict avoidance
- **Opportunity Intelligence**: Conference, podcast, and media opportunity scanning with auto-pitch generation
- **Performance Analytics**: Weekly KPI reports with Share of Voice benchmarking and enhanced pillar tracking
- **Human-in-the-Loop**: 10-minute daily approval queue with real-time dashboard

### Content Strategy

Milton's content aligns with 3 thought leadership pillars:

1. **AI Innovation in Sports Business** (The Founder) - Technical innovation, practical AI implementation
2. **Leadership & Vision** (The AD) - Executive strategy, organizational transformation
3. **The Future of College Sports** (The Futurist) - Trend analysis, industry evolution

## Project Structure

```
milton-publicist/
├── mcp_server/           # MCP server for Claude Desktop integration
├── module_i/             # Insight capture & curation
├── module_ii/            # Content generation & voice emulation
├── module_iii/           # Distribution & automation
├── module_iv/            # PR & opportunity scoring
├── module_v/             # Analytics & self-correction
├── dashboard/            # Human-in-the-loop approval UI
├── security/             # Credential management
├── monitoring/           # Health checks & metrics
├── database/             # Database schemas & migrations
├── scripts/              # Setup & utility scripts
├── tests/                # Unit and integration tests
├── requirements.txt      # Python dependencies
├── .env.template         # Environment variable template
└── README.md            # This file
```

## Configuration

### Environment Variables

See [.env.template](.env.template) for required configuration:

- `ANTHROPIC_API_KEY` - Claude API access
- `HEYGEN_API_KEY` - Avatar video generation (see [HEYGEN_SETUP_GUIDE.md](HEYGEN_SETUP_GUIDE.md))
- `ZAPIER_LINKEDIN_WEBHOOK` - LinkedIn publishing webhook
- `ZAPIER_TWITTER_WEBHOOK` - Twitter/X publishing webhook (see [ZAPIER_SETUP_GUIDE.md](ZAPIER_SETUP_GUIDE.md))
- `ZAPIER_INSTAGRAM_WEBHOOK` - Instagram publishing webhook (see [ZAPIER_SETUP_GUIDE.md](ZAPIER_SETUP_GUIDE.md))
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `VAULT_ADDR`, `VAULT_TOKEN` - HashiCorp Vault (optional, production recommended)

### Platform Setup Guides

- **HeyGen Avatar Videos**: [HEYGEN_SETUP_GUIDE.md](HEYGEN_SETUP_GUIDE.md) - Complete setup for AI avatar videos ($24/month Creator plan)
- **Zapier Publishing**: [ZAPIER_SETUP_GUIDE.md](ZAPIER_SETUP_GUIDE.md) - Multi-platform publishing setup for LinkedIn, Twitter, and Instagram

### Feature Flags

- `ENABLE_AUTO_POSTING` - Allow automated publishing (default: False, requires approval)
- `ENABLE_AVATAR_GENERATION` - Enable HeyGen video generation
- `MAX_POSTS_PER_DAY` - Daily posting limit (default: 5)
- `APPROVAL_REQUIRED` - Require human approval (default: True)

## Security & Credentials

### Recommended Setup (Production)

Use HashiCorp Vault for credential management:

```bash
# Install Vault
brew install vault  # macOS
# or download from https://www.vaultproject.io/

# Start Vault server
vault server -dev

# Store credentials
vault kv put secret/milton-publicist/anthropic api_key="YOUR_KEY"
vault kv put secret/milton-publicist/heygen api_key="YOUR_KEY"
# ... etc
```

### Alternative (AWS Secrets Manager)

```bash
# Install AWS CLI
pip install awscli boto3

# Configure AWS credentials
aws configure

# Store secrets
aws secretsmanager create-secret --name milton-publicist/anthropic --secret-string '{"api_key":"YOUR_KEY"}'
```

### Development (Local Encrypted Storage)

For development only, credentials are encrypted locally using Fernet symmetric encryption:

```bash
python security/credential_manager.py --setup
# Follow prompts to add credentials
```

## Usage

### Executive Input Methods

**Voice Notes** (recommended for quick insights):
```bash
# Via API
curl -X POST http://localhost:8000/api/v1/voice-note \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "audio=@voice_note.mp3" \
  -F "priority=high"
```

**Text Insights**:
```bash
# Via API
curl -X POST http://localhost:8000/api/v1/text-insight \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"content": "Interesting NIL trend I noticed...", "priority": "medium"}'
```

**Email Integration**: Forward emails to `insights@milton-publicist.local` (configured via n8n/Zapier)

### Approval Workflow

1. Content is auto-generated and added to approval queue
2. Dashboard displays pending items with:
   - Expected engagement score
   - Voice authenticity score
   - Platform recommendations
   - Visual suggestions
3. Review and take action:
   - **Approve** ✓ - Schedules for publishing
   - **Reject** ✗ - Provides feedback for learning
   - **Edit** ✏️ - Modify and auto-approve
4. System learns from rejections and edits

### Analytics & Reporting

Weekly reports automatically generated and emailed every Monday 9AM:

- LinkedIn engagement metrics (target: 5% engagement rate)
- Twitter/X performance
- Share of Voice vs peer ADs
- Inbound opportunities (speaking, podcast, media)
- PR pitch success rate
- Avatar video engagement
- Week-over-week growth trends
- Actionable recommendations

## Monitoring & Maintenance

### Health Checks

Access monitoring dashboard: `http://localhost:9090/metrics` (Prometheus)

Key metrics:
- API latency per service (Anthropic, LinkedIn, Twitter, HeyGen)
- Content generation success rate
- Publishing success rate
- Approval queue depth
- Database connectivity

### Daily Tasks

- Review approval queue (10 minutes)
- Check error logs: `tail -f logs/error.log`
- Monitor system health dashboard

### Weekly Tasks

- Review analytics report
- Assess content performance
- Update opportunity priorities
- Check competitor benchmarks

### Monthly Tasks

- Retrain voice profile with new content
- Adjust QA thresholds based on performance
- Update keyword lists for media monitoring
- Review and optimize posting schedule

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/

# Run specific module
pytest tests/module_i/

# Run with coverage
pytest --cov=. tests/
```

### Adding New Features

1. Create feature branch: `git checkout -b feature/new-capability`
2. Implement in appropriate module
3. Add tests to `tests/`
4. Update documentation
5. Submit PR for review

## Troubleshooting

### Common Issues

**Content generation failing**:
- Check Anthropic API key validity
- Verify credit balance
- Review error logs for specific issues

**LinkedIn posting errors**:
- Verify credentials are current
- Check LinkedIn API rate limits
- Ensure account is not restricted

**Voice profile inaccurate**:
- Retrain with more Milton content samples (recommended: 50+ posts)
- Adjust voice profile parameters in `config/voice_profile.json`

**Database connection errors**:
- Verify PostgreSQL is running: `pg_isready`
- Check connection string in `.env`
- Ensure database migrations are current

## Roadmap

### Phase 1 (MVP) - Current
- ✅ Modules I, II, III (capture → generate → publish)
- ✅ Manual approval dashboard
- ✅ LinkedIn-only posting
- ✅ Local credential storage

### Phase 2 - Completed
- ✅ Twitter/X integration via Zapier webhooks
- ✅ Instagram integration via Zapier webhooks
- ✅ Enhanced analytics schema (migration #6)
- ⬜ Module IV (opportunity scanning + pitches)
- ⬜ HashiCorp Vault integration

### Phase 3 - Planned
- ⬜ Module V (full analytics dashboard)
- ⬜ Auto-learning system
- ⬜ Competitive intelligence

### Future Enhancements
- ⬜ Crisis detection & response
- ⬜ Relationship CRM
- ⬜ Content performance ML prediction
- ⬜ Multi-user support (team collaboration)

## License

Proprietary - All rights reserved

## Support

For issues, questions, or feature requests:
- Email: support@milton-publicist.local
- GitHub Issues: [Create an issue](https://github.com/your-org/milton-publicist/issues)

## Acknowledgments

Built with:
- Claude by Anthropic (LLM engine)
- HeyGen (AI avatar technology)
- FastAPI (web framework)
- spaCy (NLP processing)

## Deployment Checklist

### This Week (2-3 hours)

- [ ] **Activate HeyGen Creator Plan** ($24/month)
  - Sign up at [heygen.com](https://www.heygen.com)
  - Follow [HEYGEN_SETUP_GUIDE.md](HEYGEN_SETUP_GUIDE.md) for complete setup
  - Create Milton's custom avatar
  - Clone Milton's voice
  - Configure API credentials

- [ ] **Set up Zapier Publishing** (Starter plan: $19.99/month)
  - Create Twitter/X publishing webhook
  - Create Instagram publishing webhook
  - Follow [ZAPIER_SETUP_GUIDE.md](ZAPIER_SETUP_GUIDE.md) for setup
  - Test each platform integration

- [ ] **Run Database Migration #6**
  ```bash
  psql $DATABASE_URL -f database/migration_006_analytics_enhancements.sql
  ```

- [ ] **Verify Claude Model Update**
  - Confirm all content generation uses `claude-sonnet-4-5-20250929`
  - Test LinkedIn post generation
  - Test Twitter thread generation
  - Test avatar script generation

### Total Monthly Cost
- HeyGen Creator: $24/month (15 min video credits)
- Zapier Starter: $19.99/month (750 tasks/month)
- **Total**: $43.99/month

---

**Last Updated**: October 22, 2025
**System Status**: Production Ready - Multi-Platform Publishing Active
