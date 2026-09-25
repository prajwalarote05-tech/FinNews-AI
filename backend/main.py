import logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.schemas import (
    HealthResponse,
    RootResponse,
    NewsListResponse,
    SimplifyRequest,
    SimplifiedArticle,
    SimplifyAllResponse
)
from backend.news_service import fetch_financial_news, NewsServiceError
from backend.ai_service import simplify_article, AIServiceError

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("finnews_ai")

# Initialize FastAPI application
app = FastAPI(
    title="FINNEWS AI — Financial News Simplifier",
    description="Backend API that retrieves financial news and simplifies it for beginners using Groq LLMs.",
    version="1.0.0"
)

# Enable CORS for local frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handlers for clean JSON errors without leaking stack traces
@app.exception_handler(NewsServiceError)
async def news_service_exception_handler(request: Request, exc: NewsServiceError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "NewsServiceError", "detail": exc.message}
    )

@app.exception_handler(AIServiceError)
async def ai_service_exception_handler(request: Request, exc: AIServiceError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "AIServiceError", "detail": exc.message}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "detail": "Unable to process request right now. Please try again."
        }
    )

# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@app.get("/", response_model=RootResponse, summary="API Status & Information")
async def root():
    """Returns general status and links for the FinNews AI API."""
    return RootResponse(
        status="online",
        name="FinNews AI - Financial News Simplifier",
        version="1.0.0",
        docs="/docs",
        health="/health"
    )

@app.get("/health", response_model=HealthResponse, summary="Health Check")
async def health():
    """Health check endpoint to monitor service availability."""
    return HealthResponse(status="healthy")

@app.get("/api/config-status", summary="Safe Configuration Diagnostics")
async def config_status():
    """Returns safe configuration status without exposing secret keys."""
    return settings.get_safe_status()


@app.get("/api/news", response_model=NewsListResponse, summary="Fetch Raw Financial News")
async def get_news(
    topic: Optional[str] = Query("all", description="News topic filter (e.g. all, stock market, economy, business, finance)"),
    page_size: int = Query(5, ge=1, le=10, description="Number of articles to fetch (1-10)")
):
    """
    Fetches raw financial news from NewsAPI.
    Applies deduplication, topic filtering, and content sanitization.
    """
    articles = await fetch_financial_news(topic=topic, page_size=page_size)
    return NewsListResponse(articles=articles, total=len(articles), topic=topic or "all")

@app.post("/api/simplify", response_model=SimplifiedArticle, summary="Simplify a Single News Article")
async def simplify(payload: SimplifyRequest):
    """
    Simplifies an article using Groq LLM.
    Returns plain English summary, 3 key points, why it matters, and jargon explanations.
    """
    # Prefer publishedAt or published_at
    pub_date = payload.publishedAt or payload.published_at

    result = await simplify_article(
        title=payload.title,
        description=payload.description,
        content=payload.content,
        source=payload.source,
        published_at=pub_date,
        url=payload.url
    )
    return result

@app.post("/api/news/simplify-all", response_model=SimplifyAllResponse, summary="Fetch and Simplify Financial News")
async def simplify_all_news(
    topic: Optional[str] = Query("all", description="News topic filter"),
    limit: int = Query(3, ge=1, le=5, description="Number of articles to simplify (1-5 to conserve rate limits)")
):
    """
    End-to-end endpoint:
    1. Fetches recent financial news matching topic.
    2. Sequentially sends each article to Groq LLM for beginner-friendly simplification.
    3. Returns collection of structured simplified articles.
    """
    articles = await fetch_financial_news(topic=topic, page_size=limit)

    simplified_list = []
    for art in articles:
        try:
            simplified = await simplify_article(
                title=art.title,
                description=art.description,
                content=art.content,
                source=art.source,
                published_at=art.published_at,
                url=art.url
            )
            simplified_list.append(simplified)
        except Exception as exc:
            logger.warning("Failed to simplify article '%s': %s", art.title, exc)
            # Continue simplifying remaining articles instead of failing the whole batch

    if not simplified_list and articles:
        # If all simplification calls failed, raise an error
        raise AIServiceError(
            "Failed to simplify news articles. Please verify your Groq API key.",
            status_code=502
        )

    return SimplifyAllResponse(
        articles=simplified_list,
        count=len(simplified_list),
        topic=topic or "all"
    )

# ---------------------------------------------------------------------------
# Serve Frontend Static Files
# ---------------------------------------------------------------------------
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.is_dir():
    app.mount("/app", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
