"""Command-line interface for Citation Arbitrage."""

import asyncio
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from .openalex_client import OpenAlexClient, save_papers_to_yaml, load_papers_from_yaml
from .citation_graph import CitationGraph, update_papers_with_pagerank
from .author_analysis import AuthorAnalyzer


console = Console()


@click.group()
def main():
    """Citation Arbitrage: Find overlooked startup opportunities by tracking influential researchers."""
    pass


@main.command()
@click.option("--from-year", default=2020, help="Start year for papers")
@click.option("--to-year", default=2025, help="End year for papers")
@click.option("--min-citations", default=100, help="Minimum citation count")
@click.option("--max-papers", default=None, type=int, help="Maximum papers to fetch")
@click.option("--email", default=None, help="Your email for OpenAlex polite pool")
@click.option("--output-dir", default="data/papers", help="Output directory for YAML files")
def fetch_papers(from_year, to_year, min_citations, max_papers, email, output_dir):
    """Fetch influential papers from OpenAlex."""
    async def _fetch():
        async with OpenAlexClient(email=email) as client:
            papers = await client.fetch_papers(
                from_year=from_year,
                to_year=to_year,
                min_citations=min_citations,
                max_papers=max_papers
            )

            console.print(f"[green]✓ Fetched {len(papers)} papers")

            # Save to YAML
            output_path = Path(output_dir)
            save_papers_to_yaml(papers, output_path)
            console.print(f"[green]✓ Saved papers to {output_path}")

            return papers

    asyncio.run(_fetch())


@main.command()
@click.option("--papers-dir", default="data/papers", help="Directory with paper YAML files")
@click.option("--output", default="data/analysis/citation_graph.yaml", help="Output file for graph")
@click.option("--top-n", default=100, help="Number of top papers to show")
def compute_pagerank(papers_dir, output, top_n):
    """Build citation graph and compute PageRank."""
    # Load papers
    papers_path = Path(papers_dir)
    console.print(f"[cyan]Loading papers from {papers_path}...")
    papers = load_papers_from_yaml(papers_path)
    console.print(f"[green]✓ Loaded {len(papers)} papers")

    # Build citation graph
    cg = CitationGraph()
    cg.build_from_papers(papers)

    # Compute PageRank
    pagerank_scores = cg.compute_pagerank()

    # Update papers with PageRank
    papers = update_papers_with_pagerank(papers, pagerank_scores)

    # Save updated papers
    save_papers_to_yaml(papers, papers_path)
    console.print(f"[green]✓ Updated papers with PageRank scores")

    # Save graph
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cg.save_graph(output_path)

    # Show top papers
    console.print(f"\n[bold cyan]Top {top_n} Papers by PageRank:[/bold cyan]\n")
    top_papers = cg.get_top_papers_by_pagerank(papers, top_n=top_n)

    from rich.table import Table
    table = Table(title=f"Top {min(top_n, len(top_papers))} Papers")
    table.add_column("Rank", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Year", style="yellow")
    table.add_column("Citations", style="blue")
    table.add_column("PageRank", style="magenta")

    for rank, (paper, pagerank) in enumerate(top_papers[:20], 1):
        table.add_row(
            str(rank),
            paper.title[:60] + "..." if len(paper.title) > 60 else paper.title,
            str(paper.publication_year),
            str(paper.cited_by_count),
            f"{pagerank:.6f}"
        )

    console.print(table)


@main.command()
@click.option("--papers-dir", default="data/papers", help="Directory with paper YAML files")
@click.option("--output", default="data/analysis/grad_students.yaml", help="Output file")
@click.option("--min-score", default=0.3, type=float, help="Minimum confidence score")
def identify_grad_students(papers_dir, output, min_score):
    """Identify grad students from paper authorships."""
    # Load papers
    papers_path = Path(papers_dir)
    console.print(f"[cyan]Loading papers from {papers_path}...")
    papers = load_papers_from_yaml(papers_path)
    console.print(f"[green]✓ Loaded {len(papers)} papers")

    # Analyze authors
    analyzer = AuthorAnalyzer()
    candidates = analyzer.identify_grad_students(papers)

    # Filter by minimum score
    filtered_candidates = [(aid, score) for aid, score in candidates if score >= min_score]

    console.print(f"[green]✓ Found {len(filtered_candidates)} candidates above score {min_score}")

    # Generate report
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    analyzer.generate_report(filtered_candidates, papers, output_path)


@main.command()
@click.option("--author-ids", required=True, help="Comma-separated author IDs to fetch")
@click.option("--email", default=None, help="Your email for OpenAlex polite pool")
@click.option("--output-dir", default="data/authors", help="Output directory for author data")
def fetch_authors(author_ids, email, output_dir):
    """Fetch detailed author information from OpenAlex."""
    async def _fetch():
        author_id_list = [aid.strip() for aid in author_ids.split(",")]

        async with OpenAlexClient(email=email) as client:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            for author_id in author_id_list:
                console.print(f"[cyan]Fetching author {author_id}...")

                author = await client.fetch_author(author_id)

                if author:
                    # Save to YAML
                    author_file = output_path / f"{author_id.split('/')[-1]}.yaml"
                    import yaml
                    with open(author_file, "w") as f:
                        yaml.dump(author.model_dump(mode="json"), f, default_flow_style=False)

                    console.print(f"[green]✓ Saved {author.display_name} to {author_file}")
                else:
                    console.print(f"[yellow]⚠ Author {author_id} not found")

    asyncio.run(_fetch())


@main.command()
@click.option("--papers-dir", default="data/papers", help="Directory with paper YAML files")
@click.option("--top-n", default=20, help="Number of top papers to show")
def show_top_papers(papers_dir, top_n):
    """Show top papers by combined PageRank and citation score."""
    # Load papers
    papers_path = Path(papers_dir)
    console.print(f"[cyan]Loading papers from {papers_path}...")
    papers = load_papers_from_yaml(papers_path)
    console.print(f"[green]✓ Loaded {len(papers)} papers")

    # Filter papers with PageRank
    papers_with_pr = [p for p in papers if p.pagerank and p.pagerank > 0]

    if not papers_with_pr:
        console.print("[red]No papers with PageRank found. Run 'compute-pagerank' first.")
        return

    # Sort by PageRank
    papers_with_pr.sort(key=lambda p: p.pagerank or 0, reverse=True)

    from rich.table import Table
    table = Table(title=f"Top {min(top_n, len(papers_with_pr))} Papers")
    table.add_column("Rank", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Year", style="yellow")
    table.add_column("Citations", style="blue")
    table.add_column("PageRank", style="magenta")
    table.add_column("First Author", style="red")

    for rank, paper in enumerate(papers_with_pr[:top_n], 1):
        first_author = "Unknown"
        if paper.authorships:
            first_auth = next((a for a in paper.authorships if a.author_position == "first"),
                            paper.authorships[0])
            first_author = first_auth.display_name[:30]

        table.add_row(
            str(rank),
            paper.title[:50] + "..." if len(paper.title) > 50 else paper.title,
            str(paper.publication_year),
            str(paper.cited_by_count),
            f"{paper.pagerank:.6f}",
            first_author
        )

    console.print(table)


if __name__ == "__main__":
    main()
