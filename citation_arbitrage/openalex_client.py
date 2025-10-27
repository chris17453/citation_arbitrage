"""Client for OpenAlex API."""

import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
import yaml
from pathlib import Path

import httpx
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID

from .models import Paper, Author, Authorship, Institution, InstitutionType


class OpenAlexClient:
    """Client for fetching data from OpenAlex API."""

    BASE_URL = "https://api.openalex.org"

    def __init__(self, email: Optional[str] = None):
        """
        Initialize the OpenAlex client.

        Args:
            email: Your email for the polite pool (gets faster API access)
        """
        self.email = email
        self.session = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()

    def _add_email_to_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add email to params for polite pool access."""
        if self.email:
            params["mailto"] = self.email
        return params

    async def fetch_papers(
        self,
        from_year: int = 2020,
        to_year: int = 2025,
        min_citations: int = 100,
        per_page: int = 200,
        max_papers: Optional[int] = None,
    ) -> List[Paper]:
        """
        Fetch influential papers from OpenAlex.

        Args:
            from_year: Start year for publication date
            to_year: End year for publication date
            min_citations: Minimum citation count
            per_page: Papers per API request
            max_papers: Maximum number of papers to fetch (None for all)

        Returns:
            List of Paper objects
        """
        papers = []
        page = 1

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:

            task = progress.add_task(
                f"Fetching papers ({from_year}-{to_year}, {min_citations}+ citations)...",
                total=None
            )

            while True:
                if max_papers and len(papers) >= max_papers:
                    break

                params = {
                    "filter": f"from_publication_date:{from_year}-01-01,to_publication_date:{to_year}-12-31,cited_by_count:>{min_citations}",
                    "per_page": per_page,
                    "page": page,
                }
                params = self._add_email_to_params(params)

                response = await self.session.get(f"{self.BASE_URL}/works", params=params)
                response.raise_for_status()
                data = response.json()

                if not data["results"]:
                    break

                for work_data in data["results"]:
                    if max_papers and len(papers) >= max_papers:
                        break

                    paper = self._parse_paper(work_data)
                    papers.append(paper)

                progress.update(task, completed=len(papers))
                page += 1

                # Rate limiting
                await asyncio.sleep(0.1)

        return papers

    def _parse_paper(self, data: Dict[str, Any]) -> Paper:
        """Parse paper data from OpenAlex API response."""
        authorships = []
        for auth_data in data.get("authorships", []):
            author = auth_data.get("author", {})
            institutions = [
                Institution(
                    id=inst.get("id", ""),
                    display_name=inst.get("display_name", ""),
                    ror=inst.get("ror"),
                    country_code=inst.get("country_code"),
                    type=InstitutionType(inst.get("type", "unknown").lower())
                        if inst.get("type") else InstitutionType.UNKNOWN
                )
                for inst in auth_data.get("institutions", [])
            ]

            authorship = Authorship(
                author_id=author.get("id", ""),
                display_name=author.get("display_name", ""),
                orcid=author.get("orcid"),
                author_position=auth_data.get("author_position", "middle"),
                institutions=institutions,
                is_corresponding=auth_data.get("is_corresponding", False),
                raw_affiliation_strings=auth_data.get("raw_affiliation_strings", [])
            )
            authorships.append(authorship)

        # Parse publication date
        pub_date_str = data.get("publication_date")
        pub_date = datetime.fromisoformat(pub_date_str).date() if pub_date_str else None

        # Get citation percentile
        citation_percentile = None
        if data.get("citation_normalized_percentile"):
            citation_percentile = data["citation_normalized_percentile"].get("value")

        # Get primary topic
        primary_topic = None
        if data.get("primary_topic"):
            primary_topic = data["primary_topic"].get("display_name")

        return Paper(
            id=data.get("id", ""),
            doi=data.get("doi"),
            title=data.get("title", ""),
            publication_date=pub_date,
            publication_year=data.get("publication_year", 0),
            cited_by_count=data.get("cited_by_count", 0),
            citation_percentile=citation_percentile,
            authorships=authorships,
            referenced_works=data.get("referenced_works", []),
            primary_topic=primary_topic,
            open_access=data.get("open_access", {}).get("is_oa", False)
        )

    async def fetch_author(self, author_id: str) -> Optional[Author]:
        """
        Fetch detailed author information.

        Args:
            author_id: OpenAlex author ID

        Returns:
            Author object or None if not found
        """
        # Clean the author_id to get just the ID part
        author_id_clean = author_id.split("/")[-1]

        params = self._add_email_to_params({})
        response = await self.session.get(
            f"{self.BASE_URL}/authors/{author_id_clean}",
            params=params
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        data = response.json()

        return self._parse_author(data)

    def _parse_author(self, data: Dict[str, Any]) -> Author:
        """Parse author data from OpenAlex API response."""
        from .models import AffiliationPeriod, CareerStatus

        # Parse affiliation history
        affiliation_history = []
        for aff_data in data.get("affiliations", []):
            inst_data = aff_data.get("institution", {})
            years = aff_data.get("years", [])

            institution = Institution(
                id=inst_data.get("id", ""),
                display_name=inst_data.get("display_name", ""),
                ror=inst_data.get("ror"),
                country_code=inst_data.get("country_code"),
                type=InstitutionType(inst_data.get("type", "unknown").lower())
                    if inst_data.get("type") else InstitutionType.UNKNOWN
            )

            period = AffiliationPeriod(
                institution=institution,
                start_year=min(years) if years else None,
                end_year=max(years) if years else None
            )
            affiliation_history.append(period)

        # Get current institution
        current_institution = None
        if data.get("last_known_institutions"):
            inst_data = data["last_known_institutions"][0]
            current_institution = Institution(
                id=inst_data.get("id", ""),
                display_name=inst_data.get("display_name", ""),
                ror=inst_data.get("ror"),
                country_code=inst_data.get("country_code"),
                type=InstitutionType(inst_data.get("type", "unknown").lower())
                    if inst_data.get("type") else InstitutionType.UNKNOWN
            )

        # Determine career status based on current institution type
        current_status = CareerStatus.UNKNOWN
        if current_institution:
            if current_institution.type == InstitutionType.COMPANY:
                current_status = CareerStatus.INDUSTRY
            elif current_institution.type == InstitutionType.EDUCATION:
                current_status = CareerStatus.PROFESSOR  # Simplified assumption

        # Get summary stats
        summary_stats = data.get("summary_stats", {})

        return Author(
            id=data.get("id", ""),
            orcid=data.get("orcid"),
            display_name=data.get("display_name", ""),
            affiliation_history=affiliation_history,
            current_institution=current_institution,
            current_status=current_status,
            works_count=data.get("works_count", 0),
            cited_by_count=data.get("cited_by_count", 0),
            h_index=summary_stats.get("h_index")
        )

    async def fetch_paper_citations(self, paper_id: str) -> List[str]:
        """
        Fetch all papers that cite this paper.

        Args:
            paper_id: OpenAlex paper ID

        Returns:
            List of citing paper IDs
        """
        paper_id_clean = paper_id.split("/")[-1]
        citations = []
        page = 1

        while True:
            params = {
                "filter": f"cites:{paper_id_clean}",
                "per_page": 200,
                "page": page,
            }
            params = self._add_email_to_params(params)

            response = await self.session.get(f"{self.BASE_URL}/works", params=params)
            response.raise_for_status()
            data = response.json()

            if not data["results"]:
                break

            citations.extend([work["id"] for work in data["results"]])
            page += 1

            # Rate limiting
            await asyncio.sleep(0.1)

        return citations


def save_papers_to_yaml(papers: List[Paper], output_dir: Path):
    """Save papers to YAML files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for paper in papers:
        # Use the paper ID as filename (sanitized)
        paper_id = paper.id.split("/")[-1]
        output_file = output_dir / f"{paper_id}.yaml"

        with open(output_file, "w") as f:
            yaml.dump(paper.model_dump(mode="json"), f, default_flow_style=False, sort_keys=False)


def load_papers_from_yaml(input_dir: Path) -> List[Paper]:
    """Load papers from YAML files."""
    papers = []

    for yaml_file in input_dir.glob("*.yaml"):
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)
            papers.append(Paper(**data))

    return papers
