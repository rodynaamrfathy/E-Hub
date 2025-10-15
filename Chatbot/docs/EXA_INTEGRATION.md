# Exa Search Integration for Newsletter Generation

The newsletter system now includes **automatic fallback to Exa search** when no local articles are found in the database.

## 🎯 How It Works

### Smart Article Sourcing Flow

```
1. Check local database for articles
   ├─ Found? → Use local articles ✅
   └─ Not found? → Search Exa automatically 🔍

2. Exa Search (Fallback)
   ├─ Uses category topics as search terms
   ├─ Searches last 30 days of web content
   ├─ Returns 5 most relevant articles
   └─ Generates article with external sources

3. Article Generation
   ├─ Works with both local & Exa articles
   ├─ Proper citations included
   └─ References list with URLs
```

## 🚀 Features

✅ **Automatic Fallback** - No manual intervention needed
✅ **Smart Search** - Uses category topics for relevant results
✅ **Recent Content** - Searches last 30 days automatically
✅ **Seamless Integration** - Works with existing article generation
✅ **Full Citations** - External sources properly referenced

## 📋 Prerequisites

### 1. Install exa-py

```bash
uv pip install exa-py==1.0.9
```

Already added to [requirements.txt](../backend/requirements.txt) and [pyproject.toml](../pyproject.toml).

### 2. Get Exa API Key

Sign up at https://exa.ai/ and get your API key.

### 3. Add to Environment

```bash
# Add to .env file
EXA_API_KEY=your_exa_api_key_here
```

## 💡 Usage Examples

### Example 1: Generate Article (Auto Exa Fallback)

If no local articles exist, Exa search runs automatically:

```bash
curl -X POST http://localhost:8000/newsletter/articles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": 3,
    "days_back": 7
  }'
```

**What happens:**
1. System checks database for "Plastic Credits" articles from last 7 days
2. None found? Searches Exa using category topics:
   - `plastic credits`
   - `plastic neutrality`
   - `Verra plastic credits`
3. Returns 5 relevant external articles
4. Generates 250-word article with proper citations

### Example 2: Custom Topic with Exa

```bash
curl -X POST http://localhost:8000/newsletter/articles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": 1,
    "topic": "blockchain in supply chain sustainability",
    "days_back": 7
  }'
```

If no local articles, Exa searches for: `"blockchain in supply chain sustainability"`

### Example 3: Random Category

```bash
curl -X POST http://localhost:8000/newsletter/articles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "days_back": 7
  }'
```

Picks random category, uses its topics for Exa search if needed.

## 🔧 Technical Details

### Search Strategy

When searching Exa, the system:

1. **Uses Category Topics**
   ```python
   # Example: Plastic Credits category
   topics = ["plastic credits", "plastic neutrality", "Verra"]
   query = "plastic credits OR plastic neutrality OR Verra"
   ```

2. **Or Uses Custom Topic**
   ```python
   topic = "blockchain traceability"
   query = "blockchain traceability"
   ```

3. **Neural Search**
   ```python
   exa.search_and_contents(
       query,
       type="neural",           # Semantic understanding
       use_autoprompt=True,     # Query optimization
       num_results=5,
       start_published_date="2025-09-15"  # Last 30 days
   )
   ```

### Article Format

Exa articles are converted to match local article format:

```python
{
    "id": "exa_abc123",
    "title": "Plastic Credits Gain Momentum...",
    "summary": "First 500 chars of content...",
    "content": "Full article text...",
    "url": "https://source.com/article",
    "category": "Plastic Credits & Offsetting",
    "published_at": "2025-10-10T12:00:00",
    "source": "exa"
}
```

### Mixed Sources

The generator handles both seamlessly:

```python
# Database Article (SQLAlchemy object)
article.title          # attribute access
article.published_at   # datetime object

# Exa Article (dict)
article['title']       # dict access
article['published_at'] # datetime object

# Generator handles both! ✅
```

## 📊 Logging

The system logs search activity:

```
⚠️  No local articles found for Plastic Credits & Offsetting. Searching Exa...
🔍 Searching Exa for: plastic credits OR plastic neutrality OR Verra
✅ Found 5 articles from Exa
✅ Using 5 articles from Exa search
```

