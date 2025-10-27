"""Batch fetch author profiles for all candidates."""

import asyncio
import yaml
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from citation_arbitrage.openalex_client import OpenAlexClient
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()


async def batch_fetch_authors(candidate_file: Path, output_dir: Path, batch_size: int = 50, delay: float = 0.2):
    """
    Fetch author profiles for all candidates in batches.

    Args:
        candidate_file: Path to grad_students.yaml
        output_dir: Directory to save author YAML files
        batch_size: Number of authors to fetch before showing progress
        delay: Delay between requests (seconds)
    """
    # Load candidates
    with open(candidate_file) as f:
        data = yaml.safe_load(f)

    candidates = data['candidates']
    author_ids = [c['author_id'] for c in candidates]

    console.print(f"[cyan]Fetching profiles for {len(author_ids)} candidates...")
    console.print(f"[yellow]This will take approximately {len(author_ids) * delay / 60:.1f} minutes")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Check which we already have
    existing = set(f.stem for f in output_dir.glob("*.yaml"))
    to_fetch = [aid for aid in author_ids if aid.split("/")[-1] not in existing]

    if to_fetch:
        console.print(f"[green]{len(existing)} already fetched, {len(to_fetch)} remaining")
    else:
        console.print(f"[green]All {len(author_ids)} authors already fetched!")
        return

    async with OpenAlexClient() as client:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("Fetching authors", total=len(to_fetch))

            fetched = 0
            failed = 0

            for author_id in to_fetch:
                try:
                    author = await client.fetch_author(author_id)

                    if author:
                        # Save to YAML
                        author_file = output_dir / f"{author_id.split('/')[-1]}.yaml"
                        with open(author_file, "w") as f:
                            yaml.dump(author.model_dump(mode="json"), f, default_flow_style=False)
                        fetched += 1
                    else:
                        failed += 1

                    progress.update(task, advance=1)
                    await asyncio.sleep(delay)

                except Exception as e:
                    console.print(f"[red]Error fetching {author_id}: {e}")
                    failed += 1
                    progress.update(task, advance=1)

    console.print(f"\n[green]✓ Fetched {fetched} new authors")
    if failed > 0:
        console.print(f"[yellow]⚠ Failed to fetch {failed} authors")


if __name__ == "__main__":
    candidate_file = Path("data/analysis/grad_students.yaml")
    output_dir = Path("data/authors")

    asyncio.run(batch_fetch_authors(candidate_file, output_dir))
