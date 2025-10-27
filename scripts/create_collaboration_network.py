#!/usr/bin/env python3
"""
Create a focused collaboration network showing researchers at companies
and their connections.
"""

from pathlib import Path
import yaml
import csv
from collections import defaultdict

try:
    import matplotlib
    matplotlib.use('Agg')
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


def load_investment_leads():
    """Load our identified researchers at companies."""
    data_dir = Path(__file__).parent.parent / "data" / "analysis"
    leads = []

    with open(data_dir / "INVESTMENT_LEADS.csv", 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Author ID'):
                leads.append({
                    'author_id': row['Author ID'],
                    'name': row['Name'],
                    'company': row['Company'].split('(')[0].strip(),
                    'score': float(row['Score']),
                })

    return leads


def build_collaboration_network(leads_authors_ids, max_papers=1000):
    """Build co-authorship network focused on investment leads."""
    papers_dir = Path(__file__).parent.parent / "data" / "papers"

    # Build network
    G = nx.Graph()
    author_names = {}
    author_companies = {}
    paper_count = 0

    print(f"   Scanning papers for collaborations...")

    for paper_file in papers_dir.glob("*.yaml"):
        if paper_count >= max_papers:
            break

        with open(paper_file) as f:
            paper = yaml.safe_load(f)

        # Only consider papers with decent PageRank
        if not paper.get('pagerank') or paper['pagerank'] < 0.0000005:
            continue

        authors = []
        for authorship in paper.get('authorships', []):
            author_id = authorship['author_id']
            authors.append(author_id)

            # Store name if it's one of our leads
            if author_id in leads_authors_ids:
                author_names[author_id] = authorship['display_name']

        # Add edges if any author is in our leads
        has_lead = any(aid in leads_authors_ids for aid in authors)

        if has_lead:
            for i, author1 in enumerate(authors):
                for author2 in authors[i+1:]:
                    if G.has_edge(author1, author2):
                        G[author1][author2]['weight'] += 1
                    else:
                        G.add_edge(author1, author2, weight=1)

        paper_count += 1

        if paper_count % 200 == 0:
            print(f"   Processed {paper_count} papers, {len(G.nodes())} authors, {len(G.edges())} collaborations")

    return G, author_names


def create_focused_network(top_n=100):
    """Create collaboration network focused on our investment leads."""
    print("📊 Creating focused collaboration network...")

    # Load our investment leads
    print("   Loading investment leads...")
    leads = load_investment_leads()
    leads_dict = {lead['author_id']: lead for lead in leads}
    leads_ids = set(leads_dict.keys())

    print(f"   Found {len(leads)} researchers at companies")

    # Build collaboration network
    G, author_names = build_collaboration_network(leads_ids, max_papers=2000)

    print(f"   Network has {len(G.nodes())} authors, {len(G.edges())} collaborations")

    # Filter to only show leads and their direct collaborators
    leads_with_connections = [nid for nid in leads_ids if nid in G and G.degree(nid) > 0]

    # Take top N by score
    leads_with_connections.sort(key=lambda aid: leads_dict.get(aid, {}).get('score', 0), reverse=True)
    focus_leads = leads_with_connections[:top_n]

    # Get all collaborators of these leads
    network_nodes = set(focus_leads)
    for lead_id in focus_leads:
        if lead_id in G:
            network_nodes.update(G.neighbors(lead_id))

    # Create subgraph
    subgraph = G.subgraph(network_nodes)

    print(f"   Focused network: {len(subgraph.nodes())} nodes, {len(subgraph.edges())} edges")

    # Create visualization
    plt.figure(figsize=(24, 20))

    # Layout
    pos = nx.spring_layout(subgraph, k=2.0, iterations=50, seed=42)

    # Separate leads from collaborators
    lead_nodes = [n for n in subgraph.nodes() if n in leads_ids]
    collab_nodes = [n for n in subgraph.nodes() if n not in leads_ids]

    # Draw edges
    edges = subgraph.edges()
    if edges:
        weights = [subgraph[u][v]['weight'] for u, v in edges]
        max_weight = max(weights) if weights else 1
        nx.draw_networkx_edges(subgraph, pos,
                              width=[w/max_weight * 2 for w in weights],
                              alpha=0.2,
                              edge_color='gray')

    # Draw collaborators (small, gray)
    if collab_nodes:
        nx.draw_networkx_nodes(collab_nodes, pos,
                              node_size=100,
                              node_color='lightgray',
                              alpha=0.5)

    # Draw investment leads (large, colored by score)
    if lead_nodes:
        scores = [leads_dict[n]['score'] for n in lead_nodes]
        node_sizes = [500 + s * 1000 for s in scores]  # Bigger = higher score

        nx.draw_networkx_nodes(lead_nodes, pos,
                              node_size=node_sizes,
                              node_color=scores,
                              cmap='YlOrRd',
                              vmin=0.3,
                              vmax=0.7,
                              alpha=0.9,
                              edgecolors='black',
                              linewidths=2)

    # Add labels for leads with company names
    labels = {}
    for aid in lead_nodes:
        lead = leads_dict.get(aid)
        if lead:
            name = lead['name']
            company = lead['company'][:15]  # Truncate long company names
            labels[aid] = f"{name}\n@{company}"

    # Draw labels with better positioning
    nx.draw_networkx_labels(subgraph, pos, labels,
                           font_size=9,
                           font_weight='bold',
                           font_color='black',
                           bbox=dict(boxstyle='round,pad=0.3',
                                   facecolor='white',
                                   edgecolor='none',
                                   alpha=0.7))

    plt.title(f"Collaboration Network: Top {top_n} Company-Affiliated Researchers\n" +
             f"(Node size = confidence score, Color = red = higher score)",
             fontsize=18, fontweight='bold', pad=20)
    plt.axis('off')
    plt.tight_layout()

    # Add colorbar legend
    sm = plt.cm.ScalarMappable(cmap='YlOrRd', norm=plt.Normalize(vmin=0.3, vmax=0.7))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=plt.gca(), fraction=0.046, pad=0.04)
    cbar.set_label('Confidence Score', fontsize=12)

    output_file = Path(__file__).parent.parent / "data" / "analysis" / "collaboration_network.png"
    plt.savefig(output_file, dpi=200, bbox_inches='tight')
    print(f"   ✅ Saved to {output_file}")
    plt.close()


