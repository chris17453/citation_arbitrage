"""Data models for papers, authors, and career tracking."""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class InstitutionType(str, Enum):
    """Types of institutions."""
    EDUCATION = "education"
    COMPANY = "company"
    NONPROFIT = "nonprofit"
    GOVERNMENT = "government"
    HEALTHCARE = "healthcare"
    FUNDER = "funder"
    ARCHIVE = "archive"
    FACILITY = "facility"
    OTHER = "other"
    UNKNOWN = "unknown"


class Institution(BaseModel):
    """An institution (university, company, etc.)."""
    id: str
    display_name: str
    ror: Optional[str] = None
    country_code: Optional[str] = None
    type: InstitutionType = InstitutionType.UNKNOWN


class Authorship(BaseModel):
    """Author information for a specific paper."""
    author_id: str
    display_name: str
    orcid: Optional[str] = None
    author_position: str  # "first", "middle", "last"
    institutions: List[Institution] = Field(default_factory=list)
    is_corresponding: bool = False
    raw_affiliation_strings: List[str] = Field(default_factory=list)


class Paper(BaseModel):
    """A research paper with citation metrics."""
    id: str
    doi: Optional[str] = None
    title: str
    publication_date: date
    publication_year: int

    # Citation metrics
    cited_by_count: int = 0
    citation_percentile: Optional[float] = None
    pagerank: Optional[float] = None  # Computed PageRank score

    # Authors
    authorships: List[Authorship] = Field(default_factory=list)

    # References (for building citation graph)
    referenced_works: List[str] = Field(default_factory=list)

    # Metadata
    primary_topic: Optional[str] = None
    open_access: bool = False

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }


class AffiliationPeriod(BaseModel):
    """An author's affiliation at a specific institution during a time period."""
    institution: Institution
    start_year: Optional[int] = None
    end_year: Optional[int] = None  # None means current
    role: Optional[str] = None  # e.g., "Graduate Student", "Postdoc", "Professor"


class CareerStatus(str, Enum):
    """Career status at time of analysis."""
    GRAD_STUDENT = "grad_student"
    POSTDOC = "postdoc"
    PROFESSOR = "professor"
    INDUSTRY = "industry"
    STARTUP = "startup"
    UNKNOWN = "unknown"


class Author(BaseModel):
    """An author with career trajectory information."""
    id: str
    orcid: Optional[str] = None
    display_name: str

    # Career info
    affiliation_history: List[AffiliationPeriod] = Field(default_factory=list)
    current_institution: Optional[Institution] = None
    current_status: CareerStatus = CareerStatus.UNKNOWN

    # Was this person a grad student when they published influential work?
    was_grad_student_during_key_work: bool = False
    grad_student_years: Optional[tuple[int, int]] = None  # (start, end)

    # Publication metrics
    works_count: int = 0
    cited_by_count: int = 0
    h_index: Optional[int] = None

    # Key papers (IDs of papers where they were first/second author)
    key_papers: List[str] = Field(default_factory=list)


class CompanyInfo(BaseModel):
    """Information about a company/startup."""
    name: str
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    founded_year: Optional[int] = None
    funding_stage: Optional[str] = None  # "Seed", "Series A", etc.
    total_funding: Optional[float] = None  # in USD
    employee_count: Optional[int] = None
    description: Optional[str] = None
    is_public: bool = False
    ticker: Optional[str] = None


class InvestmentLead(BaseModel):
    """A potential investment opportunity based on researcher tracking."""
    author: Author
    company: CompanyInfo
    confidence_score: float = Field(ge=0.0, le=1.0)

    # Why is this interesting?
    key_papers_pagerank: List[float] = Field(default_factory=list)
    research_areas: List[str] = Field(default_factory=list)

    # Career transition info
    transition_date: Optional[date] = None
    years_since_transition: Optional[float] = None

    notes: str = ""
