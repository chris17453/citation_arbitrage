#!/usr/bin/env python3
"""
Create a clear company clusters visualization showing which researchers
work at the same companies.
"""

from pathlib import Path
import csv
from collections import defaultdict

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
except ImportError:
    print("Installing matplotlib...")
    import subprocess
    subprocess.run(["pip", "install", "matplotlib"], check=True)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np


def load_enriched_leads():
    """Load enriched investment leads with stock data."""
    data_dir = Path(__file__).parent.parent / "data" / "analysis"

    # Try enriched file first, fall back to regular
    try:
        input_file = data_dir / "INVESTMENT_LEADS_ENRICHED.csv"
        with open(input_file, 'r') as f:
            reader = csv.DictReader(f)
            leads = [row for row in reader if row.get('Name')]
    except FileNotFoundError:
        input_file = data_dir / "INVESTMENT_LEADS.csv"
        with open(input_file, 'r') as f:
            reader = csv.DictReader(f)
            leads = [row for row in reader if row.get('Name')]

    return leads


def create_company_clusters_table():
    """Create a clean table-style visualization of companies and their researchers."""
    print("📊 Creating company clusters table...")

    leads = load_enriched_leads()

    # Group by company
    companies = defaultdict(list)
    for lead in leads:
        company = lead['Company'].split('(')[0].strip()
        companies[company].append(lead)

    # Filter to companies with 2+ researchers
    multi_companies = {k: v for k, v in companies.items() if len(v) >= 2}

    # Sort by number of researchers
    sorted_companies = sorted(multi_companies.items(), key=lambda x: len(x[1]), reverse=True)

    print(f"   Found {len(sorted_companies)} companies with 2+ researchers")

    # Create figure
    fig, ax = plt.subplots(figsize=(20, 14))
    ax.axis('off')

    # Starting position
    y_pos = 0.95
    x_start = 0.05

    # Color palette
    colors = plt.cm.Set3(np.linspace(0, 1, len(sorted_companies)))

    for idx, (company, researchers) in enumerate(sorted_companies):
        color = colors[idx]

        # Get company info from first researcher
        status = researchers[0].get('Status', 'Unknown')
        ticker = researchers[0].get('Stock_Ticker', '')
        market_cap = researchers[0].get('Market_Cap', '')

        # Company header box
        company_text = f"{company}"
        if ticker:
            company_text += f" ({ticker})"
        if market_cap and market_cap not in ['', 'Unknown', 'Private']:
            company_text += f"\n{market_cap}"

        # Draw company box
        box_height = 0.06 + len(researchers) * 0.025
        rect = mpatches.FancyBboxPatch(
            (x_start - 0.01, y_pos - box_height),
            0.92,
            box_height,
            boxstyle="round,pad=0.01",
            linewidth=3,
            edgecolor=color,
            facecolor=(*color[:3], 0.15),
            transform=ax.transAxes
        )
        ax.add_patch(rect)

        # Company name header
        ax.text(x_start, y_pos - 0.02, company_text,
               fontsize=14, fontweight='bold',
               transform=ax.transAxes,
               bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.8))

        # Status badge
        status_color = 'green' if status == 'Public' else 'gray'
        ax.text(0.85, y_pos - 0.02, status,
               fontsize=10, fontweight='bold',
               color='white',
               transform=ax.transAxes,
               bbox=dict(boxstyle='round,pad=0.4', facecolor=status_color, alpha=0.9))

        # List researchers
        y_researcher = y_pos - 0.05
        for researcher in sorted(researchers, key=lambda x: float(x.get('Score', 0)), reverse=True):
            name = researcher['Name']
            score = float(researcher.get('Score', 0))
            citations = researcher.get('Citations', 'N/A')
            h_index = researcher.get('H-Index', 'N/A')

            # Researcher info
            researcher_text = f"  • {name}"
            stats_text = f"Score: {score:.3f} | Citations: {citations} | H-index: {h_index}"

            ax.text(x_start + 0.02, y_researcher, researcher_text,
                   fontsize=11,
                   transform=ax.transAxes)

            ax.text(x_start + 0.35, y_researcher, stats_text,
                   fontsize=9,
                   color='gray',
                   transform=ax.transAxes)

            y_researcher -= 0.025

        y_pos -= box_height + 0.03

        # Break to second column if needed
        if y_pos < 0.15 and idx < len(sorted_companies) - 1:
            x_start = 0.52
            y_pos = 0.95

    # Title
    fig.suptitle('Companies with Multiple High-Impact Researchers\n' +
                f'({len(sorted_companies)} companies with 2+ researchers)',
                fontsize=18, fontweight='bold', y=0.98)

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='green', label='Public Company'),
        mpatches.Patch(facecolor='gray', label='Private/Unknown')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=11)

    plt.tight_layout()

    output_file = Path(__file__).parent.parent / "data" / "analysis" / "company_clusters.png"
    plt.savefig(output_file, dpi=200, bbox_inches='tight')
    print(f"   ✅ Saved to {output_file}")
    plt.close()


