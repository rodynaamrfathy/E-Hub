# Newsletter Categories Setup Guide

## ✅ What Was Done

I've created a comprehensive category system with **16 detailed categories** and **200+ related topics/keywords** for your newsletter system.

## 📂 Files Created

1. **[populate_newsletter_categories.sql](backend/services/models/populate_newsletter_categories.sql)** - Complete SQL script with all categories and topics
2. Updated **[newsletter.py](backend/services/models/newsletter.py)** - Added `topics` field to model
3. Updated **[NewsletterDTO.py](backend/services/dto/NewsletterDTO.py)** - Added topics to DTOs
4. Updated **[newsletter_service.py](backend/services/repositories/newsletter_service.py)** - Topics handling
5. Updated **[newsletter_router.py](backend/api/newsletter_router.py)** - Topics in API

## 📊 Categories Included

### 1. **Supply Chain Transparency & Circularity**
Topics: supply chain transparency, blockchain, digital product passport, EPR compliance, circular procurement (16 topics)

### 2. **Digital Transformation & Smart Technologies**
Topics: IoT waste tracking, AI circular economy, digital twins, smart waste management (14 topics)

### 3. **Plastic Credits & Offsetting**
Topics: plastic credits, Verra standards, plastic neutrality, verification, social impact (18 topics)

### 4. **Waste Management & Recycling**
Topics: recycling technologies, zero waste, waste-to-energy, e-waste, composting (14 topics)

### 5. **Community Engagement & Social Impact**
Topics: citizen reporting, GPS tracking, informal sector, waste education (13 topics)

### 6. **Circular Economy & Sustainability**
Topics: 3R/10R frameworks, circular design, zero waste systems, material lifecycles (15 topics)

### 7. **SDG & Development Frameworks**
Topics: All 17 SDGs, sustainable consumption, climate action, biodiversity (27 topics)

### 8. **Climate Change & Environment**
Topics: global warming, carbon emissions, Paris Agreement, net zero, climate resilience (15 topics)

### 9. **Renewable Energy**
Topics: solar, wind, hydro, energy transition, battery storage, green hydrogen (15 topics)

### 10. **Sustainability News & Trends**
Topics: circularity news, ESG regulations, business sustainability, global plastics treaty (16 topics)

### 11. **Conservation & Biodiversity**
Topics: wildlife protection, habitat preservation, ecosystem restoration, endangered species (14 topics)

### 12. **Sustainable Living**
Topics: eco-friendly lifestyle, zero waste living, sustainable fashion, plastic-free (14 topics)

### 13. **Environmental Policy & Regulation**
Topics: environmental law, EPR regulations, carbon pricing, international agreements (14 topics)

### 14. **Green Technology & Innovation**
Topics: clean tech, environmental innovation, sustainable materials, green chemistry (14 topics)

### 15. **Ocean & Marine Life**
Topics: ocean conservation, plastic in oceans, marine ecosystems, ocean cleanup (15 topics)

### 16. **Regional Sustainability & Local Impact**
Topics: Dawar app, Egypt waste management, MENA sustainability, regional circular economy (14 topics)

**Total: 16 categories with 200+ searchable keywords**

## 🚀 Installation

### Method 1: Run SQL Script (Recommended)

```bash
# Connect to your database
psql "postgresql://neondb_owner:npg_YhJoUDEH61TF@ep-empty-poetry-adnc151z-pooler.c-2.us-east-1.aws.neon.tech/Dawar?sslmode=require" \
  -f backend/services/models/populate_newsletter_categories.sql
```

### Method 2: Copy/Paste into Database Client

Open the SQL file and run it in your preferred database client (pgAdmin, DBeaver, etc.)

### Method 3: Let FastAPI Auto-Create

Start the server and it will create the table structure automatically:
```bash
python backend/main.py
```

Then use the API to populate categories (see below).

## 📡 Using the API

### Create Category with Topics

```bash
curl -X POST http://localhost:8000/newsletter/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Plastic Credits & Offsetting",
    "description": "Plastic credit schemes and verification standards",
    "topics": [
      "plastic credits",
      "plastic footprint offsetting",
      "Verra plastic credits",
      "plastic neutrality"
    ]
  }'
```

### List All Categories with Topics

```bash
curl http://localhost:8000/newsletter/categories
```

