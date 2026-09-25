# FINNEWS AI — Financial News Simplifier

> **"Understand financial news without the jargon."**

A modern, full-stack capstone web application designed to fetch real-time financial and business news and simplify complex market reports into clear, beginner-friendly takeaways using Groq LLM (LLaMA 3.3 70B).

---

## 1. Project Title
**FINNEWS AI — Financial News Simplifier**

---

## 2. Project Description
FinNews AI is an educational web application that bridges the gap between institutional Wall Street reporting and everyday readers. It retrieves current headlines across the stock market, economy, corporate business, and banking sectors via NewsAPI, cleans and deduplicates the content, and transforms the stories using Groq's ultra-fast LLM inference into easy-to-understand summaries, key takeaways, real-world impacts ("Why It Matters"), and glossary definitions of difficult financial terms.

---

## 3. Problem Statement
Financial news outlets often rely heavily on dense terminology (e.g., *quantitative tightening, basis points, yield inversion, EBITDA compression, liquidity crunches*). For college students, beginner investors, non-finance professionals, and busy readers:
- Articles are intimidating and time-consuming to read.
- Essential takeaways get obscured by market jargon.
- Misinterpretation can lead to anxiety or poor financial decisions.
- Existing AI tools often over-engineer responses or provide risky, unwarranted financial advice.

---

## 4. The Solution
FinNews AI offers a streamlined, single-click solution:
- **Direct Curation:** Pulls reliable, real-time business and market news from NewsAPI.
- **Strict Guardrails:** An AI prompt strictly forbids investment advice, stock predictions, or hallucinations while preserving exact figures, dates, percentages, and company names.
- **Educational Breakdown:** Deconstructs each story into four easy components:
  1. **Simple Summary:** 2–3 sentences in plain English.
  2. **Key Takeaways:** 3 bullet points highlighting facts.
  3. **Why It Matters:** Relatable explanation of real-world impacts on everyday consumers and investors.
  4. **Financial Terms Explained:** Pocket glossary defining tricky words used in the article.
- **Clean Interface:** An accessible, responsive financial dashboard with zero build steps or heavyweight frontend frameworks.

---

## 5. Key Features
- **One-Click Simplification:** Click **"Fetch & Simplify News"** to automatically process the top stories.
- **Topic Filtering:** Filter by **All**, **Stock Market**, **Economy**, **Business**, or **Finance**.
- **Real-Time Deduplication:** Cleans duplicate wire stories, removes broken/withdrawn articles, and sanitizes truncated feeds.
- **Configurable Groq LLM:** Easily change LLM models (default: `llama-3.3-70b-versatile`) directly via an environment variable without touching Python code.
- **Strict JSON Output:** Uses Groq's JSON-mode schema enforcement for consistent parsing and UI rendering.
- **Responsive Dashboard:** Beautiful financial/AI dark mode dashboard that works seamlessly on desktop, tablet, and mobile devices.
- **Automated Windows Script (`run.bat`):** Sets up the virtual environment, installs dependencies, initializes `.env`, and launches Uvicorn automatically.
- **Interactive Swagger Docs:** Full OpenAPI exploration available at `/docs`.

---

## 6. Technology Stack

### Backend
- **Python 3.12+ (Tested on 3.13):** Core programming language.
- **FastAPI:** High-performance, asynchronous web framework.
- **Uvicorn:** ASGI web server.
- **httpx:** Async HTTP client with timeout management for NewsAPI requests.
- **groq:** Official Python SDK for lightning-fast Groq LLM inference.
- **pydantic (v2):** Robust request and response data validation.
- **python-dotenv:** Environment variable management.

### AI Engine
- **Groq Cloud API:** High-throughput, low-latency LLM serving.
- **LLaMA 3.3 70B Versatile (`llama-3.3-70b-versatile`):** Open-weights state-of-the-art model for complex reasoning and summarization.

### News Provider
- **NewsAPI:** Real-time global financial and business news endpoint.

### Frontend
- **HTML5:** Semantic document structure.
- **CSS3:** Modern design system utilizing CSS Grid, Flexbox, custom properties, and animations.
- **Vanilla JavaScript (ES6+):** Lightweight reactive UI logic without node_modules or build steps.

### Testing
- **pytest & pytest-asyncio:** Automated test execution.
- **FastAPI TestClient:** End-to-end API testing with mocked external dependencies.

---

## 7. System Architecture