def create_company_clusters():
    """Show which researchers at the same companies are connected."""
    print("\n📊 Creating company cluster network...")

    # Load investment leads
    leads = load_investment_leads()

    # Group by company
    companies = defaultdict(list)
    for lead in leads:
        companies[lead['company']].append(lead)

    # Only show companies with 2+ researchers
    multi_researcher_companies = {k: v for k, v in companies.items() if len(v) >= 2}

    print(f"   Found {len(multi_researcher_companies)} companies with 2+ researchers")

    # Create graph
    G = nx.Graph()
    colors = []
    labels = {}
    company_colors = {}

    # Assign colors to companies
    import matplotlib.cm as cm
    color_map = cm.get_cmap('tab10')
    for i, company in enumerate(sorted(multi_researcher_companies.keys())):
        company_colors[company] = color_map(i % 10)

    # Add nodes
    for company, researchers in multi_researcher_companies.items():
        for researcher in researchers:
            G.add_node(researcher['author_id'])
            colors.append(company_colors[company])
            labels[researcher['author_id']] = f"{researcher['name']}\n@{company[:12]}"

    # Create layout by company
    plt.figure(figsize=(20, 16))

    # Position nodes by company in clusters
    pos = {}
    angle_step = 2 * 3.14159 / len(multi_researcher_companies)

    for i, (company, researchers) in enumerate(sorted(multi_researcher_companies.items())):
        angle = i * angle_step
        # Company center
        cx = 5 * np.cos(angle)
        cy = 5 * np.sin(angle)

        # Arrange researchers around company center
        for j, researcher in enumerate(researchers):
            sub_angle = j * (2 * 3.14159 / len(researchers))
            pos[researcher['author_id']] = (
                cx + 1.5 * np.cos(sub_angle),
                cy + 1.5 * np.sin(sub_angle)
            )

    # Draw
    nx.draw_networkx_nodes(G, pos,
                          node_size=800,
                          node_color=colors,
                          alpha=0.8,
                          edgecolors='black',
                          linewidths=2)

    nx.draw_networkx_labels(G, pos, labels,
                           font_size=8,
                           font_weight='bold',
                           bbox=dict(boxstyle='round,pad=0.3',
                                   facecolor='white',
                                   alpha=0.7))

    plt.title("Companies with Multiple High-Impact Researchers\n" +
             "(Each color = different company)",
             fontsize=18, fontweight='bold', pad=20)
    plt.axis('off')
    plt.tight_layout()

    output_file = Path(__file__).parent.parent / "data" / "analysis" / "company_clusters.png"
    plt.savefig(output_file, dpi=200, bbox_inches='tight')
    print(f"   ✅ Saved to {output_file}")
    plt.close()


def main():
    """Create all collaboration visualizations."""
    print("="*80)
    print("📊 CREATING COLLABORATION VISUALIZATIONS")
    print("="*80)
    print()

    # Import numpy for positioning
    global np
    import numpy as np

    create_focused_network(top_n=30)
    create_company_clusters()

    print()
    print("="*80)
    print("✅ COLLABORATION VISUALIZATIONS COMPLETE")
    print("="*80)
    print("\nFiles created:")
    print("  • data/analysis/collaboration_network.png - Co-authorship network")
    print("  • data/analysis/company_clusters.png - Companies with multiple researchers")


if __name__ == "__main__":
    main()
