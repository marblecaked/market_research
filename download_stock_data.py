"""
Stock Market Historical Data Downloader

This script downloads comprehensive historical stock data including:
- Price data (Open, High, Low, Close, Volume)
- Market cap, P/B ratio, P/E ratio
- Earnings and profitability metrics
- Financial statements (Income Statement, Balance Sheet, Cash Flow)

Supports S&P 500 and other indices with 30+ years of historical data.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
from tqdm import tqdm
import json
import warnings
warnings.filterwarnings('ignore')


def get_sp500_tickers():
    """
    Get current S&P 500 ticker list from Wikipedia
    Returns: List of ticker symbols
    """
    print("Fetching S&P 500 ticker list...")

    try:
        # Use requests with user agent to avoid 403 errors
        import requests
        from io import StringIO

        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        tables = pd.read_html(StringIO(response.text))
        sp500_table = tables[0]
        tickers = sp500_table['Symbol'].tolist()

        # Clean up tickers (replace dots with hyphens for Yahoo Finance)
        tickers = [ticker.replace('.', '-') for ticker in tickers]

        print(f"Found {len(tickers)} S&P 500 tickers")
        return tickers

    except Exception as e:
        print(f"Error fetching from Wikipedia: {e}")
        print("Using fallback ticker list (sample of major S&P 500 stocks)...")

        # Fallback list of major S&P 500 companies
        fallback_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
            'JPM', 'JNJ', 'V', 'PG', 'UNH', 'MA', 'HD', 'CVX', 'MRK', 'ABBV',
            'PEP', 'KO', 'AVGO', 'COST', 'LLY', 'WMT', 'ADBE', 'MCD', 'CSCO',
            'ACN', 'TMO', 'DHR', 'ABT', 'VZ', 'NFLX', 'CRM', 'NKE', 'TXN',
            'ORCL', 'PM', 'DIS', 'INTC', 'BMY', 'AMD', 'NEE', 'CMCSA', 'UPS',
            'HON', 'RTX', 'QCOM', 'INTU', 'AMGN', 'LOW', 'IBM', 'BA', 'CAT',
            'SPGI', 'PFE', 'DE', 'GE', 'GS', 'AXP', 'SBUX', 'BLK', 'ISRG',
            'MMM', 'CVS', 'MDLZ', 'AMT', 'ADP', 'NOW', 'GILD', 'SCHW', 'ZTS',
            'TJX', 'MO', 'LMT', 'SYK', 'BKNG', 'PLD', 'AMAT', 'ADI', 'C', 'CB',
            'VRTX', 'CI', 'TMUS', 'BDX', 'SHW', 'SO', 'EL', 'DUK', 'CL', 'NOC'
        ]

        print(f"Using {len(fallback_tickers)} major S&P 500 tickers as fallback")
        return fallback_tickers


def get_russell3000_tickers():
    """
    Get Russell 3000 tickers (note: this is harder to get for free)
    Returns: List of ticker symbols
    """
    print("Note: Russell 3000 ticker list is not freely available.")
    print("Consider using a broader market dataset or purchasing from a data provider.")
    return []


def download_price_data(ticker, start_date, end_date, progress_bar=None):
    """
    Download historical price data for a single ticker

    Args:
        ticker: Stock ticker symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        progress_bar: Optional tqdm progress bar

    Returns:
        DataFrame with price data or None if failed
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)

        if df.empty:
            if progress_bar:
                progress_bar.write(f"No data for {ticker}")
            return None

        df['Ticker'] = ticker
        return df

    except Exception as e:
        if progress_bar:
            progress_bar.write(f"Error downloading {ticker}: {str(e)}")
        return None


