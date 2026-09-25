/**
 * FinNews AI - Frontend Script
 * Handles topic selection, API requests, dynamic card rendering, and UI states.
 */

// Determine API Base URL dynamically
const API_BASE_URL = (
  window.location.protocol.startsWith("http") && window.location.port === "8000"
) ? "" : "http://127.0.0.1:8000";

// DOM Elements
const fetchBtn = document.getElementById("fetch-btn");
const filterButtons = document.querySelectorAll(".filter-btn");
const loadingState = document.getElementById("loading-state");
const loadingStatusText = document.getElementById("loading-status-text");
const errorBanner = document.getElementById("error-banner");
const errorMessage = document.getElementById("error-message");
const closeErrorBtn = document.getElementById("close-error-btn");
const cardsContainer = document.getElementById("cards-container");
const emptyState = document.getElementById("empty-state");
const resultsMeta = document.getElementById("results-meta");
const resultsTitle = document.getElementById("results-title");
const resultsCount = document.getElementById("results-count");
const apiStatusText = document.getElementById("api-status-text");
const statusIndicator = document.querySelector(".status-indicator");

// State
let currentTopic = "all";
let isProcessing = false;

// -----------------------------------------------------------------------------
// Health Check on Load
// -----------------------------------------------------------------------------
async function checkApiHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (res.ok) {
      const data = await res.json();
      if (data.status === "healthy") {
        if (apiStatusText) apiStatusText.textContent = "Backend Connected";
        if (statusIndicator) statusIndicator.classList.remove("error");
      }
    } else {
      markApiOffline();
    }
  } catch (err) {
    markApiOffline();
  }
}

function markApiOffline() {
  if (apiStatusText) apiStatusText.textContent = "Backend Offline (Port 8000)";
  if (statusIndicator) statusIndicator.classList.add("error");
}

// -----------------------------------------------------------------------------
// Topic Filter Handling
// -----------------------------------------------------------------------------
filterButtons.forEach(button => {
  button.addEventListener("click", () => {
    if (isProcessing) return;

    filterButtons.forEach(btn => btn.classList.remove("active"));
    button.classList.add("active");
    currentTopic = button.dataset.topic || "all";
  });
});

// Close error alert
if (closeErrorBtn) {
  closeErrorBtn.addEventListener("click", () => {
    errorBanner.classList.add("hidden");
  });
}

// -----------------------------------------------------------------------------
// Main Fetch & Simplify Workflow
// -----------------------------------------------------------------------------
fetchBtn.addEventListener("click", async () => {
  if (isProcessing) return;

  setLoadingState(true);
  hideError();

  // Sequential loading text updates
  loadingStatusText.textContent = "Fetching latest financial news...";
  
  const stepTimer = setTimeout(() => {
    if (isProcessing) {
      loadingStatusText.textContent = "Simplifying with AI...";
    }
  }, 1200);

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/news/simplify-all?topic=${encodeURIComponent(currentTopic)}&limit=3`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        }
      }
    );

    clearTimeout(stepTimer);

    if (!response.ok) {
      const errData = await response.json().catch(() => null);
      const detail = errData?.detail || "";
      
      // If missing key or known message, present helpful guidance
      if (detail.includes("NEWS_API_KEY") || detail.includes("NewsAPI key")) {
        showError("NewsAPI key is not configured. Please add NEWS_API_KEY to your .env file.");
      } else if (detail.includes("GROQ_API_KEY") || detail.includes("Groq API key")) {
        showError("Groq API key is not configured. Please add GROQ_API_KEY to your .env file.");
      } else if (detail) {
        showError(detail);
      } else {
        showError("Unable to fetch news right now. Please check your API keys or try again.");
      }
      return;
    }

    const data = await response.json();
    renderCards(data.articles || []);

  } catch (err) {
    clearTimeout(stepTimer);
    console.error("Network or fetch error:", err);
    showError("Unable to fetch news right now. Please check your API keys or try again.");
  } finally {
    setLoadingState(false);
  }
});

// -----------------------------------------------------------------------------
// UI State Helpers
// -----------------------------------------------------------------------------
function setLoadingState(loading) {
  isProcessing = loading;
  fetchBtn.disabled = loading;
  if (loading) {
    loadingState.classList.remove("hidden");
  } else {
    loadingState.classList.add("hidden");
  }
}

function showError(message) {
  errorMessage.textContent = message;
  errorBanner.classList.remove("hidden");
}

function hideError() {
  errorBanner.classList.add("hidden");
}

// -----------------------------------------------------------------------------
// Render News Cards
// -----------------------------------------------------------------------------
function renderCards(articles) {
  if (!articles || articles.length === 0) {
    cardsContainer.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="8" y1="12" x2="16" y2="12"></line>
          </svg>
        </div>
        <h4>No articles found</h4>
        <p>No recent news matching this topic could be retrieved. Try selecting a different topic.</p>
      </div>
    `;
    resultsMeta.classList.add("hidden");
    return;
  }

  // Update meta
  resultsTitle.textContent = `Market Insights: ${capitalize(currentTopic)}`;
  resultsCount.textContent = `${articles.length} Article${articles.length > 1 ? "s" : ""} Simplified`;
  resultsMeta.classList.remove("hidden");

  // Build card markup
  const cardsHtml = articles.map(article => buildCardHtml(article)).join("");
  cardsContainer.innerHTML = cardsHtml;

  // Smooth scroll down to results
  resultsMeta.scrollIntoView({ behavior: "smooth", block: "start" });
}

