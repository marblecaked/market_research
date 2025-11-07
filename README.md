# Stock Market Historical Data Research

Comprehensive tool for downloading and analyzing 30 years of historical stock market data including S&P 500 and Russell 3000 indices.

## Features

This project downloads the following data for stocks:

### Price Data (30 years)
- Open, High, Low, Close prices
- Adjusted Close prices
- Trading Volume
- Daily, Weekly, and Monthly data available

### Fundamental Metrics
- **Valuation Ratios**: P/E, P/B, P/S, PEG, Enterprise Value multiples
- **Market Data**: Market Cap, Enterprise Value, Beta
- **Profitability**: Profit Margin, Operating Margin, ROA, ROE
- **Earnings**: EPS (trailing & forward), Revenue, EBITDA, Net Income
- **Per-Share Metrics**: Book Value, Revenue Per Share, EPS
- **Dividends**: Dividend Rate, Yield, Payout Ratio

### Financial Statements (Annual & Quarterly)
- Income Statements
- Balance Sheets
- Cash Flow Statements

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd market_research
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start (Sample Mode)

Test with a small sample of stocks first (recommended):

```bash
python download_stock_data.py
# When prompted, enter a sample size (e.g., 10)
```

### Full Download

To download all S&P 500 stocks:

```bash
python download_stock_data.py
# When prompted, press Enter for full download
```

**Note**: Full download of 500+ stocks takes several hours and makes thousands of API calls.

## Output

All data is saved in the `./data/` directory:

```
data/
├── historical_prices.csv           # Price data for all stocks
├── current_fundamentals.csv        # Latest fundamental metrics
├── income_statement.csv            # Annual income statements
├── balance_sheet.csv               # Annual balance sheets
├── cash_flow.csv                   # Annual cash flow statements
├── quarterly_income.csv            # Quarterly income statements
├── quarterly_balance.csv           # Quarterly balance sheets
└── quarterly_cashflow.csv          # Quarterly cash flow statements
```

## Data Sources

### S&P 500
- Current ticker list: Wikipedia (updated regularly)
- Historical data: Yahoo Finance via yfinance library
- Data history: 30+ years for most stocks

### Russell 3000
The Russell 3000 ticker list is not freely available. Options:

1. **Purchase from data providers**: Bloomberg, FactSet, Refinitiv
2. **Use alternatives**: Download all US stocks and filter by market cap
3. **Academic sources**: CRSP, Compustat (requires institutional access)

## Data Quality Notes

### Survivorship Bias
The current script downloads data for **current** index constituents. This introduces survivorship bias (companies that failed or were removed from the index are not included).

For academic research, consider:
- Historical index constituent lists
- Survivorship bias-free datasets (SimFin, CRSP)
- Point-in-time data providers

### Data Limitations
- Free data is limited compared to premium sources
- Some metrics may be missing for certain stocks
- Historical fundamentals (30 years back) may be incomplete
- Yahoo Finance data quality varies by stock

## Advanced Usage

### Custom Date Range

Edit `download_stock_data.py` and modify:

```python
# For specific date range
start_date = '1995-01-01'
end_date = '2024-12-31'
```

### Custom Ticker List

Add your own ticker list:

```python
custom_tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
data = download_all_data(custom_tickers, start_date, end_date)
```

### Rate Limiting

The script includes rate limiting to avoid overwhelming Yahoo Finance servers. Adjust in the code:

```python
time.sleep(0.1)  # Sleep between requests (seconds)
```

## Alternative Data Sources

For more comprehensive data, consider these options:

### Free/Freemium APIs
1. **Alpha Vantage** - Free tier with rate limits
2. **SimFin** - Free fundamental data (20+ years)
3. **EODHD** - 20 API calls/day free
4. **Finnhub** - Free tier available

### Premium Sources
1. **Bloomberg Terminal** - Most comprehensive ($$$$)
2. **FactSet** - Institutional data provider ($$$)
3. **Refinitiv** - Historical data ($$)
4. **Quandl/Nasdaq Data Link** - Various datasets ($$)

### Academic Sources
1. **CRSP** - Stock prices (requires university access)
2. **Compustat** - Fundamentals (requires university access)
3. **WRDS** - Comprehensive database (requires institutional access)

## Troubleshooting

### Common Issues

**"No data for ticker"**
- Stock may not have 30 years of history
- Ticker may have changed or been delisted
- Yahoo Finance may not have data

**"Rate limit exceeded"**
- Increase sleep time between requests
- Run script during off-peak hours
- Consider premium API with higher limits

**"Connection timeout"**
- Check internet connection
- Yahoo Finance may be temporarily down
- Try again later

## Performance Tips

1. **Start with a sample**: Test with 10-20 stocks first
2. **Run overnight**: Full download takes several hours
3. **Save intermediate results**: Script saves data progressively
4. **Use caching**: yfinance caches some requests automatically

## Contributing

Suggestions for improvement:
- Add support for more exchanges (international stocks)
- Implement incremental updates (only download new data)
- Add data validation and cleaning
- Create analysis and visualization scripts

## Legal & Ethical Use

- This tool is for **personal research and educational purposes only**
- Yahoo Finance API is for personal use only
- Do not use for commercial purposes without proper licensing
- Respect rate limits and terms of service
- Be aware of data usage policies

## License

This project is provided as-is for educational and research purposes.

## Resources

- [yfinance Documentation](https://github.com/ranaroussi/yfinance)
- [Yahoo Finance](https://finance.yahoo.com/)
- [Pandas Documentation](https://pandas.pydata.org/)
- [SimFin](https://simfin.com/) - Alternative free data source

## Next Steps

After downloading data:
1. Data cleaning and validation
2. Calculate additional metrics (Sharpe ratio, etc.)
3. Time series analysis
4. Sector/industry comparisons
5. Backtesting trading strategies
6. Machine learning model development
