# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Stock Analyzer is a Python application for analyzing stocks and identifying intraday swing trading opportunities. It combines technical analysis, volume analysis, and sentiment analysis to provide actionable trade recommendations with entry, target, and stop-loss prices.

## Commands

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys (optional)
cp .env.example .env
# Edit .env and add NEWS_API_KEY for sentiment analysis
```

### Running the Application
```bash
# Basic analysis (5-minute intervals, 5 days of data)
python main.py AAPL

# Custom interval (1m, 5m, 15m, 30m)
python main.py TSLA --interval 15m

# Custom historical data period
python main.py MSFT --days 7

# JSON output format
python main.py NVDA --output json

# Enable verbose logging
python main.py GOOGL --verbose

# With NewsAPI key for sentiment analysis
python main.py AMD --news-api-key YOUR_API_KEY
```

### Testing
There are currently no automated tests in the repository. Test directories exist at `tests/unit/` and `tests/integration/` but contain only `__init__.py` files.

## Architecture

### Data Flow Pipeline

The application follows a multi-stage pipeline orchestrated by `StockAnalyzer` (src/orchestrator.py):

1. **Data Fetching** (`DataFetcher`) → Retrieves market data via provider pattern
2. **Technical Analysis** (`TechnicalAnalyzer`) → Calculates indicators and identifies patterns
3. **Volume Analysis** (`VolumeAnalyzer`) → Analyzes volume patterns and price-volume relationships
4. **Sentiment Analysis** (`SentimentAnalyzer`) → Fetches and analyzes news sentiment
5. **Decision Engine** (`DecisionEngine`) → Synthesizes all analyses into trade recommendation
6. **Output Formatting** → Presents results in rich console or JSON format

### Core Components

**Orchestrator** (`src/orchestrator.py`):
- `StockAnalyzer` coordinates all analysis components
- Initializes analyzers with optional configuration
- Generates warnings based on market conditions, volume, and technical signals
- Returns complete `AnalysisResult` with all analysis components

**Data Layer** (`src/data/`):
- **Provider Pattern**: `DataProvider` abstract base class defines interface
  - `YFinanceProvider` is the current implementation (uses yfinance library)
  - Easy to add new providers (Alpha Vantage, IEX Cloud, etc.)
- `DataFetcher` combines stock info, intraday data, and historical data
- Returns `MarketData` model with current price, volume, and OHLCV data

**Analysis Modules** (`src/analysis/`):
- **Technical** (`technical/`): EMA, VWAP, RSI, MACD, support/resistance
  - `IndicatorCalculator` (in `indicators.py`) performs raw calculations
  - `TechnicalAnalyzer` (in `analyzer.py`) interprets indicators and generates signals
- **Volume** (`volume/`): Relative volume, volume spikes, price-volume confirmation
- **Sentiment** (`sentiment/`): News fetching and sentiment scoring via TextBlob
  - Can integrate NewsAPI for better coverage

**Decision Engine** (`src/analysis/decision_engine.py`):
- Calculates weighted confidence score (50% technical, 30% volume, 20% sentiment)
- Maps confidence + signal strength → Trade Signal (STRONG_BUY, MODERATE_BUY, etc.)
- Calculates entry/target/stop-loss based on support/resistance or percentage rules
- Ensures minimum risk:reward ratio (default 2:0)
- Generates human-readable reasoning and key factors

**Models** (`src/models/`):
- Pydantic models ensure type safety throughout the pipeline
- `MarketData`: Contains stock info, OHLCV data, current price
- `TechnicalAnalysis`, `VolumeAnalysis`, `SentimentAnalysis`: Analysis outputs
- `TradeRecommendation`: Final recommendation with price levels
- `AnalysisResult`: Complete result container with all components

**Configuration** (`config/settings.py`):
- `Settings` class uses pydantic-settings to load from environment or .env
- All thresholds configurable: EMA periods, RSI period, confidence thresholds, risk management
- Modify thresholds via environment variables or .env file

**Output Formatters** (`src/output/formatters/`):
- `RichFormatter`: Beautiful CLI output with tables and colors
- `JsonFormatter`: Machine-readable JSON output

### Key Design Patterns

**Provider Pattern**: Data providers implement `DataProvider` interface. To add a new data source:
1. Create new provider class in `src/data/providers/` inheriting from `DataProvider`
2. Implement `get_stock_info()`, `get_intraday_data()`, `is_market_open()`
3. Pass provider instance to `DataFetcher`

**Analyzer Pattern**: Each analysis module (technical, volume, sentiment) follows same interface:
- Takes market data as input
- Returns analysis object with confidence score and summary
- Independent and can be run in parallel

**Weighted Scoring**: The decision engine combines multiple signals using weighted confidence scores rather than simple voting, allowing nuanced trade decisions.

**Risk Management**: Trade recommendations always include stop-loss and target prices with minimum risk:reward ratio enforcement.

## Configuration Defaults

See `.env.example` for all configurable parameters. Key defaults:
- Intraday interval: 5m
- Historical days: 5
- EMA periods: 20 (short), 50 (long)
- RSI period: 14
- Min confidence: 60%
- Strong buy threshold: 75%
- Risk:reward ratio: 2.0
- Stop loss: 1.5%
- Target: 3.0%
- Max position size: 100 shares

## Data Sources

**Yahoo Finance (yfinance)**:
- Free, no API key required
- Intraday data limited by granularity (1m: 7 days, 5m/15m: 60 days)
- May have rate limits
- Real-time data only during market hours

**NewsAPI (optional)**:
- Free tier: 100 requests/day
- Improves sentiment analysis
- Set `NEWS_API_KEY` environment variable

## Important Notes

**Adding New Indicators**:
1. Add calculation method to `IndicatorCalculator` in `src/analysis/technical/indicators.py`
2. Update `TechnicalIndicators` model in `src/models/analysis.py`
3. Call calculator in `TechnicalAnalyzer.analyze()` in `src/analysis/technical/analyzer.py`
4. Update decision logic in `DecisionEngine` if needed

**Trade Signal Logic** (`DecisionEngine._determine_signal()`):
- Counts bullish/bearish signals from all analyses
- Technical signals weighted higher (3 points) than sentiment (1 point)
- Requires minimum confidence threshold (60%) for any BUY signal
- Checks bullish ratio (bullish / total signals) for signal strength

**Price Level Calculation** (`DecisionEngine._calculate_price_levels()`):
- Prefers technical levels (support/resistance) over percentage-based
- Entry slightly above current price unless already breaking out
- Stop loss below support or 1.5% below entry
- Target near resistance or enforces 2:1 risk:reward minimum

**Logging**:
- Logs written to `stock_analyzer.log` in working directory
- Use `--verbose` flag for console logging
- Each component logs at INFO level by default

**No Tests**: Repository has empty test directories. When adding tests:
- Use `pytest` (add to requirements.txt)
- Unit tests: `tests/unit/` - test individual components
- Integration tests: `tests/integration/` - test full pipeline
