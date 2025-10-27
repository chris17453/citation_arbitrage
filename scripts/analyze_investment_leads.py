"""Analyze authors for investment opportunities - find those at companies/startups."""

import yaml
from pathlib import Path
from collections import defaultdict
from rich.console import Console
from rich.table import Table

console = Console()


def analyze_company_affiliations():
    """Find all authors currently at companies."""
    authors_dir = Path("data/authors")
    candidates_file = Path("data/analysis/grad_students.yaml")

    # Load candidates with rankings
    with open(candidates_file) as f:
        candidates_data = yaml.safe_load(f)

    candidate_map = {c['author_id']: c for c in candidates_data['candidates']}

    # Analyze all author files
    company_authors = []
    edu_to_company_transitions = []
    unknown_status = []

    total_authors = 0
    for author_file in authors_dir.glob("*.yaml"):
        with open(author_file) as f:
            author = yaml.safe_load(f)
            total_authors += 1

        author_id = author['id']
        if author_id not in candidate_map:
            continue  # Not in our candidates list

        candidate_info = candidate_map[author_id]

        # Check current institution
        current_inst = author.get('current_institution')
        if current_inst and current_inst.get('type') == 'company':
            company_authors.append({
                'author': author,
                'candidate': candidate_info,
                'company': current_inst['display_name'],
                'country': current_inst.get('country_code', 'Unknown')
            })

        # Check for education → company transition in history
        aff_history = author.get('affiliation_history', [])
        had_edu = False
        has_company = False

        for aff in aff_history:
            inst_type = aff.get('institution', {}).get('type', '')
            if inst_type == 'education':
                had_edu = True
            elif inst_type == 'company':
                has_company = True

        if had_edu and has_company:
            edu_to_company_transitions.append({
                'author': author,
                'candidate': candidate_info
            })

    console.print(f"\n[cyan]═══ INVESTMENT LEADS ANALYSIS ═══[/cyan]\n")
    console.print(f"Total authors analyzed: {total_authors}")
    console.print(f"Candidates in our dataset: {len(candidate_map)}")
    console.print(f"Authors currently at companies: {len(company_authors)}")
    console.print(f"Education → Company transitions: {len(edu_to_company_transitions)}\n")

    # Sort by candidate score
    company_authors.sort(key=lambda x: x['candidate']['score'], reverse=True)

    # Create detailed report
    table = Table(title="Top Investment Leads (High-Score Researchers at Companies)")
    table.add_column("Rank", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Company", style="yellow")
    table.add_column("Score", style="magenta")
    table.add_column("Papers", style="blue")
    table.add_column("Citations", style="red")
    table.add_column("H-index", style="white")

    for i, item in enumerate(company_authors[:50], 1):
        author = item['author']
        candidate = item['candidate']

        table.add_row(
            str(candidate['rank']),
            author['display_name'][:30],
            item['company'][:35],
            f"{candidate['score']:.3f}",
            str(candidate['paper_count']),
            f"{author['cited_by_count']:,}",
            str(author.get('h_index', 'N/A'))
        )

    console.print(table)

    # Save to YAML
    investment_leads = []
    for item in company_authors:
        author = item['author']
        candidate = item['candidate']

        investment_leads.append({
            'rank': candidate['rank'],
            'author_id': author['id'],
            'name': author['display_name'],
            'orcid': author.get('orcid'),
            'company': {
                'name': item['company'],
                'country': item['country']
            },
            'metrics': {
                'confidence_score': candidate['score'],
                'paper_count': candidate['paper_count'],
                'first_author_count': candidate['first_author_count'],
                'citations': author['cited_by_count'],
                'h_index': author.get('h_index'),
                'avg_pagerank': candidate['avg_pagerank']
            },
            'paper_ids': candidate['paper_ids']
        })

    output_file = Path("data/analysis/investment_leads.yaml")
    with open(output_file, "w") as f:
        yaml.dump({'leads': investment_leads}, f, default_flow_style=False, sort_keys=False)

    console.print(f"\n[green]✓ Investment leads report saved to {output_file}")

    # Group by company
    by_company = defaultdict(list)
    for lead in investment_leads:
        by_company[lead['company']['name']].append(lead)

    console.print(f"\n[cyan]═══ COMPANIES WITH MULTIPLE HIGH-IMPACT RESEARCHERS ═══[/cyan]\n")

    companies_table = Table()
    companies_table.add_column("Company", style="yellow")
    companies_table.add_column("Count", style="cyan")
    companies_table.add_column("Avg Score", style="magenta")
    companies_table.add_column("Top Researcher", style="green")

    multi_company = [(name, authors) for name, authors in by_company.items() if len(authors) >= 2]
    multi_company.sort(key=lambda x: len(x[1]), reverse=True)

    for company_name, authors in multi_company[:20]:
        avg_score = sum(a['metrics']['confidence_score'] for a in authors) / len(authors)
        top_researcher = max(authors, key=lambda x: x['metrics']['confidence_score'])

        companies_table.add_row(
            company_name[:40],
            str(len(authors)),
            f"{avg_score:.3f}",
            top_researcher['name'][:30]
        )

    console.print(companies_table)

    # Save company groupings
    company_report = []
    for company_name, authors in multi_company:
        company_report.append({
            'company': company_name,
            'researcher_count': len(authors),
            'avg_confidence_score': sum(a['metrics']['confidence_score'] for a in authors) / len(authors),
            'total_citations': sum(a['metrics']['citations'] for a in authors),
            'researchers': [
                {
                    'name': a['name'],
                    'score': a['metrics']['confidence_score'],
                    'citations': a['metrics']['citations']
                } for a in authors
            ]
        })

    company_output = Path("data/analysis/companies_of_interest.yaml")
    with open(company_output, "w") as f:
        yaml.dump({'companies': company_report}, f, default_flow_style=False, sort_keys=False)

    console.print(f"\n[green]✓ Company groupings saved to {company_output}")

    return investment_leads


if __name__ == "__main__":
    leads = analyze_company_affiliations()

    console.print(f"\n[cyan]═══ NEXT STEPS ═══[/cyan]\n")
    console.print("1. Review data/analysis/investment_leads.yaml")
    console.print("2. Check data/analysis/companies_of_interest.yaml for company clusters")
    console.print("3. For each lead, research:")
    console.print("   • LinkedIn profile (current role, when they joined)")
    console.print("   • Company website (product, stage)")
    console.print("   • Crunchbase (funding, investors)")
    console.print("   • Twitter/X (public presence)")
    console.print("\n4. Focus on:")
    console.print("   • Pre-Series B startups")
    console.print("   • Multiple top researchers at same company")
    console.print("   • Recent transitions (last 2-3 years)")
    console.print("   • Hot research areas (AI/ML, crypto, bio)")
