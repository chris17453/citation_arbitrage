# Citation Arbitrage - Action Plan

## ✅ What You Have Now

### 📊 Data Files (Open in Excel/Numbers)
- **`data/analysis/INVESTMENT_LEADS.csv`** - 81 researchers at companies with all their data
- **`data/analysis/COMPANIES.csv`** - Companies with 2+ researchers

### 📈 Visualizations
- **`data/analysis/pagerank_distribution.png`** - Shows impact distribution
- **`data/analysis/collaboration_network.png`** - Co-author connections
- **`data/analysis/citation_network.png`** - Paper citation flows

### 📁 Raw Data (YAML)
- **`data/papers/`** - 5,000 papers as YAML files
- **`data/authors/`** - 3,562 author profiles as YAML files
- **`data/analysis/investment_leads.yaml`** - Full structured data
- **`data/analysis/grad_students.yaml`** - All 3,562 candidates ranked

---

## 🎯 Top 10 Leads to Research NOW

### 1. **Sandhini Agarwal @ OpenAI** 🔥
- **Why interesting**: OpenAI (obvious unicorn)
- Citations: 24,373 | H-index: 12
- **Action**: LinkedIn search → Check role, when joined
- **Crunchbase**: Already $80B+ valuation (too late, but validates our method)

### 2. **Daníel F. Guðbjartsson @ deCODE Genetics** 🧬
- **Why interesting**: Biotech company in Iceland
- Citations: 77,968 | H-index: 138 (!!!)
- **Action**: Research deCODE Genetics funding
- **Note**: Acquired by Amgen in 2012 for $415M (another validation!)

### 3. **Ashkan Afshin @ Novel (United States)** ⚠️
- **Why interesting**: Company name "Novel" - might be startup
- Citations: 136,909 | H-index: 66
- **Action**: Search "Novel United States" + "Ashkan Afshin" on LinkedIn
- **Red flag**: Very high citations - might be established researcher

### 4. **Ivan Kobyzev @ Huawei Technologies**
- Citations: 1,522 | H-index: 8
- **Note**: Huawei is huge company (not startup)
- **Skip**: Established tech giant

### 5. **William Thielicke @ Faseroptische Systeme Messtechnik** 🔬
- **Why interesting**: German optical systems company
- Citations: 3,595 | H-index: 10
- **Action**: Research company - is it a startup or established?
- **LinkedIn**: Find his profile, check company size

### 6-10. See CSV for more...

---

## 📋 Research Workflow (For Each Lead)

### Step 1: LinkedIn Research (5 min)
```
Search: "[Name] [Company]" on LinkedIn
```

Look for:
- ✅ **Current role**: Founder? CTO? Researcher?
- ✅ **Join date**: When did they start?
- ✅ **Company**: Click through to company page
- ✅ **Employee count**: <50? Startup signal!
- ✅ **Posts/updates**: Are they hiring?

### Step 2: Company Research (5 min)

**Crunchbase** (crunchbase.com):
```
Search: [Company Name]
```
- Funding stage (Seed, Series A, B, C?)
- Total raised
- Investors (smart money?)
- Last funding date

**Google Search**:
```
"[Company Name]" startup OR funding OR Series A
```
- News articles
- Product launches
- Customer traction

### Step 3: Author Verification (2 min)

**Google Scholar**:
```
[Author Name] [University/Institution]
```
- Verify they're real
- Check recent publications
- Confirm research area

**ORCID** (if available in CSV):
- Click ORCID link
- See employment history
- Verify timeline

---

## 🚩 Red Flags (Skip These)

### False Positives
- ❌ Historical figures (Karl Marx, Kant - data errors)
- ❌ FAANG companies (Google, Meta, Microsoft)
- ❌ Huge corporations (Nvidia, Huawei, Ericsson)
- ❌ Old established companies (>20 years)

