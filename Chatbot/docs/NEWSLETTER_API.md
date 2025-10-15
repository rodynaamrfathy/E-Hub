# Newsletter API Documentation

The Newsletter API provides automated article generation from crawled news sources with proper citations, subscriber management, and email delivery capabilities.

## Features

✅ **AI-Powered Article Generation** - Generates 250-word (~2 min read) articles from recent news
✅ **Automatic Citations** - Includes inline citations [1], [2], etc. with full reference list
✅ **Smart Topic Selection** - Picks relevant topics based on most recent news trends
✅ **Category Management** - Create and manage newsletter categories
✅ **Subscriber Management** - Full CRUD operations for newsletter subscribers
✅ **Email Delivery** - Send newsletters via SMTP to all subscribers or test mode
✅ **Category Preferences** - Subscribers can select which categories they want to receive

---

## Table of Contents

1. [Setup](#setup)
2. [Database Models](#database-models)
3. [API Endpoints](#api-endpoints)
4. [Usage Examples](#usage-examples)
5. [Email Configuration](#email-configuration)

---

## Setup

### 1. Environment Variables

Add to your `.env` file:

```bash
# Newsletter SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your_email@gmail.com
FROM_NAME=E-Hub Newsletter
```

For Gmail, generate an App Password: https://support.google.com/accounts/answer/185833

### 2. Database Migration

The following tables will be created automatically:

- `newsletter_subscribers` - Subscriber information and preferences
- `newsletter_categories` - Newsletter topic categories
- `generated_articles` - AI-generated articles with citations

### 3. Initial Setup

Create initial categories:

```bash
curl -X POST http://localhost:8000/newsletter/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Climate Change",
    "description": "News about climate change, global warming, and environmental policy"
  }'
```

---

## Database Models

### NewsletterSubscriber

```python
{
    "id": int,
    "email": str,              # Unique email address
    "name": str,               # Optional subscriber name
    "is_active": bool,         # Subscription status
    "categories": List[int],   # Subscribed category IDs
    "subscribed_at": datetime,
    "unsubscribed_at": datetime,
    "last_sent_at": datetime   # Last newsletter sent timestamp
}
```

### NewsletterCategory

```python
{
    "id": int,
    "name": str,               # Category name (e.g., "Renewable Energy")
    "description": str,        # Category description
    "is_active": bool,         # Active status
    "created_at": datetime
}
```

### GeneratedArticle

```python
{
    "id": int,
    "title": str,              # AI-generated headline
    "content": str,            # 250-word article with citations
    "topic": str,              # Article topic
    "category_id": int,        # Associated category
    "source_articles": List[int],  # IDs of source articles used
    "references": List[dict],      # Full citation list
    "word_count": int,
    "generated_at": datetime,
    "sent_to_subscribers": bool
}
```

---

## API Endpoints

### Subscriber Management

#### Subscribe to Newsletter

```http
POST /newsletter/subscribers
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "categories": [1, 2, 3]
}
```

**Response:** `201 Created`

#### Get Subscriber Details

```http
GET /newsletter/subscribers/{email}
```

#### List All Subscribers

```http
GET /newsletter/subscribers?active_only=true
```

#### Update Subscriber Preferences

```http
PATCH /newsletter/subscribers/{email}
Content-Type: application/json

{
  "name": "Jane Doe",
  "categories": [1, 3, 5]
}
```

#### Unsubscribe

```http
POST /newsletter/subscribers/{email}/unsubscribe
```

---

### Category Management

#### Create Category

```http
POST /newsletter/categories
Content-Type: application/json

{
  "name": "Renewable Energy",
  "description": "Solar, wind, hydro, and other renewable energy sources"
}
```

#### List Categories

```http
GET /newsletter/categories?active_only=true
```

#### Update Category

```http
PATCH /newsletter/categories/{category_id}
Content-Type: application/json

{
  "name": "Green Energy",
  "is_active": true
}
```

#### Delete Category

```http
DELETE /newsletter/categories/{category_id}
```

---

### Article Generation

#### Generate Article from Recent News

```http
POST /newsletter/articles/generate
Content-Type: application/json

{
  "category_id": 1,           # Optional: specific category
  "topic": "Solar Energy",    # Optional: custom topic
  "days_back": 7              # Look back N days for articles (default: 7)
}
```

**Example Response:**

```json
{
  "id": 42,
  "title": "Solar Power Reaches Record Efficiency in 2025",
  "content": "Recent developments in solar technology have achieved unprecedented efficiency rates... [1] According to researchers at MIT, new perovskite cells can convert 31% of sunlight to electricity [2]...\n\nREFERENCES:\n[1] MIT News - Solar Breakthrough 2025\n[2] Nature Energy Journal...",
  "topic": "Solar Energy Innovations",
  "category_id": 1,
  "references": [
    {
      "title": "MIT Announces Solar Breakthrough",
      "url": "https://news.mit.edu/solar-2025",
      "published_at": "2025-10-14 10:30",
      "category": "Renewable Energy"
    }
  ],
  "word_count": 248,
  "generated_at": "2025-10-15T12:00:00Z",
  "read_time_minutes": 2
}
```

#### List Generated Articles

```http
GET /newsletter/articles?limit=10&category_id=1
```

#### Get Specific Article

```http
GET /newsletter/articles/{article_id}
```

---

### Newsletter Sending

#### Send Newsletter to All Subscribers

```http
POST /newsletter/send
Content-Type: application/json

{
  "article_id": 42,
  "test_mode": false
}
```

**Response:**

```json
{
  "article_id": 42,
  "total_subscribers": 150,
  "sent_successfully": 148,
  "failed": 2
}
```

#### Send Test Newsletter

```http
POST /newsletter/send
Content-Type: application/json

{
  "article_id": 42,
  "test_mode": true,
  "test_email": "test@example.com"
}
```

---

### Source Articles

#### Get Today's Crawled Articles

```http
GET /newsletter/today-articles?category=Climate%20Change&days_back=1&limit=10
```

Returns the raw articles that were crawled and can be used for newsletter generation.

---

## Usage Examples

### Complete Workflow Example

```python
import httpx
import asyncio

async def newsletter_workflow():
    base_url = "http://localhost:8000/newsletter"

    # 1. Create categories
    async with httpx.AsyncClient() as client:
        categories = [
            {"name": "Climate Change", "description": "Climate and global warming news"},
            {"name": "Renewable Energy", "description": "Solar, wind, and clean energy"},
            {"name": "Conservation", "description": "Wildlife and habitat protection"}
        ]

        category_ids = []
        for cat in categories:
            response = await client.post(f"{base_url}/categories", json=cat)
            category_ids.append(response.json()["id"])

        # 2. Add subscribers
        subscribers = [
            {"email": "user1@example.com", "name": "Alice", "categories": category_ids[:2]},
            {"email": "user2@example.com", "name": "Bob", "categories": [category_ids[0]]}
        ]

        for sub in subscribers:
            await client.post(f"{base_url}/subscribers", json=sub)

        # 3. Generate daily article (picks trending topic automatically)
        article_response = await client.post(
            f"{base_url}/articles/generate",
            json={"days_back": 7}
        )
        article = article_response.json()
        print(f"Generated: {article['title']}")
        print(f"References: {len(article['references'])} sources cited")

        # 4. Send test email first
        test_response = await client.post(
            f"{base_url}/send",
            json={
                "article_id": article["id"],
                "test_mode": True,
                "test_email": "test@example.com"
            }
        )
        print("Test email sent!")

        # 5. Send to all subscribers
        send_response = await client.post(
            f"{base_url}/send",
            json={"article_id": article["id"]}
        )
        print(f"Sent to {send_response.json()['sent_successfully']} subscribers")

asyncio.run(newsletter_workflow())
```

### Daily Automation Script

```python
# daily_newsletter.py
import asyncio
import httpx
from datetime import datetime

async def generate_and_send_daily_newsletter():
    """Run this daily via cron job or scheduler"""
    base_url = "http://localhost:8000/newsletter"

    async with httpx.AsyncClient() as client:
        # Generate article based on today's trending news
        article_response = await client.post(
            f"{base_url}/articles/generate",
            json={"days_back": 3}  # Use last 3 days of articles
        )

        if article_response.status_code != 201:
            print("Failed to generate article")
            return

        article = article_response.json()
        print(f"✅ Generated: {article['title']}")

        # Send to subscribers
        send_response = await client.post(
            f"{base_url}/send",
            json={"article_id": article["id"]}
        )

        result = send_response.json()
        print(f"📧 Sent to {result['sent_successfully']}/{result['total_subscribers']} subscribers")

if __name__ == "__main__":
    asyncio.run(generate_and_send_daily_newsletter())
```

Schedule with cron:
```bash
# Run daily at 8 AM
0 8 * * * cd /path/to/project && python daily_newsletter.py
```

---

## Email Configuration

### Gmail Setup

1. Enable 2-Factor Authentication in your Google Account
2. Go to: https://myaccount.google.com/apppasswords
3. Create an app password for "Mail"
4. Use the generated password in `SMTP_PASSWORD`

### Other Email Providers

**SendGrid:**
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
```

**AWS SES:**
```env
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your_ses_smtp_username
SMTP_PASSWORD=your_ses_smtp_password
```

---

## Article Generation Details

### How It Works

1. **Fetch Recent Articles:** Queries the `articles` table for news published in the last N days
2. **Select Topic:** Either uses custom topic or identifies trending topic from most discussed category
3. **AI Generation:** Uses Gemini to write a 250-word article citing the source articles
4. **Citation Format:** Inline citations [1], [2] throughout the article
5. **Reference List:** Full reference list with titles, URLs, and publication dates
6. **Storage:** Saves generated article to `generated_articles` table

### Example Generated Article

**Topic:** "Electric Vehicle Adoption Accelerates"

**Content:**
```
Global electric vehicle sales surged by 45% in the first quarter of 2025,
driven by falling battery costs and expanded charging infrastructure [1].
Major automakers including Ford and GM announced plans to phase out
combustion engines by 2030 [2].

Battery technology improvements have reduced costs by 60% since 2020,
making EVs price-competitive with traditional vehicles [3]. Governments
worldwide are offering incentives, with Norway reaching 90% EV market share [1].

Charging infrastructure expanded dramatically, with 500,000 new stations
installed globally [4]. Industry experts predict EVs will represent 50%
of new car sales by 2028 [5].

The transition faces challenges including grid capacity and raw material
sourcing [3]. However, renewable energy integration and battery recycling
programs are addressing these concerns [2][4].
```

**References:**
1. Bloomberg - "EV Sales Hit Record High" (2025-10-10)
2. Reuters - "Automakers Accelerate EV Plans" (2025-10-12)
3. Nature - "Battery Cost Reduction Analysis" (2025-10-08)
4. IEA - "Global Charging Infrastructure Report" (2025-10-14)
5. McKinsey - "EV Market Forecast 2028" (2025-10-11)

---

## Best Practices

1. **Test First:** Always send test emails before broadcasting to subscribers
2. **Rate Limiting:** Consider adding rate limiting for subscriber endpoints
3. **Unsubscribe Link:** The email template includes unsubscribe functionality
4. **Daily Generation:** Run article generation once per day during off-peak hours
5. **Category Diversity:** Create 5-10 categories for subscriber choice
6. **Source Quality:** Ensure crawled articles are from reputable sources
7. **Monitoring:** Track send success rates and unsubscribe patterns

---

## Troubleshooting

**SMTP Connection Failed:**
- Verify SMTP credentials
- Check firewall/network restrictions
- Ensure 2FA and app passwords are configured (Gmail)

**No Articles Generated:**
- Check if there are recent articles in the `articles` table
- Verify Gemini API key is configured
- Check category has associated articles

**Subscribers Not Receiving:**
- Check subscriber `is_active` status
- Verify category subscriptions match article category
- Check spam folders
- Review SMTP logs

---

## API Authentication (Optional)

To add authentication to newsletter endpoints, use FastAPI dependencies:

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_admin(token = Depends(security)):
    # Implement your auth logic
    if not is_valid_admin_token(token):
        raise HTTPException(status_code=403, detail="Admin access required")

# Add to protected endpoints
@router.post("/categories", dependencies=[Depends(verify_admin)])
async def create_category(...):
    ...
```

---

## Support

For issues or questions:
- GitHub: https://github.com/your-org/e-hub
- Documentation: `/docs` endpoint when running locally
