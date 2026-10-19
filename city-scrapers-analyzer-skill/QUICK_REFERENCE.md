# City Scrapers Analyzer - Quick Reference

## Installation

```bash
cd city-scrapers-analyzer-skill
pip install -r requirements.txt
export GITHUB_TOKEN="your_token"  # or use $(gh auth token)
```

## Basic Usage

### Single Repository (API Only - Fast)

```python
from src.analyzer import RepositoryAnalyzer

analyzer = RepositoryAnalyzer()
report = analyzer.analyze_repository("city-scrapers-atl", clone_locally=False)

print(f"Success rate: {report['summary']['success_rate']:.1%}")
print(f"Repair hours: {report['effort_summary']['total_hours_estimated']}")
```

### Ecosystem Analysis

```python
ecosystem = analyzer.analyze_ecosystem(clone_locally=False)
print(f"Total scrapers: {ecosystem['total_scrapers']}")
print(f"Success rate: {ecosystem['ecosystem_health']['overall_success_rate']:.1%}")
```

### With Execution (Slow but Detailed)

```python
report = analyzer.analyze_repository("city-scrapers-atl", clone_locally=True)
# Takes 5-10 minutes, clones repo and runs scrapers
```

## Quick Commands

```bash
# Run examples
python example_usage.py

# Run tests
export GITHUB_TOKEN=$(gh auth token)
python test_skill.py

# Check rate limit
python -c "from src.github_client import GitHubClient; print(GitHubClient().check_rate_limit())"
```

## Status Classifications

| Status | What It Means | Repair Effort |
|--------|---------------|---------------|
| SUCCESS | Works fine | N/A |
| SELECTOR_FAILURE | HTML changed, selectors broke | 3-6 hours |
| HTTP_ERROR | URL returns 404/403/500 | 2-4 hours |
| JAVASCRIPT_REQUIRED | Needs browser automation | 12+ hours → Harambe |
| EMPTY_RESULT | Runs but finds nothing | 4-8 hours (investigate) |
| IMPORT_ERROR | Dependency issue | 1-2 hours |
| DORMANT | Repo inactive >90 days | Reactivate repo first |

## Priority Tiers

- **CRITICAL** (≥8.0): Immediate attention
- **HIGH** (6.0-7.9): Within 2 weeks
- **MEDIUM** (4.0-5.9): Schedule
- **LOW** (<4.0): Monitor/defer

## Harambe Recommendations

- **HARAMBE_CONVERSION** (score ≥6): Convert to Harambe
- **CONSIDER_HARAMBE** (score 4-5): Viable option
- **CONVENTIONAL_REPAIR** (score <4): Fix with Scrapy

## Finding Specific Scrapers

### Critical Priority
```python
critical = [s for r in ecosystem['repos']
            for s in r['scrapers']
            if s['priority_assessment']['priority_tier'] == 'CRITICAL']
```

### Harambe Candidates
```python
harambe = [s for r in ecosystem['repos']
           for s in r['scrapers']
           if s['harambe_candidacy']['recommendation'] == 'HARAMBE_CONVERSION']
```

### Quick Wins (Low effort + High priority)
```python
quick_wins = [s for r in ecosystem['repos']
              for s in r['scrapers']
              if s['repair_estimate']['effort_rating'] == 'LOW'
              and s['priority_assessment']['priority_tier'] in ['CRITICAL', 'HIGH']]
```

### Selector Failures (Most common)
```python
selector_fails = [s for r in ecosystem['repos']
                  for s in r['scrapers']
                  if s['execution_results']['status'] == 'SELECTOR_FAILURE']
```

## Output Locations

- **JSON Reports**: `./reports/*.json`
- **Markdown Summaries**: `./reports/*.md`
- **Test Reports**: `./test_reports/*.json`

## Common Issues

### Rate Limit Exceeded
```python
rate_limit = analyzer.check_rate_limit()
# Wait until rate_limit['reset_at']
```

### Timeout Errors
```python
analyzer = RepositoryAnalyzer(timeout_seconds=1800)  # Increase to 30 min
```

### Missing Dependencies
```bash
cd {repo_path}
pipenv install --skip-lock
```

## Performance

| Operation | Time |
|-----------|------|
| API-only (1 scraper) | 2-3 seconds |
| API-only (20 scrapers) | 30-45 seconds |
| API-only (ecosystem) | 15-20 minutes |
| With execution (1 scraper) | 15-30 seconds |
| With execution (20 scrapers) | 5-10 minutes |
| With execution (ecosystem) | 2-4 hours |

## API Rate Limits

- **Without token**: 60 requests/hour
- **With token**: 5,000 requests/hour
- **Usage**: ~4 requests per scraper

## Report Structure

```
report
├── summary (total, functional, failed, success_rate)
├── failure_breakdown (counts by status)
├── effort_summary (total hours, by tier)
├── priority_distribution (counts by tier)
├── harambe_candidates (count)
├── strategic_assessment
└── scrapers[] (detailed assessments)
```

## Key Metrics

### Effort Ratings
- TRIVIAL: <1 hour
- LOW: 1-4 hours
- MEDIUM: 4-8 hours
- HIGH: 8-16 hours
- VERY_HIGH: 16+ hours

### Base Repair Hours
- SELECTOR_FAILURE: 3 hours
- HTTP_ERROR: 2 hours
- JAVASCRIPT_REQUIRED: 12 hours
- IMPORT_ERROR: 1 hour

Multiplied by complexity (1.0x-2.5x) and dependencies (1.0x-1.5x)

## Example Workflows

### Workflow 1: Quick Health Check
```python
analyzer = RepositoryAnalyzer()
repos = ['city-scrapers-atl', 'city-scrapers-cle', 'city-scrapers-det']
for repo in repos:
    r = analyzer.analyze_repository(repo, clone_locally=False, max_scrapers=5)
    print(f"{repo}: {r['summary']['success_rate']:.0%} success")
```

### Workflow 2: Deep Dive on One Repo
```python
report = analyzer.analyze_repository('city-scrapers-atl', clone_locally=True)
for s in report['scrapers']:
    if s['priority_assessment']['priority_tier'] == 'CRITICAL':
        print(f"CRITICAL: {s['scraper_name']}")
        print(f"  Status: {s['execution_results']['status']}")
        print(f"  Effort: {s['repair_estimate']['total_estimated_hours']} hours")
        print(f"  Fix: {s['repair_estimate']['repair_approach']}")
```

### Workflow 3: Generate Executive Report
```python
ecosystem = analyzer.analyze_ecosystem(clone_locally=False)
# Automatically generates:
# - reports/ecosystem_analysis_YYYYMMDD_HHMMSS.json
# - reports/analysis_summary_YYYYMMDD_HHMMSS.md
```

## Documentation Files

- `README.md` - Quick start
- `SKILL.md` - Complete documentation
- `QUICK_REFERENCE.md` - This file
- `example_usage.py` - Runnable examples
- `test_skill.py` - Automated tests

## Support

- Issues: [github.com/City-Bureau/city-scrapers/issues](https://github.com/City-Bureau/city-scrapers/issues)
- Slack: [Join Documenters](https://airtable.com/shrRv027NLgToRFd6)
- Email: documenters@citybureau.org

---

**Version**: 1.0.0
**Last Updated**: 2025-11-14