def create_company_bar_chart():
    """Create a bar chart showing companies ranked by total citations."""
    print("\n📊 Creating company impact chart...")

    leads = load_enriched_leads()

    # Group by company
    companies = defaultdict(lambda: {'researchers': 0, 'total_citations': 0, 'avg_score': 0, 'status': 'Unknown'})

    for lead in leads:
        company = lead['Company'].split('(')[0].strip()
        companies[company]['researchers'] += 1
        companies[company]['total_citations'] += int(lead.get('Citations', 0))
        companies[company]['avg_score'] += float(lead.get('Score', 0))
        companies[company]['status'] = lead.get('Status', 'Unknown')

    # Calculate averages and filter
    multi_companies = {}
    for company, data in companies.items():
        if data['researchers'] >= 2:
            data['avg_score'] /= data['researchers']
            multi_companies[company] = data

    # Sort by total citations
    sorted_companies = sorted(multi_companies.items(),
                             key=lambda x: x[1]['total_citations'],
                             reverse=True)

    # Create chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

    # Chart 1: Total Citations
    companies_names = [c[0][:25] for c in sorted_companies]  # Truncate long names
    citations = [c[1]['total_citations'] for c in sorted_companies]
    colors1 = ['green' if c[1]['status'] == 'Public' else 'gray' for c in sorted_companies]

    ax1.barh(companies_names, citations, color=colors1, alpha=0.7)
    ax1.set_xlabel('Total Citations', fontsize=12, fontweight='bold')
    ax1.set_title('Total Research Impact by Company', fontsize=14, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)

    # Add citation numbers
    for i, (company, data) in enumerate(sorted_companies):
        ax1.text(data['total_citations'], i, f"  {data['total_citations']:,}",
                va='center', fontsize=9)

    # Chart 2: Number of Researchers
    sorted_by_count = sorted(multi_companies.items(),
                            key=lambda x: x[1]['researchers'],
                            reverse=True)

    companies_names2 = [c[0][:25] for c in sorted_by_count]
    researcher_counts = [c[1]['researchers'] for c in sorted_by_count]
    colors2 = ['green' if c[1]['status'] == 'Public' else 'gray' for c in sorted_by_count]

    ax2.barh(companies_names2, researcher_counts, color=colors2, alpha=0.7)
    ax2.set_xlabel('Number of Researchers', fontsize=12, fontweight='bold')
    ax2.set_title('Researcher Count by Company', fontsize=14, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)

    # Add counts
    for i, (company, data) in enumerate(sorted_by_count):
        ax2.text(data['researchers'], i, f"  {data['researchers']}",
                va='center', fontsize=10, fontweight='bold')

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='green', alpha=0.7, label='Public Company'),
        mpatches.Patch(facecolor='gray', alpha=0.7, label='Private/Unknown')
    ]
    ax1.legend(handles=legend_elements, loc='lower right', fontsize=10)

    fig.suptitle('Company Analysis: Companies with Multiple High-Impact Researchers',
                fontsize=16, fontweight='bold')

    plt.tight_layout()

    output_file = Path(__file__).parent.parent / "data" / "analysis" / "company_impact_chart.png"
    plt.savefig(output_file, dpi=200, bbox_inches='tight')
    print(f"   ✅ Saved to {output_file}")
    plt.close()


def main():
    """Create all company visualizations."""
    print("="*80)
    print("📊 CREATING COMPANY CLUSTER VISUALIZATIONS")
    print("="*80)
    print()

    create_company_clusters_table()
    create_company_bar_chart()

    print()
    print("="*80)
    print("✅ COMPANY VISUALIZATIONS COMPLETE")
    print("="*80)
    print("\nFiles created:")
    print("  • data/analysis/company_clusters.png - Detailed company groupings")
    print("  • data/analysis/company_impact_chart.png - Citation & researcher counts")


if __name__ == "__main__":
    main()
