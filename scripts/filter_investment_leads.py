#!/usr/bin/env python3
"""
Filter investment leads to remove false positives and large companies.
Create a prioritized list of genuine startup opportunities.
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any
import csv

# Companies to exclude (FAANG + large tech + obvious corporates)
EXCLUDED_COMPANIES = {
    'google', 'meta', 'microsoft', 'nvidia', 'huawei', 'ericsson',
    'openai',  # Already $80B valuation, too late
    'apple', 'amazon', 'facebook', 'netflix', 'tesla',
    'samsung', 'intel', 'amd', 'qualcomm', 'broadcom',
    'oracle', 'salesforce', 'adobe', 'ibm', 'cisco',
    'glaxosmithkline', 'eli lilly', 'daiichi sankyo',
    'continental', 'framatome', 'tesat-spacecom',
    'yahoo', 'snap', 'juniper networks', 'accenture'
}

# Known false positives (historical figures, data errors)
EXCLUDED_NAMES = {
    'karl marx', 'gottlob frege', 'herbert marcuse',
    'george armstrong kelly', 'immanuel kant'
}

# Minimum criteria for quality leads
MIN_SCORE = 0.4
MIN_PAPERS = 1
MAX_H_INDEX = 50  # Too high suggests established researcher


def load_investment_leads(path: Path) -> List[Dict[str, Any]]:
    """Load investment leads from CSV."""
    leads = []
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('Name'):  # Skip empty rows
                continue
            leads.append(row)
    return leads


def is_excluded_company(company: str) -> bool:
    """Check if company should be excluded."""
    company_lower = company.lower()
    for excluded in EXCLUDED_COMPANIES:
        if excluded in company_lower:
            return True
    return False


def is_excluded_name(name: str) -> bool:
    """Check if name is a known false positive."""
    name_lower = name.lower()
    return any(excluded in name_lower for excluded in EXCLUDED_NAMES)


def filter_leads(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter out false positives and large companies."""
    filtered = []

    for lead in leads:
        # Skip empty rows
        if not lead.get('Name'):
            continue

        # Check exclusions
        if is_excluded_name(lead['Name']):
            print(f"  ❌ Excluding {lead['Name']}: Historical figure/false positive")
            continue

        if is_excluded_company(lead['Company']):
            print(f"  ❌ Excluding {lead['Name']} @ {lead['Company']}: Large company")
            continue

        # Check quality criteria
        try:
            score = float(lead['Score'])
            h_index = int(lead['H-Index']) if lead['H-Index'] else 0
            papers = int(lead['Papers']) if lead['Papers'] else 0

            if score < MIN_SCORE:
                print(f"  ⚠️  Excluding {lead['Name']}: Score too low ({score})")
                continue

            if h_index > MAX_H_INDEX:
                print(f"  ⚠️  Excluding {lead['Name']}: H-index too high ({h_index}), likely established researcher")
                continue

        except (ValueError, KeyError) as e:
            print(f"  ⚠️  Excluding {lead['Name']}: Data quality issue ({e})")
            continue

        # Passed all filters
        filtered.append(lead)

    return filtered


