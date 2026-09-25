import logging
import re
from typing import List, Dict, Any, Optional
import httpx
from backend.config import settings
from backend.schemas import RawArticle

logger = logging.getLogger(__name__)

# Topic search queries focusing on financial terminology
TOPIC_QUERIES: Dict[str, str] = {
    "all": '(finance OR "stock market" OR economy OR "Federal Reserve" OR earnings OR banking)',
    "stock market": '("stock market" OR stocks OR equities OR "Wall Street" OR "S&P 500" OR Nasdaq)',
    "economy": '(economy OR inflation OR "Federal Reserve" OR "interest rates" OR GDP OR unemployment)',
    "business": '(business OR "quarterly earnings" OR corporate OR revenue OR merger OR acquisition)',
    "finance": '(finance OR banking OR investment OR fintech OR "interest rate" OR credit)'
}

# Negative content patterns: immediately disqualify non-financial topics
NEGATIVE_PATTERNS = [
    # Travel / flight deals / airfare
    r"\b(flight deal|basic economy|regular economy|roundtrip|cheap flights?|airfare|hotel deal|resort deal|fare alert|airline tickets?)\b",
    # Sports & athletics
    r"\b(baseball|mlb|home run|pitcher|innings?|strikeout|mound|braves|dodgers|yankees|red sox|mets|cubs|cardinals|astros|phillies)\b",
    r"\b(football|nfl|quarterback|touchdown|super bowl|field goal|linebacker|interception|end zone)\b",
    r"\b(basketball|nba|slam dunk|rebound|triple-double|lakers|celtics|warriors|point guard)\b",
    r"\b(hockey|nhl|stanley cup|soccer|premier league|champions league|la liga|bundesliga|world cup|penalty kick)\b",
    r"\b(formula 1|f1|nascar|grand prix|ufc|mma|knockout|wwe|wrestling|game preview|postgame|pregame)\b",
    # Tech troubleshooting & gaming
    r"\b(error code|how to fix|blue screen|bsod|driver update|firmware update|patch notes|system crash|troubleshooting|windows update)\b",
    r"\b(gameplay|ps5|playstation|xbox|nintendo switch|steam deck|modding|speedrun|boss fight|dlc release|esports|walkthrough)\b",
    # Entertainment, movies, celebrities
    r"\b(movie review|film review|box office|rom-com|trailer released|series finale|season premiere|streaming release|rotten tomatoes)\b",
    r"\b(celebrity dating|red carpet|spotted with|k-pop|pop star|album review|concert tour|grammy|oscar nomination)\b",
    # Lifestyle, recipes, crime
    r"\b(horoscope|zodiac sign|recipe|diet plan|weight loss|beauty tips|murder trial|homicide suspect|shooting suspect|police standoff)\b"
]
NEGATIVE_REGEX = re.compile("|".join(NEGATIVE_PATTERNS), re.IGNORECASE)

# Domains known for sports, gaming, celebrity gossip, or ticket promotions
DISQUALIFIED_DOMAINS = {
    "theflightdeal.com", "ign.com", "kotaku.com", "tmz.com", "espn.com",
    "polygon.com", "pcgamer.com", "gamespot.com", "bleacherreport.com",
    "batterypower.com", "fangraphs.com", "baseballprospectus.com"
}

# High-confidence financial / market concepts (+2 points each)
STRONG_FINANCIAL_PATTERNS = [
    r"\b(fed|federal reserve|central bank|reserve bank|interest rates?|rate hikes?|rate cuts?|monetary policy|basis points)\b",
    r"\b(inflation|cpi|deflation|gdp|recession|stagflation|treasury|treasuries|bond yields?|bond rout)\b",
    r"\b(wall street|s&p 500|nasdaq|dow jones|equities|stock market|bull market|bear market)\b",
    r"\b(quarterly earnings|earnings report|revenue growth|profit margins?|operating income|shareholders?|dividends?)\b",
    r"\b(borrowing costs?|mortgage rates?|tariffs?|unemployment rate|jobs report|nonfarm payrolls)\b",
    r"\b(ipo|initial public offering|market cap|market capitalization|merger|acquisition|buyout|sec filing)\b"
]
STRONG_REGEX = re.compile("|".join(STRONG_FINANCIAL_PATTERNS), re.IGNORECASE)

# General financial terms (+1 point each)
MODERATE_FINANCIAL_PATTERNS = [
    r"\b(stock|stocks|shares|market|markets|economy|economic|economist|economists)\b",
    r"\b(finance|financial|investor|investors|investing|investment|valuation)\b",
    r"\b(bank|banking|banker|debt|credit|loan|loans|crypto|bitcoin|etf|fintech)\b",
    r"\b(commodity|crude oil|trade deficit|consumer spending|retail sales|guidance)\b"
]
MODERATE_REGEX = re.compile("|".join(MODERATE_FINANCIAL_PATTERNS), re.IGNORECASE)

# Recognized high-quality financial journalism publishers (+2 points)
KNOWN_FINANCIAL_SOURCES = {
    "bloomberg", "reuters", "cnbc", "financial times", "the wall street journal",
    "marketwatch", "forbes", "fortune", "barron's", "yahoo finance", "business insider",
    "the economist", "benzinga", "seeking alpha", "investor's business daily", "thestreet",
    "biztoc", "coindesk", "cointelegraph", "business standard", "investopedia"
}


