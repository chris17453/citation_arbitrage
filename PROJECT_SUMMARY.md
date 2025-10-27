# Citation Arbitrage - Project Summary

## What We Built

A complete Python tool to identify investment opportunities by tracking influential academic researchers and their career transitions.

## Core Hypothesis

**Smart grad students who do breakthrough research often join or start companies before the market realizes their impact.**

By using PageRank (not just citation counts) to identify the most influential papers, then tracking where those researchers are now, we can find undervalued investment opportunities.

## Key Features

### 1. Data Collection
- Fetch papers from OpenAlex API (2020-present, or historical 2010-2015)
- Store all data in YAML format for easy inspection and iteration
- Supports filtering by year range, citation count, topic

### 2. Citation Analysis
- Build directed citation graph from paper references
- Compute PageRank scores (like Google's algorithm, but for papers)
- PageRank captures network effects better than raw citation counts
- Identify truly influential work vs just popular work

### 3. Author Identification
- Heuristics to identify grad students at time of publication:
  - First/second authorship on high-impact papers
  - Affiliated with universities
  - Published 2-10 papers over 3-6 year PhD timeline
  - High PageRank scores on their work
- Confidence scoring for each candidate

### 4. Career Tracking
- Fetch detailed author profiles from OpenAlex
- Track affiliation history over time
- Identify transitions from academia to industry
- Flag authors now at companies (potential startups)

### 5. Investment Analysis
- Historical validation workflow to test hypothesis with 2010-2015 data
- Manual research workflows for LinkedIn, Crunchbase, etc.
- Extensible data models for adding funding/valuation data

## Project Structure

```
citation_arbitrage/
├── citation_arbitrage/      # Main Python package
│   ├── models.py           # Pydantic data models
│   ├── openalex_client.py  # API client + YAML I/O
│   ├── citation_graph.py   # Graph building + PageRank
│   ├── author_analysis.py  # Grad student identification
│   └── cli.py             # Command-line interface
├── data/                   # Data storage (gitignored)
│   ├── papers/            # Paper YAML files
│   ├── authors/           # Author YAML files
│   └── analysis/          # Reports and graphs
├── README.md              # Project overview
├── EXAMPLE.md             # Workflow examples
├── HISTORICAL_VALIDATION.md  # Validation strategy
└── pyproject.toml         # Python project config
```

## Tech Stack

- **Python 3.10+** with modern async/await
- **Pydantic** for type-safe data models
- **NetworkX** for graph algorithms and PageRank
- **httpx** for async HTTP requests
- **Click** for CLI
- **Rich** for beautiful terminal output
- **YAML** for human-readable data storage
- **UV** for fast package management

## CLI Commands

```bash
# 1. Fetch papers
citation-arbitrage fetch-papers --from-year 2020 --min-citations 100

# 2. Compute PageRank
citation-arbitrage compute-pagerank

# 3. Identify grad students
citation-arbitrage identify-grad-students

# 4. View results
citation-arbitrage show-top-papers --top-n 50

# 5. Fetch author details
citation-arbitrage fetch-authors --author-ids "A123,A456"
```

## Workflow

### Forward-Looking (Current Opportunities)

1. Fetch 2020-2025 papers with 100+ citations
2. Compute PageRank on citation graph
3. Identify grad students (first authors on top papers)
4. Fetch their current affiliations
5. Filter for those who joined companies 2015-2025
6. Research the companies (LinkedIn, Crunchbase)
7. Identify pre-Series B startups for potential investment

### Historical Validation

1. Fetch 2010-2015 papers
2. Compute PageRank
3. Identify who was a grad student then
4. Fetch their 2025 status
5. Calculate success rate:
   - Founded/joined successful startups?
   - Achieved high industry positions?
   - Continued prestigious academic careers?
6. Validate correlation between PageRank and success
7. Refine scoring algorithm based on findings

## Why This Works

### Information Asymmetry

- Academic impact is public but takes time to be recognized
- Markets are slow to price in researcher quality
- 2-5 years after PhD is optimal timing window
- Grad students often first authors on breakthrough work

### PageRank Advantage

- Better than citation count alone
- Captures "citations from important papers" signal
- Identifies foundational vs derivative work
- Reduces false positives from hype/spam citations

### Network Effects

- Top researchers collaborate with other top researchers
- Successful startup founders often worked together in grad school
- Can track "teams" not just individuals

## Next Steps to Build

1. **Automated LinkedIn Scraping**
   - Selenium-based scraper for current positions
   - Headless browser automation
   - Rate limiting and anti-detection

2. **Company Database Integration**
   - Crunchbase API for funding data
   - Pitchbook integration
   - Company website scraping

3. **Investment Scoring**
   - Combine PageRank + funding stage + team quality
   - ML model trained on historical success
   - Automated alerts for high-value opportunities

4. **Network Analysis**
   - Co-author graphs
   - Find "teams" of collaborators
   - Track group transitions to same companies

5. **Topic Filtering**
   - Focus on specific research areas (AI/ML, crypto, bio)
   - Track trending research topics
   - Predict next hot areas

## Example Success Cases to Find

Historical examples our algorithm should identify:

- **OpenAI founders** (Ilya Sutskever, Greg Brockman)
- **DeepMind founders** (Demis Hassabis, Shane Legg)
- **Anthropic founders** (Dario Amodei, Chris Olah)
- **Waymo researchers** (early self-driving car PhDs)
- **Stripe** (Patrick Collison - though he dropped out)

## Limitations & Risks

1. **Data Lag**: OpenAlex might be 6-12 months behind
2. **False Positives**: Not every smart researcher starts a unicorn
3. **Market Timing**: Even great tech needs market readiness
4. **Selection Bias**: Famous cases are visible, failures are not
5. **Execution Risk**: Research brilliance ≠ business execution

## Validation is Critical

Before deploying capital, we MUST validate with historical data:
- Run on 2010-2015 cohort
- Calculate actual success rate
- Check correlation with PageRank
- Identify false positives/negatives
- Refine scoring algorithm

If historical success rate is <20%, strategy needs rework.
If >40%, extremely promising.

## Usage Notes

- Start with small samples (500 papers) to test
- OpenAlex API is free but rate-limited
- Use `--email` flag for faster "polite pool" access
- All data in YAML for easy manual inspection
- Iterate on scoring weights based on findings

## Future Research

- **Field-specific models**: Different weights for AI vs bio vs crypto
- **Time-series analysis**: Track citation velocity, not just totals
- **Geographic effects**: Does university location matter?
- **Advisor network**: Does advisor reputation predict success?
- **Gender/diversity**: Are there systematic biases in our model?

## License

MIT (or whatever you choose)

## Contributing

This is an alpha research project. Contributions welcome for:
- Better grad student identification heuristics
- LinkedIn/Crunchbase integrations
- Historical case studies
- Success metric definitions

