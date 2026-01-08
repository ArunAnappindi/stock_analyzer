# Stock Analyzer - Intraday Swing Trade Analysis

A comprehensive Python application for analyzing stocks and identifying intraday swing trading opportunities. This tool combines technical analysis, volume analysis, and sentiment analysis to provide actionable trade recommendations.

## Features

- **Technical Analysis**: EMA, VWAP, RSI, MACD, Support/Resistance
- **Volume Analysis**: Relative volume, volume spikes, price-volume confirmation
- **Sentiment Analysis**: News sentiment analysis with catalyst detection
- **Trade Recommendations**: Entry, target, and stop-loss prices with risk metrics
- **Beautiful CLI Output**: Rich console formatting with tables and colors
- **JSON Export**: Programmatic access to analysis results

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd stock-analyzer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Configure API keys:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

## Quick Start

Analyze a stock with default settings (5-minute intervals):
```bash
python main.py AAPL
```

## Usage Examples

### Basic Analysis
```bash
# Analyze Apple with default settings
python main.py AAPL

# Analyze Tesla with 15-minute intervals
python main.py TSLA --interval 15m

# Analyze Microsoft with 7 days of historical data
python main.py MSFT --days 7
```

### Advanced Usage
```bash
# Output in JSON format
python main.py NVDA --output json

# Enable verbose logging
python main.py GOOGL --verbose

# Specify NewsAPI key for sentiment analysis
python main.py AMD --news-api-key YOUR_API_KEY
```

## Configuration

The application can be configured via environment variables or a `.env` file:

```bash
# API Keys (optional but recommended)
NEWS_API_KEY=your_newsapi_key_here

# Analysis Settings
INTRADAY_INTERVAL=5m
HISTORICAL_DAYS=5
EMA_SHORT_PERIOD=20
EMA_LONG_PERIOD=50
RSI_PERIOD=14

# Trade Decision Thresholds
MIN_CONFIDENCE_SCORE=60
STRONG_BUY_THRESHOLD=75
MODERATE_BUY_THRESHOLD=60

# Risk Management
DEFAULT_RISK_REWARD_RATIO=2.0
DEFAULT_STOP_LOSS_PCT=1.5
DEFAULT_TARGET_PCT=3.0
MAX_POSITION_SIZE=100
```

## Output Interpretation

### Trade Signals

- **STRONG BUY**: High confidence (75%+) with strong technical and volume confirmation
- **MODERATE BUY**: Good confidence (60-75%) with decent alignment
- **WEAK BUY**: Lower confidence but still positive signals
- **HOLD**: Mixed signals, wait for better setup
- **NO TRADE**: Insufficient confidence or no clear direction
- **AVOID**: Bearish signals detected

### Trade Recommendation

When a BUY signal is generated, the output includes:

- **Entry Price**: Suggested buy price
- **Target Price**: Profit-taking level
- **Stop Loss**: Risk management exit point
- **Risk:Reward Ratio**: Expected reward per unit of risk
- **Max Quantity**: Recommended position size
- **Risk Level**: LOW, MEDIUM, HIGH, or VERY_HIGH

## Architecture

```
stock-analyzer/
├── config/           # Configuration and settings
├── src/
│   ├── data/        # Data providers (yfinance)
│   ├── models/      # Data models (Pydantic)
│   ├── analysis/    # Analysis modules
│   │   ├── technical/   # Technical indicators
│   │   ├── volume/      # Volume analysis
│   │   └── sentiment/   # Sentiment analysis
│   ├── output/      # Output formatters
│   ├── orchestrator.py  # Main orchestrator
│   └── cli.py       # CLI interface
├── main.py          # Entry point
└── requirements.txt
```

## Risk Disclaimer

**IMPORTANT**: This application is for educational and analytical purposes only. It does NOT provide financial advice.

- Trading involves substantial risk of loss
- Past performance does not guarantee future results
- Always do your own research
- Consult with a qualified financial advisor before making investment decisions
- Never trade with money you cannot afford to lose

## API Keys

### NewsAPI (Optional)
For sentiment analysis, you can obtain a free API key from [NewsAPI.org](https://newsapi.org/).

- Free tier: 100 requests/day
- Provides news headlines and articles
- Improves sentiment analysis accuracy

## Limitations

- **Data Source**: Uses Yahoo Finance (yfinance) which has rate limits
- **Intraday Data**: Limited to recent data (1m: 7 days, 5m/15m: 60 days)
- **Market Hours**: Real-time data only available during market hours
- **Sentiment**: Basic sentiment analysis; can be improved with paid APIs
- **No Guarantee**: Analysis does not guarantee profitable trades

## Troubleshooting

### Common Issues

**"Failed to analyze ticker"**
- Check if the ticker symbol is correct
- Verify internet connectivity
- Try a different interval or reduce historical days

**"No data available"**
- The ticker might not have intraday data
- Try a less granular interval (15m instead of 1m)
- Check if the market is open

**Rate Limiting**
- Yahoo Finance has rate limits
- Add delays between multiple analyses
- Consider using a paid data provider

### Debug Mode

Enable verbose logging to see detailed information:
```bash
python main.py AAPL --verbose
```

Check the log file:
```bash
cat stock_analyzer.log
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is provided as-is for educational purposes.

## Acknowledgments

- Technical indicators powered by [pandas-ta](https://github.com/twopirllc/pandas-ta)
- Market data from [yfinance](https://github.com/ranaroussi/yfinance)
- Sentiment analysis using [TextBlob](https://textblob.readthedocs.io/)
- CLI powered by [Click](https://click.palletsprojects.com/)
- Beautiful output using [Rich](https://rich.readthedocs.io/)
