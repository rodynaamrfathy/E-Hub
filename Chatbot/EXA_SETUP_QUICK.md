# Quick Setup: Exa Search Integration

## ✅ What Was Added

**Automatic Exa search fallback** when no local articles are found in the database.

## 🚀 Setup (3 Steps)

### 1. Install Package

```bash
uv pip install exa-py
```

Already added to `requirements.txt` and `pyproject.toml`.

### 2. Get API Key

1. Sign up at https://exa.ai/
2. Get your API key from dashboard
3. Free tier: 1000 searches/month

### 3. Add to Environment

```bash
# Add to .env file
EXA_API_KEY=your_exa_api_key_here
```

## 🎯 How It Works

```
Generate Article Request
    ↓
Check Database for Articles
    ↓
Found? → Use Local Articles ✅
    ↓
Not Found? → Search Exa Automatically 🔍
    ↓
Generate Article with Citations
```

## 💡 Example

```bash
# Generate article for Plastic Credits category
curl -X POST http://localhost:8000/newsletter/articles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": 3,
    "days_back": 7
  }'
```

**If no local articles:**
1. Automatically searches Exa for: `"plastic credits" OR "plastic neutrality" OR "Verra"`
2. Returns 5 most relevant articles from last 30 days
3. Generates article with proper citations
4. Includes reference list with URLs

## 🔍 What Exa Searches

Uses **category topics** as search terms:

| Category | Search Terms |
|----------|-------------|
| Plastic Credits | plastic credits, Verra, plastic neutrality |
| Supply Chain | blockchain, DPP, traceability |
| SDG Frameworks | SDG 12, sustainable consumption, climate action |
| Regional (Egypt) | Dawar app, Egypt waste management, MENA |

## ✨ Features

✅ **Zero Config** - Works automatically when API key is set
✅ **Smart Search** - Uses category topics for relevance
✅ **Recent Content** - Searches last 30 days
✅ **Full Citations** - Proper references with URLs
✅ **Seamless** - Works exactly like local articles

## 📊 Benefits

- **Never run out of content** - Always have source material
- **Global coverage** - Access worldwide news
- **Always current** - Latest web articles (30 days)
- **High quality** - Exa returns reputable sources

## 🧪 Test It

```bash
# Start server
python backend/main.py

# Generate article (will use Exa if no local articles)
curl -X POST http://localhost:8000/newsletter/articles/generate \
  -d '{"category_id": 1, "days_back": 7}'
```

Check logs for:
```
⚠️  No local articles found for Supply Chain Transparency. Searching Exa...
🔍 Searching Exa for: blockchain OR digital product passport OR traceability
✅ Found 5 articles from Exa
```

## 📖 Full Documentation

See [docs/EXA_INTEGRATION.md](docs/EXA_INTEGRATION.md) for:
- Technical details
- Configuration options
- Testing examples
- Troubleshooting

## ⚠️ Notes

- **Free tier**: 1000 searches/month
- **Cost**: Monitor usage in Exa dashboard
- **Quality**: Review generated articles before sending

That's it! Your newsletter system now has **automatic external content sourcing**! 🎉