def prioritize_leads(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort leads by investment potential."""
    # Scoring criteria:
    # - Higher confidence score
    # - Has ORCID (data quality)
    # - Moderate h-index (10-30 = impactful but not too senior)
    # - Multiple papers as first author

    def priority_score(lead: Dict[str, Any]) -> float:
        score = float(lead['Score'])
        h_index = int(lead['H-Index']) if lead['H-Index'] else 0
        first_author = int(lead['First Author Papers']) if lead['First Author Papers'] else 0
        has_orcid = 1 if lead.get('ORCID') else 0

        # Sweet spot: h-index between 10-30
        h_bonus = 0
        if 10 <= h_index <= 30:
            h_bonus = 0.2
        elif 5 <= h_index < 10:
            h_bonus = 0.1

        # First author papers bonus
        first_author_bonus = min(first_author * 0.05, 0.15)

        # ORCID bonus (data quality)
        orcid_bonus = 0.1 if has_orcid else 0

        return score + h_bonus + first_author_bonus + orcid_bonus

    return sorted(leads, key=priority_score, reverse=True)


def save_filtered_csv(leads: List[Dict[str, Any]], output_path: Path):
    """Save filtered leads to CSV."""
    if not leads:
        print("No leads to save!")
        return

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=leads[0].keys())
        writer.writeheader()
        writer.writerows(leads)

    print(f"\n✅ Saved {len(leads)} filtered leads to {output_path}")


def save_research_report(leads: List[Dict[str, Any]], output_path: Path):
    """Create a detailed research report."""
    with open(output_path, 'w') as f:
        f.write("# Filtered Investment Leads - Research Report\n\n")
        f.write(f"**Total Leads**: {len(leads)}\n\n")
        f.write("**Filters Applied**:\n")
        f.write("- ❌ Removed FAANG and large tech companies\n")
        f.write("- ❌ Removed historical figures (data errors)\n")
        f.write("- ❌ Minimum score: 0.4\n")
        f.write("- ❌ Maximum h-index: 50 (avoid established researchers)\n")
        f.write("- ✅ Has ORCID preferred (data quality)\n\n")
        f.write("---\n\n")

        for i, lead in enumerate(leads, 1):
            f.write(f"## {i}. {lead['Name']} @ {lead['Company']}\n\n")
            f.write(f"**Country**: {lead['Country']}\n")
            f.write(f"**Score**: {lead['Score']}\n")
            f.write(f"**Citations**: {lead['Citations']}\n")
            f.write(f"**H-Index**: {lead['H-Index']}\n")
            f.write(f"**Papers**: {lead['Papers']} ({lead['First Author Papers']} as first author)\n")

            if lead.get('ORCID'):
                f.write(f"**ORCID**: {lead['ORCID']}\n")

            f.write(f"**OpenAlex**: {lead['Author ID']}\n\n")

            f.write("### Research Actions:\n\n")
            f.write(f"1. **LinkedIn Search**: `{lead['Name']} {lead['Company']}`\n")
            f.write(f"2. **Company Search**: `{lead['Company']}` on Crunchbase\n")
            f.write(f"3. **Google**: `\"{lead['Company']}\" startup funding Series A`\n")
            f.write(f"4. **Verify**: Check if they're still at this company\n\n")

            f.write("### Questions to Answer:\n\n")
            f.write("- [ ] Is this a startup or established company?\n")
            f.write("- [ ] What is their role? (Founder, CTO, Researcher?)\n")
            f.write("- [ ] When did they join?\n")
            f.write("- [ ] Company size (<50, 50-200, 200+)?\n")
            f.write("- [ ] Funding stage (Seed, Series A, B, C)?\n")
            f.write("- [ ] Total funding raised?\n")
            f.write("- [ ] Who are the investors?\n\n")

            f.write("### Notes:\n\n")
            f.write("_[Add your research findings here]_\n\n")
            f.write("---\n\n")

    print(f"✅ Saved research report to {output_path}")


def main():
    """Main filtering and prioritization workflow."""
    data_dir = Path(__file__).parent.parent / "data" / "analysis"

    print("🔍 Loading investment leads...")
    leads = load_investment_leads(data_dir / "INVESTMENT_LEADS.csv")
    print(f"   Loaded {len(leads)} leads\n")

    print("🧹 Filtering out false positives and large companies...")
    filtered = filter_leads(leads)
    print(f"\n   {len(filtered)} leads passed filters\n")

    print("📊 Prioritizing by investment potential...")
    prioritized = prioritize_leads(filtered)

    # Save outputs
    save_filtered_csv(prioritized, data_dir / "FILTERED_LEADS.csv")
    save_research_report(prioritized, data_dir / "RESEARCH_REPORT.md")

    # Print top 10 summary
    print("\n" + "="*80)
    print("🎯 TOP 10 PRIORITY LEADS:")
    print("="*80 + "\n")

    for i, lead in enumerate(prioritized[:10], 1):
        orcid = "✓" if lead.get('ORCID') else "✗"
        print(f"{i:2d}. {lead['Name']}")
        print(f"    Company: {lead['Company']} ({lead['Country']})")
        print(f"    Score: {lead['Score']} | H-index: {lead['H-Index']} | ORCID: {orcid}")
        print()


if __name__ == "__main__":
    main()
