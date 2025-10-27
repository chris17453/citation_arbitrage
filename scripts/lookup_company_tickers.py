#!/usr/bin/env python3
"""
Look up stock tickers for company names using multiple methods.
Adds public/private status, exchange, and valuation data.
"""

import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import time

try:
    import yfinance as yf
    import requests
except ImportError:
    print("Installing dependencies...")
    import subprocess
    subprocess.run(["pip", "install", "yfinance", "requests"], check=True)
    import yfinance as yf
    import requests


def search_ticker_yahoo(company_name: str) -> Optional[str]:
    """Search for ticker using Yahoo Finance search."""
    try:
        # Yahoo Finance search API
        url = "https://query2.finance.yahoo.com/v1/finance/search"
        params = {
            'q': company_name,
            'quotesCount': 5,
            'newsCount': 0
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            quotes = data.get('quotes', [])

            if quotes:
                # Return the first result's symbol
                return quotes[0].get('symbol')
    except Exception as e:
        print(f"      Yahoo search error: {e}")

    return None


def verify_ticker(ticker: str) -> Optional[Dict[str, Any]]:
    """Verify ticker exists and get current data."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Check if we got valid data
        if not info or len(info) < 5:
            return None

        # Get key data
        price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
        market_cap = info.get('marketCap')
        currency = info.get('currency', 'USD')
        exchange = info.get('exchange') or info.get('exchangeName', 'Unknown')
        company_name = info.get('longName') or info.get('shortName', '')

        return {
            'ticker': ticker,
            'price': price,
            'market_cap': market_cap,
            'currency': currency,
            'exchange': exchange,
            'verified_name': company_name,
        }
    except Exception as e:
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


def extract_company_name(company_str: str) -> str:
    """Extract clean company name from 'Company (Country)' format."""
    if '(' in company_str:
        return company_str.split('(')[0].strip()
    return company_str.strip()


# Enhanced manual ticker mappings (verified)
KNOWN_COMPANIES = {
    # Tech giants
    'nvidia': {'ticker': 'NVDA', 'exchange': 'NASDAQ'},
    'meta': {'ticker': 'META', 'exchange': 'NASDAQ'},
    'microsoft': {'ticker': 'MSFT', 'exchange': 'NASDAQ'},
    'microsoft research': {'ticker': 'MSFT', 'exchange': 'NASDAQ'},
    'google': {'ticker': 'GOOGL', 'exchange': 'NASDAQ'},
    'apple': {'ticker': 'AAPL', 'exchange': 'NASDAQ'},
    'amazon': {'ticker': 'AMZN', 'exchange': 'NASDAQ'},

    # Known private companies
    'openai': {'ticker': None, 'status': 'Private', 'valuation': '$80B+ (2024)'},
    'huawei': {'ticker': None, 'status': 'Private', 'note': 'Chinese private company'},
    'huawei technologies': {'ticker': None, 'status': 'Private', 'note': 'Chinese private company'},

    # Telecom
    'ericsson': {'ticker': 'ERIC', 'exchange': 'NASDAQ'},
    'nokia': {'ticker': 'NOK', 'exchange': 'NYSE'},

    # Pharma/Biotech
    'glaxosmithkline': {'ticker': 'GSK', 'exchange': 'NYSE'},
    'eli lilly': {'ticker': 'LLY', 'exchange': 'NYSE'},
    'biontech': {'ticker': 'BNTX', 'exchange': 'NASDAQ'},
    'daiichi sankyo': {'ticker': '4568.T', 'exchange': 'Tokyo'},

    # Other known public
    'continental': {'ticker': 'CON.DE', 'exchange': 'XETRA'},
    'juniper networks': {'ticker': 'JNPR', 'exchange': 'NYSE'},
    'accenture': {'ticker': 'ACN', 'exchange': 'NYSE'},
    'netflix': {'ticker': 'NFLX', 'exchange': 'NASDAQ'},
    'snap': {'ticker': 'SNAP', 'exchange': 'NYSE'},
    'exact sciences': {'ticker': 'EXAS', 'exchange': 'NASDAQ'},
    '10x genomics': {'ticker': 'TXG', 'exchange': 'NASDAQ'},
    'vimicro': {'ticker': 'VIMC', 'exchange': 'NASDAQ'},
    'sabre': {'ticker': 'SABR', 'exchange': 'NASDAQ'},
    'raysearch laboratories': {'ticker': 'RAYB.ST', 'exchange': 'Stockholm'},
    'wave life sciences': {'ticker': 'WVE', 'exchange': 'NASDAQ'},

    # Known private/small
    'decode genetics': {'ticker': None, 'status': 'Acquired', 'note': 'Acquired by Amgen 2012 for $415M'},
    'megvii': {'ticker': None, 'status': 'Private', 'note': 'Chinese AI unicorn'},
    'dataminr': {'ticker': None, 'status': 'Private', 'note': 'Last valued at $4.1B (2021)'},
}


def lookup_company(company_name: str) -> Dict[str, Any]:
    """Look up company ticker and details."""
    company_lower = company_name.lower()

    # Check manual mappings first
    for known_name, data in KNOWN_COMPANIES.items():
        if known_name in company_lower:
            ticker = data.get('ticker')

            if ticker:
                # Verify and get current data
                verified = verify_ticker(ticker)
                if verified:
                    return {
                        'is_public': True,
                        'ticker': ticker,
                        'price': verified['price'],
                        'currency': verified['currency'],
                        'market_cap': verified['market_cap'],
                        'market_cap_formatted': format_market_cap(verified['market_cap']),
                        'exchange': data.get('exchange', verified['exchange']),
                        'verified_name': verified['verified_name'],
                        'status': 'Public',
                    }
            else:
                # Private company from manual mapping
                return {
                    'is_public': False,
                    'ticker': None,
                    'price': None,
                    'currency': None,
                    'market_cap': None,
                    'market_cap_formatted': data.get('valuation', 'Private'),
                    'exchange': None,
                    'status': data.get('status', 'Private'),
                    'note': data.get('note', ''),
                }

    # Try Yahoo Finance search
    print(f"      Searching Yahoo Finance for '{company_name}'...")
    ticker = search_ticker_yahoo(company_name)

    if ticker:
        print(f"      Found ticker: {ticker}")
        verified = verify_ticker(ticker)

        if verified:
            return {
                'is_public': True,
                'ticker': ticker,
                'price': verified['price'],
                'currency': verified['currency'],
                'market_cap': verified['market_cap'],
                'market_cap_formatted': format_market_cap(verified['market_cap']),
                'exchange': verified['exchange'],
                'verified_name': verified['verified_name'],
                'status': 'Public',
            }

    # Not found - assume private
    return {
        'is_public': False,
        'ticker': None,
        'price': None,
        'currency': None,
        'market_cap': None,
        'market_cap_formatted': 'Unknown',
        'exchange': None,
        'status': 'Private/Unknown',
        'note': 'Company not found in public markets',
    }


def process_companies_csv():
    """Process COMPANIES.csv and add stock data."""
    data_dir = Path(__file__).parent.parent / "data" / "analysis"
    input_file = data_dir / "COMPANIES.csv"
    output_file = data_dir / "COMPANIES_ENRICHED.csv"

    print("📊 Processing companies...\n")

    # Load companies
    companies = []
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        companies = [row for row in reader if row.get('Company')]

    enriched = []

    for i, company_row in enumerate(companies, 1):
        company_full = company_row['Company']
        company_name = extract_company_name(company_full)

        print(f"[{i}/{len(companies)}] {company_name}")

        # Look up company
        data = lookup_company(company_name)

        # Create enriched row
        enriched_row = company_row.copy()
        enriched_row['Status'] = data['status']
        enriched_row['Stock_Ticker'] = data['ticker'] or ''
        enriched_row['Exchange'] = data['exchange'] or ''
        enriched_row['Stock_Price'] = f"${data['price']:.2f}" if data['price'] else ''
        enriched_row['Currency'] = data['currency'] or ''
        enriched_row['Market_Cap'] = data['market_cap_formatted']
        enriched_row['Note'] = data.get('note', '')

        if data['is_public']:
            print(f"   ✅ PUBLIC - {data['ticker']} @ {data['exchange']}")
            print(f"      Price: ${data['price']:.2f} | Market Cap: {data['market_cap_formatted']}")
        else:
            print(f"   🔒 {data['status']} - {data['market_cap_formatted']}")
            if data.get('note'):
                print(f"      Note: {data['note']}")

        enriched.append(enriched_row)
        print()
        time.sleep(1)  # Be polite to APIs

    # Save
    if enriched:
        fieldnames = list(enriched[0].keys())
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(enriched)

        print(f"✅ Saved to {output_file}")

    return enriched


def process_investment_leads():
    """Process INVESTMENT_LEADS.csv and add stock data."""
    data_dir = Path(__file__).parent.parent / "data" / "analysis"
    input_file = data_dir / "INVESTMENT_LEADS.csv"
    output_file = data_dir / "INVESTMENT_LEADS_ENRICHED.csv"

    print("\n📊 Processing investment leads...\n")

    # Load leads
    leads = []
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        leads = [row for row in reader if row.get('Company')]

    # Get unique companies
    companies_data = {}
    unique_companies = set()

    for lead in leads:
        company_full = lead['Company']
        company_name = extract_company_name(company_full)
        unique_companies.add(company_name)

    print(f"Looking up {len(unique_companies)} unique companies...\n")

    # Look up each unique company
    for i, company_name in enumerate(sorted(unique_companies), 1):
        print(f"[{i}/{len(unique_companies)}] {company_name}")
        companies_data[company_name] = lookup_company(company_name)

        data = companies_data[company_name]
        if data['is_public']:
            print(f"   ✅ PUBLIC - {data['ticker']}")
        else:
            print(f"   🔒 {data['status']}")
        print()
        time.sleep(1)

    # Enrich leads
    enriched = []
    for lead in leads:
        company_name = extract_company_name(lead['Company'])
        data = companies_data.get(company_name, {})

        enriched_lead = lead.copy()
        enriched_lead['Status'] = data.get('status', 'Unknown')
        enriched_lead['Stock_Ticker'] = data.get('ticker') or ''
        enriched_lead['Exchange'] = data.get('exchange') or ''
        enriched_lead['Stock_Price'] = f"${data['price']:.2f}" if data.get('price') else ''
        enriched_lead['Currency'] = data.get('currency') or ''
        enriched_lead['Market_Cap'] = data.get('market_cap_formatted', '')
        enriched_lead['Note'] = data.get('note', '')

        enriched.append(enriched_lead)

    # Save
    if enriched:
        fieldnames = list(enriched[0].keys())
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(enriched)

        print(f"✅ Saved to {output_file}")

    return enriched


def main():
    """Main workflow."""
    print("="*80)
    print("🔍 COMPANY TICKER LOOKUP & ENRICHMENT")
    print("="*80)
    print()

    # Process both files
    process_companies_csv()
    process_investment_leads()

    print("\n" + "="*80)
    print("✅ COMPLETE")
    print("="*80)
    print("\nFiles created:")
    print("  • data/analysis/COMPANIES_ENRICHED.csv")
    print("  • data/analysis/INVESTMENT_LEADS_ENRICHED.csv")


if __name__ == "__main__":
    main()
