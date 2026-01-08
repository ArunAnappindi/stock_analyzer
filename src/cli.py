"""
Command-line interface for the stock analyzer.
"""

import click
import logging
import sys
from pathlib import Path
from typing import Optional

from src.orchestrator import StockAnalyzer
from src.output import RichFormatter, JsonFormatter
from config.settings import settings


# Configure logging
def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('stock_analyzer.log'),
            logging.StreamHandler(sys.stdout) if verbose else logging.NullHandler()
        ]
    )


@click.command()
@click.argument('ticker', type=str)
@click.option(
    '--interval',
    type=click.Choice(['1m', '5m', '15m', '30m'], case_sensitive=False),
    default='5m',
    help='Intraday data interval (default: 5m)'
)
@click.option(
    '--days',
    type=int,
    default=5,
    help='Number of days of historical data (default: 5)'
)
@click.option(
    '--output',
    type=click.Choice(['rich', 'json'], case_sensitive=False),
    default='rich',
    help='Output format (default: rich)'
)
@click.option(
    '--news-api-key',
    type=str,
    default=None,
    help='NewsAPI key for sentiment analysis (optional)'
)
@click.option(
    '--verbose',
    is_flag=True,
    help='Enable verbose logging'
)
@click.version_option(version='1.0.0', prog_name='Stock Analyzer')
def analyze_stock(
    ticker: str,
    interval: str,
    days: int,
    output: str,
    news_api_key: Optional[str],
    verbose: bool
):
    """
    Analyze a stock for intraday swing trading opportunities.

    TICKER: Stock ticker symbol (e.g., AAPL, TSLA, MSFT)

    Examples:

        stock-analyzer AAPL

        stock-analyzer TSLA --interval 15m --days 7

        stock-analyzer MSFT --output json

        stock-analyzer NVDA --news-api-key YOUR_KEY
    """
    # Setup logging
    setup_logging(verbose)

    try:
        # Display header
        if output == 'rich':
            click.echo("\n" + "="*70)
            click.echo(f"  INTRADAY STOCK ANALYZER - {ticker.upper()}")
            click.echo("="*70 + "\n")

        # Create analyzer
        analyzer = StockAnalyzer(news_api_key=news_api_key or settings.news_api_key)

        # Perform analysis
        if output == 'rich':
            click.echo(f"Analyzing {ticker.upper()} with {interval} intervals...\n")

        result = analyzer.analyze(
            ticker=ticker,
            interval=interval,
            historical_days=days
        )

        if not result:
            click.echo(
                click.style(f"✗ Failed to analyze {ticker.upper()}", fg='red', bold=True),
                err=True
            )
            click.echo(
                "\nPossible reasons:\n"
                "  • Invalid ticker symbol\n"
                "  • No data available for this stock\n"
                "  • Network connectivity issues\n"
                "  • API rate limits reached",
                err=True
            )
            sys.exit(1)

        # Format and display output
        if output == 'json':
            formatter = JsonFormatter()
            json_output = formatter.format(result)
            click.echo(json_output)
        else:
            formatter = RichFormatter()
            formatter.format(result)

        # Exit with success
        sys.exit(0)

    except KeyboardInterrupt:
        click.echo("\n\nAnalysis interrupted by user.", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(
            click.style(f"\n✗ Error: {str(e)}", fg='red', bold=True),
            err=True
        )
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@click.group()
def cli():
    """Stock Analyzer - Intraday swing trade analysis tool."""
    pass


cli.add_command(analyze_stock, name='analyze')


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
