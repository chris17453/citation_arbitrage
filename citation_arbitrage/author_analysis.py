"""Analyze authors and identify grad students at time of publication."""

from typing import List, Dict, Set, Tuple, Optional
from pathlib import Path
import yaml

from rich.console import Console
from rich.table import Table
from rich.progress import track

from .models import Paper, Author, CareerStatus, InstitutionType, AffiliationPeriod


console = Console()


class AuthorAnalyzer:
    """Analyze authors to identify grad students and track career transitions."""

    def __init__(self):
        """Initialize the author analyzer."""
        self.authors: Dict[str, Author] = {}

    def identify_grad_students(
        self,
        papers: List[Paper],
        current_year: int = 2025
    ) -> List[Tuple[str, float]]:
        """
        Identify authors who were likely grad students when they published key work.

        Heuristics:
        1. First author on highly-ranked papers
        2. Affiliated with education institutions at time of publication
        3. Published 2-8 papers in a 4-6 year window (typical PhD)
        4. Has since moved to different institution (indicates career transition)

        Args:
            papers: List of Paper objects (should have PageRank computed)
            current_year: Current year for age calculations

        Returns:
            List of (author_id, confidence_score) tuples
        """
        console.print("[cyan]Identifying grad students from paper authorships...")

        # Collect first/second authors from top papers
        candidate_authors: Dict[str, List[Paper]] = {}

        for paper in papers:
            # Only consider papers with good PageRank or high citations
            if (paper.pagerank or 0) < 0.0001 and paper.cited_by_count < 500:
                continue

            for authorship in paper.authorships:
                # Focus on first and second authors (typical grad student positions)
                if authorship.author_position in ["first", "middle"]:
                    # Check if at educational institution
                    is_at_university = any(
                        inst.type == InstitutionType.EDUCATION
                        for inst in authorship.institutions
                    )

                    if is_at_university or not authorship.institutions:
                        author_id = authorship.author_id
                        if author_id not in candidate_authors:
                            candidate_authors[author_id] = []
                        candidate_authors[author_id].append(paper)

        console.print(f"[green]Found {len(candidate_authors)} candidate authors")

        # Score each candidate
        scored_candidates = []
        for author_id, author_papers in track(
            candidate_authors.items(),
            description="Scoring candidates"
        ):
            score = self._score_grad_student_likelihood(
                author_id,
                author_papers,
                current_year
            )

            if score > 0.3:  # Threshold for inclusion
                scored_candidates.append((author_id, score))

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        console.print(f"[green]✓ Identified {len(scored_candidates)} likely grad students")

        return scored_candidates

    def _score_grad_student_likelihood(
        self,
        author_id: str,
        papers: List[Paper],
        current_year: int
    ) -> float:
        """
        Score how likely this author was a grad student during these publications.

        Returns:
            Score between 0.0 and 1.0
        """
        score = 0.0

        # Factor 1: First authorship (strong signal)
        first_author_count = sum(
            1 for paper in papers
            if any(auth.author_id == author_id and auth.author_position == "first"
                   for auth in paper.authorships)
        )
        first_author_ratio = first_author_count / len(papers) if papers else 0
        score += 0.3 * first_author_ratio

        # Factor 2: Publication timeline (typical PhD is 4-6 years)
        if papers:
            years = sorted(p.publication_year for p in papers)
            year_span = years[-1] - years[0]

            if 2 <= year_span <= 8:  # Typical PhD timeline
                score += 0.2
            elif year_span < 2:  # Might be a sprint/specific project
                score += 0.1

        # Factor 3: Paper count (2-10 papers is typical for a PhD)
        paper_count = len(papers)
        if 2 <= paper_count <= 10:
            score += 0.2
        elif paper_count == 1 and papers[0].pagerank and papers[0].pagerank > 0.001:
            # One blockbuster paper can be enough
            score += 0.15

        # Factor 4: Educational affiliation
        edu_affiliation_ratio = sum(
            1 for paper in papers
            if any(
                any(inst.type == InstitutionType.EDUCATION for inst in auth.institutions)
                for auth in paper.authorships
                if auth.author_id == author_id
            )
        ) / len(papers) if papers else 0

        score += 0.2 * edu_affiliation_ratio

        # Factor 5: PageRank of papers (high-impact work)
        if papers and any(p.pagerank for p in papers):
            avg_pagerank = sum(p.pagerank or 0 for p in papers) / len(papers)
            # Normalize (rough approximation)
            normalized_pagerank = min(avg_pagerank * 10000, 1.0)
            score += 0.1 * normalized_pagerank

        return min(score, 1.0)

    def add_author(self, author: Author):
        """Add an author to the analyzer."""
        self.authors[author.id] = author

    def analyze_career_transition(
        self,
        author: Author,
        papers: List[Paper]
    ) -> Dict[str, any]:
        """
        Analyze an author's career transition based on their publication and affiliation history.

        Args:
            author: Author object
            papers: List of all papers (to find author's papers)

        Returns:
            Dictionary with career transition info
        """
        # Find papers by this author
        author_papers = [
            p for p in papers
            if any(auth.author_id == author.id for auth in p.authorships)
        ]

        if not author_papers:
            return {"has_data": False}

        # Sort papers by year
        author_papers.sort(key=lambda p: p.publication_year)

        # Analyze affiliation changes
        affiliation_timeline = []
        for paper in author_papers:
            for authorship in paper.authorships:
                if authorship.author_id == author.id:
                    affiliation_timeline.append({
                        "year": paper.publication_year,
                        "institutions": [inst.display_name for inst in authorship.institutions],
                        "institution_types": [inst.type.value for inst in authorship.institutions]
                    })

        # Detect transition from education to industry/startup
        education_years = [
            item["year"] for item in affiliation_timeline
            if "education" in item["institution_types"]
        ]

        industry_years = [
            item["year"] for item in affiliation_timeline
            if "company" in item["institution_types"]
        ]

        transition_detected = False
        transition_year = None

        if education_years and industry_years:
            last_edu_year = max(education_years)
            first_industry_year = min(industry_years)

            if first_industry_year > last_edu_year:
                transition_detected = True
                transition_year = first_industry_year

        return {
            "has_data": True,
            "total_papers": len(author_papers),
            "first_paper_year": author_papers[0].publication_year,
            "latest_paper_year": author_papers[-1].publication_year,
            "affiliation_timeline": affiliation_timeline,
            "transition_detected": transition_detected,
            "transition_year": transition_year,
            "current_status": author.current_status.value,
            "current_institution": author.current_institution.display_name
                if author.current_institution else None
        }

    def generate_report(
        self,
        top_authors: List[Tuple[str, float]],
        papers: List[Paper],
        output_path: Optional[Path] = None
    ):
        """
        Generate a report of top grad student candidates.

        Args:
            top_authors: List of (author_id, score) tuples
            papers: List of all papers
            output_path: Optional path to save YAML report
        """
        table = Table(title="Top Grad Student Candidates")
        table.add_column("Rank", style="cyan")
        table.add_column("Author ID", style="green")
        table.add_column("Score", style="yellow")
        table.add_column("Papers", style="blue")
        table.add_column("First Author", style="magenta")
        table.add_column("Avg PageRank", style="red")

        report_data = []

        # Process ALL authors for YAML, but only show top 50 in table
        for rank, (author_id, score) in enumerate(top_authors, 1):
            # Find author's papers
            author_papers = [
                p for p in papers
                if any(auth.author_id == author_id for auth in p.authorships)
            ]

            first_author_count = sum(
                1 for paper in author_papers
                if any(auth.author_id == author_id and auth.author_position == "first"
                       for auth in paper.authorships)
            )

            avg_pagerank = sum(p.pagerank or 0 for p in author_papers) / len(author_papers) \
                if author_papers else 0

            # Only add to table if in top 50
            if rank <= 50:
                table.add_row(
                    str(rank),
                    author_id.split("/")[-1][:20],
                    f"{score:.3f}",
                    str(len(author_papers)),
                    str(first_author_count),
                    f"{avg_pagerank:.6f}"
                )

            # Collect ALL for YAML output
            if output_path:
                report_data.append({
                    "rank": rank,
                    "author_id": author_id,
                    "score": float(score),
                    "paper_count": len(author_papers),
                    "first_author_count": first_author_count,
                    "avg_pagerank": float(avg_pagerank),
                    "paper_ids": [p.id for p in author_papers]
                })

        console.print(table)

        if output_path:
            with open(output_path, "w") as f:
                yaml.dump({"candidates": report_data}, f, default_flow_style=False)
            console.print(f"[green]✓ Report saved to {output_path}")
