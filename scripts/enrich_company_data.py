#!/usr/bin/env python3
"""
Enrich company data with valuation, public/private status, and stock prices.
Uses yfinance for public company stock data.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import time

try:
    import yfinance as yf
except ImportError:
    print("Installing yfinance...")
    import subprocess
    subprocess.run(["pip", "install", "yfinance"], check=True)
    import yfinance as yf


# Known public company tickers (manual mapping for common cases)
KNOWN_TICKERS = {
    'nvidia': 'NVDA',
    'meta': 'META',
    'microsoft': 'MSFT',
    'google': 'GOOGL',
    'openai': None,  # Private
    'huawei': None,  # Private (not US traded)
    'ericsson': 'ERIC',
    'glaxosmithkline': 'GSK',
    'eli lilly': 'LLY',
    'daiichi sankyo': '4568.T',
    'continental': 'CON.DE',
    'juniper networks': 'JNPR',
    'accenture': 'ACN',
    'netflix': 'NFLX',
    'yahoo': None,  # Private now (Verizon subsidiary)
    'snap': 'SNAP',
    'exact sciences': 'EXAS',
    'biontech': 'BNTX',
    '10x genomics': 'TXG',
    'megvii': None,  # Private
    'vimicro': 'VIMC',
    'sabre': 'SABR',
    'daiminr': None,  # Private (Dataminr)
    'raysearch laboratories': 'RAYB.ST',
    'wave life sciences': 'WVE',
    'nokia': 'NOK',
}


def extract_company_name(company_str: str) -> str:
    """Extract clean company name from 'Company (Country)' format."""
    if '(' in company_str:
        return company_str.split('(')[0].strip()
    return company_str.strip()


def find_ticker(company_name: str) -> Optional[str]:
    """Try to find stock ticker for a company."""
    company_lower = company_name.lower()

    # Check known tickers first
    for known_name, ticker in KNOWN_TICKERS.items():
        if known_name in company_lower:
            return ticker

    # Try searching with yfinance
    try:
        # Create a ticker object and see if it exists
        ticker = yf.Ticker(company_name)
        info = ticker.info

        # If we get valid info back, it's probably a real ticker
        if info and 'regularMarketPrice' in info:
            return company_name
    except:
        pass

    return None


def get_stock_data(ticker: str) -> Optional[Dict[str, Any]]:
    """Get current stock price and market cap."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Get current price
        price = info.get('currentPrice') or info.get('regularMarketPrice')

        # Get market cap
        market_cap = info.get('marketCap')

        # Get company name
        company_name = info.get('longName') or info.get('shortName')

        if price:
            return {
                'ticker': ticker,
                'price': price,
                'currency': info.get('currency', 'USD'),
                'market_cap': market_cap,
                'company_name': company_name,
                'exchange': info.get('exchange'),
            }
    except Exception as e:
        print(f"  ⚠️  Error fetching {ticker}: {e}")

    return None


def format_market_cap(market_cap: Optional[int]) -> str:
    """Format market cap in readable form."""
    if not market_cap:
        return "N/A"

    if market_cap >= 1_000_000_000_000:  # Trillion
        return f"${market_cap / 1_000_000_000_000:.2f}T"
    elif market_cap >= 1_000_000_000:  # Billion
        return f"${market_cap / 1_000_000_000:.2f}B"
    elif market_cap >= 1_000_000:  # Million
        return f"${market_cap / 1_000_000:.2f}M"
    else:
        return f"${market_cap:,}"


