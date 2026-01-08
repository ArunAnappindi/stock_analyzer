"""
Sentiment analysis engine for analyzing news and social sentiment.
"""

import logging
from typing import List, Dict
from textblob import TextBlob
from src.models import SentimentAnalysis, Sentiment, StockInfo
from .news_fetcher import NewsFetcher
from config.settings import settings

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Sentiment analysis engine."""

    def __init__(self, news_api_key: str = None):
        """
        Initialize sentiment analyzer.

        Args:
            news_api_key: Optional NewsAPI key
        """
        self.news_fetcher = NewsFetcher(news_api_key)

    def analyze(self, stock_info: StockInfo) -> SentimentAnalysis:
        """
        Perform sentiment analysis on news and social data.

        Args:
            stock_info: Stock information

        Returns:
            SentimentAnalysis result
        """
        try:
            # Fetch news articles
            articles = self.news_fetcher.fetch_news(
                stock_info.ticker,
                stock_info.company_name,
                hours_back=24
            )

            # Analyze news sentiment
            news_sentiment, news_score = self._analyze_news_sentiment(articles)

            # Detect major catalysts
            catalysts = self.news_fetcher.detect_catalysts(stock_info.ticker, articles)

            # For now, social sentiment mirrors news sentiment
            # In production, this would integrate with Twitter/Reddit APIs
            social_sentiment = news_sentiment
            social_score = news_score

            # Calculate overall sentiment
            overall_sentiment = self._calculate_overall_sentiment(
                news_sentiment, social_sentiment
            )

            # Calculate confidence
            confidence = self._calculate_confidence(
                news_score, social_score, len(articles), len(catalysts)
            )

            # Generate summary
            summary = self._generate_summary(
                overall_sentiment, news_score, len(articles), catalysts
            )

            return SentimentAnalysis(
                news_sentiment=news_sentiment,
                news_score=news_score,
                social_sentiment=social_sentiment,
                social_score=social_score,
                major_catalysts=catalysts,
                overall_sentiment=overall_sentiment,
                confidence=confidence,
                summary=summary
            )

        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return SentimentAnalysis(
                summary="Error performing sentiment analysis"
            )

    def _analyze_news_sentiment(
        self,
        articles: List[Dict]
    ) -> tuple[Sentiment, float]:
        """
        Analyze sentiment from news articles.

        Args:
            articles: List of news articles

        Returns:
            Tuple of (Sentiment enum, score from -1 to 1)
        """
        if not articles:
            return Sentiment.NEUTRAL, 0.0

        try:
            sentiments = []

            for article in articles:
                # Combine title and description for analysis
                text = f"{article.get('title', '')} {article.get('description', '')}"

                if text.strip():
                    # Use TextBlob for sentiment analysis
                    blob = TextBlob(text)
                    polarity = blob.sentiment.polarity  # -1 to 1
                    sentiments.append(polarity)

            if not sentiments:
                return Sentiment.NEUTRAL, 0.0

            # Calculate average sentiment
            avg_sentiment = sum(sentiments) / len(sentiments)

            # Convert to Sentiment enum
            if avg_sentiment > 0.3:
                sentiment_enum = Sentiment.VERY_POSITIVE
            elif avg_sentiment > 0.1:
                sentiment_enum = Sentiment.POSITIVE
            elif avg_sentiment < -0.3:
                sentiment_enum = Sentiment.VERY_NEGATIVE
            elif avg_sentiment < -0.1:
                sentiment_enum = Sentiment.NEGATIVE
            else:
                sentiment_enum = Sentiment.NEUTRAL

            return sentiment_enum, float(avg_sentiment)

        except Exception as e:
            logger.error(f"Error analyzing news sentiment: {e}")
            return Sentiment.NEUTRAL, 0.0

    def _calculate_overall_sentiment(
        self,
        news_sentiment: Sentiment,
        social_sentiment: Sentiment
    ) -> Sentiment:
        """Calculate overall sentiment from news and social."""
        # Simple average approach
        sentiment_scores = {
            Sentiment.VERY_NEGATIVE: -2,
            Sentiment.NEGATIVE: -1,
            Sentiment.NEUTRAL: 0,
            Sentiment.POSITIVE: 1,
            Sentiment.VERY_POSITIVE: 2
        }

        news_score = sentiment_scores[news_sentiment]
        social_score = sentiment_scores[social_sentiment]

        avg_score = (news_score + social_score) / 2

        # Convert back to enum
        if avg_score >= 1.5:
            return Sentiment.VERY_POSITIVE
        elif avg_score >= 0.5:
            return Sentiment.POSITIVE
        elif avg_score <= -1.5:
            return Sentiment.VERY_NEGATIVE
        elif avg_score <= -0.5:
            return Sentiment.NEGATIVE
        else:
            return Sentiment.NEUTRAL

    def _calculate_confidence(
        self,
        news_score: float,
        social_score: float,
        num_articles: int,
        num_catalysts: int
    ) -> int:
        """Calculate confidence score (0-100)."""
        confidence = 30  # Base confidence

        # More articles = higher confidence
        if num_articles >= 5:
            confidence += 30
        elif num_articles >= 3:
            confidence += 20
        elif num_articles >= 1:
            confidence += 10

        # Strong sentiment = higher confidence
        max_score = max(abs(news_score), abs(social_score))
        if max_score > 0.4:
            confidence += 20
        elif max_score > 0.2:
            confidence += 10

        # Catalysts increase confidence
        if num_catalysts > 0:
            confidence += min(num_catalysts * 10, 20)

        return min(confidence, 100)

    def _generate_summary(
        self,
        sentiment: Sentiment,
        news_score: float,
        num_articles: int,
        catalysts: List[str]
    ) -> str:
        """Generate a text summary of sentiment analysis."""
        summary_parts = []

        # Overall sentiment
        summary_parts.append(f"Sentiment: {sentiment.value.replace('_', ' ').title()}")

        # Score
        if news_score != 0:
            summary_parts.append(f"Score: {news_score:+.2f}")

        # Articles
        if num_articles > 0:
            summary_parts.append(f"{num_articles} recent articles")
        else:
            summary_parts.append("No recent news")

        # Catalysts
        if catalysts:
            summary_parts.append(f"Catalysts: {', '.join(catalysts[:2])}")

        return " | ".join(summary_parts)