function buildCardHtml(article) {
  const sourceName = escapeHtml(article.source || "Financial Press");
  const dateFormatted = formatDate(article.published_at);
  const title = escapeHtml(article.title || "Financial Update");
  const summary = escapeHtml(article.simple_summary || "Summary not available.");
  const matters = escapeHtml(article.why_it_matters || "Understanding market movements helps track economic trends.");

  // Key points
  const keyPoints = Array.isArray(article.key_points) ? article.key_points : [];
  const keyPointsHtml = keyPoints.length > 0
    ? keyPoints.map(pt => `<li>${escapeHtml(pt)}</li>`).join("")
    : `<li>Refer to the full article for additional details.</li>`;

  // Terms explained
  const terms = Array.isArray(article.terms_explained) ? article.terms_explained : [];
  const termsHtml = terms.length > 0
    ? `
      <div class="section-block">
        <div class="section-label">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
          Financial Terms Explained
        </div>
        <div class="terms-grid">
          ${terms.map(t => `
            <div class="term-item">
              <span class="term-name">${escapeHtml(t.term)}</span>
              <p class="term-meaning">${escapeHtml(t.meaning)}</p>
            </div>
          `).join("")}
        </div>
      </div>
    `
    : "";

  // Article Link
  const articleLinkHtml = article.url
    ? `
      <div class="card-footer">
        <a href="${escapeHtml(article.url)}" target="_blank" rel="noopener noreferrer" class="article-link">
          Read Original Article 
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
            <polyline points="15 3 21 3 21 9"></polyline>
            <line x1="10" y1="14" x2="21" y2="3"></line>
          </svg>
        </a>
      </div>
    `
    : "";

  return `
    <article class="news-card">
      <header class="card-header">
        <span class="source-badge">${sourceName}</span>
        <span class="published-date">${dateFormatted}</span>
      </header>

      <h3 class="card-title">${title}</h3>

      <!-- Simple Summary -->
      <div class="section-block">
        <div class="section-label">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
          </svg>
          Simple Summary
        </div>
        <div class="summary-box">
          <p>${summary}</p>
        </div>
      </div>

      <!-- Key Points -->
      <div class="section-block">
        <div class="section-label">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 11 12 14 22 4"></polyline>
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
          </svg>
          Key Takeaways
        </div>
        <ul class="key-points-list">
          ${keyPointsHtml}
        </ul>
      </div>

      <!-- Why It Matters -->
      <div class="section-block">
        <div class="matters-box">
          <div class="section-label">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
            </svg>
            Why It Matters
          </div>
          <p>${matters}</p>
        </div>
      </div>

      <!-- Financial Terms Explained -->
      ${termsHtml}

      <!-- Original Link -->
      ${articleLinkHtml}
    </article>
  `;
}

// -----------------------------------------------------------------------------
// Utilities
// -----------------------------------------------------------------------------
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatDate(dateStr) {
  if (!dateStr) return "Recent";
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return "Recent";
    return d.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric"
    });
  } catch {
    return "Recent";
  }
}

function capitalize(str) {
  if (!str) return "";
  return str.split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
}

// Initialize on page load
window.addEventListener("DOMContentLoaded", () => {
  checkApiHealth();
});
