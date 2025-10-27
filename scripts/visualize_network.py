"""Visualize the citation network and author relationships."""

import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
import yaml
from collections import defaultdict


def load_graph(graphml_path: Path) -> nx.DiGraph:
    """Load citation graph from GraphML."""
    return nx.read_graphml(graphml_path)


def visualize_top_papers_subgraph(papers_dir: Path, graphml_path: Path, top_n: int = 50):
    """
    Visualize the citation network for top N papers by PageRank.
    """
    # Load papers with PageRank
    papers = []
    for paper_file in papers_dir.glob("*.yaml"):
        with open(paper_file) as f:
            paper = yaml.safe_load(f)
            if paper.get('pagerank'):
                papers.append(paper)

    # Sort by PageRank
    papers.sort(key=lambda p: p['pagerank'], reverse=True)
    top_papers = papers[:top_n]
    top_paper_ids = set(p['id'] for p in top_papers)

    # Load full graph
    G = load_graph(graphml_path)

    # Create subgraph with top papers and their direct connections
    subgraph_nodes = set()
    for paper_id in top_paper_ids:
        if paper_id in G:
            subgraph_nodes.add(paper_id)
            # Add papers that cite this one
            subgraph_nodes.update(G.predecessors(paper_id))
            # Add papers this one cites
            subgraph_nodes.update(G.successors(paper_id))

    subgraph = G.subgraph(subgraph_nodes)

    # Create layout
    pos = nx.spring_layout(subgraph, k=0.5, iterations=50)

    # Draw
    plt.figure(figsize=(20, 20))

    # Draw edges
    nx.draw_networkx_edges(subgraph, pos, alpha=0.2, arrows=True, arrowsize=10)

    # Draw top papers in red
    top_paper_nodes = [n for n in subgraph.nodes() if n in top_paper_ids]
    other_nodes = [n for n in subgraph.nodes() if n not in top_paper_ids]

    nx.draw_networkx_nodes(other_nodes, pos, node_size=20, node_color='lightblue', alpha=0.6)
    nx.draw_networkx_nodes(top_paper_nodes, pos, node_size=200, node_color='red', alpha=0.9)

    plt.title(f"Citation Network: Top {top_n} Papers by PageRank (red) and their connections",
              fontsize=16)
    plt.axis('off')
    plt.tight_layout()

    output_file = Path("data/analysis/citation_network.png")
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Saved visualization to {output_file}")
    plt.close()


def visualize_author_collaboration_network(papers_dir: Path, top_n: int = 100):
    """
    Visualize collaboration network of top authors.
    """
    # Load papers
    papers = []
    for paper_file in papers_dir.glob("*.yaml"):
        with open(paper_file) as f:
            papers.append(yaml.safe_load(f))

    # Build co-authorship graph
    G = nx.Graph()
    author_names = {}
    author_paper_counts = defaultdict(int)

    for paper in papers:
        if not paper.get('pagerank') or paper['pagerank'] < 0.000001:
            continue

        authors = [a['author_id'] for a in paper.get('authorships', [])]

        # Add nodes
        for authorship in paper.get('authorships', []):
            author_id = authorship['author_id']
            author_names[author_id] = authorship['display_name']
            author_paper_counts[author_id] += 1

        # Add edges between co-authors
        for i, author1 in enumerate(authors):
            for author2 in authors[i+1:]:
                if G.has_edge(author1, author2):
                    G[author1][author2]['weight'] += 1
                else:
                    G.add_edge(author1, author2, weight=1)

    # Get top authors by paper count
    top_authors = sorted(author_paper_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_author_ids = set(aid for aid, _ in top_authors)

    # Create subgraph
    subgraph = G.subgraph(top_author_ids)

    if len(subgraph.nodes()) == 0:
        print("No collaboration network to visualize")
        return

    # Create layout
    pos = nx.spring_layout(subgraph, k=1.0, iterations=50)

    # Draw
    plt.figure(figsize=(20, 20))

    # Draw edges with weight-based alpha
    edges = subgraph.edges()
    weights = [subgraph[u][v]['weight'] for u, v in edges]
    max_weight = max(weights) if weights else 1

    nx.draw_networkx_edges(subgraph, pos,
                          width=[w/max_weight * 3 for w in weights],
                          alpha=0.3)

    # Draw nodes sized by paper count
    node_sizes = [author_paper_counts[node] * 50 for node in subgraph.nodes()]
    nx.draw_networkx_nodes(subgraph, pos,
                          node_size=node_sizes,
                          node_color='lightgreen',
                          alpha=0.7)

    # Add labels for top 20
    top_20 = dict(top_authors[:20])
    labels = {aid: author_names.get(aid, aid.split('/')[-1])[:20]
              for aid in subgraph.nodes() if aid in top_20}
    nx.draw_networkx_labels(subgraph, pos, labels, font_size=8)

    plt.title(f"Author Collaboration Network: Top {top_n} Authors by Paper Count",
              fontsize=16)
    plt.axis('off')
    plt.tight_layout()

    output_file = Path("data/analysis/collaboration_network.png")
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Saved visualization to {output_file}")
    plt.close()


def create_pagerank_histogram(papers_dir: Path):
    """Create histogram of PageRank scores."""
    papers = []
    for paper_file in papers_dir.glob("*.yaml"):
        with open(paper_file) as f:
            paper = yaml.safe_load(f)
            if paper.get('pagerank'):
                papers.append(paper)

    pageranks = [p['pagerank'] for p in papers]

    plt.figure(figsize=(12, 6))
    plt.hist(pageranks, bins=100, log=True, alpha=0.7)
    plt.xlabel('PageRank Score')
    plt.ylabel('Number of Papers (log scale)')
    plt.title(f'Distribution of PageRank Scores ({len(papers)} papers)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    output_file = Path("data/analysis/pagerank_distribution.png")
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Saved histogram to {output_file}")
    plt.close()


if __name__ == "__main__":
    papers_dir = Path("data/papers")
    graphml_path = Path("data/analysis/citation_graph.graphml")

    print("Creating visualizations...")
    print("\n1. PageRank distribution histogram...")
    create_pagerank_histogram(papers_dir)

    print("\n2. Author collaboration network...")
    visualize_author_collaboration_network(papers_dir, top_n=100)

    print("\n3. Citation network (this may take a while)...")
    visualize_top_papers_subgraph(papers_dir, graphml_path, top_n=50)

    print("\n✓ All visualizations complete!")
    print("\nFiles created:")
    print("  - data/analysis/pagerank_distribution.png")
    print("  - data/analysis/collaboration_network.png")
    print("  - data/analysis/citation_network.png")
