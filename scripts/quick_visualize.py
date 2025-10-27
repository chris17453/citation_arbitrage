#!/usr/bin/env python3
"""
Quick visualizations from existing data - no data re-fetching.
"""

from pathlib import Path
import yaml
import csv

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import networkx as nx
except ImportError:
    print("Installing matplotlib...")
    import subprocess
    subprocess.run(["pip", "install", "matplotlib"], check=True)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import networkx as nx


def create_pagerank_histogram():
    """Create PageRank distribution histogram."""
    print("📊 Creating PageRank distribution...")

    data_dir = Path(__file__).parent.parent / "data"

    # Load grad students scores
    with open(data_dir / "analysis" / "grad_students.yaml", 'r') as f:
        data = yaml.safe_load(f)

    scores = [candidate['score'] for candidate in data['candidates'][:1000]]  # Limit to top 1000 for speed

    plt.figure(figsize=(10, 6))
    plt.hist(scores, bins=50, edgecolor='black', alpha=0.7)
    plt.xlabel('Confidence Score', fontsize=12)
    plt.ylabel('Number of Candidates', fontsize=12)
    plt.title('PageRank-based Confidence Score Distribution\n(Top 1000 Grad Student Candidates)', fontsize=14)
    plt.grid(True, alpha=0.3)

    output_path = data_dir / "analysis" / "pagerank_distribution.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"   ✅ Saved to {output_path}")


def create_company_chart():
    """Create chart of companies with multiple researchers."""
    print("📊 Creating companies chart...")

    data_dir = Path(__file__).parent.parent / "data" / "analysis"

    # Load enriched companies
    companies = []
    with open(data_dir / "COMPANIES_ENRICHED.csv", 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Company'):
                companies.append(row)

    # Create bar chart
    names = [row['Company'].split('(')[0].strip()[:20] for row in companies]  # Truncate long names
    counts = [int(row['Researcher Count']) for row in companies]
    colors = ['green' if row['Status'] == 'Public' else 'gray' for row in companies]

    plt.figure(figsize=(12, 6))
    bars = plt.barh(names, counts, color=colors, alpha=0.7)
    plt.xlabel('Number of Researchers', fontsize=12)
    plt.title('Companies with Multiple High-Impact Researchers\n(Green = Public, Gray = Private)', fontsize=14)
    plt.grid(True, axis='x', alpha=0.3)
    plt.tight_layout()

    output_path = data_dir / "companies_chart.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"   ✅ Saved to {output_path}")


def create_citation_distribution():
    """Create citation distribution chart."""
    print("📊 Creating citation distribution...")

    data_dir = Path(__file__).parent.parent / "data" / "analysis"

    # Load investment leads
    leads = []
    with open(data_dir / "INVESTMENT_LEADS.csv", 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Citations'):
                leads.append(row)

    # Get citations (show all)
    citations = [int(row['Citations']) for row in leads]
    names = [f"{row['Name'][:15]}..." if len(row['Name']) > 15 else row['Name'] for row in leads]

    plt.figure(figsize=(16, 8))
    plt.scatter(range(len(citations)), citations, s=100, alpha=0.6, c='blue')
    plt.xlabel('Researcher Rank', fontsize=12)
    plt.ylabel('Total Citations', fontsize=12)
    plt.title(f'Citation Count Distribution (All {len(leads)} Leads)', fontsize=14)
    plt.yscale('log')
    plt.grid(True, alpha=0.3)

    output_path = data_dir / "citations_distribution.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"   ✅ Saved to {output_path}")


def create_hindex_vs_score():
    """Create H-index vs confidence score scatter plot."""
    print("📊 Creating H-index vs Score plot...")

    data_dir = Path(__file__).parent.parent / "data" / "analysis"

    # Load investment leads
    leads = []
    with open(data_dir / "INVESTMENT_LEADS.csv", 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('H-Index') and row.get('Score'):
                leads.append(row)

    h_indices = [int(row['H-Index']) for row in leads]
    scores = [float(row['Score']) for row in leads]

    plt.figure(figsize=(10, 6))
    plt.scatter(h_indices, scores, s=80, alpha=0.5, c='purple')
    plt.xlabel('H-Index', fontsize=12)
    plt.ylabel('Confidence Score', fontsize=12)
    plt.title('H-Index vs Confidence Score\n(All Investment Leads)', fontsize=14)
    plt.grid(True, alpha=0.3)

    output_path = data_dir / "hindex_vs_score.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"   ✅ Saved to {output_path}")


def main():
    """Create all visualizations."""
    print("="*80)
    print("📊 GENERATING VISUALIZATIONS FROM EXISTING DATA")
    print("="*80)
    print()

    create_pagerank_histogram()
    create_company_chart()
    create_citation_distribution()
    create_hindex_vs_score()

    print()
    print("="*80)
    print("✅ ALL VISUALIZATIONS COMPLETE")
    print("="*80)
    print("\nGenerated files:")
    print("  • data/analysis/pagerank_distribution.png")
    print("  • data/analysis/companies_chart.png")
    print("  • data/analysis/citations_distribution.png")
    print("  • data/analysis/hindex_vs_score.png")


if __name__ == "__main__":
    main()
