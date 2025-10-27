#!/usr/bin/env python3
"""
Generate comprehensive Top 100 investment leads report.
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


def generate_markdown_report(leads, output_file, top_n=100):
    """Generate comprehensive markdown report."""

    with open(output_file, 'w') as f:
        f.write(f"# Top {top_n} Investment Leads - Detailed Report\n\n")
        f.write(f"**Generated:** 2025-10-27\n")
        f.write(f"**Total Leads:** {len(leads)}\n")
        f.write(f"**Showing:** Top {min(top_n, len(leads))}\n\n")

        f.write("---\n\n")

        # Summary statistics
        f.write("## 📊 Summary Statistics\n\n")

        public_companies = sum(1 for lead in leads if lead.get('Status') == 'Public')
        private_companies = sum(1 for lead in leads if lead.get('Status') in ['Private', 'Private/Unknown'])

        f.write(f"- **Public Companies:** {public_companies}\n")
        f.write(f"- **Private/Unknown Companies:** {private_companies}\n")
        f.write(f"- **Total Citations:** {sum(int(lead.get('Citations', 0)) for lead in leads):,}\n")
        f.write(f"- **Average H-Index:** {sum(int(lead.get('H-Index', 0)) for lead in leads) / len(leads):.1f}\n")
        f.write(f"- **Average Score:** {sum(float(lead.get('Score', 0)) for lead in leads) / len(leads):.3f}\n\n")

        f.write("---\n\n")

        # Detailed list
        for i, lead in enumerate(leads[:top_n], 1):
            name = lead['Name']
            company = lead['Company'].split('(')[0].strip()
            country = lead.get('Country', 'N/A')
            score = float(lead.get('Score', 0))
            citations = lead.get('Citations', 'N/A')
            h_index = lead.get('H-Index', 'N/A')
            papers = lead.get('Papers', 'N/A')
            first_author = lead.get('First Author Papers', 'N/A')
            orcid = lead.get('ORCID', '')

            # Stock info
            status = lead.get('Status', 'Unknown')
            ticker = lead.get('Stock_Ticker', '')
            exchange = lead.get('Exchange', '')
            price = lead.get('Stock_Price', '')
            market_cap = lead.get('Market_Cap', '')

            f.write(f"## {i}. {name}\n\n")

            # Company info box
            f.write(f"### 🏢 Company: {company}\n\n")

            if ticker:
                f.write(f"**Stock:** {ticker} ({exchange})\n\n")
                if price:
                    f.write(f"**Price:** {price}\n\n")
                if market_cap and market_cap not in ['', 'Unknown']:
                    f.write(f"**Market Cap:** {market_cap}\n\n")
            else:
                f.write(f"**Status:** {status}\n\n")

            f.write(f"**Country:** {country}\n\n")

            # Research metrics
            f.write(f"### 📊 Research Metrics\n\n")
            f.write(f"| Metric | Value |\n")
            f.write(f"|--------|-------|\n")
            f.write(f"| **Confidence Score** | {score:.3f} |\n")
            f.write(f"| **Total Citations** | {citations} |\n")
            f.write(f"| **H-Index** | {h_index} |\n")
            f.write(f"| **Total Papers** | {papers} |\n")
            f.write(f"| **First Author Papers** | {first_author} |\n")

            if orcid:
                f.write(f"| **ORCID** | [{orcid}]({orcid}) |\n")

            f.write("\n")

            # Research checklist
            f.write(f"### 🔍 Research Actions\n\n")
            f.write(f"- [ ] **LinkedIn:** Search `{name} {company}`\n")
            f.write(f"- [ ] **Company Research:** Search `{company}` on Crunchbase\n")
            if not ticker:
                f.write(f"- [ ] **Funding:** Search `\"{company}\" startup funding Series A`\n")
            f.write(f"- [ ] **Verify Role:** Is {name} still at {company}?\n")
            f.write(f"- [ ] **Company Stage:** Startup, established, or enterprise?\n\n")

            # Notes section
            f.write(f"### 📝 Notes\n\n")
            f.write(f"_Add your research findings here..._\n\n")

            f.write("---\n\n")

    print(f"✅ Generated markdown report: {output_file}")


def generate_csv_top_100(leads, output_file, top_n=100):
    """Generate CSV of top 100 for Excel."""

    top_leads = leads[:top_n]

    if not top_leads:
        print("No leads to save!")
        return

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=top_leads[0].keys())
        writer.writeheader()
        writer.writerows(top_leads)

    print(f"✅ Generated CSV: {output_file}")


def generate_company_summary(leads):
    """Generate summary by company."""

    companies = defaultdict(list)

    for lead in leads:
        company = lead['Company'].split('(')[0].strip()
        companies[company].append(lead)

    data_dir = Path(__file__).parent.parent / "data" / "analysis"
    output_file = data_dir / "TOP_100_BY_COMPANY.md"

    with open(output_file, 'w') as f:
        f.write("# Top 100 Leads Grouped by Company\n\n")
        f.write(f"**Total Unique Companies:** {len(companies)}\n\n")
        f.write("---\n\n")

        # Sort companies by total citations
        sorted_companies = sorted(
            companies.items(),
            key=lambda x: sum(int(lead.get('Citations', 0)) for lead in x[1]),
            reverse=True
        )

        for company, researchers in sorted_companies[:100]:
            total_citations = sum(int(lead.get('Citations', 0)) for lead in researchers)
            avg_score = sum(float(lead.get('Score', 0)) for lead in researchers) / len(researchers)

            status = researchers[0].get('Status', 'Unknown')
            ticker = researchers[0].get('Stock_Ticker', '')
            market_cap = researchers[0].get('Market_Cap', '')

            f.write(f"## {company}\n\n")

            if ticker:
                f.write(f"**Stock:** {ticker} | **Market Cap:** {market_cap}\n\n")
            else:
                f.write(f"**Status:** {status}\n\n")

            f.write(f"**Researchers:** {len(researchers)} | ")
            f.write(f"**Total Citations:** {total_citations:,} | ")
            f.write(f"**Avg Score:** {avg_score:.3f}\n\n")

            f.write("**Researchers:**\n\n")

            for researcher in sorted(researchers, key=lambda x: float(x.get('Score', 0)), reverse=True):
                f.write(f"- **{researcher['Name']}** - ")
                f.write(f"Score: {float(researcher.get('Score', 0)):.3f}, ")
                f.write(f"Citations: {researcher.get('Citations', 'N/A')}, ")
                f.write(f"H-index: {researcher.get('H-Index', 'N/A')}\n")

            f.write("\n---\n\n")

    print(f"✅ Generated company summary: {output_file}")


def main():
    """Generate all top 100 reports."""

    print("="*80)
    print("📊 GENERATING TOP 100 REPORTS")
    print("="*80)
    print()

    # Load leads
    print("Loading enriched investment leads...")
    leads = load_enriched_leads()
    print(f"Loaded {len(leads)} total leads\n")

    data_dir = Path(__file__).parent.parent / "data" / "analysis"

    # Generate reports
    print("Generating reports...\n")

    generate_markdown_report(
        leads,
        data_dir / "TOP_100_LEADS.md",
        top_n=100
    )

    generate_csv_top_100(
        leads,
        data_dir / "TOP_100_LEADS.csv",
        top_n=100
    )

    generate_company_summary(leads)

    print()
    print("="*80)
    print("✅ TOP 100 REPORTS COMPLETE")
    print("="*80)
    print("\nFiles created:")
    print("  • data/analysis/TOP_100_LEADS.md - Detailed markdown report")
    print("  • data/analysis/TOP_100_LEADS.csv - Excel-ready CSV")
    print("  • data/analysis/TOP_100_BY_COMPANY.md - Grouped by company")
    print()
    print(f"Total leads available: {len(leads)}")
    print(f"Showing top: 100")


if __name__ == "__main__":
    main()
