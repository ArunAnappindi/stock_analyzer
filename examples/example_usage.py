"""
Example usage of the Stock Analyzer as a Python library.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestrator import StockAnalyzer
from src.output import RichFormatter, JsonFormatter


def example_basic_analysis():
    """Example: Basic stock analysis."""
    print("\n" + "="*70)
    print("Example 1: Basic Stock Analysis")
    print("="*70 + "\n")

    # Create analyzer
    analyzer = StockAnalyzer()

    # Analyze a stock
    result = analyzer.analyze(ticker='AAPL')

    if result:
        # Display using rich formatter
        formatter = RichFormatter()
        formatter.format(result)
    else:
        print("Analysis failed!")


def example_custom_interval():
    """Example: Custom interval analysis."""
    print("\n" + "="*70)
    print("Example 2: Custom Interval (15-minute)")
    print("="*70 + "\n")

    analyzer = StockAnalyzer()

    # Analyze with 15-minute intervals
    result = analyzer.analyze(
        ticker='TSLA',
        interval='15m',
        historical_days=7
    )

    if result:
        formatter = RichFormatter()
        formatter.format(result)


def example_json_output():
    """Example: JSON output format."""
    print("\n" + "="*70)
    print("Example 3: JSON Output")
    print("="*70 + "\n")

    analyzer = StockAnalyzer()
    result = analyzer.analyze(ticker='MSFT')

    if result:
        # Display as JSON
        formatter = JsonFormatter()
        json_output = formatter.format(result)
        print(json_output)


def example_with_news_api():
    """Example: Analysis with NewsAPI for sentiment."""
    print("\n" + "="*70)
    print("Example 4: With News Sentiment")
    print("="*70 + "\n")

    # If you have a NewsAPI key, pass it here
    news_api_key = os.getenv('NEWS_API_KEY')

    analyzer = StockAnalyzer(news_api_key=news_api_key)
    result = analyzer.analyze(ticker='NVDA')

    if result:
        formatter = RichFormatter()
        formatter.format(result)


def example_programmatic_access():
    """Example: Accessing analysis results programmatically."""
    print("\n" + "="*70)
    print("Example 5: Programmatic Access")
    print("="*70 + "\n")

    analyzer = StockAnalyzer()
    result = analyzer.analyze(ticker='AMD')

    if result:
        # Access specific parts of the analysis
        print(f"Ticker: {result.ticker}")
        print(f"Current Price: ${result.current_price:.2f}")
        print(f"Trade Signal: {result.trade_recommendation.signal.value}")
        print(f"Confidence: {result.trade_recommendation.confidence}%")

        # Check if it's a BUY signal
        if result.trade_recommendation.signal.value.endswith('_buy'):
            print(f"\nTrade Details:")
            print(f"  Entry: ${result.trade_recommendation.entry_price:.2f}")
            print(f"  Target: ${result.trade_recommendation.target_price:.2f}")
            print(f"  Stop Loss: ${result.trade_recommendation.stop_loss:.2f}")
            print(f"  Risk:Reward: 1:{result.trade_recommendation.risk_reward_ratio:.2f}")
        else:
            print(f"\nNo trade recommended: {result.trade_recommendation.reasoning}")

        # Access technical indicators
        print(f"\nTechnical Indicators:")
        print(f"  Trend: {result.technical_analysis.trend.value}")
        print(f"  RSI: {result.technical_analysis.indicators.rsi:.1f}")
        print(f"  VWAP: ${result.technical_analysis.indicators.vwap:.2f}")

        # Access volume analysis
        print(f"\nVolume Analysis:")
        print(f"  Relative Volume: {result.volume_analysis.relative_volume:.2f}x")
        print(f"  Volume Spike: {result.volume_analysis.volume_spike_detected}")


def example_batch_analysis():
    """Example: Analyze multiple stocks."""
    print("\n" + "="*70)
    print("Example 6: Batch Analysis")
    print("="*70 + "\n")

    tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    analyzer = StockAnalyzer()

    results = []
    for ticker in tickers:
        print(f"Analyzing {ticker}...")
        result = analyzer.analyze(ticker=ticker)
        if result:
            results.append(result)

    # Display summary
    print("\n" + "="*70)
    print("Summary of All Analyses")
    print("="*70 + "\n")

    for result in results:
        signal = result.trade_recommendation.signal.value.upper()
        confidence = result.trade_recommendation.confidence

        print(f"{result.ticker:6} | ${result.current_price:8.2f} | {signal:15} | {confidence:3}%")


if __name__ == '__main__':
    # Run examples
    import sys

    if len(sys.argv) > 1:
        example_num = int(sys.argv[1])

        examples = {
            1: example_basic_analysis,
            2: example_custom_interval,
            3: example_json_output,
            4: example_with_news_api,
            5: example_programmatic_access,
            6: example_batch_analysis,
        }

        if example_num in examples:
            examples[example_num]()
        else:
            print(f"Example {example_num} not found. Available examples: 1-6")
    else:
        print("Usage: python example_usage.py <example_number>")
        print("\nAvailable examples:")
        print("  1: Basic stock analysis")
        print("  2: Custom interval (15-minute)")
        print("  3: JSON output format")
        print("  4: With news sentiment")
        print("  5: Programmatic access to results")
        print("  6: Batch analysis of multiple stocks")
        print("\nExample: python example_usage.py 1")