class NewsServiceError(Exception):
    """Custom exception raised when NewsAPI operations fail."""
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def calculate_financial_relevance(
    title: str,
    description: Optional[str] = None,
    source: Optional[str] = None,
    url: Optional[str] = None
) -> int:
    """
    Evaluates whether an article is genuine financial/business news.
    Returns:
        -1 if disqualified by negative pattern or blocked domain.
        >= 0 representing the article's financial relevance score.
    """
    text = f"{title or ''} {description or ''}".lower()
    url_lower = (url or "").lower()
    source_lower = (source or "").lower()

    # 1. Check disqualified domains
    for d in DISQUALIFIED_DOMAINS:
        if d in url_lower or d in source_lower:
            return -1

    # 2. Check negative content patterns
    if NEGATIVE_REGEX.search(text):
        return -1

    # 3. Calculate positive score
    score = 0
    strong_matches = len(STRONG_REGEX.findall(text))
    score += strong_matches * 2

    moderate_matches = len(MODERATE_REGEX.findall(text))
    score += moderate_matches

    if any(k in source_lower for k in KNOWN_FINANCIAL_SOURCES):
        score += 2

    return score


async def fetch_financial_news(
    topic: Optional[str] = "all",
    page_size: int = 5
) -> List[RawArticle]:
    """
    Fetches latest financial news articles from NewsAPI with advanced filtering,
    deduplication, and content sanitization.
    """
    if not settings.has_news_key():
        raise NewsServiceError(
            "NewsAPI key is not configured. Please add NEWS_API_KEY to your .env file.",
            status_code=500
        )

    clean_topic = (topic or "all").lower().strip()
    query = TOPIC_QUERIES.get(clean_topic, TOPIC_QUERIES["all"])
    clamped_size = max(1, min(page_size, 10))

    # Fetch a wider candidate pool from NewsAPI (25-40 articles) to allow thorough filtering
    candidate_limit = min(40, max(25, clamped_size * 5))

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "searchIn": "title,description",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": candidate_limit,
        "apiKey": settings.NEWS_API_KEY
    }

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            response = await client.get(url, params=params)

        if response.status_code == 401:
            raise NewsServiceError(
                "Invalid NewsAPI key. Please verify your NEWS_API_KEY in the .env file.",
                status_code=401
            )
        elif response.status_code == 429:
            raise NewsServiceError(
                "NewsAPI rate limit exceeded. Please wait a moment or upgrade your plan.",
                status_code=429
            )
        elif response.status_code != 200:
            logger.error("NewsAPI error response: %s", response.text)
            raise NewsServiceError(
                f"News service returned an error ({response.status_code}). Please try again later.",
                status_code=502
            )

        data = response.json()
        articles_raw = data.get("articles", [])

        # Categorize candidate articles by quality score
        high_quality_articles: List[RawArticle] = []
        secondary_articles: List[RawArticle] = []
        seen_urls = set()
        seen_titles = set()

        for art in articles_raw:
            title = (art.get("title") or "").strip()
            art_url = (art.get("url") or "").strip()

            if not title or title == "[Removed]" or not art_url:
                continue

            norm_title = title.lower()
            if art_url in seen_urls or norm_title in seen_titles:
                continue

            # Extract source safely
            source_info = art.get("source")
            source_name = "Unknown Source"
            if isinstance(source_info, dict):
                source_name = source_info.get("name") or "Unknown Source"
            elif isinstance(source_info, str):
                source_name = source_info

            description = (art.get("description") or "").strip()
            content = (art.get("content") or "").strip()
            if not content:
                content = description

            # Evaluate financial relevance
            relevance = calculate_financial_relevance(
                title=title,
                description=description,
                source=source_name,
                url=art_url
            )

            # Disqualified (-1) articles are rejected immediately
            if relevance < 0:
                continue

            candidate = RawArticle(
                title=title,
                description=description if description else None,
                content=content if content else None,
                source=source_name,
                published_at=art.get("publishedAt"),
                url=art_url,
                url_to_image=art.get("urlToImage")
            )

            seen_urls.add(art_url)
            seen_titles.add(norm_title)

            if relevance >= 2:
                high_quality_articles.append(candidate)
            elif relevance >= 1:
                secondary_articles.append(candidate)

        # Assemble final articles, prioritizing high-quality matches
        final_articles = high_quality_articles[:clamped_size]
        if len(final_articles) < clamped_size:
            needed = clamped_size - len(final_articles)
            final_articles.extend(secondary_articles[:needed])

        logger.info(
            "Fetched %d articles from NewsAPI, returned %d filtered articles for topic '%s'",
            len(articles_raw),
            len(final_articles),
            clean_topic
        )
        return final_articles

    except httpx.TimeoutException:
        logger.error("Timeout occurred while contacting NewsAPI")
        raise NewsServiceError("Connection to NewsAPI timed out. Please try again.", status_code=504)
    except httpx.RequestError as exc:
        logger.error("Network error while connecting to NewsAPI: %s", exc)
        raise NewsServiceError("Unable to reach NewsAPI network. Please check internet connection.", status_code=502)

