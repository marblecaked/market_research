"""
Stock Price Trend Analysis

This script analyzes historical stock price data to identify upward trends.

Metrics calculated:
- Total return (%) over various periods
- Compound Annual Growth Rate (CAGR)
- Recent momentum (6mo, 1yr, 3yr, 5yr)
- Trend consistency (% of positive days)
- Volatility (standard deviation of returns)
- Maximum drawdown
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json


def load_price_data(filepath='data/historical_prices.csv'):
    """Load historical price data"""
    print(f"Loading price data from {filepath}...")
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(['Ticker', 'Date'])
    print(f"Loaded {len(df)} price records for {df['Ticker'].nunique()} tickers")
    return df


def calculate_returns(df):
    """Calculate returns for different time periods"""
    results = []

    for ticker in df['Ticker'].unique():
        ticker_df = df[df['Ticker'] == ticker].copy()
        ticker_df = ticker_df.sort_values('Date')

        if len(ticker_df) < 30:  # Need at least 30 days of data
            continue

        # Calculate daily returns
        ticker_df['Daily_Return'] = ticker_df['Close'].pct_change()

        # Get key dates
        latest_date = ticker_df['Date'].max()
        earliest_date = ticker_df['Date'].min()

        latest_price = ticker_df.iloc[-1]['Close']
        earliest_price = ticker_df.iloc[0]['Close']

        # Calculate total return
        total_return = ((latest_price - earliest_price) / earliest_price) * 100

        # Calculate years of data
        years = (latest_date - earliest_date).days / 365.25

        # Calculate CAGR (Compound Annual Growth Rate)
        if years > 0:
            cagr = (((latest_price / earliest_price) ** (1 / years)) - 1) * 100
        else:
            cagr = 0

        # Calculate returns for different periods
        def get_return_for_period(days):
            cutoff_date = latest_date - timedelta(days=days)
            period_df = ticker_df[ticker_df['Date'] >= cutoff_date]
            if len(period_df) < 2:
                return None
            start_price = period_df.iloc[0]['Close']
            end_price = period_df.iloc[-1]['Close']
            return ((end_price - start_price) / start_price) * 100

        returns_6mo = get_return_for_period(180)
        returns_1yr = get_return_for_period(365)
        returns_3yr = get_return_for_period(365 * 3)
        returns_5yr = get_return_for_period(365 * 5)
        returns_10yr = get_return_for_period(365 * 10)

        # Calculate trend consistency (% of positive days)
        positive_days = (ticker_df['Daily_Return'] > 0).sum()
        total_days = ticker_df['Daily_Return'].notna().sum()
        positive_pct = (positive_days / total_days * 100) if total_days > 0 else 0

        # Calculate volatility (annualized standard deviation)
        daily_std = ticker_df['Daily_Return'].std()
        annual_volatility = daily_std * np.sqrt(252) * 100  # 252 trading days

        # Calculate maximum drawdown
        ticker_df['Cumulative_Max'] = ticker_df['Close'].cummax()
        ticker_df['Drawdown'] = (ticker_df['Close'] - ticker_df['Cumulative_Max']) / ticker_df['Cumulative_Max'] * 100
        max_drawdown = ticker_df['Drawdown'].min()

        # Calculate Sharpe-like ratio (return / volatility)
        risk_adjusted_return = cagr / annual_volatility if annual_volatility > 0 else 0

        # Recent momentum score (weighted recent performance)
        momentum_score = 0
        if returns_6mo is not None:
            momentum_score += returns_6mo * 0.5
        if returns_1yr is not None:
            momentum_score += returns_1yr * 0.3
        if returns_3yr is not None:
            momentum_score += (returns_3yr / 3) * 0.2

        results.append({
            'Ticker': ticker,
            'Latest_Price': latest_price,
            'Total_Return_%': round(total_return, 2),
            'CAGR_%': round(cagr, 2),
            'Years_of_Data': round(years, 1),
            'Return_6mo_%': round(returns_6mo, 2) if returns_6mo is not None else None,
            'Return_1yr_%': round(returns_1yr, 2) if returns_1yr is not None else None,
            'Return_3yr_%': round(returns_3yr, 2) if returns_3yr is not None else None,
            'Return_5yr_%': round(returns_5yr, 2) if returns_5yr is not None else None,
            'Return_10yr_%': round(returns_10yr, 2) if returns_10yr is not None else None,
            'Positive_Days_%': round(positive_pct, 2),
            'Annual_Volatility_%': round(annual_volatility, 2),
            'Max_Drawdown_%': round(max_drawdown, 2),
            'Risk_Adjusted_Return': round(risk_adjusted_return, 3),
            'Momentum_Score': round(momentum_score, 2),
            'Start_Date': earliest_date.strftime('%Y-%m-%d'),
            'End_Date': latest_date.strftime('%Y-%m-%d'),
        })

    return pd.DataFrame(results)


def identify_uptrends(analysis_df):
    """Identify stocks with strong upward trends"""

    print("\n" + "="*80)
    print("UPWARD TREND ANALYSIS")
    print("="*80)

    # Define uptrend criteria
    uptrend_stocks = analysis_df[
        (analysis_df['CAGR_%'] > 0) &  # Positive long-term growth
        (analysis_df['Total_Return_%'] > 0)  # Positive total return
    ].copy()

    # Sort by different metrics
    print(f"\n{len(uptrend_stocks)} out of {len(analysis_df)} stocks have positive upward trends")

    # Top performers by CAGR
    print("\n" + "-"*80)
    print("TOP 10 STOCKS BY COMPOUND ANNUAL GROWTH RATE (CAGR)")
    print("-"*80)
    top_cagr = uptrend_stocks.nlargest(10, 'CAGR_%')
    print(top_cagr[['Ticker', 'CAGR_%', 'Total_Return_%', 'Years_of_Data', 'Latest_Price']].to_string(index=False))

    # Top performers by total return
    print("\n" + "-"*80)
    print("TOP 10 STOCKS BY TOTAL RETURN")
    print("-"*80)
    top_total = uptrend_stocks.nlargest(10, 'Total_Return_%')
    print(top_total[['Ticker', 'Total_Return_%', 'CAGR_%', 'Years_of_Data', 'Latest_Price']].to_string(index=False))

    # Top recent performers (momentum)
    print("\n" + "-"*80)
    print("TOP 10 STOCKS BY RECENT MOMENTUM (6mo + 1yr weighted)")
    print("-"*80)
    momentum_stocks = uptrend_stocks[uptrend_stocks['Momentum_Score'].notna()]
    if len(momentum_stocks) > 0:
        top_momentum = momentum_stocks.nlargest(10, 'Momentum_Score')
        print(top_momentum[['Ticker', 'Momentum_Score', 'Return_6mo_%', 'Return_1yr_%', 'CAGR_%']].to_string(index=False))

    # Best risk-adjusted returns
    print("\n" + "-"*80)
    print("TOP 10 STOCKS BY RISK-ADJUSTED RETURN (CAGR / Volatility)")
    print("-"*80)
    risk_adj_stocks = uptrend_stocks[uptrend_stocks['Risk_Adjusted_Return'] > 0]
    if len(risk_adj_stocks) > 0:
        top_risk_adj = risk_adj_stocks.nlargest(10, 'Risk_Adjusted_Return')
        print(top_risk_adj[['Ticker', 'Risk_Adjusted_Return', 'CAGR_%', 'Annual_Volatility_%', 'Max_Drawdown_%']].to_string(index=False))

    # Consistent performers (high % of positive days)
    print("\n" + "-"*80)
    print("TOP 10 MOST CONSISTENT STOCKS (% Positive Days)")
    print("-"*80)
    top_consistent = uptrend_stocks.nlargest(10, 'Positive_Days_%')
    print(top_consistent[['Ticker', 'Positive_Days_%', 'CAGR_%', 'Annual_Volatility_%', 'Total_Return_%']].to_string(index=False))

    return uptrend_stocks


def generate_summary_stats(analysis_df):
    """Generate summary statistics"""
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)

    stats = {
        'Total Stocks Analyzed': len(analysis_df),
        'Stocks with Positive CAGR': len(analysis_df[analysis_df['CAGR_%'] > 0]),
        'Stocks with Negative CAGR': len(analysis_df[analysis_df['CAGR_%'] < 0]),
        'Average CAGR (%)': analysis_df['CAGR_%'].mean(),
        'Median CAGR (%)': analysis_df['CAGR_%'].median(),
        'Average Total Return (%)': analysis_df['Total_Return_%'].mean(),
        'Average Volatility (%)': analysis_df['Annual_Volatility_%'].mean(),
        'Average Years of Data': analysis_df['Years_of_Data'].mean(),
    }

    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")

    # Show distribution
    print("\n" + "-"*80)
    print("CAGR DISTRIBUTION")
    print("-"*80)

    bins = [-100, -10, 0, 10, 20, 50, 100, 1000]
    labels = ['< -10%', '-10% to 0%', '0% to 10%', '10% to 20%', '20% to 50%', '50% to 100%', '> 100%']
    analysis_df['CAGR_Bucket'] = pd.cut(analysis_df['CAGR_%'], bins=bins, labels=labels)

    distribution = analysis_df['CAGR_Bucket'].value_counts().sort_index()
    for bucket, count in distribution.items():
        pct = (count / len(analysis_df)) * 100
        print(f"{bucket}: {count} stocks ({pct:.1f}%)")


def time_period_analysis(analysis_df):
    """Analyze performance across different time periods"""
    print("\n" + "="*80)
    print("TIME PERIOD PERFORMANCE COMPARISON")
    print("="*80)

    periods = ['Return_6mo_%', 'Return_1yr_%', 'Return_3yr_%', 'Return_5yr_%', 'Return_10yr_%']
    period_names = ['6 Months', '1 Year', '3 Years', '5 Years', '10 Years']

    for period, name in zip(periods, period_names):
        valid_data = analysis_df[analysis_df[period].notna()]
        if len(valid_data) > 0:
            avg_return = valid_data[period].mean()
            median_return = valid_data[period].median()
            positive_count = len(valid_data[valid_data[period] > 0])
            total_count = len(valid_data)
            positive_pct = (positive_count / total_count) * 100

            print(f"\n{name} ({total_count} stocks with data):")
            print(f"  Average Return: {avg_return:.2f}%")
            print(f"  Median Return: {median_return:.2f}%")
            print(f"  Stocks with Positive Returns: {positive_count}/{total_count} ({positive_pct:.1f}%)")


def save_results(analysis_df, uptrend_stocks, output_dir='data'):
    """Save analysis results to CSV"""
    os.makedirs(output_dir, exist_ok=True)

    # Save full analysis
    analysis_path = os.path.join(output_dir, 'price_trend_analysis.csv')
    analysis_df.to_csv(analysis_path, index=False)
    print(f"\nFull analysis saved to: {analysis_path}")

    # Save uptrend stocks only
    uptrend_path = os.path.join(output_dir, 'uptrend_stocks.csv')
    uptrend_stocks.to_csv(uptrend_path, index=False)
    print(f"Uptrend stocks saved to: {uptrend_path}")

    # Save summary as JSON
    summary = {
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_stocks': len(analysis_df),
        'uptrend_stocks': len(uptrend_stocks),
        'average_cagr': float(analysis_df['CAGR_%'].mean()),
        'median_cagr': float(analysis_df['CAGR_%'].median()),
        'top_performers': uptrend_stocks.nlargest(10, 'CAGR_%')[['Ticker', 'CAGR_%', 'Total_Return_%']].to_dict('records')
    }

    summary_path = os.path.join(output_dir, 'trend_analysis_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Summary saved to: {summary_path}")


def main():
    """Main execution function"""
    print("="*80)
    print("STOCK PRICE TREND ANALYSIS")
    print("="*80)

    # Check if data exists
    if not os.path.exists('data/historical_prices.csv'):
        print("\nERROR: No price data found!")
        print("Please run download_stock_data.py first to download historical data.")
        return

    # Load data
    price_df = load_price_data()

    # Calculate returns and metrics
    print("\nCalculating returns and trend metrics...")
    analysis_df = calculate_returns(price_df)

    if len(analysis_df) == 0:
        print("\nERROR: No data to analyze!")
        return

    # Identify uptrends
    uptrend_stocks = identify_uptrends(analysis_df)

    # Generate summary statistics
    generate_summary_stats(analysis_df)

    # Time period analysis
    time_period_analysis(analysis_df)

    # Save results
    save_results(analysis_df, uptrend_stocks)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print("\nKey files generated:")
    print("- data/price_trend_analysis.csv (all stocks)")
    print("- data/uptrend_stocks.csv (only positive trends)")
    print("- data/trend_analysis_summary.json (summary statistics)")


if __name__ == "__main__":
    main()
