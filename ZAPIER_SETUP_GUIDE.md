# Zapier Integration Setup Guide

This guide explains how to set up social media publishing via Zapier webhooks for Twitter/X and Instagram.

## Why Zapier?

Using Zapier webhooks provides several benefits:
- **No OAuth complexity**: Zapier handles all authentication
- **Multi-platform support**: Single webhook approach works for all platforms
- **Enterprise reliability**: Zapier's infrastructure handles rate limits and retries
- **Easy maintenance**: Platform API changes are handled by Zapier

## Prerequisites

- Active Zapier account (Free or paid plan)
- Social media accounts:
  - LinkedIn (already configured)
  - Twitter/X account
  - Instagram Business account (must be connected to Facebook Page)

## Setup Instructions

### 1. Twitter/X Integration

#### Step 1: Create Twitter Zap
1. Go to [Zapier Dashboard](https://zapier.com/app/editor)
2. Click "Create Zap"
3. Name it: "Milton AI Publicist - Twitter"

#### Step 2: Configure Trigger
1. **Trigger**: Choose "Webhooks by Zapier"
2. **Event**: Select "Catch Hook"
3. Click "Continue"
4. **Copy the webhook URL** (you'll need this later)
5. Click "Test trigger" (we'll send test data shortly)

#### Step 3: Configure Action
1. **Action**: Choose "Twitter"
2. **Event**: Select "Create Tweet"
3. Click "Continue"
4. **Connect your Twitter account** (follow OAuth flow)
5. **Map the fields**:
   - Message: `1. Content` (from webhook)
   - Image URL (optional): `1. Image Url` (from webhook)
6. **Test the action**

#### Step 4: Activate Zap
1. Click "Publish"
2. Turn the Zap ON
3. Copy the webhook URL from Step 2

#### Step 5: Add to Environment
Add to your `.env` file:
```bash
ZAPIER_TWITTER_WEBHOOK=https://hooks.zapier.com/hooks/catch/XXXXX/YYYYY/
```

### 2. Instagram Integration

#### Step 1: Prerequisites
- Instagram must be a Business or Creator account
- Instagram must be connected to a Facebook Page
- You need Facebook Business integration access

#### Step 2: Create Instagram Zap
1. Go to [Zapier Dashboard](https://zapier.com/app/editor)
2. Click "Create Zap"
3. Name it: "Milton AI Publicist - Instagram"

#### Step 3: Configure Trigger
1. **Trigger**: Choose "Webhooks by Zapier"
2. **Event**: Select "Catch Hook"
3. Click "Continue"
4. **Copy the webhook URL**
5. Click "Test trigger"

#### Step 4: Configure Action
1. **Action**: Choose "Instagram for Business"
2. **Event**: Select "Create Photo Post" or "Create Media Post"
3. Click "Continue"
4. **Connect your Instagram Business account**
5. **Map the fields**:
   - Caption: `1. Content` (from webhook)
   - Image URL: `1. Image Url` (from webhook)
   - Instagram Account: (select your account)
6. **Test the action**

#### Step 5: Activate Zap
1. Click "Publish"
2. Turn the Zap ON
3. Copy the webhook URL

#### Step 6: Add to Environment
Add to your `.env` file:
```bash
ZAPIER_INSTAGRAM_WEBHOOK=https://hooks.zapier.com/hooks/catch/XXXXX/ZZZZZ/
```

### 3. LinkedIn Integration (Already Configured)

If you need to set up LinkedIn via Zapier as well:

1. Create new Zap: "Milton AI Publicist - LinkedIn"
2. **Trigger**: Webhooks by Zapier → Catch Hook
3. **Action**: LinkedIn → Create Share Update
4. **Map fields**:
   - Comment: `1. Content`
   - Image URL (optional): `1. Image Url`
5. Add to `.env`:
```bash
ZAPIER_LINKEDIN_WEBHOOK=https://hooks.zapier.com/hooks/catch/XXXXX/WWWWW/
```

## Testing Your Setup

### Test via Dashboard

1. Start the approval dashboard:
```bash
python dashboard/approval_dashboard.py
```

2. Generate test content or select existing content
3. Click "Publish to Twitter" or "Publish to Instagram"
4. Check the Zapier Task History for success/failure

### Test via Python

```python
import asyncio
from dashboard.zapier_publisher import ZapierPublisher

async def test_publishing():
    publisher = ZapierPublisher()

    # Test Twitter
    result = await publisher.publish_to_platform(
        platform="twitter",
        content="Test post from Milton AI Publicist! 🦉",
        post_id=999,
        metadata={"test": True}
    )
    print("Twitter result:", result)

    # Test Instagram
    result = await publisher.publish_to_platform(
        platform="instagram",
        content="Go Owls! Testing the AI publicist system.",
        image_url="https://example.com/keuka-athletics.jpg",
        post_id=1000,
        metadata={"test": True}
    )
    print("Instagram result:", result)

asyncio.run(test_publishing())
```

## Webhook Payload Format

The system sends the following JSON payload to Zapier:

```json
{
  "content": "Your post content here...",
  "platform": "twitter",
  "post_id": 123,
  "timestamp": "2025-10-22T10:30:00",
  "source": "milton_ai_publicist",
  "image_url": "https://optional-image-url.com/image.jpg",
  "video_url": "https://optional-video-url.com/video.mp4",
  "metadata": {
    "pillar": "AI Innovation in Sports Business",
    "urgency": "standard"
  }
}
```

## Platform-Specific Notes

### Twitter/X
- Character limit: 280 characters per tweet
- For threads, the system automatically breaks content into multiple tweets
- Images: Supports JPG, PNG, GIF (up to 5MB)
- Videos: Supports MP4 (up to 512MB, max 2:20 duration)

### Instagram
- **Requires an image** - Instagram doesn't support text-only posts
- Caption limit: 2,200 characters
- Image formats: JPG, PNG (recommended: 1080x1080 px square)
- Video: MP4 (3-60 seconds for feed, up to 15 minutes for IGTV)
- Hashtags: Include in caption (recommended: 5-10 hashtags)

### LinkedIn
- Character limit: 3,000 characters (optimal: 300-500 words)
- Images: JPG, PNG (recommended: 1200x627 px)
- Videos: MP4 (25MB-5GB, 3 seconds-10 minutes)

## Troubleshooting

### "Platform not configured" Error
- Ensure webhook URL is added to `.env` file
- Restart the dashboard after updating `.env`
- Check that the URL starts with `https://hooks.zapier.com/`

### "Failed to publish" Error
- Check Zapier Task History for detailed error
- Verify the Zap is turned ON
- Ensure social media account is still connected in Zapier
- Check platform-specific requirements (e.g., Instagram needs image)

### Rate Limiting
- Twitter: 300 tweets per 3 hours (100/hour)
- Instagram: 25 posts per day
- LinkedIn: 100 posts per day
- The system has built-in rate limiting (MAX_POSTS_PER_DAY=5)

### Webhook Timeout
- Default timeout: 30 seconds
- If posts fail due to timeout, check Zapier task history
- Consider adding retry logic in Zapier (premium feature)

## Cost Considerations

### Zapier Plans
- **Free**: 100 tasks/month (sufficient for testing)
- **Starter** ($19.99/month): 750 tasks/month
- **Professional** ($49/month): 2,000 tasks/month
- **Team** ($299/month): 50,000 tasks/month

### Recommended Plan
For Milton's use case (5 posts/day × 3 platforms × 30 days = 450 tasks/month):
- **Starter plan** is sufficient
- Provides buffer for retries and testing

## Security Best Practices

1. **Keep webhook URLs secret**: Treat them like API keys
2. **Use HTTPS only**: Zapier webhooks use HTTPS by default
3. **Validate responses**: Check Zapier's response status
4. **Monitor task history**: Regularly review Zapier task logs
5. **Rotate webhooks**: If compromised, create new Zaps with new URLs

## Advanced Configuration

### Multi-Platform Publishing

To publish to multiple platforms simultaneously:

```python
from dashboard.zapier_publisher import ZapierPublisher

async def publish_everywhere():
    publisher = ZapierPublisher()

    results = await publisher.publish_to_multiple(
        platforms=["linkedin", "twitter", "instagram"],
        content="Exciting news from Keuka College Athletics!",
        image_url="https://example.com/image.jpg",
        post_id=123
    )

    for platform, result in results.items():
        if result["success"]:
            print(f"✅ Published to {platform}")
        else:
            print(f"❌ Failed to publish to {platform}: {result['error']}")
```

### Custom Metadata

Pass custom metadata to track performance:

```python
result = await publisher.publish_to_platform(
    platform="twitter",
    content="AI is transforming college athletics...",
    metadata={
        "campaign": "AI_Innovation_Week",
        "pillar": "AI Innovation in Sports Business",
        "ab_test_variant": "A"
    }
)
```

## Next Steps

1. Set up webhooks for desired platforms
2. Test each integration thoroughly
3. Monitor Zapier task history for first week
4. Adjust posting strategy based on analytics
5. Consider upgrading Zapier plan if needed

## Support Resources

- [Zapier Documentation](https://zapier.com/help)
- [Twitter API Docs](https://developer.twitter.com/en/docs)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
- [LinkedIn Share API](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares)

---

**Last Updated**: October 22, 2025
**System Version**: 2.0
