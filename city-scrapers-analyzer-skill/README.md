# City Scrapers Repository Analyzer

A comprehensive Claude Skill for assessing the health and functionality of city-scrapers repositories across the Documenters Network.

## Quick Start

### Installation

```bash
cd city-scrapers-analyzer-skill
pip install -r requirements.txt
```

### Set GitHub Token

```bash
export GITHUB_TOKEN="your_github_personal_access_token"
```

Get a token from: https://github.com/settings/tokens

### Run Examples

```bash
python example_usage.py
```

### Basic Usage

```python
from src.analyzer import RepositoryAnalyzer

# Initialize
analyzer = RepositoryAnalyzer(github_token="your_token")

# Analyze single repo
report = analyzer.analyze_repository("city-scrapers-atl")

# Analyze ecosystem
ecosystem = analyzer.analyze_ecosystem()
```

## What This Skill Does

1. **Discovers** all city-scrapers-* repositories in City-Bureau organization
2. **Executes** scrapers with timeout protection and comprehensive logging
3. **Classifies** failures into 12 distinct categories
4. **Estimates** repair effort based on complexity and failure type
5. **Prioritizes** repairs using weighted scoring (contractual risk, usage, freshness, feasibility)
6. **Identifies** Harambe conversion candidates
7. **Generates** JSON and Markdown reports at multiple levels

## Key Features

### Status Classification

- SUCCESS / STALE_SUCCESS
- SELECTOR_FAILURE (most common - 47% of failures)
- HTTP_ERROR (404, 403, 500)
- JAVASCRIPT_REQUIRED (needs browser automation)
- EMPTY_RESULT / TIMEOUT
- IMPORT_ERROR / ENCODING_ERROR / SSL_ERROR
- DORMANT (repo inactive >90 days)
- UNKNOWN_FAILURE

### Priority Scoring

Weighted algorithm:
- **40%** Contractual Risk (San Diego, Wichita, Columbia Gorge)
- **30%** Usage Frequency (Documenters assignments)
- **20%** Data Freshness (impact of missing data)
- **10%** Repair Feasibility (quick wins prioritized)

Tiers: CRITICAL (≥8.0), HIGH (6.0-7.9), MEDIUM (4.0-5.9), LOW (<4.0)

### Harambe Candidacy

Scoring factors:
- +3: JavaScript requirement
- +4: Existing Reworkd implementation
- +2: High complexity
- +1: Difficult conventional repair
- -2: Maintenance burden

Recommendation: Score ≥6 = HARAMBE_CONVERSION

### Repair Effort Estimation

Base hours by failure type × complexity multiplier × dependency factor

| Failure | Base Hours | Example |
|---------|------------|---------|
| IMPORT_ERROR | 1.0 | Update Pipfile |
| SELECTOR_FAILURE | 3.0 | Update CSS selectors |
| JAVASCRIPT_REQUIRED | 12.0 | Convert to Harambe |

## Output Examples

### Repository Report

```json
{
  "repo_name": "city-scrapers-atl",
  "summary": {
    "total_scrapers": 20,
    "functional": 12,
    "success_rate": 0.60
  },
  "effort_summary": {
    "total_hours_estimated": 42.5
  },
  "strategic_assessment": {
    "overall_health": "MODERATE"
  }
}
```

### Ecosystem Report

```json
{
  "total_scrapers": 342,
  "ecosystem_health": {
    "overall_success_rate": 0.588
  },
  "total_repair_effort": {
    "hours": 428,
    "parallel_effort_estimate": "4-6 weeks with 2 developers"
  }
}
```

## Use Cases

### 1. Single Repository Deep Dive

```python
report = analyzer.analyze_repository(
    "city-scrapers-atl",
    clone_locally=True,  # Execute scrapers
    max_scrapers=None    # Analyze all
)
```

### 2. Quick Ecosystem Scan

```python
ecosystem = analyzer.analyze_ecosystem(
    clone_locally=False,  # API only, no execution
    max_scrapers_per_repo=None
)
```

### 3. Priority Triage

```python
# Find critical failures
for repo in ecosystem['repos']:
    critical = [s for s in repo['scrapers']
                if s['priority_assessment']['priority_tier'] == 'CRITICAL']
```

### 4. Harambe Candidate Identification

```python
candidates = [s for s in all_scrapers
              if s['harambe_candidacy']['recommendation'] == 'HARAMBE_CONVERSION']
```

## Performance

- **API Only**: ~15-20 minutes for 342 scrapers
- **With Execution**: ~2-4 hours for 342 scrapers
- **Rate Limits**: GitHub API 5000 requests/hour (with token)
- **Memory**: ~100-200MB for ecosystem analysis

## Architecture

```
src/
├── analyzer.py         # Main orchestrator
├── github_client.py    # GitHub API integration
├── executor.py         # Scraper execution engine
├── classifier.py       # Status classification
├── scorer.py           # Priority & Harambe scoring
└── reporter.py         # Report generation
```

## Configuration

### Environment Variables

```bash
export GITHUB_TOKEN="..."        # Required for >60 requests/hour
export OUTPUT_DIR="./reports"    # Optional, default: ./reports
```

### Initialization Options

```python
analyzer = RepositoryAnalyzer(
    github_token=None,          # Or use GITHUB_TOKEN env var
    timeout_seconds=900,        # 15 min timeout per scraper
    output_dir="./reports",     # Report output directory
    stale_threshold_days=30     # Data staleness threshold
)
```

## Limitations

- Requires Python 3.11+
- Requires Git and Pipenv for local execution
- GitHub API rate limits (5000/hour with token)
- Local execution is time-intensive
- Estimates are heuristic, not definitive

## Troubleshooting

### Rate Limit Exceeded

```python
rate_limit = analyzer.check_rate_limit()
print(f"Reset at: {rate_limit['reset_at']}")
# Wait until reset time
```

### Scraper Timeouts

```python
# Increase timeout
analyzer = RepositoryAnalyzer(timeout_seconds=1800)  # 30 min
```

### Import Errors in Cloned Repo

```bash
cd /tmp/city-scrapers-xxx
pipenv install --skip-lock
```

## Documentation

- **SKILL.md**: Complete skill documentation
- **example_usage.py**: Runnable examples
- **CITY_SCRAPERS_SKILL_CREATION_GUIDE.md**: Guide for creating this skill

## Integration

### With Subagents (Orchestrator Pattern)

```python
# In orchestrator Claude session
repos = discover_all_repos()

for batch in chunks(repos, 10):
    # Launch subagents in parallel
    results = []
    for repo in batch:
        result = subagent_with_skill.analyze_repository(repo)
        results.append(result)

    # Aggregate batch results
    aggregate_and_save(results)
```

### In CI/CD Pipeline

```yaml
# .github/workflows/scraper-health-check.yml
name: Scraper Health Check
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run analyzer
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python -m src.analyzer --repos city-scrapers-atl
```

## Contributing

See main [city-scrapers CONTRIBUTING.md](https://github.com/City-Bureau/city-scrapers/blob/main/CONTRIBUTING.md)

## License

MIT License (same as city-scrapers project)

## Support

- GitHub Issues: [City-Bureau/city-scrapers](https://github.com/City-Bureau/city-scrapers/issues)
- Slack: [Join Documenters Slack](https://airtable.com/shrRv027NLgToRFd6)
- Email: documenters@citybureau.org

---

**Version**: 1.0.0
**Last Updated**: 2025-11-14
**Maintained By**: City Bureau / Documenters Network