```text
       +---------------------------------------------+
       |               User Browser                  |
       |  (HTML5 / CSS3 / Vanilla JS Dashboard UI)   |
       +----------------------+----------------------+
                              |
                              | HTTP REST Requests
                              v
       +---------------------------------------------+
       |            FastAPI Backend Engine           |
       |               (Port 8000)                   |
       |  - CORS & Error Handling                    |
       |  - Pydantic Schema Validation               |
       |  - Static Files Mount (/app)                |
       +-------------+----------------+--------------+
                     |                |
    1. Query News    |                | 2. Raw Text to Simplify
    (Filtered &      |                | (System Guardrail Prompt)
     Deduplicated)   v                v
            +----------------+   +-------------------+
            |    NewsAPI     |   |     Groq Cloud    |
            |  (v2/everything|   | (LLaMA 3.3 70B    |
            |    headlines)  |   |  JSON Mode)       |
            +----------------+   +-------------------+
                     |                    |
                     +-------->-----------+
                                |
                                v
               [ Structured Simplified News JSON ]
                                |
                                v
                      Display to User Cards
```

---

## 8. Project Structure

```
finnews-ai/
│
├── backend/
│   ├── main.py              # FastAPI application, endpoints, CORS, static file hosting
│   ├── config.py            # Environment variable configuration and validation
│   ├── news_service.py      # NewsAPI fetcher, query mapper, deduplication logic
│   ├── ai_service.py        # Groq client, prompt engineering, JSON parser & validator
│   ├── schemas.py           # Pydantic data models for requests and responses
│   ├── requirements.txt     # Python backend dependencies
│   └── .env.example         # Environment template with placeholder keys
│
├── frontend/
│   ├── index.html           # Main user interface structure
│   ├── style.css            # Dark financial-tech styling and responsiveness
│   └── script.js            # Frontend state, API integration, and card renderer
│
├── tests/
│   ├── test_health.py       # Health check and root endpoint tests
│   └── test_api.py          # News and simplification tests with mock services
│
├── .gitignore               # Excludes secrets, caches, and virtual environments
├── README.md                # Comprehensive project documentation
└── run.bat                  # One-click startup script for Windows users
```

---

## 9. Installation Steps

### Prerequisites
- **Python 3.12 or higher** installed. Check via:
  ```bash
  python --version
  ```
- **Git** (optional).

### Step 1: Clone or Open the Project Directory
Navigate into the project root directory:
```bash
cd finnews-ai
```

### Step 2: Create a Python Virtual Environment
**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

---

## 10. API Key Setup

To fetch live news and generate AI simplifications, you will need two free API keys:

