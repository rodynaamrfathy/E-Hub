from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, JSON, Text
from .base import Base

class NewsletterSubscriber(Base):
    __tablename__ = "newsletter_subscribers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False)
    categories = Column(JSON, default=list)  # List of subscribed category IDs
    subscribed_at = Column(TIMESTAMP, server_default="now()")
    unsubscribed_at = Column(TIMESTAMP, nullable=True)
    last_sent_at = Column(TIMESTAMP, nullable=True)


class NewsletterCategory(Base):
    __tablename__ = "newsletter_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    topics = Column(JSON, default=list)  # List of related keywords/topics
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default="now()")


class GeneratedArticle(Base):
    __tablename__ = "generated_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    topic = Column(String(255), nullable=False)
    category_id = Column(Integer, nullable=False)
    source_articles = Column(JSON, default=list)  # List of article IDs used
    references = Column(JSON, default=list)  # Formatted citation list
    word_count = Column(Integer)
    generated_at = Column(TIMESTAMP, server_default="now()")
    sent_to_subscribers = Column(Boolean, default=False)