def download_fundamentals(ticker, progress_bar=None):
    """
    Download fundamental data for a single ticker

    Args:
        ticker: Stock ticker symbol
        progress_bar: Optional tqdm progress bar

    Returns:
        Dictionary with fundamental data or None if failed
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Extract key fundamental metrics
        fundamentals = {
            'ticker': ticker,
            'market_cap': info.get('marketCap'),
            'enterprise_value': info.get('enterpriseValue'),
            'trailing_pe': info.get('trailingPE'),
            'forward_pe': info.get('forwardPE'),
            'peg_ratio': info.get('pegRatio'),
            'price_to_book': info.get('priceToBook'),
            'price_to_sales': info.get('priceToSalesTrailing12Months'),
            'enterprise_to_revenue': info.get('enterpriseToRevenue'),
            'enterprise_to_ebitda': info.get('enterpriseToEbitda'),
            'profit_margin': info.get('profitMargins'),
            'operating_margin': info.get('operatingMargins'),
            'return_on_assets': info.get('returnOnAssets'),
            'return_on_equity': info.get('returnOnEquity'),
            'revenue': info.get('totalRevenue'),
            'revenue_per_share': info.get('revenuePerShare'),
            'gross_profit': info.get('grossProfits'),
            'ebitda': info.get('ebitda'),
            'net_income': info.get('netIncomeToCommon'),
            'eps_trailing': info.get('trailingEps'),
            'eps_forward': info.get('forwardEps'),
            'book_value': info.get('bookValue'),
            'shares_outstanding': info.get('sharesOutstanding'),
            'dividend_rate': info.get('dividendRate'),
            'dividend_yield': info.get('dividendYield'),
            'payout_ratio': info.get('payoutRatio'),
            'beta': info.get('beta'),
            'sector': info.get('sector'),
            'industry': info.get('industry'),
            'current_price': info.get('currentPrice'),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
        }

        return fundamentals

    except Exception as e:
        if progress_bar:
            progress_bar.write(f"Error downloading fundamentals for {ticker}: {str(e)}")
        return None


def download_financial_statements(ticker, progress_bar=None):
    """
    Download financial statements (Income Statement, Balance Sheet, Cash Flow)

    Args:
        ticker: Stock ticker symbol
        progress_bar: Optional tqdm progress bar

    Returns:
        Dictionary with DataFrames for each statement or None if failed
    """
    try:
        stock = yf.Ticker(ticker)

        statements = {
            'income_statement': stock.financials,
            'balance_sheet': stock.balance_sheet,
            'cash_flow': stock.cashflow,
            'quarterly_income': stock.quarterly_financials,
            'quarterly_balance': stock.quarterly_balance_sheet,
            'quarterly_cashflow': stock.quarterly_cashflow,
        }

        # Add ticker to each statement
        for key, df in statements.items():
            if not df.empty:
                df['Ticker'] = ticker

        return statements

    except Exception as e:
        if progress_bar:
            progress_bar.write(f"Error downloading financial statements for {ticker}: {str(e)}")
        return None


def save_data(data, filename, data_type='csv'):
    """Save data to file"""
    os.makedirs('data', exist_ok=True)
    filepath = os.path.join('data', filename)

    if data_type == 'csv':
        data.to_csv(filepath)
    elif data_type == 'excel':
        data.to_excel(filepath)
    elif data_type == 'json':
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    print(f"Saved to {filepath}")


def download_all_data(tickers, start_date, end_date, sample_size=None):
    """
    Download all data for a list of tickers

    Args:
        tickers: List of ticker symbols
        start_date: Start date for price data (YYYY-MM-DD)
        end_date: End date for price data (YYYY-MM-DD)
        sample_size: Optional - only download first N tickers (for testing)
    """
    if sample_size:
        tickers = tickers[:sample_size]
        print(f"\nSample mode: Downloading data for first {sample_size} tickers")

    print(f"\nDownloading data for {len(tickers)} tickers from {start_date} to {end_date}")
    print("="*80)

    # Storage for all data
    all_price_data = []
    all_fundamentals = []
    all_statements = {
        'income_statement': [],
        'balance_sheet': [],
        'cash_flow': [],
        'quarterly_income': [],
        'quarterly_balance': [],
        'quarterly_cashflow': [],
    }

    # Download data with progress bar
    print("\n1. Downloading Price Data...")
    for ticker in tqdm(tickers, desc="Price Data"):
        df = download_price_data(ticker, start_date, end_date, tqdm)
        if df is not None:
            all_price_data.append(df)
        time.sleep(0.1)  # Rate limiting

    print("\n2. Downloading Fundamental Data...")
    for ticker in tqdm(tickers, desc="Fundamentals"):
        fundamentals = download_fundamentals(ticker, tqdm)
        if fundamentals is not None:
            all_fundamentals.append(fundamentals)
        time.sleep(0.1)  # Rate limiting

    print("\n3. Downloading Financial Statements...")
    for ticker in tqdm(tickers, desc="Statements"):
        statements = download_financial_statements(ticker, tqdm)
        if statements is not None:
            for key, df in statements.items():
                if df is not None and not df.empty:
                    all_statements[key].append(df)
        time.sleep(0.2)  # Rate limiting

    # Combine and save data
    print("\n4. Combining and Saving Data...")

    # Save price data
    if all_price_data:
        price_df = pd.concat(all_price_data, ignore_index=False)
        price_df.reset_index(inplace=True)
        price_df.rename(columns={'index': 'Date'}, inplace=True)
        save_data(price_df, 'historical_prices.csv')
        print(f"Price data shape: {price_df.shape}")

    # Save fundamentals
    if all_fundamentals:
        fundamentals_df = pd.DataFrame(all_fundamentals)
        save_data(fundamentals_df, 'current_fundamentals.csv')
        print(f"Fundamentals data shape: {fundamentals_df.shape}")

    # Save financial statements
    for statement_type, dataframes in all_statements.items():
        if dataframes:
            try:
                combined = pd.concat(dataframes, axis=1)
                save_data(combined, f'{statement_type}.csv')
                print(f"{statement_type} shape: {combined.shape}")
            except Exception as e:
                print(f"Error saving {statement_type}: {str(e)}")

    print("\n" + "="*80)
    print("Download complete!")
    print(f"Data saved in './data/' directory")
    print(f"- {len(all_price_data)} tickers with price data")
    print(f"- {len(all_fundamentals)} tickers with fundamental data")

    return {
        'price_data': all_price_data,
        'fundamentals': all_fundamentals,
        'statements': all_statements
    }


def main():
    """Main execution function"""
    print("="*80)
    print("STOCK MARKET DATA DOWNLOADER")
    print("="*80)

    # Configuration
    # Download 30 years of data (adjust if needed)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30*365)).strftime('%Y-%m-%d')

    print(f"\nDate Range: {start_date} to {end_date}")

    # Get tickers
    print("\nFetching ticker lists...")
    sp500_tickers = get_sp500_tickers()

    # Option to test with a small sample first
    print("\n" + "="*80)
    print("RECOMMENDATION: Start with a sample to test (e.g., 10 stocks)")
    print("Full download of 500+ stocks will take several hours")
    print("="*80)

    sample = input("\nEnter sample size (or press Enter for all stocks): ").strip()
    sample_size = int(sample) if sample.isdigit() else None

    # Download data
    data = download_all_data(sp500_tickers, start_date, end_date, sample_size)

    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("1. Review the data in the './data/' directory")
    print("2. Run analysis on the downloaded data")
    print("3. For Russell 3000, you'll need a data provider or scrape from other sources")
    print("="*80)


if __name__ == "__main__":
    main()
