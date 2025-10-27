# Historical Validation: Testing the Hypothesis

Before investing based on recent grad students, let's validate the strategy by looking at 2010-2015 data.

## Hypothesis

**Smart grad students who published influential research go on to create/join successful companies.**

## Validation Approach

We'll look back 10-15 years to see if there's correlation between:
1. High-impact research (measured by PageRank) in 2010-2015
2. Success in private sector 5-10 years later (2015-2025)

## Step 1: Fetch Historical Papers

```bash
# Fetch papers from 2010-2015 with high citations
# Note: Use lower min-citations since papers need time to accumulate citations
citation-arbitrage fetch-papers \
    --from-year 2010 \
    --to-year 2015 \
    --min-citations 200 \
    --max-papers 3000 \
    --output-dir data/historical/papers
```

## Step 2: Compute Historical PageRank

```bash
citation-arbitrage compute-pagerank \
    --papers-dir data/historical/papers \
    --output data/historical/citation_graph.yaml \
    --top-n 100
```

## Step 3: Identify 2010-2015 Grad Students

```bash
citation-arbitrage identify-grad-students \
    --papers-dir data/historical/papers \
    --output data/historical/grad_students.yaml \
    --min-score 0.4
```

This will identify people who were likely grad students in 2010-2015.

## Step 4: Fetch Their Current Status

```bash
# Extract top 100 author IDs from grad_students.yaml
# Then fetch their current (2025) status:
citation-arbitrage fetch-authors \
    --author-ids "..." \
    --output-dir data/historical/authors
```

## Step 5: Manual Success Analysis

For each author, research their career outcome:

### Success Metrics

1. **Startup Success**:
   - Founded/co-founded a startup that raised Series A+
   - Company acquired for $50M+
   - Company reached IPO

2. **Industry Impact**:
   - Joined FAANG/major tech company in senior role
   - Led major product/research at tech company
   - Built influential open-source projects

3. **Continued Academia**:
   - Became professor at top university
   - Won major research awards
   - Founded influential research lab

### Data Sources for Validation

1. **LinkedIn**: Search for the person, check:
   - Current role
   - Company history
   - Endorsements and connections

2. **Crunchbase**: For startup founders, check:
   - Total funding raised
   - Funding stage
   - Acquisition status
   - Valuation (if available)

3. **Google Scholar**: Check:
   - Citation growth over time
   - Collaboration networks
   - Industry publications

4. **News/PR**: Search "[Name] startup" or "[Name] acquisition"

5. **Twitter/X**: Many successful researchers are active on social media

## Example Analysis

Let's say we identify "Dr. Jane Smith" who:
- PhD from Stanford (2010-2015)
- First author on 5 papers with avg PageRank in top 1%
- Research area: Deep Learning for Computer Vision

We then discover:
- 2015: Joined Google Brain
- 2017: Left to co-found "VisionAI" (stealth startup)
- 2018: VisionAI raised $5M seed (a16z, Sequoia)
- 2020: Series A $25M
- 2023: Acquired by Meta for $400M

**This is a HIT** - our strategy would have identified her in 2015-2017.

## Success Rate Analysis

Create a spreadsheet to track:

| Author Name | PhD Year | Top PageRank | Career Path | Company | Funding/Exit | Success? |
|-------------|----------|--------------|-------------|---------|--------------|----------|
| Jane Smith | 2015 | 0.0023 | Startup Founder | VisionAI | $400M exit | ✅ |
| John Doe | 2013 | 0.0019 | FAANG | Google | N/A | ✅ |
| ... | ... | ... | ... | ... | ... | ... |

Calculate:
- **Success rate**: % who achieved startup success, senior industry role, or prestigious academic position
- **Correlation**: Does higher PageRank correlate with success?
- **Timing**: How long after PhD did they achieve success?
- **Field**: Which research areas had highest success rates?

## Hypotheses to Test

1. **PageRank Correlation**: Do authors with top 1% PageRank scores have higher success rates?
2. **First Authorship**: Are first authors more successful than middle authors?
3. **University Effect**: Does the university matter? (Stanford/MIT/CMU vs others)
4. **Research Area**: Which fields have highest private sector success rates?
   - Expected hot areas: ML/AI, computer vision, NLP, robotics, crypto
5. **Publication Count**: Is there an optimal number? (Too few = not enough impact, too many = stayed in academia?)
6. **Collaboration Network**: Do successful researchers collaborate with other successful researchers?

## Automation Script

Create a Python script to help with analysis:

```python
# validation_analysis.py
import yaml
from pathlib import Path
from collections import defaultdict

def analyze_historical_cohort(year_range=(2010, 2015)):
    """Analyze success of grad students from a historical cohort."""

    # Load grad student candidates
    with open('data/historical/grad_students.yaml') as f:
        candidates = yaml.safe_load(f)

    # Load author data
    stats = {
        'total_candidates': len(candidates['candidates']),
        'founders': 0,
        'faang': 0,
        'professors': 0,
        'unknown': 0,
        'by_pagerank': defaultdict(list)
    }

    for candidate in candidates['candidates']:
        author_id = candidate['author_id'].split('/')[-1]
        author_file = Path(f'data/historical/authors/{author_id}.yaml')

        if not author_file.exists():
            stats['unknown'] += 1
            continue

        with open(author_file) as f:
            author = yaml.safe_load(f)

        # Categorize career path
        current_inst = author.get('current_institution', {})
        inst_type = current_inst.get('type', 'unknown')
        inst_name = current_inst.get('display_name', 'Unknown')

        # Track by PageRank bucket
        avg_pr = candidate.get('avg_pagerank', 0)
        stats['by_pagerank'][avg_pr].append({
            'name': author['display_name'],
            'institution': inst_name,
            'type': inst_type
        })

        if inst_type == 'company':
            # TODO: Manual classification of startup vs FAANG
            if 'founders' in author.get('notes', ''):
                stats['founders'] += 1
            else:
                stats['faang'] += 1
        elif inst_type == 'education':
            stats['professors'] += 1

    return stats

if __name__ == '__main__':
    stats = analyze_historical_cohort()
    print(f"Total candidates: {stats['total_candidates']}")
    print(f"Startup founders: {stats['founders']}")
    print(f"FAANG/Industry: {stats['faang']}")
    print(f"Professors: {stats['professors']}")
    print(f"Unknown: {stats['unknown']}")
```

## Expected Findings

If the hypothesis is correct, we should see:

1. **High success rate** (>30%) of top PageRank authors in private sector
2. **Timing**: 2-5 years after PhD is optimal for startup transition
3. **Network effects**: Successful founders often worked with other successful researchers
4. **Field concentration**: AI/ML, bio, crypto will have highest success rates

## Iteration

Based on findings, refine the scoring algorithm:
- Adjust weights for PageRank vs citation count
- Add network analysis (co-author success)
- Consider university prestige
- Factor in research area trends

## Case Studies to Find

Try to find famous examples we know:
- OpenAI founders (Ilya Sutskever, Greg Brockman, etc.)
- DeepMind founders (Demis Hassabis, Shane Legg, Mustafa Suleyman)
- Anthropic founders (Dario Amodei, Chris Olah, etc.)
- Scale AI (Alexandr Wang - though he dropped out)

Can our algorithm identify them from their early papers?

## Next Steps

1. Run historical analysis on 2010-2015 cohort
2. Calculate success metrics
3. Validate correlation with PageRank
4. Publish findings (blog post?)
5. Use validated methodology for current (2020-2025) cohort

This validation is crucial - if we don't see correlation in historical data, the strategy needs refinement before deploying capital!
