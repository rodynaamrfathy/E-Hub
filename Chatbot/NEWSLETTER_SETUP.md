# Newsletter Feature Setup Guide

## ✅ What Was Fixed

1. **Added missing dependency**: `email-validator==2.1.1` to both requirements files
2. **Fixed import paths**: Changed from relative imports (`..services`) to absolute imports (`services`)
3. **Updated requirements**: Both `backend/requirements.txt` and `pyproject.toml` now include `email-validator`

## 📦 Installation

### If you haven't installed `email-validator` yet:

```bash
# Using pip
pip install email-validator==2.1.1

# Or using uv
uv pip install email-validator==2.1.1

# Or install pydantic with email support (already done)
pip install "pydantic[email]"
```

### Verify Installation

```bash
cd /Users/safey/Dev/E-Hub/Chatbot
python test_imports.py
```

This should show:
```
✓ Importing newsletter models...
✓ Importing newsletter DTOs...
✓ Importing newsletter service...
✓ Importing article generator...
✓ Importing newsletter router...

✅ All imports successful!
```

## 🚀 Starting the Server

```bash
cd /Users/safey/Dev/E-Hub/Chatbot
python backend/main.py
```

The server will start on `http://127.0.0.1:8000`

Access:
- **API Documentation**: http://127.0.0.1:8000/docs
- **Newsletter endpoints**: http://127.0.0.1:8000/newsletter/*

## ⚙️ Configuration

### 1. Update Environment Variables

Edit `/Users/safey/Dev/E-Hub/Chatbot/.env` and configure SMTP:

```bash
# Newsletter SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com        # Replace with your email
SMTP_PASSWORD=your_app_password        # Replace with app password
FROM_EMAIL=your_email@gmail.com        # Replace with your email
FROM_NAME=E-Hub Newsletter
```

**For Gmail:**
1. Enable 2-Factor Authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the 16-character password in `SMTP_PASSWORD`

### 2. Database Setup

The following tables will be created automatically on first run:
- `newsletter_subscribers`
- `newsletter_categories`
- `generated_articles`

## 📝 Quick Start Guide

### 1. Create Categories

```bash
curl -X POST http://localhost:8000/newsletter/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Climate Change",
    "description": "News about climate change and environmental policy"
  }'

curl -X POST http://localhost:8000/newsletter/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Renewable Energy",
    "description": "Solar, wind, and clean energy news"
  }'
```

### 2. Add a Test Subscriber

```bash
curl -X POST http://localhost:8000/newsletter/subscribers \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "categories": [1]
  }'
```

### 3. Generate an Article

```bash
curl -X POST http://localhost:8000/newsletter/articles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "days_back": 7
  }'
```

This will:
- Fetch articles from the last 7 days
- Pick a trending topic
- Generate a 250-word article with citations
- Return article with references

### 4. Send Test Newsletter

```bash
curl -X POST http://localhost:8000/newsletter/send \
  -H "Content-Type: application/json" \
  -d '{
    "article_id": 1,
    "test_mode": true,
    "test_email": "your.email@gmail.com"
  }'
```

### 5. Send to All Subscribers

```bash
curl -X POST http://localhost:8000/newsletter/send \
  -H "Content-Type: application/json" \
  -d '{
    "article_id": 1,
    "test_mode": false
  }'
```

## 📚 API Endpoints Reference

### Subscribers
- `POST /newsletter/subscribers` - Subscribe
- `GET /newsletter/subscribers/{email}` - Get subscriber
- `GET /newsletter/subscribers` - List all subscribers
- `PATCH /newsletter/subscribers/{email}` - Update preferences
- `POST /newsletter/subscribers/{email}/unsubscribe` - Unsubscribe

### Categories
- `POST /newsletter/categories` - Create category
- `GET /newsletter/categories` - List categories
- `PATCH /newsletter/categories/{id}` - Update category
- `DELETE /newsletter/categories/{id}` - Delete category

### Articles
- `POST /newsletter/articles/generate` - Generate article from news
- `GET /newsletter/articles` - List generated articles
- `GET /newsletter/articles/{id}` - Get specific article
- `GET /newsletter/today-articles` - Get source articles

### Sending
- `POST /newsletter/send` - Send newsletter

## 🤖 Automated Daily Newsletter

Create a daily automation script:

```python
# daily_newsletter.py
import asyncio
import httpx

async def send_daily_newsletter():
    base_url = "http://localhost:8000/newsletter"

    async with httpx.AsyncClient() as client:
        # Generate article
        response = await client.post(
            f"{base_url}/articles/generate",
            json={"days_back": 3}
        )

        if response.status_code == 201:
            article = response.json()
            print(f"Generated: {article['title']}")

            # Send to subscribers
            send_response = await client.post(
                f"{base_url}/send",
                json={"article_id": article["id"]}
            )
            print(f"Sent to {send_response.json()['sent_successfully']} subscribers")

if __name__ == "__main__":
    asyncio.run(send_daily_newsletter())
```

**Schedule with cron:**
```bash
# Run daily at 8 AM
0 8 * * * cd /Users/safey/Dev/E-Hub/Chatbot && python daily_newsletter.py
```

## 📖 Full Documentation

See [docs/NEWSLETTER_API.md](docs/NEWSLETTER_API.md) for complete API documentation with examples.

## 🐛 Troubleshooting

### Import Error: email-validator not installed
```bash
pip install email-validator==2.1.1
# or
pip install "pydantic[email]"
```

### SMTP Authentication Failed
- Check Gmail app password is correct
- Verify 2FA is enabled
- Test with different email provider

### No Articles Generated
- Check if articles exist in database: `GET /newsletter/today-articles`
- Verify Gemini API key is configured
- Check category exists and has articles

### Server Won't Start
```bash
# Test imports first
python test_imports.py

# Check for port conflicts
lsof -i :8000
```

## ✅ Files Created

- `backend/services/models/newsletter.py` - Database models
- `backend/services/dto/NewsletterDTO.py` - Request/response schemas
- `backend/services/repositories/news_article_generator.py` - AI article generation
- `backend/services/repositories/newsletter_service.py` - Newsletter management
- `backend/api/newsletter_router.py` - API endpoints
- `docs/NEWSLETTER_API.md` - Complete API documentation
- `test_imports.py` - Import verification script

## 🎉 Ready to Use!

Your newsletter system is now fully configured and ready to deploy. Start the server and visit http://localhost:8000/docs to explore the API.
