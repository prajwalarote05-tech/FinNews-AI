import json
import logging
import re
from typing import Dict, Any, Optional
from groq import AsyncGroq, GroqError
from backend.config import settings
from backend.schemas import SimplifiedArticle, TermExplanation

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a financial news simplification assistant.

Rewrite the provided financial news article so that a college student with no finance background can understand it.

Rules:
1. Use simple English.
2. Do not invent facts.
3. Do not add information that is not present in the article.
4. Preserve important numbers, percentages, dates, companies, and events.
5. Explain difficult financial terminology.
6. Do not give investment advice.
7. Do not say whether someone should buy, sell, or hold an investment.
8. Clearly distinguish facts from interpretation.
9. Keep the summary concise.
10. Return valid JSON.

You must respond ONLY with a JSON object in this exact format:
{
  "simple_summary": "Plain English summary in 2-3 sentences.",
  "key_points": [
    "Key takeaway point 1",
    "Key takeaway point 2",
    "Key takeaway point 3"
  ],
  "why_it_matters": "Clear explanation of why this matters to everyday consumers or beginner investors.",
  "terms_explained": [
    {
      "term": "Financial Term",
      "meaning": "Simple explanation of what this term means in context."
    }
  ]
}"""

class AIServiceError(Exception):
    """Custom exception raised when Groq AI operations fail."""
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _extract_json_safely(raw_text: str) -> Dict[str, Any]:
    """Attempts standard JSON loading, falling back to regex block extraction if needed."""
    raw_text = raw_text.strip()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # Try to locate JSON inside markdown fences or brackets
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    
    # Graceful fallback structure if LLM output was completely malformed
    return {
        "simple_summary": raw_text[:300] if raw_text else "Summary unavailable.",
        "key_points": ["Key details could not be parsed automatically."],
        "why_it_matters": "Financial developments often impact market sentiment and corporate valuations.",
        "terms_explained": []
    }


async def simplify_article(
    title: str,
    description: Optional[str] = None,
    content: Optional[str] = None,
    source: Optional[str] = None,
    published_at: Optional[str] = None,
    url: Optional[str] = None
) -> SimplifiedArticle:
    """
    Sends article context to Groq LLM and returns structured simplified news.
    """
    if not settings.has_groq_key():
        raise AIServiceError(
            "Groq API key is not configured. Please add GROQ_API_KEY to your .env file.",
            status_code=500
        )

    # Prepare article content payload safely
    article_text_parts = [f"Headline: {title}"]
    if source:
        article_text_parts.append(f"Source: {source}")
    if description:
        article_text_parts.append(f"Description: {description}")
    if content:
        article_text_parts.append(f"Content: {content}")

    article_text = "\n\n".join(article_text_parts)
    user_prompt = f"Please simplify this financial news article:\n\n{article_text}"

    try:
        client = AsyncGroq(api_key=settings.GROQ_API_KEY, timeout=20.0)
        completion = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=1000
        )

        raw_output = completion.choices[0].message.content or ""
        parsed = _extract_json_safely(raw_output)

        # Validate and sanitize fields
        simple_summary = str(parsed.get("simple_summary", "")).strip() or "No summary provided."
        
        raw_key_points = parsed.get("key_points", [])
        key_points = [str(pt).strip() for pt in raw_key_points if str(pt).strip()]
        if not key_points:
            key_points = ["Refer to the full article for detailed context."]

        why_it_matters = str(parsed.get("why_it_matters", "")).strip() or "Understanding this news helps track broader economic trends."

        raw_terms = parsed.get("terms_explained", [])
        terms_explained = []
        if isinstance(raw_terms, list):
            for t in raw_terms:
                if isinstance(t, dict) and t.get("term") and t.get("meaning"):
                    terms_explained.append(
                        TermExplanation(
                            term=str(t["term"]).strip(),
                            meaning=str(t["meaning"]).strip()
                        )
                    )

        return SimplifiedArticle(
            title=title,
            simple_summary=simple_summary,
            key_points=key_points,
            why_it_matters=why_it_matters,
            terms_explained=terms_explained,
            source=source,
            published_at=published_at,
            url=url
        )

    except GroqError as exc:
        logger.error("Groq API error: %s", exc)
        raise AIServiceError(
            f"Groq AI service error: {exc.message if hasattr(exc, 'message') else str(exc)}",
            status_code=502
        )
    except Exception as exc:
        logger.error("Unexpected error in AI simplification: %s", exc)
        raise AIServiceError(
            "An error occurred while simplifying the article with AI.",
            status_code=500
        )