### Timing Issues
- ❌ Joined >5 years ago (too late)
- ❌ Still at university (haven't transitioned)

### Quality Issues
- ❌ Score <0.4 (low confidence)
- ❌ Only 1 paper (might be spurious)
- ❌ No ORCID and weird name (data quality issue)

---

## ✅ Green Flags (Prioritize These)

### Strong Signals
- ✅ Company founded 2018-2023
- ✅ Series A-B stage (pre-unicorn)
- ✅ 2+ researchers from our list at same company
- ✅ Smart money investors (a16z, Sequoia, etc.)
- ✅ Hot research area (AI/ML, bio, crypto)

### Perfect Profile
- ✅ Score >0.6
- ✅ 3-8 papers as first author
- ✅ H-index 10-30 (impactful but not too senior)
- ✅ Joined company 2-3 years ago
- ✅ Company has <100 employees

---

## 🎪 Example: OpenAI (Validation)

Let's verify our methodology works:

### From our data:
- **Sandhini Agarwal** (rank 483)
- **Alec Radford** (rank 1725)
- **Girish Sastry** (rank 1719)

### Reality check:
1. Search "Sandhini Agarwal OpenAI LinkedIn"
2. Find: She's a Senior Research Scientist at OpenAI
3. Check Crunchbase: OpenAI valued at $80B+
4. **Conclusion**: Our algorithm found them! ✅

If we'd run this in 2018-2019, we could have identified OpenAI early.

---

## 📊 Companies with Multiple Researchers (Priority)

### OpenAI - 5 researchers
Most valuable validation of our method. If you'd caught this early...

### BioNTech - 2 researchers (Özlem Türeci, Uğur Şahin)
The COVID vaccine founders! Company worth $40B+ at peak.

### Huawei - 3 researchers
Skip (huge established company)

### Meta - 3 researchers
Skip (FAANG)

### 10X Genomics - 3 researchers
**INTERESTING**: Genomics company, check if still growing

---

## 🔄 Next Steps

### This Week
1. ✅ Open `INVESTMENT_LEADS.csv` in Excel
2. ✅ Filter out FAANG/huge companies
3. ✅ Pick 10 leads with:
   - Score >0.4
   - Company NOT in (Google, Meta, Microsoft, Nvidia, Huawei)
   - Has ORCID (data quality signal)
4. ✅ Spend 10 min on each:
   - LinkedIn search
   - Company search
   - Note findings

### This Month
1. **Historical validation**: Run on 2012-2017 papers
   - Find high-impact PhDs from then
   - Check who founded companies 2018-2024
   - Calculate success rate
   - Proves the method works

2. **Crunchbase integration**:
   - Get API key ($)
   - Auto-fetch funding data
   - Filter for Series A-B companies

3. **Better filters**:
   - Remove historical figures
   - Company size data
   - Founding year

### Ongoing
- **Quarterly runs**: Re-run every 3 months
- **Track transitions**: Monitor career changes
- **Build relationships**: Connect with identified researchers
- **Refine scoring**: Based on what actually works

---

## 💰 Investment Thesis

**Bet on**: Pre-Series B startups with 2+ high-PageRank PhDs from our list

**Why it works**:
1. **Information asymmetry**: Academic impact is public but takes time to be recognized
2. **Timing window**: 2-5 years post-PhD is optimal for founding/joining startups
3. **PageRank advantage**: Better predictor than raw citations
4. **Network effects**: Top researchers attract other top researchers

**Risk factors**:
- Execution risk (research ≠ business)
- Market timing (great tech, wrong time)
- Team composition (need biz co-founder)
- Capital needs (deep tech = long runway)

---

## 📖 Files Reference

### To Open Now
1. `data/analysis/INVESTMENT_LEADS.csv` - Your main list
2. `data/analysis/COMPANIES.csv` - Company clusters

### Visualizations
1. `data/analysis/pagerank_distribution.png` - Impact distribution
2. `data/analysis/collaboration_network.png` - Who works together
3. `data/analysis/citation_network.png` - Paper connections

### Documentation
1. `README.md` - Project overview
2. `FULL_RUN_COMPLETE.md` - Complete guide
3. `EXAMPLE.md` - Usage examples
4. `ACTION_PLAN.md` - This file

---

## 🛠️ How to Re-Run

```bash
# Activate environment
source .venv/bin/activate

# Get fresh papers
citation-arbitrage fetch-papers --from-year 2020 --min-citations 300 --max-papers 5000

# Compute PageRank
citation-arbitrage compute-pagerank

# Find grad students
citation-arbitrage identify-grad-students

# Batch fetch authors (takes ~12 min)
python3 scripts/batch_fetch_authors.py

# Generate leads
python3 scripts/analyze_investment_leads.py

# Create visualizations
python3 scripts/visualize_network.py
```

---

## 🎯 Success Metrics

Track these to validate approach:

### Immediate
- **Lead quality**: % that pass manual research
- **Data quality**: % that are real researchers at real companies
- **Coverage**: % of known successful founders we identify

### 3 Months
- **Conversion**: % of leads that become investment opportunities
- **Accuracy**: % of "startups" that are actually startups (not big companies)
- **Efficiency**: Hours per vetted lead

### 1 Year
- **Portfolio**: Number of investments made from this method
- **Returns**: IRR on investments (if any closed)
- **Network**: Relationships built with researchers

---

**Built with Citation Arbitrage v0.1.0**
*Find overlooked opportunities by tracking influential researchers*

Last Updated: 2025-10-27