Response includes all topics:
```json
[
  {
    "id": 1,
    "name": "Supply Chain Transparency & Circularity",
    "description": "Supply chain transparency, traceability...",
    "topics": [
      "supply chain transparency",
      "blockchain in supply chain",
      "digital product passport"
    ],
    "is_active": true,
    "created_at": "2025-10-15T..."
  }
]
```

### Update Category Topics

```bash
curl -X PATCH http://localhost:8000/newsletter/categories/1 \
  -H "Content-Type: application/json" \
  -d '{
    "topics": ["new topic", "another topic"]
  }'
```

## 🔍 How Topics Are Used

### 1. **Article Generation**
When generating articles, the system can:
- Search news based on category topics
- Pick trending topics from the keyword list
- Generate relevant content matching subscriber interests

### 2. **Smart Topic Selection**
```python
# The generator will use topics to find relevant news
category = await get_category(1)  # Supply Chain category
topics = category.topics  # ["blockchain", "DPP", "traceability"...]

# Search news articles matching these topics
articles = await search_articles(topics)
```

### 3. **Subscriber Preferences**
Subscribers choose categories, and receive articles based on category topics:
```json
{
  "email": "user@example.com",
  "categories": [1, 3, 7],  // Supply Chain, Plastic Credits, SDGs
  "name": "John Doe"
}
```

## 🗄️ Database Schema

```sql
CREATE TABLE newsletter_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    topics JSONB DEFAULT '[]'::jsonb,  -- ← New field
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- GIN index for fast topic searches
CREATE INDEX idx_newsletter_categories_topics
ON newsletter_categories USING GIN (topics);
```

## 🔎 Searching by Topics

### Find categories containing a specific topic:
```sql
SELECT name, description
FROM newsletter_categories
WHERE topics @> '["plastic credits"]'::jsonb;
```

### Get all unique topics:
```sql
SELECT DISTINCT jsonb_array_elements_text(topics) as topic
FROM newsletter_categories
ORDER BY topic;
```

### Search multiple topics:
```sql
SELECT name
FROM newsletter_categories
WHERE topics ?| ARRAY['blockchain', 'AI', 'IoT'];
```

## 📈 Benefits

✅ **200+ Keywords** for comprehensive news coverage
✅ **Smart Categorization** - Articles auto-matched to categories
✅ **Flexible Topics** - Easily add/remove keywords via API
✅ **Searchable** - Fast JSONB searches with GIN indexes
✅ **SDG Aligned** - All 17 UN SDGs included
✅ **Regional Focus** - Egypt/MENA and Dawar-specific topics
✅ **Trend Tracking** - Latest sustainability trends covered

## 🧪 Testing

```bash
# 1. Start server
python backend/main.py

# 2. List categories (should show 16 with topics)
curl http://localhost:8000/newsletter/categories

# 3. Create a test category
curl -X POST http://localhost:8000/newsletter/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Category",
    "description": "Testing topics",
    "topics": ["test topic 1", "test topic 2"]
  }'

# 4. Generate article (will use topics for smart matching)
curl -X POST http://localhost:8000/newsletter/articles/generate \
  -H "Content-Type: application/json" \
  -d '{"days_back": 7}'
```

## 📝 Next Steps

1. **Run the SQL script** to populate all categories
2. **Verify in database** - Check categories have topics
3. **Test API** - Create/update categories with topics
4. **Generate articles** - Topics will be used for smart content matching
5. **Monitor usage** - See which topics generate most engagement

## 🎯 Example Use Cases

### Use Case 1: Dawar-Focused Newsletter
```bash
# Subscribe user to regional topics
curl -X POST http://localhost:8000/newsletter/subscribers \
  -d '{
    "email": "user@example.com",
    "categories": [16]  // Regional Sustainability category
  }'
```

### Use Case 2: Plastic Credits Deep Dive
```bash
# Generate article on plastic credits
curl -X POST http://localhost:8000/newsletter/articles/generate \
  -d '{
    "category_id": 3,  // Plastic Credits category
    "days_back": 7
  }'
```

### Use Case 3: SDG Reporting
```bash
# Generate SDG-aligned content
curl -X POST http://localhost:8000/newsletter/articles/generate \
  -d '{
    "category_id": 7,  // SDG category with all 17 goals
    "topic": "SDG 12 Responsible Consumption"
  }'
```

Your newsletter system is now equipped with comprehensive, searchable categories! 🎉
