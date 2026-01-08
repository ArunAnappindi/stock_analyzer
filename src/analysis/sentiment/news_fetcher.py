"""
News fetching for sentiment analysis.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from config.settings import settings

logger = logging.getLogger(__name__)


class NewsFetcher:
    """Fetches news articles for sentiment analysis."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize news fetcher.

        Args:
            api_key: NewsAPI key (optional)
        """
        self.api_key = api_key or settings.news_api_key
        self.base_url = "https://newsapi.org/v2/everything"

    def fetch_news(
        self,
        ticker: str,
        company_name: Optional[str] = None,
        hours_back: int = 24
    ) -> List[Dict]:
        """
        Fetch recent news articles for a stock.

        Args:
            ticker: Stock ticker symbol
            company_name: Company name for better search results
            hours_back: How many hours of news to fetch

        Returns:
            List of news article dictionaries
        """
        if not self.api_key:
            logger.warning("No NewsAPI key provided, returning empty news list")
            return []

        try:
            # Build search query
            query = f"{ticker} stock"
            if company_name:
                query += f" OR {company_name}"

            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(hours=hours_back)

            params = {
                "q": query,
                "from": from_date.isoformat(),
                "to": to_date.isoformat(),
                "sortBy": "publishedAt",
                "language": "en",
                "apiKey": self.api_key
            }

            response = requests.get(self.base_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])

                # Filter and format articles
                formatted_articles = []
                for article in articles[:10]:  # Limit to 10 most recent
                    formatted_articles.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "content": article.get("content", ""),
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "published_at": article.get("publishedAt", ""),
                        "url": article.get("url", "")
                    })

                logger.info(f"Fetched {len(formatted_articles)} news articles for {ticker}")
                return formatted_articles

            else:
                logger.warning(f"NewsAPI returned status {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []

    def detect_catalysts(
        self,
        ticker: str,
        articles: List[Dict]
    ) -> List[str]:
        """
        Detect major catalysts from news headlines.

        Args:
            ticker: Stock ticker
            articles: List of news articles

        Returns:
            List of detected catalyst keywords
        """
        catalysts = []

        # Catalyst keywords
        catalyst_keywords = {
            "earnings": ["earnings", "EPS", "revenue beat", "revenue miss", "quarterly results"],
            "merger": ["merger", "acquisition", "buyout", "M&A"],
            "product": ["new product", "product launch", "innovation"],
            "regulatory": ["FDA approval", "regulatory", "approval granted"],
            "executive": ["CEO", "CFO", "executive", "resignation", "appointment"],
            "guidance": ["guidance raised", "guidance lowered", "outlook"],
            "contract": ["contract", "deal", "partnership"],
            "upgrade": ["upgrade", "downgrade", "rating"],
        }

        try:
            # Combine all article text
            all_text = " ".join([
                f"{a.get('title', '')} {a.get('description', '')}"
                for a in articles
            ]).lower()

            # Check for catalyst keywords
            for catalyst_type, keywords in catalyst_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in all_text:
                        catalysts.append(f"{catalyst_type.capitalize()}: {keyword}")
                        break  # Only add once per category

        except Exception as e:
            logger.error(f"Error detecting catalysts: {e}")

        return catalysts
