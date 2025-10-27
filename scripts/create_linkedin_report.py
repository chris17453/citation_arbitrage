#!/usr/bin/env python3
"""
Create a single LinkedIn-ready report with:
1. Top 100 contributors and their companies
2. Top 100 companies and their researchers
"""

from pathlib import Path
import csv
from collections import defaultdict


def load_enriched_leads():
    """Load enriched investment leads."""
    data_dir = Path(__file__).parent.parent / "data" / "analysis"

    try:
        input_file = data_dir / "INVESTMENT_LEADS_ENRICHED.csv"
        with open(input_file, 'r') as f:
            reader = csv.DictReader(f)
            return [row for row in reader if row.get('Name')]
    except FileNotFoundError:
        input_file = data_dir / "INVESTMENT_LEADS.csv"
        with open(input_file, 'r') as f:
            reader = csv.DictReader(f)
            return [row for row in reader if row.get('Name')]


def generate_linkedin_report(leads, output_file, top_n=100):
    """Generate single markdown file with both reports."""

    with open(output_file, 'w') as f:
        # Header
        f.write("# High-Impact Academic Researchers in Industry\n\n")
        f.write("*Analysis of 5,000 research papers (2020-2024) identifying influential researchers now working in industry*\n\n")
        f.write(f"**Date:** 2025-10-27\n\n")
        f.write("---\n\n")

        # Section 1: Top Contributors
        f.write(f"## 📊 Top {min(top_n, len(leads))} Research Contributors in Industry\n\n")
        f.write("Ranked by research impact (PageRank-based confidence score)\n\n")

        f.write("| # | Name | Company | Status | Ticker | Stock Price | Citations | H-Index |\n")
        f.write("|---|------|---------|--------|--------|-------------|-----------|----------|\n")

        for i, lead in enumerate(leads[:top_n], 1):
            name = lead['Name']
            company = lead['Company'].split('(')[0].strip()
            status = lead.get('Status', 'Unknown')
            ticker = lead.get('Stock_Ticker', '-')
            price = lead.get('Stock_Price', '-')
            citations = lead.get('Citations', 'N/A')
            h_index = lead.get('H-Index', 'N/A')

            # Shorten long company names
            if len(company) > 30:
                company = company[:27] + "..."

            # Format status
            status_display = "🟢 Public" if status == "Public" else "🔒 Private"
            if status == "Acquired":
                status_display = "💰 Acquired"

            # Format ticker and price
            ticker_display = f"`{ticker}`" if ticker and ticker != '-' else '-'
            price_display = price if price and price != '-' else '-'

            f.write(f"| {i} | **{name}** | {company} | {status_display} | {ticker_display} | {price_display} | {citations} | {h_index} |\n")

        f.write("\n---\n\n")

        # Section 2: Companies with Multiple Researchers
        f.write("## 🏢 Companies with Multiple High-Impact Researchers\n\n")
        f.write("Companies ranked by number of influential researchers\n\n")

        # Group by company
        companies = defaultdict(list)
        for lead in leads:
            company = lead['Company'].split('(')[0].strip()
            companies[company].append(lead)

        # Sort by researcher count, then total citations
        sorted_companies = sorted(
            companies.items(),
            key=lambda x: (len(x[1]), sum(int(lead.get('Citations', 0)) for lead in x[1])),
            reverse=True
        )

        company_rank = 0
        for company, researchers in sorted_companies[:top_n]:
            company_rank += 1

            # Calculate stats
            total_citations = sum(int(lead.get('Citations', 0)) for lead in researchers)
            avg_h_index = sum(int(lead.get('H-Index', 0)) for lead in researchers) / len(researchers)

            # Get company info from first researcher
            status = researchers[0].get('Status', 'Unknown')
            ticker = researchers[0].get('Stock_Ticker', '')
            market_cap = researchers[0].get('Market_Cap', '')

            # Format status
            if status == "Public":
                status_icon = "🟢"
            elif status == "Acquired":
                status_icon = "💰"
            else:
                status_icon = "🔒"

            # Company header
            f.write(f"### {company_rank}. {company} {status_icon}\n\n")

            # Company details
            if ticker:
                f.write(f"**Ticker:** `{ticker}`")
                if market_cap and market_cap not in ['', 'Unknown', 'Private']:
                    f.write(f" | **Market Cap:** {market_cap}")
                f.write("\n\n")
            else:
                f.write(f"**Status:** {status}\n\n")

            # Stats
            f.write(f"- **Researchers:** {len(researchers)}\n")
            f.write(f"- **Total Citations:** {total_citations:,}\n")
            f.write(f"- **Avg H-Index:** {avg_h_index:.1f}\n\n")

            # List researchers
            f.write("**Researchers:**\n\n")

            # Sort researchers by score
            sorted_researchers = sorted(researchers, key=lambda x: float(x.get('Score', 0)), reverse=True)

            for researcher in sorted_researchers:
                name = researcher['Name']
                score = float(researcher.get('Score', 0))
                citations = researcher.get('Citations', 'N/A')
                h_index = researcher.get('H-Index', 'N/A')

                f.write(f"- **{name}** - Score: {score:.3f}, Citations: {citations}, H-index: {h_index}\n")

            f.write("\n")

        f.write("---\n\n")

        # Footer
        f.write("## 📈 Methodology\n\n")
        f.write("This analysis uses PageRank algorithm (similar to Google's original search algorithm) on academic citation networks to identify truly influential research. We then track where these researchers work to find companies attracting top talent.\n\n")
        f.write("**Data Sources:**\n")
        f.write("- Research papers: OpenAlex API (5,000 papers, 2020-2024)\n")
        f.write("- Citation network: 392,239 papers analyzed\n")
        f.write("- Stock data: Yahoo Finance\n\n")
        f.write("**Key Findings:**\n")

        public_count = sum(1 for lead in leads if lead.get('Status') == 'Public')
        private_count = len(leads) - public_count

        f.write(f"- Total researchers identified: {len(leads)}\n")
        f.write(f"- Public companies: {public_count}\n")
        f.write(f"- Private/Unknown companies: {private_count}\n")
        f.write(f"- Total citations: {sum(int(lead.get('Citations', 0)) for lead in leads):,}\n\n")

        f.write("---\n\n")
        f.write("*Generated with Citation Arbitrage - Finding overlooked opportunities by tracking influential researchers*\n")

    print(f"✅ LinkedIn report generated: {output_file}")


def main():
    """Generate LinkedIn report."""

    print("="*80)
    print("📊 GENERATING LINKEDIN REPORT")
    print("="*80)
    print()

    # Load leads
    print("Loading enriched investment leads...")
    leads = load_enriched_leads()
    print(f"Loaded {len(leads)} total leads\n")

    data_dir = Path(__file__).parent.parent / "data" / "analysis"

    # Generate single report
    print("Generating LinkedIn report...\n")

    generate_linkedin_report(
        leads,
        data_dir / "LINKEDIN_REPORT.md",
        top_n=100
    )

    print()
    print("="*80)
    print("✅ LINKEDIN REPORT COMPLETE")
    print("="*80)
    print("\nFile created:")
    print("  • data/analysis/LINKEDIN_REPORT.md")
    print()
    print("This file contains:")
    print("  1. Top 100 contributors with company info & stock data")
    print("  2. Companies ranked by number of researchers")
    print()
    print("Ready to post on LinkedIn!")


if __name__ == "__main__":
    main()
