# Citation Arbitrage

Arbitrage academic citation impact to identify overlooked startup opportunities.

**Core Insight**: The smartest grad students who did breakthrough research often join or start companies before the market realizes their impact. By tracking highly-cited papers (weighted by PageRank, not just citation count) and finding where those researchers are now, we can identify undervalued investment opportunities.

## Overview

This tool analyzes academic publications from OpenAlex to:
1. Identify highly-cited research papers (2020-present)
2. Find the key contributors (typically grad students/early-career researchers)
3. Track their current positions
4. Identify which are working at startups
5. Generate investment research reports

## Installation

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Usage

```bash
# 1. Fetch influential papers from OpenAlex (2020-present, 100+ citations)
citation-arbitrage fetch-papers --from-year 2020 --min-citations 100

# 2. Build citation graph and compute PageRank
citation-arbitrage compute-pagerank

# 3. Identify grad students from paper authorships
citation-arbitrage identify-grad-students

# 4. Show top papers by PageRank
citation-arbitrage show-top-papers --top-n 20

# 5. Fetch detailed author information
citation-arbitrage fetch-authors --author-ids "A5082191284,A5051830072"
```

## Data Structure

All data is stored in YAML format in the `data/` directory:
- `data/papers/` - Paper metadata and citations
- `data/authors/` - Author profiles and career trajectories
- `data/analysis/` - Investment analysis and reports
