# Citation Arbitrage - Example Workflow

This guide shows a complete workflow for finding investment opportunities.

## Quick Start

### 1. Fetch Papers (Sample Run)

Let's start by fetching a smaller sample of highly-cited papers to test the system:

```bash
# Fetch papers from 2020-2024 with 500+ citations (will get ~500-1000 papers)
citation-arbitrage fetch-papers \
    --from-year 2020 \
    --to-year 2024 \
    --min-citations 500 \
    --max-papers 500 \
    --output-dir data/papers
```

This will create YAML files in `data/papers/` for each paper.

### 2. Compute PageRank

Build the citation graph and compute PageRank scores:

```bash
citation-arbitrage compute-pagerank \
    --papers-dir data/papers \
    --output data/analysis/citation_graph.yaml \
    --top-n 20
```

This will:
- Build a directed graph of citations
- Compute PageRank (like Google's algorithm but for papers)
- Update all paper YAML files with PageRank scores
- Show the top 20 papers

**Why PageRank?**

Raw citation count can be misleading. A paper might have 1000 citations, but if they're all from low-impact papers, it's less significant than a paper with 500 citations from highly-cited papers. PageRank captures this network effect.

### 3. View Top Papers

```bash
citation-arbitrage show-top-papers --top-n 50
```

This shows papers ranked by PageRank with their first authors.

### 4. Identify Grad Students

Now identify which authors were likely grad students when they published key work:

```bash
citation-arbitrage identify-grad-students \
    --papers-dir data/papers \
    --output data/analysis/grad_students.yaml \
    --min-score 0.4
```

This uses heuristics to identify grad students:
- First or second authorship on high-PageRank papers
- Affiliated with universities at time of publication
- Published 2-10 papers over 3-6 years (typical PhD timeline)
- Strong PageRank scores on their papers

### 5. Fetch Author Details

Take the top candidates and fetch their full profiles:

```bash
# From the grad_students.yaml file, get the top author IDs
# Example IDs (replace with actual ones from your results):
citation-arbitrage fetch-authors \
    --author-ids "A5082191284,A5051830072,A5047300895" \
    --output-dir data/authors
```

This fetches:
- Full publication history
- Affiliation timeline
- Current institution
- Citation metrics (h-index, etc.)

### 6. Manual Analysis (Next Steps)

Now you have the data to manually investigate:

1. **Check current positions**: Look at the author YAML files to see where they are now
2. **Identify startups**: If `current_institution.type == "company"`, investigate the company
3. **LinkedIn research**: Search LinkedIn for the author name to:
   - Verify current position
   - Find the company they work for
   - Check company funding stage, investors, etc.
4. **Company research**:
   - Check Crunchbase for funding info
   - Look for company website, product announcements
   - Check if they're hiring (growth signal)
   - Review social media presence

## Full Workflow Example

Let's say you want to find AI/ML researchers who transitioned to startups:

```bash
# 1. Fetch AI/ML papers (use OpenAlex topic filtering)
# For now, fetch broadly and filter later
citation-arbitrage fetch-papers \
    --from-year 2020 \
    --min-citations 300 \
    --max-papers 2000

# 2. Compute PageRank
citation-arbitrage compute-pagerank

# 3. Find top papers
citation-arbitrage show-top-papers --top-n 100 > top_papers.txt

# 4. Identify grad students
citation-arbitrage identify-grad-students --min-score 0.4

# 5. Review the grad_students.yaml file
cat data/analysis/grad_students.yaml

# 6. Pick top 50 candidates and fetch their profiles
# Extract author IDs from the YAML and fetch:
citation-arbitrage fetch-authors --author-ids "A123,A456,A789,..."

# 7. Filter for company affiliations
# Write a simple script or manually check:
grep -r "type: company" data/authors/*.yaml
```

## Investment Research Checklist

For each promising candidate:

- [ ] **Academic Impact**: What was their key contribution? Is it foundational?
- [ ] **PageRank Score**: Are their papers in the top 1%?
- [ ] **Career Timing**: How long since PhD? (2-5 years is ideal)
- [ ] **Company Stage**: Seed/Series A is ideal (undervalued)
- [ ] **Market Timing**: Is their research area getting hot?
- [ ] **Team**: Who else is at the company? Other star researchers?
- [ ] **Product**: Has the company launched anything yet?
- [ ] **Funding**: Who invested? Smart money or tourists?

## Advanced: Automated Filtering

You can write Python scripts to automate filtering. For example:

```python
import yaml
from pathlib import Path

# Load grad student candidates
with open('data/analysis/grad_students.yaml') as f:
    candidates = yaml.safe_load(f)

# Filter for high-score candidates
top_candidates = [
    c for c in candidates['candidates']
    if c['score'] > 0.6 and c['first_author_count'] >= 2
]

# Load author details
for candidate in top_candidates:
    author_id = candidate['author_id'].split('/')[-1]
    author_file = Path(f'data/authors/{author_id}.yaml')

    if author_file.exists():
        with open(author_file) as f:
            author = yaml.safe_load(f)

        # Check if at a company
        if author.get('current_institution', {}).get('type') == 'company':
            print(f"🎯 {author['display_name']}")
            print(f"   Company: {author['current_institution']['display_name']}")
            print(f"   Score: {candidate['score']:.3f}")
            print(f"   Papers: {candidate['paper_count']}")
            print()
```

## Data Schema

All data is stored as YAML for easy inspection and manual editing.

### Paper YAML

```yaml
id: "https://openalex.org/W3128646645"
doi: "https://doi.org/10.1234/example"
title: "Example Paper Title"
publication_date: "2021-02-04"
publication_year: 2021
cited_by_count: 5432
pagerank: 0.001234
authorships:
  - author_id: "https://openalex.org/A5082191284"
    display_name: "Jane Smith"
    author_position: "first"
    institutions:
      - display_name: "Stanford University"
        type: "education"
```

### Author YAML

```yaml
id: "https://openalex.org/A5082191284"
display_name: "Jane Smith"
orcid: "https://orcid.org/0000-0002-8021-5997"
works_count: 45
cited_by_count: 12000
h_index: 22
current_institution:
  display_name: "Example AI Startup"
  type: "company"
  country_code: "US"
affiliation_history:
  - institution:
      display_name: "Stanford University"
      type: "education"
    start_year: 2018
    end_year: 2023
  - institution:
      display_name: "Example AI Startup"
      type: "company"
    start_year: 2023
```

## Tips

1. **Start small**: Begin with 500-1000 papers to test the workflow
2. **Focus on timing**: The best opportunities are 1-3 years after PhD completion
3. **Look for transitions**: Education → Company is the key signal
4. **Check funding**: Pre-seed/Seed companies are most undervalued
5. **Verify on LinkedIn**: OpenAlex might be outdated, always cross-check
6. **Track over time**: Run this quarterly to catch new transitions

## Next Steps

Future enhancements to build:
- [ ] Automated LinkedIn scraping (with Selenium)
- [ ] Integration with Crunchbase API for funding data
- [ ] Automated scoring of investment opportunities
- [ ] Email alerts for high-value transitions
- [ ] Network analysis (who works together)
