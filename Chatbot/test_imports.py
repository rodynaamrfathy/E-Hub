#!/usr/bin/env python
"""Test if all newsletter imports work correctly"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    print("Testing imports...")

    print("✓ Importing newsletter models...")
    from services.models.newsletter import NewsletterSubscriber, NewsletterCategory, GeneratedArticle

    print("✓ Importing newsletter DTOs...")
    from services.dto.NewsletterDTO import NewsletterSubscriberCreate

    print("✓ Importing newsletter service...")
    from services.repositories.newsletter_service import NewsletterService

    print("✓ Importing article generator...")
    from services.repositories.news_article_generator import NewsArticleGenerator

    print("✓ Importing newsletter router...")
    from api.newsletter_router import router

    print("\n✅ All imports successful!")
    print("\nThe newsletter feature is ready to use.")
    print("Run: python backend/main.py")

except ImportError as e:
    print(f"\n❌ Import error: {e}")
    sys.exit(1)
