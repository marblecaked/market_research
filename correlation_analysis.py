"""
Correlation Analysis: Fundamentals vs Price Growth

This script analyzes which fundamental metrics correlate most strongly with
stock price growth and identifies strategies for enhanced returns.
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime


def load_data():
    """Load price trend analysis and fundamental data"""
    print("Loading data...")

    # Load price trend analysis
    trends_df = pd.read_csv('data/price_trend_analysis.csv')
    print(f"Loaded {len(trends_df)} stocks from trend analysis")

    # Load fundamentals
    fundamentals_df = pd.read_csv('data/current_fundamentals.csv')
    print(f"Loaded {len(fundamentals_df)} stocks with fundamental data")

    # Merge datasets
    merged_df = pd.merge(trends_df, fundamentals_df,
                         left_on='Ticker', right_on='ticker',
                         how='inner')
    print(f"Merged dataset: {len(merged_df)} stocks with both price and fundamental data")

    return merged_df


def calculate_correlations(df):
    """Calculate correlations between fundamentals and returns"""
    print("\n" + "="*80)
    print("CORRELATION ANALYSIS: FUNDAMENTALS vs RETURNS")
    print("="*80)

    # Select return metrics
    return_metrics = ['CAGR_%', 'Total_Return_%', 'Return_1yr_%',
                      'Return_3yr_%', 'Return_5yr_%', 'Return_10yr_%',
                      'Risk_Adjusted_Return', 'Momentum_Score']

    # Select fundamental metrics (excluding non-numeric or identifiers)
    fundamental_metrics = [
        'trailing_pe', 'forward_pe', 'peg_ratio', 'price_to_book',
        'price_to_sales', 'enterprise_to_revenue', 'enterprise_to_ebitda',
        'profit_margin', 'operating_margin', 'return_on_assets',
        'return_on_equity', 'revenue_per_share', 'eps_trailing',
        'eps_forward', 'dividend_yield', 'payout_ratio', 'beta',
        'market_cap', 'enterprise_value'
    ]

    # Calculate correlations for each return metric
    all_correlations = {}

    for return_metric in return_metrics:
        print(f"\n{'-'*80}")
        print(f"Correlations with {return_metric}")
        print(f"{'-'*80}")

        correlations = []
        for fund_metric in fundamental_metrics:
            # Only calculate if both columns exist and have enough valid data
            if return_metric in df.columns and fund_metric in df.columns:
                valid_data = df[[return_metric, fund_metric]].dropna()
                if len(valid_data) >= 10:  # Need at least 10 data points
                    corr = valid_data[return_metric].corr(valid_data[fund_metric])
                    correlations.append({
                        'Metric': fund_metric,
                        'Correlation': corr,
                        'Abs_Correlation': abs(corr),
                        'Sample_Size': len(valid_data)
                    })

        if correlations:
            corr_df = pd.DataFrame(correlations)
            corr_df = corr_df.sort_values('Abs_Correlation', ascending=False)
            all_correlations[return_metric] = corr_df

            # Print top 10 correlations
            print("\nTop 10 Strongest Correlations:")
            print(corr_df.head(10)[['Metric', 'Correlation', 'Sample_Size']].to_string(index=False))

    return all_correlations


def analyze_by_sector(df):
    """Analyze performance by sector"""
    print("\n" + "="*80)
    print("SECTOR PERFORMANCE ANALYSIS")
    print("="*80)

    if 'sector' not in df.columns:
        print("No sector data available")
        return None

    # Group by sector
    sector_stats = df.groupby('sector').agg({
        'CAGR_%': ['mean', 'median', 'count'],
        'Total_Return_%': ['mean', 'median'],
        'Return_1yr_%': ['mean', 'median'],
        'Return_5yr_%': ['mean', 'median'],
        'Annual_Volatility_%': ['mean', 'median'],
        'Risk_Adjusted_Return': ['mean', 'median'],
        'profit_margin': ['mean', 'median'],
        'return_on_equity': ['mean', 'median']
    }).round(2)

    # Flatten column names
    sector_stats.columns = ['_'.join(col).strip() for col in sector_stats.columns.values]
    sector_stats = sector_stats.sort_values('CAGR_%_mean', ascending=False)

    print("\nSector Rankings by Average CAGR:")
    print(sector_stats[['CAGR_%_mean', 'CAGR_%_median', 'CAGR_%_count']].to_string())

    print("\nSector Rankings by Risk-Adjusted Returns:")
    print(sector_stats[['Risk_Adjusted_Return_mean', 'Annual_Volatility_%_mean']].to_string())

    return sector_stats


def identify_winning_characteristics(df):
    """Identify characteristics of top performers"""
    print("\n" + "="*80)
    print("CHARACTERISTICS OF TOP PERFORMERS")
    print("="*80)

    # Define top performers (top quartile by CAGR)
    cagr_threshold = df['CAGR_%'].quantile(0.75)
    top_performers = df[df['CAGR_%'] >= cagr_threshold]
    bottom_performers = df[df['CAGR_%'] <= df['CAGR_%'].quantile(0.25)]

    print(f"\nTop Quartile (CAGR >= {cagr_threshold:.2f}%): {len(top_performers)} stocks")
    print(f"Bottom Quartile: {len(bottom_performers)} stocks")

    # Compare metrics between top and bottom performers
    metrics_to_compare = [
        'profit_margin', 'operating_margin', 'return_on_equity',
        'return_on_assets', 'trailing_pe', 'price_to_book',
        'peg_ratio', 'beta', 'Annual_Volatility_%'
    ]

    print("\n" + "-"*80)
    print("Average Metrics: Top Performers vs Bottom Performers")
    print("-"*80)
    print(f"{'Metric':<25} {'Top Quartile':>15} {'Bottom Quartile':>18} {'Difference':>15}")
    print("-"*80)

    for metric in metrics_to_compare:
        if metric in df.columns:
            top_mean = top_performers[metric].mean()
            bottom_mean = bottom_performers[metric].mean()
            diff = top_mean - bottom_mean

            if pd.notna(top_mean) and pd.notna(bottom_mean):
                print(f"{metric:<25} {top_mean:>15.2f} {bottom_mean:>18.2f} {diff:>15.2f}")


def find_value_opportunities(df):
    """Find potential value opportunities"""
    print("\n" + "="*80)
    print("POTENTIAL VALUE OPPORTUNITIES")
    print("="*80)
    print("Stocks with strong fundamentals but recent underperformance")
    print("-"*80)

    # Criteria: Strong long-term CAGR but negative recent returns
    opportunities = df[
        (df['CAGR_%'] > 10) &  # Good long-term growth
        (df['Return_1yr_%'] < 0) &  # Down in last year
        (df['profit_margin'] > 0.1)  # Profitable
    ].copy()

    if len(opportunities) > 0:
        opportunities = opportunities.sort_values('CAGR_%', ascending=False)
        print(opportunities[['Ticker', 'sector', 'CAGR_%', 'Return_1yr_%',
                           'profit_margin', 'return_on_equity', 'trailing_pe']].to_string(index=False))
    else:
        print("No stocks meeting criteria in current dataset")

    return opportunities


def find_momentum_plays(df):
    """Find high momentum stocks"""
    print("\n" + "="*80)
    print("HIGH MOMENTUM OPPORTUNITIES")
    print("="*80)
    print("Stocks with strong recent and long-term momentum")
    print("-"*80)

    # Criteria: High momentum score and strong CAGR
    momentum = df[
        (df['Momentum_Score'] > 20) &  # Strong recent momentum
        (df['CAGR_%'] > 15) &  # Strong long-term growth
        (df['Return_1yr_%'] > 0)  # Positive 1-year return
    ].copy()

    if len(momentum) > 0:
        momentum = momentum.sort_values('Momentum_Score', ascending=False)
        print(momentum[['Ticker', 'sector', 'Momentum_Score', 'CAGR_%',
                       'Return_6mo_%', 'Return_1yr_%', 'beta']].to_string(index=False))
    else:
        print("No stocks meeting criteria in current dataset")

    return momentum


def find_quality_growth(df):
    """Find quality growth stocks"""
    print("\n" + "="*80)
    print("QUALITY GROWTH STOCKS")
    print("="*80)
    print("Stocks with high returns, strong margins, and reasonable valuations")
    print("-"*80)

    # Criteria: Good growth, profitability, and not overvalued
    quality = df[
        (df['CAGR_%'] > df['CAGR_%'].median()) &  # Above-average growth
        (df['profit_margin'] > 0.15) &  # Strong profit margins
        (df['return_on_equity'] > 0.15) &  # Good ROE
        (df['trailing_pe'] < 40)  # Not extremely overvalued
    ].copy()

    if len(quality) > 0:
        quality = quality.sort_values('Risk_Adjusted_Return', ascending=False)
        print(quality[['Ticker', 'sector', 'CAGR_%', 'Risk_Adjusted_Return',
                      'profit_margin', 'return_on_equity', 'trailing_pe']].to_string(index=False))
    else:
        print("No stocks meeting criteria in current dataset")

    return quality


def generate_enhanced_strategies(df, correlations, sector_stats):
    """Generate enhanced return strategies based on analysis"""
    print("\n" + "="*80)
    print("ENHANCED RETURN STRATEGIES")
    print("="*80)

    strategies = []

    # Strategy 1: Sector Focus
    if sector_stats is not None:
        top_sectors = sector_stats.nlargest(3, 'CAGR_%_mean')
        strategy = {
            'name': 'Sector Focus Strategy',
            'description': 'Focus on highest-performing sectors',
            'top_sectors': top_sectors.index.tolist(),
            'expected_benefit': f"+{(top_sectors['CAGR_%_mean'].mean() - df['CAGR_%'].mean()):.2f}% CAGR vs average"
        }
        strategies.append(strategy)

        print("\n1. SECTOR FOCUS STRATEGY")
        print(f"   Focus on: {', '.join(top_sectors.index.tolist())}")
        print(f"   Expected benefit: {strategy['expected_benefit']}")

    # Strategy 2: Quality Metrics
    print("\n2. QUALITY METRICS STRATEGY")
    print("   Select stocks with:")
    print("   - ROE > 15%")
    print("   - Profit Margin > 15%")
    print("   - CAGR > median")
    quality_stocks = df[(df['return_on_equity'] > 0.15) &
                        (df['profit_margin'] > 0.15) &
                        (df['CAGR_%'] > df['CAGR_%'].median())]
    if len(quality_stocks) > 0:
        print(f"   Average CAGR of qualifying stocks: {quality_stocks['CAGR_%'].mean():.2f}%")
        print(f"   vs Overall average: {df['CAGR_%'].mean():.2f}%")
        print(f"   Benefit: +{(quality_stocks['CAGR_%'].mean() - df['CAGR_%'].mean()):.2f}% CAGR")

    # Strategy 3: Low Volatility
    print("\n3. LOW VOLATILITY STRATEGY")
    print("   Select stocks with:")
    print("   - Volatility < median")
    print("   - Positive CAGR")
    low_vol = df[(df['Annual_Volatility_%'] < df['Annual_Volatility_%'].median()) &
                 (df['CAGR_%'] > 0)]
    if len(low_vol) > 0:
        print(f"   Average CAGR: {low_vol['CAGR_%'].mean():.2f}%")
        print(f"   Average Volatility: {low_vol['Annual_Volatility_%'].mean():.2f}%")
        print(f"   Risk-Adjusted Return: {low_vol['Risk_Adjusted_Return'].mean():.3f}")
        print(f"   vs Overall: {df['Risk_Adjusted_Return'].mean():.3f}")

    # Strategy 4: Momentum + Quality
    print("\n4. MOMENTUM + QUALITY STRATEGY")
    print("   Select stocks with:")
    print("   - Positive 6mo and 1yr returns")
    print("   - CAGR > 12%")
    print("   - ROE > 10%")
    momentum_quality = df[(df['Return_6mo_%'] > 0) &
                         (df['Return_1yr_%'] > 0) &
                         (df['CAGR_%'] > 12) &
                         (df['return_on_equity'] > 0.1)]
    if len(momentum_quality) > 0:
        print(f"   Average CAGR: {momentum_quality['CAGR_%'].mean():.2f}%")
        print(f"   Average 1yr return: {momentum_quality['Return_1yr_%'].mean():.2f}%")
        print(f"   Benefit: +{(momentum_quality['CAGR_%'].mean() - df['CAGR_%'].mean()):.2f}% CAGR")

    return strategies


def save_results(df, correlations, sector_stats):
    """Save correlation analysis results"""
    os.makedirs('data', exist_ok=True)

    # Save merged dataset
    df.to_csv('data/fundamentals_vs_returns.csv', index=False)
    print(f"\nSaved: data/fundamentals_vs_returns.csv")

    # Save correlation summary
    corr_summary = {}
    for metric, corr_df in correlations.items():
        corr_summary[metric] = corr_df.head(10).to_dict('records')

    with open('data/correlation_analysis.json', 'w') as f:
        json.dump(corr_summary, f, indent=2)
    print(f"Saved: data/correlation_analysis.json")

    # Save sector stats
    if sector_stats is not None:
        sector_stats.to_csv('data/sector_performance.csv')
        print(f"Saved: data/sector_performance.csv")


def main():
    """Main execution"""
    print("="*80)
    print("FUNDAMENTALS vs RETURNS CORRELATION ANALYSIS")
    print("="*80)

    # Check for required files
    required_files = [
        'data/price_trend_analysis.csv',
        'data/current_fundamentals.csv'
    ]

    for file in required_files:
        if not os.path.exists(file):
            print(f"\nERROR: Required file not found: {file}")
            print("Please run download_stock_data.py and analyze_trends.py first")
            return

    # Load and merge data
    df = load_data()

    # Calculate correlations
    correlations = calculate_correlations(df)

    # Analyze by sector
    sector_stats = analyze_by_sector(df)

    # Identify winning characteristics
    identify_winning_characteristics(df)

    # Find opportunities
    value_opportunities = find_value_opportunities(df)
    momentum_plays = find_momentum_plays(df)
    quality_growth = find_quality_growth(df)

    # Generate strategies
    strategies = generate_enhanced_strategies(df, correlations, sector_stats)

    # Save results
    save_results(df, correlations, sector_stats)

    print("\n" + "="*80)
    print("CORRELATION ANALYSIS COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    main()