## 🛠️ Configuration

### Adjust Search Parameters

Edit [news_article_generator.py](../backend/services/repositories/news_article_generator.py):

```python
# Change number of results
max_results=5  # default

# Change time window
start_published_date=(datetime.now() - timedelta(days=30))  # default 30 days

# Change search type
type="neural"  # or "keyword" for exact matching
```

### Disable Exa (Optional)

To use only local articles:

```python
# Remove or comment EXA_API_KEY from .env
# EXA_API_KEY=

# System will raise error if no local articles found
```

## 🎭 Examples by Category

### Supply Chain Transparency
**Topics used**: `blockchain`, `digital product passport`, `traceability`
**Exa finds**: Latest DPP regulations, blockchain case studies

### Plastic Credits
**Topics used**: `plastic credits`, `Verra`, `plastic neutrality`
**Exa finds**: Credit schemes, verification standards, market news

### SDG Frameworks
**Topics used**: `SDG 12`, `sustainable consumption`, `climate action`
**Exa finds**: UN reports, policy updates, SDG progress

### Regional (Dawar/Egypt)
**Topics used**: `Dawar app`, `Egypt waste management`, `MENA sustainability`
**Exa finds**: Regional initiatives, local policy, Middle East projects

## 📈 Benefits

### 1. **Never Run Out of Content**
Even without crawled articles, you can generate newsletters.

### 2. **Always Current**
Exa searches the latest web content (last 30 days).

### 3. **Global Coverage**
Access worldwide sustainability news beyond your crawlers.

### 4. **Smart Matching**
Neural search understands context, not just keywords.

### 5. **Zero Maintenance**
Automatic fallback requires no manual intervention.

## ⚠️ Important Notes

### API Costs
- Exa charges per search
- Monitor usage via Exa dashboard
- Set up billing alerts

### Rate Limits
- Default: 1000 requests/month (free tier)
- Production: Upgrade plan for higher limits

### Quality
- Exa returns high-quality sources
- Still includes fact-checking responsibility
- Review generated articles before sending

## 🧪 Testing

### Test Exa Search Directly

```python
import asyncio
from services.repositories.news_article_generator import NewsArticleGenerator
from services.db.postgres import db_manager

async def test_exa():
    async with db_manager.get_session() as db:
        generator = NewsArticleGenerator(db)

        # Get a category
        from services.models.newsletter import NewsletterCategory
        from sqlalchemy import select

        result = await db.execute(
            select(NewsletterCategory).where(NewsletterCategory.id == 3)
        )
        category = result.scalar_one()

        # Search Exa
        articles = await generator.search_exa_articles(
            category=category,
            topic="plastic credits verification",
            max_results=5
        )

        print(f"Found {len(articles)} articles:")
        for article in articles:
            print(f"- {article['title']}")
            print(f"  {article['url']}")

asyncio.run(test_exa())
```

### Test Full Generation Flow

```bash
# 1. Clear local articles (optional - for testing)
# DELETE FROM articles WHERE category = 'Plastic Credits & Offsetting';

# 2. Generate article (will use Exa)
curl -X POST http://localhost:8000/newsletter/articles/generate \
  -d '{"category_id": 3}'

# 3. Check result includes external sources
```

## 🔐 Security

- ✅ API key stored in environment (not code)
- ✅ No sensitive data sent to Exa
- ✅ Results sanitized before storage
- ✅ URLs validated before including in references

## 📚 Additional Resources

- [Exa API Documentation](https://docs.exa.ai/)
- [Exa Python SDK](https://github.com/exa-labs/exa-py)
- [Newsletter API Docs](NEWSLETTER_API.md)
- [Category Setup Guide](../CATEGORIES_SETUP.md)

## 🎉 Summary

Exa integration ensures your newsletter **always has content**, combining:
- 📰 Local crawled articles (primary)
- 🌐 Exa web search (fallback)
- 🤖 AI generation (Gemini)
- 📝 Proper citations (both sources)

Your newsletter system is now fully resilient and production-ready! 🚀