def enrich_investment_leads():
    """Enrich INVESTMENT_LEADS.csv with company data."""
    data_dir = Path(__file__).parent.parent / "data" / "analysis"
    input_file = data_dir / "INVESTMENT_LEADS.csv"
    output_file = data_dir / "INVESTMENT_LEADS_ENRICHED.csv"

    print("📊 Enriching investment leads with company data...\n")

    # Load existing data
    leads = []
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        leads = list(reader)

    # Process each unique company
    companies_processed = set()
    company_data = {}

    for lead in leads:
        if not lead.get('Company'):
            continue

        company_full = lead['Company']
        company_name = extract_company_name(company_full)

        if company_name in companies_processed:
            continue

        companies_processed.add(company_name)
        print(f"🔍 Researching: {company_name}")

        # Try to find ticker
        ticker = find_ticker(company_name)

        if ticker:
            print(f"   Found ticker: {ticker}")
            stock_data = get_stock_data(ticker)

            if stock_data:
                company_data[company_name] = {
                    'is_public': True,
                    'ticker': ticker,
                    'stock_price': stock_data['price'],
                    'currency': stock_data['currency'],
                    'market_cap': stock_data['market_cap'],
                    'market_cap_formatted': format_market_cap(stock_data['market_cap']),
                    'exchange': stock_data.get('exchange', 'N/A'),
                }
                print(f"   ✅ ${stock_data['price']:.2f} | Market Cap: {format_market_cap(stock_data['market_cap'])}")
            else:
                company_data[company_name] = {
                    'is_public': True,
                    'ticker': ticker,
                    'stock_price': 'N/A',
                    'currency': 'USD',
                    'market_cap': None,
                    'market_cap_formatted': 'N/A',
                    'exchange': 'N/A',
                }
                print(f"   ⚠️  Ticker found but no data available")
        else:
            company_data[company_name] = {
                'is_public': False,
                'ticker': None,
                'stock_price': None,
                'currency': None,
                'market_cap': None,
                'market_cap_formatted': 'Private',
                'exchange': None,
            }
            print(f"   🔒 Private company (no public ticker)")

        time.sleep(0.5)  # Be polite to API
        print()

    # Enrich leads with company data
    enriched_leads = []
    for lead in leads:
        if not lead.get('Company'):
            enriched_leads.append(lead)
            continue

        company_name = extract_company_name(lead['Company'])
        data = company_data.get(company_name, {})

        enriched_lead = lead.copy()
        enriched_lead['Is_Public'] = 'Yes' if data.get('is_public') else 'No'
        enriched_lead['Stock_Ticker'] = data.get('ticker') or ''
        enriched_lead['Stock_Price'] = data.get('stock_price') or ''
        enriched_lead['Currency'] = data.get('currency') or ''
        enriched_lead['Market_Cap'] = data.get('market_cap_formatted') or ''
        enriched_lead['Exchange'] = data.get('exchange') or ''

        enriched_leads.append(enriched_lead)

    # Save enriched data
    if enriched_leads:
        fieldnames = list(enriched_leads[0].keys())
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(enriched_leads)

        print(f"✅ Saved enriched leads to {output_file}")

    return company_data


def enrich_companies_csv():
    """Enrich COMPANIES.csv with stock data."""
    data_dir = Path(__file__).parent.parent / "data" / "analysis"
    input_file = data_dir / "COMPANIES.csv"
    output_file = data_dir / "COMPANIES_ENRICHED.csv"

    print("\n📊 Enriching companies list...\n")

    # Load existing data
    companies = []
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        companies = list(reader)

    # Process each company
    enriched_companies = []

    for company_row in companies:
        if not company_row.get('Company'):
            continue

        company_full = company_row['Company']
        company_name = extract_company_name(company_full)

        print(f"🔍 {company_name}")

        # Try to find ticker
        ticker = find_ticker(company_name)

        enriched_row = company_row.copy()

        if ticker:
            print(f"   Found ticker: {ticker}")
            stock_data = get_stock_data(ticker)

            if stock_data:
                enriched_row['Is_Public'] = 'Yes'
                enriched_row['Stock_Ticker'] = ticker
                enriched_row['Stock_Price'] = f"${stock_data['price']:.2f}"
                enriched_row['Currency'] = stock_data['currency']
                enriched_row['Market_Cap'] = format_market_cap(stock_data['market_cap'])
                enriched_row['Exchange'] = stock_data.get('exchange', 'N/A')
                print(f"   ✅ ${stock_data['price']:.2f} | Market Cap: {format_market_cap(stock_data['market_cap'])}")
            else:
                enriched_row['Is_Public'] = 'Yes'
                enriched_row['Stock_Ticker'] = ticker
                enriched_row['Stock_Price'] = 'N/A'
                enriched_row['Currency'] = 'USD'
                enriched_row['Market_Cap'] = 'N/A'
                enriched_row['Exchange'] = 'N/A'
                print(f"   ⚠️  Ticker found but no data available")
        else:
            enriched_row['Is_Public'] = 'No'
            enriched_row['Stock_Ticker'] = ''
            enriched_row['Stock_Price'] = ''
            enriched_row['Currency'] = ''
            enriched_row['Market_Cap'] = 'Private'
            enriched_row['Exchange'] = ''
            print(f"   🔒 Private company")

        enriched_companies.append(enriched_row)
        time.sleep(0.5)
        print()

    # Save enriched data
    if enriched_companies:
        fieldnames = list(enriched_companies[0].keys())
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(enriched_companies)

        print(f"✅ Saved enriched companies to {output_file}")


def main():
    """Main enrichment workflow."""
    print("="*80)
    print("🏢 COMPANY DATA ENRICHMENT")
    print("="*80)
    print("\nAdding valuation, stock prices, and public/private status to company data\n")

    # Enrich investment leads
    enrich_investment_leads()

    # Enrich companies list
    enrich_companies_csv()

    print("\n" + "="*80)
    print("✅ ENRICHMENT COMPLETE")
    print("="*80)
    print("\nNew files created:")
    print("  • data/analysis/INVESTMENT_LEADS_ENRICHED.csv")
    print("  • data/analysis/COMPANIES_ENRICHED.csv")


if __name__ == "__main__":
    main()
