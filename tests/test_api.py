from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.schemas import RawArticle, SimplifiedArticle, TermExplanation
from backend.news_service import NewsServiceError

client = TestClient(app)

def test_simplify_validation_missing_title():
    """Verify POST /api/simplify rejects requests missing required fields."""
    response = client.post("/api/simplify", json={
        "description": "Some description without title"
    })
    assert response.status_code == 422  # Pydantic validation error

@patch("backend.main.simplify_article", new_callable=AsyncMock)
def test_simplify_success(mock_simplify):
    """Verify POST /api/simplify processes valid requests and returns structured output."""
    mock_simplify.return_value = SimplifiedArticle(
        title="Fed Keeps Interest Rates Steady",
        simple_summary="The Federal Reserve decided not to change interest rates today.",
        key_points=[
            "Interest rates remain between 5.25% and 5.50%.",
            "Inflation has slowed but remains above the 2% target.",
            "Officials want more evidence before cutting rates."
        ],
        why_it_matters="Borrowing costs for mortgages, credit cards, and auto loans will stay elevated for now.",
        terms_explained=[
            TermExplanation(
                term="Federal Reserve",
                meaning="The central bank of the United States responsible for managing money supply and interest rates."
            )
        ],
        source="Bloomberg",
        published_at="2026-09-25T14:00:00Z",
        url="https://bloomberg.com/news/fed-rates"
    )

    payload = {
        "title": "Fed Keeps Interest Rates Steady",
        "description": "The central bank opted to hold rates.",
        "content": "Full article content here...",
        "source": "Bloomberg",
        "publishedAt": "2026-09-25T14:00:00Z",
        "url": "https://bloomberg.com/news/fed-rates"
    }

    response = client.post("/api/simplify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Fed Keeps Interest Rates Steady"
    assert "Federal Reserve" in data["simple_summary"]
    assert len(data["key_points"]) == 3
    assert len(data["terms_explained"]) == 1
    assert data["terms_explained"][0]["term"] == "Federal Reserve"

@patch("backend.news_service.settings.has_news_key", return_value=False)
def test_get_news_missing_api_key(mock_has_key):
    """Verify GET /api/news returns a friendly error when API key is unconfigured."""
    response = client.get("/api/news")
    assert response.status_code == 500
    data = response.json()
    assert "NewsAPI key is not configured" in data.get("detail", "")

@patch("backend.main.fetch_financial_news", new_callable=AsyncMock)
def test_get_news_success(mock_fetch_news):
    """Verify GET /api/news returns parsed articles cleanly."""
    mock_fetch_news.return_value = [
        RawArticle(
            title="Tech Stocks Surge After Strong Earnings",
            description="Major tech companies beat analyst expectations.",
            content="Detailed earnings breakdown...",
            source="Reuters",
            published_at="2026-09-25T12:00:00Z",
            url="https://reuters.com/markets/tech-surge"
        )
    ]

    response = client.get("/api/news?topic=stock market&page_size=1")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["articles"][0]["title"] == "Tech Stocks Surge After Strong Earnings"
    assert data["articles"][0]["source"] == "Reuters"

@patch("backend.main.fetch_financial_news", new_callable=AsyncMock)
@patch("backend.main.simplify_article", new_callable=AsyncMock)
def test_simplify_all_news_success(mock_simplify, mock_fetch):
    """Verify POST /api/news/simplify-all fetches and simplifies multiple articles."""
    mock_fetch.return_value = [
        RawArticle(
            title="Treasury Yields Dip",
            description="Bond yields fell slightly this morning.",
            content="Bond market movements...",
            source="CNBC",
            published_at="2026-09-25T10:00:00Z",
            url="https://cnbc.com/bonds"
        )
    ]

    mock_simplify.return_value = SimplifiedArticle(
        title="Treasury Yields Dip",
        simple_summary="Returns on government bonds dropped slightly.",
        key_points=["Bond prices rose as yields fell."],
        why_it_matters="Lower yields can lead to lower mortgage rates.",
        terms_explained=[
            TermExplanation(
                term="Treasury Yield",
                meaning="The interest rate paid to investors who lend money to the government."
            )
        ],
        source="CNBC",
        published_at="2026-09-25T10:00:00Z",
        url="https://cnbc.com/bonds"
    )

    response = client.post("/api/news/simplify-all?topic=economy&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert len(data["articles"]) == 1
    assert data["articles"][0]["title"] == "Treasury Yields Dip"
    assert data["articles"][0]["why_it_matters"] == "Lower yields can lead to lower mortgage rates."
