from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re


class NewsletterSubscriberCreate(BaseModel):
    email: str
    name: Optional[str] = None
    categories: List[int] = Field(default_factory=list)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Simple email validation without external dependency"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email address')
        return v.lower()


class NewsletterSubscriberUpdate(BaseModel):
    name: Optional[str] = None
    categories: Optional[List[int]] = None
    is_active: Optional[bool] = None


class NewsletterSubscriberResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    is_active: bool
    categories: List[int]
    subscribed_at: datetime
    last_sent_at: Optional[datetime]

    class Config:
        from_attributes = True


class NewsletterCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    topics: List[str] = Field(default_factory=list)


class NewsletterCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    topics: Optional[List[str]] = None
    is_active: Optional[bool] = None


class NewsletterCategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    topics: List[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ArticleReference(BaseModel):
    title: str
    url: str
    published_at: str
    category: str


class GeneratedArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    topic: str
    category_id: int
    references: List[ArticleReference]
    word_count: int
    generated_at: datetime
    read_time_minutes: int = Field(default=2)

    class Config:
        from_attributes = True


class GenerateArticleRequest(BaseModel):
    category_id: Optional[int] = None
    topic: Optional[str] = None
    days_back: int = Field(default=7, ge=1, le=30)


class SendNewsletterRequest(BaseModel):
    article_id: int
    test_mode: bool = Field(default=False)
    test_email: Optional[str] = None

    @field_validator('test_email')
    @classmethod
    def validate_test_email(cls, v: Optional[str]) -> Optional[str]:
        """Simple email validation for test email"""
        if v is None:
            return v
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email address')
        return v.lower()
