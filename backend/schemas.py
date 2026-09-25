from typing import List, Optional
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(default="healthy", description="Current service health status")

class RootResponse(BaseModel):
    """Root endpoint API status response."""
    status: str = Field(default="online", description="API running state")
    name: str = Field(default="FinNews AI - Financial News Simplifier", description="Application name")
    version: str = Field(default="1.0.0", description="API version")
    docs: str = Field(default="/docs", description="Interactive API documentation endpoint")
    health: str = Field(default="/health", description="Health check endpoint")

class RawArticle(BaseModel):
    """Represents a financial news article fetched from NewsAPI."""
    title: str = Field(..., description="Headline of the article")
    description: Optional[str] = Field(None, description="Brief description or snippet")
    content: Optional[str] = Field(None, description="Body content of the article")
    source: Optional[str] = Field(None, description="Publishing organization or source name")
    published_at: Optional[str] = Field(None, description="Publication timestamp (ISO or formatted)")
    url: Optional[str] = Field(None, description="Link to the original article")
    url_to_image: Optional[str] = Field(None, description="URL of cover image if available")

class TermExplanation(BaseModel):
    """A financial term and its plain-English explanation."""
    term: str = Field(..., description="The financial or economic term")
    meaning: str = Field(..., description="Plain-English, beginner-friendly explanation")

class SimplifyRequest(BaseModel):
    """Payload to simplify a specific article."""
    title: str = Field(..., description="Title of the article")
    description: Optional[str] = Field(None, description="Article description")
    content: Optional[str] = Field(None, description="Article content or body")
    source: Optional[str] = Field(None, description="Source of the article")
    publishedAt: Optional[str] = Field(None, description="Publication date from NewsAPI")
    published_at: Optional[str] = Field(None, description="Alternative field for publication date")
    url: Optional[str] = Field(None, description="Original article URL")

class SimplifiedArticle(BaseModel):
    """Structured response containing AI-simplified financial news."""
    title: str = Field(..., description="Article title")
    simple_summary: str = Field(..., description="Jargon-free summary tailored for beginners")
    key_points: List[str] = Field(default_factory=list, description="List of 3-5 key takeaways")
    why_it_matters: str = Field(..., description="Why this development matters to everyday people/investors")
    terms_explained: List[TermExplanation] = Field(
        default_factory=list,
        description="Definitions of tricky financial terms found in the article"
    )
    source: Optional[str] = Field(None, description="Original publisher")
    published_at: Optional[str] = Field(None, description="Publication date")
    url: Optional[str] = Field(None, description="Link to the original full article")

class NewsListResponse(BaseModel):
    """Response returned when querying raw news."""
    articles: List[RawArticle] = Field(default_factory=list, description="Fetched articles")
    total: int = Field(..., description="Number of articles returned")
    topic: str = Field(default="all", description="Topic query used")

class SimplifyAllResponse(BaseModel):
    """Response returned when fetching and simplifying articles in batch."""
    articles: List[SimplifiedArticle] = Field(default_factory=list, description="Simplified articles")
    count: int = Field(..., description="Number of successfully simplified articles")
    topic: str = Field(default="all", description="Topic query used")
