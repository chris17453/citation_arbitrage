"""Build citation graphs and compute PageRank."""

from pathlib import Path
from typing import List, Dict, Tuple
import yaml

import networkx as nx
from rich.console import Console
from rich.progress import track

from .models import Paper


console = Console()


class CitationGraph:
    """Citation graph with PageRank computation."""

    def __init__(self):
        """Initialize an empty citation graph."""
        self.graph = nx.DiGraph()
        self.pagerank_scores: Dict[str, float] = {}

    def add_paper(self, paper: Paper):
        """Add a paper to the citation graph."""
        self.graph.add_node(
            paper.id,
            title=paper.title,
            year=paper.publication_year,
            citations=paper.cited_by_count
        )

        # Add edges for references (this paper cites these works)
        for ref_id in paper.referenced_works:
            self.graph.add_edge(paper.id, ref_id)

    def build_from_papers(self, papers: List[Paper]):
        """
        Build citation graph from a list of papers.

        Args:
            papers: List of Paper objects
        """
        console.print(f"[cyan]Building citation graph from {len(papers)} papers...")

        for paper in track(papers, description="Adding papers to graph"):
            self.add_paper(paper)

        console.print(f"[green]✓ Graph built: {self.graph.number_of_nodes()} nodes, "
                     f"{self.graph.number_of_edges()} edges")

    def compute_pagerank(self, alpha: float = 0.85, max_iter: int = 100) -> Dict[str, float]:
        """
        Compute PageRank scores for all papers in the graph.

        Args:
            alpha: Damping parameter (probability of following a link)
            max_iter: Maximum number of iterations

        Returns:
            Dictionary mapping paper IDs to PageRank scores
        """
        console.print(f"[cyan]Computing PageRank (alpha={alpha}, max_iter={max_iter})...")

        if self.graph.number_of_nodes() == 0:
            console.print("[red]Error: Graph is empty!")
            return {}

        try:
            self.pagerank_scores = nx.pagerank(
                self.graph,
                alpha=alpha,
                max_iter=max_iter,
                tol=1e-6
            )
            console.print(f"[green]✓ PageRank computed for {len(self.pagerank_scores)} papers")
            return self.pagerank_scores

        except nx.PowerIterationFailedConvergence as e:
            console.print(f"[yellow]Warning: PageRank did not converge: {e}")
            # Return partial results if available
            return {}

    def get_top_papers_by_pagerank(self, papers: List[Paper], top_n: int = 100) -> List[Tuple[Paper, float]]:
        """
        Get the top N papers by PageRank score.

        Args:
            papers: List of Paper objects
            top_n: Number of top papers to return

        Returns:
            List of (Paper, pagerank_score) tuples, sorted by PageRank descending
        """
        if not self.pagerank_scores:
            console.print("[yellow]PageRank not computed yet. Computing now...")
            self.compute_pagerank()

        # Map paper IDs to Paper objects
        paper_map = {p.id: p for p in papers}

        # Get papers with their PageRank scores
        paper_scores = [
            (paper_map[paper_id], score)
            for paper_id, score in self.pagerank_scores.items()
            if paper_id in paper_map
        ]

        # Sort by PageRank descending
        paper_scores.sort(key=lambda x: x[1], reverse=True)

        return paper_scores[:top_n]

    def get_top_papers_by_combined_score(
        self,
        papers: List[Paper],
        top_n: int = 100,
        pagerank_weight: float = 0.7,
        citation_weight: float = 0.3
    ) -> List[Tuple[Paper, float, float, float]]:
        """
        Get top papers by a combined score of PageRank and citation count.

        Args:
            papers: List of Paper objects
            top_n: Number of top papers to return
            pagerank_weight: Weight for PageRank score (0-1)
            citation_weight: Weight for normalized citation count (0-1)

        Returns:
            List of (Paper, combined_score, pagerank, norm_citations) tuples
        """
        if not self.pagerank_scores:
            console.print("[yellow]PageRank not computed yet. Computing now...")
            self.compute_pagerank()

        # Normalize scores
        max_citations = max(p.cited_by_count for p in papers) if papers else 1
        max_pagerank = max(self.pagerank_scores.values()) if self.pagerank_scores else 1

        # Compute combined scores
        paper_scores = []
        for paper in papers:
            if paper.id not in self.pagerank_scores:
                continue

            norm_pagerank = self.pagerank_scores[paper.id] / max_pagerank
            norm_citations = paper.cited_by_count / max_citations

            combined_score = (
                pagerank_weight * norm_pagerank +
                citation_weight * norm_citations
            )

            paper_scores.append((paper, combined_score, norm_pagerank, norm_citations))

        # Sort by combined score descending
        paper_scores.sort(key=lambda x: x[1], reverse=True)

        return paper_scores[:top_n]

    def analyze_author_influence(self, author_id: str, papers: List[Paper]) -> Dict[str, any]:
        """
        Analyze an author's influence based on their papers' PageRank scores.

        Args:
            author_id: OpenAlex author ID
            papers: List of Paper objects

        Returns:
            Dictionary with influence metrics
        """
        if not self.pagerank_scores:
            console.print("[yellow]PageRank not computed yet. Computing now...")
            self.compute_pagerank()

        # Find papers by this author
        author_papers = [
            p for p in papers
            if any(auth.author_id == author_id for auth in p.authorships)
        ]

        if not author_papers:
            return {
                "paper_count": 0,
                "avg_pagerank": 0.0,
                "max_pagerank": 0.0,
                "total_pagerank": 0.0,
            }

        # Get PageRank scores for author's papers
        pagerank_values = [
            self.pagerank_scores.get(p.id, 0.0)
            for p in author_papers
        ]

        # Find first-author papers (typically grad student work)
        first_author_papers = [
            p for p in author_papers
            if any(auth.author_id == author_id and auth.author_position == "first"
                   for auth in p.authorships)
        ]

        first_author_pageranks = [
            self.pagerank_scores.get(p.id, 0.0)
            for p in first_author_papers
        ]

        return {
            "paper_count": len(author_papers),
            "first_author_count": len(first_author_papers),
            "avg_pagerank": sum(pagerank_values) / len(pagerank_values) if pagerank_values else 0.0,
            "max_pagerank": max(pagerank_values) if pagerank_values else 0.0,
            "total_pagerank": sum(pagerank_values),
            "first_author_avg_pagerank": sum(first_author_pageranks) / len(first_author_pageranks)
                if first_author_pageranks else 0.0,
            "top_papers": sorted(
                [(p.title, self.pagerank_scores.get(p.id, 0.0)) for p in author_papers],
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }

    def save_graph(self, output_path: Path):
        """Save the citation graph to a file."""
        console.print(f"[cyan]Saving graph to {output_path}...")

        # Save graph structure
        graph_data = {
            "nodes": len(self.graph.nodes),
            "edges": len(self.graph.edges),
            "pagerank_scores": self.pagerank_scores
        }

        with open(output_path, "w") as f:
            yaml.dump(graph_data, f, default_flow_style=False)

        # Also save as GraphML for visualization
        graphml_path = output_path.with_suffix(".graphml")
        nx.write_graphml(self.graph, graphml_path)

        console.print(f"[green]✓ Graph saved to {output_path} and {graphml_path}")

    @classmethod
    def load_graph(cls, input_path: Path) -> "CitationGraph":
        """Load a citation graph from a file."""
        console.print(f"[cyan]Loading graph from {input_path}...")

        cg = cls()

        with open(input_path, "r") as f:
            data = yaml.safe_load(f)
            cg.pagerank_scores = data.get("pagerank_scores", {})

        # Load GraphML if available
        graphml_path = input_path.with_suffix(".graphml")
        if graphml_path.exists():
            cg.graph = nx.read_graphml(graphml_path)

        console.print(f"[green]✓ Graph loaded")
        return cg


def update_papers_with_pagerank(papers: List[Paper], pagerank_scores: Dict[str, float]) -> List[Paper]:
    """
    Update Paper objects with their PageRank scores.

    Args:
        papers: List of Paper objects
        pagerank_scores: Dictionary mapping paper IDs to PageRank scores

    Returns:
        List of updated Paper objects
    """
    for paper in papers:
        paper.pagerank = pagerank_scores.get(paper.id, 0.0)

    return papers