1. **NewsAPI Key (Free):**
   - Register at [https://newsapi.org/register](https://newsapi.org/register)
   - Copy your 32-character API key.

2. **Groq API Key (Free):**
   - Register or sign in at [https://console.groq.com/keys](https://console.groq.com/keys)
   - Click **"Create API Key"** and copy the secret key.

### Configure Your `.env` File
Create a file named `.env` in the root `finnews-ai/` directory (or copy `backend/.env.example`):

```bash
# Copy example file
copy backend\.env.example .env
```

Open `.env` in any text editor and fill in your keys:
```env
NEWS_API_KEY=your_actual_newsapi_key_here
GROQ_API_KEY=your_actual_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

> **Security Note:** Never commit your `.env` file to GitHub. The `.gitignore` file already protects it.

---

## 11. How to Run

### Method 1: One-Click Startup on Windows (Recommended)
Simply double-click `run.bat` in the project root, or execute:
```cmd
run.bat
```
`run.bat` will automatically:
1. Verify Python is installed.
2. Create `venv` if missing.
3. Activate the virtual environment.
4. Install all dependencies from `requirements.txt`.
5. Create `.env` from template if missing.
6. Launch Uvicorn with auto-reload at `http://127.0.0.1:8000`.

### Method 2: Manual Terminal Execution
With your virtual environment activated:
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Viewing the Application
Open your web browser and navigate to:
- **Web App Dashboard:** [http://127.0.0.1:8000/app/](http://127.0.0.1:8000/app/)
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **API Health Endpoint:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

*(You can also double-click `frontend/index.html` directly in your browser. It will connect to `http://127.0.0.1:8000` via CORS).*

---

## 12. API Endpoints

| Method | Endpoint | Description | Request Query / Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | API status and links | None |
| `GET` | `/health` | Service health status | None |
| `GET` | `/api/news` | Retrieve raw deduplicated news | `?topic=all&page_size=5` |
| `POST` | `/api/simplify` | Simplify a single article | JSON `SimplifyRequest` |
| `POST` | `/api/news/simplify-all` | Batch fetch and simplify news | `?topic=all&limit=3` |

### Sample `POST /api/simplify` Request Body
```json
{
  "title": "Fed Holds Benchmark Rate at 5.25%-5.50% Amid Sticky Inflation",
  "description": "Federal Reserve policymakers voted unanimously to keep rates steady.",
  "content": "The Federal Open Market Committee left its benchmark policy rate unchanged...",
  "source": "Bloomberg",
  "publishedAt": "2026-09-25T14:30:00Z",
  "url": "https://bloomberg.com/news/fed-rate-decision"
}
```

### Sample `POST /api/simplify` Response
```json
{
  "title": "Fed Holds Benchmark Rate at 5.25%-5.50% Amid Sticky Inflation",
  "simple_summary": "The Federal Reserve decided not to raise or lower interest rates today. Officials want to see more proof that price increases are cooling down before making borrowing cheaper.",
  "key_points": [
    "U.S. central bank keeps interest rates unchanged at 5.25% to 5.50%.",
    "Inflation has improved over the past year but remains above the 2% target.",
    "Policymakers are waiting for clearer economic data before cutting rates."
  ],
  "why_it_matters": "When interest rates stay high, borrowing money for mortgages, student loans, and credit cards stays more expensive, while high-yield savings accounts keep earning good returns.",
  "terms_explained": [
    {
      "term": "Federal Reserve",
      "meaning": "The central bank of the United States that regulates banks and controls the nation's money supply."
    },
    {
      "term": "Benchmark Rate",
      "meaning": "The baseline interest rate that banks charge each other for overnight loans, which influences all other consumer interest rates."
    }
  ],
  "source": "Bloomberg",
  "published_at": "2026-09-25T14:30:00Z",
  "url": "https://bloomberg.com/news/fed-rate-decision"
}
```

---

## 13. Example Workflow
1. **User Access:** User opens [http://127.0.0.1:8000/app/](http://127.0.0.1:8000/app/).
2. **Health Check:** Browser performs an immediate background ping to `/health`, updating the status badge to *"Backend Connected"*.
3. **Filter Selection:** User clicks the **"Stock Market"** topic filter.
4. **Trigger:** User clicks **"Fetch & Simplify News"**.
5. **State Feedback:** Button enters disabled state and display sequentially updates:
   - *"Fetching latest financial news..."*
   - *"Simplifying with AI..."*
6. **Backend Processing:**
   - FastAPI queries NewsAPI for fresh stock market articles.
   - Articles are deduplicated and validated.
   - Groq API is called with strict JSON mode and guardrail prompt.
7. **Presentation:** Cards render dynamically with badges, summary box, bulleted key takeaways, "Why It Matters" callout, and jargon glossary items.

---

## 14. Testing

A complete automated test suite is provided in the `tests/` directory. Tests mock external network requests so they run quickly and reliably without consuming live API tokens.

### Run All Tests:
```bash
pytest -v
```

### Expected Output:
```text
tests/test_health.py::test_root_endpoint PASSED
tests/test_health.py::test_health_endpoint PASSED
tests/test_api.py::test_simplify_validation_missing_title PASSED
tests/test_api.py::test_simplify_success PASSED
tests/test_api.py::test_get_news_missing_api_key PASSED
tests/test_api.py::test_get_news_success PASSED
tests/test_api.py::test_simplify_all_news_success PASSED

======================== 7 passed in 0.45s ========================
```

---

## 15. Future Enhancements
- **Audio Briefings (TTS):** Integrate browser SpeechSynthesis or an AI voice model (e.g., ElevenLabs) to read simplified summaries aloud.
- **Search Query Input:** Allow users to search for specific company tickers (e.g., `$AAPL`, `$TSLA`) or custom keywords.
- **Bookmarks / Local Favorites:** Let users save favorite news cards into browser `localStorage`.
- **Multi-language Support:** Translate simplified summaries into Spanish, Hindi, French, and Mandarin.
- **Sentiment Gauge:** Add a visual indicator showing whether an article reflects positive, neutral, or cautious economic sentiment.

---

## 16. Limitations
- **NewsAPI Developer Tier:** The free tier of NewsAPI limits requests to 100 queries/day and restricts articles to a 24-hour publication delay.
- **Article Truncation:** Free NewsAPI responses may truncate full body text at 200 characters (`[+1234 chars]`). FinNews AI safely combines title and description when body content is truncated.
- **Rate Limits:** Free Groq tier has per-minute request limits. FinNews AI clamps batch requests to a maximum of 3–5 articles at a time to prevent quota exhaustion.

---

## 17. Disclaimer

> **IMPORTANT DISCLAIMER:**  
> **FinNews AI provides simplified summaries for educational and informational purposes only. It does NOT provide financial, investment, legal, or tax advice.**  
> The application does not recommend buying, selling, or holding any securities, stocks, cryptocurrencies, or financial instruments. Always consult a certified financial advisor before making investment decisions.
