

 # City Scrapers Repository Analyzer - Claude Skill

## Overview

This Skill provides comprehensive assessment of city-scrapers repositories across the Documenters Network, identifying non-functional scrapers, categorizing failure modes, estimating repair complexity, and generating actionable reports.

## Purpose

Systematically assess scraper health to inform migration strategy decisions before the December 31, 2025 Reworkd shutdown deadline.

## Capabilities

1. **Repository Discovery**: Automatically discover all city-scrapers-* repositories in City-Bureau organization
2. **Scraper Execution**: Run scrapers with timeout handling and comprehensive logging
3. **Status Classification**: Categorize scraper status into 12 distinct failure modes
4. **Complexity Assessment**: Evaluate scraper complexity based on code metrics
5. **Effort Estimation**: Calculate repair effort estimates with confidence levels
6. **Priority Scoring**: Weighted scoring based on contractual risk, usage, freshness, and feasibility
7. **Harambe Candidacy**: Identify scrapers that should be converted to Harambe SDK
8. **Comprehensive Reporting**: Generate JSON and Markdown reports at multiple levels

## Installation

```bash
cd city-scrapers-analyzer-skill
pip install -r requirements.txt
```

## Configuration

Set environment variables:

```bash
export GITHUB_TOKEN="your_github_personal_access_token"
```

## Usage

### Analyze Single Repository

```python
from src.analyzer import RepositoryAnalyzer

# Initialize analyzer
analyzer = RepositoryAnalyzer(
    github_token="your_token",  # or set GITHUB_TOKEN env var
    timeout_seconds=900,
    output_dir="./reports",
    stale_threshold_days=30
)

# Analyze a repository
report = analyzer.analyze_repository(
    repo_name="city-scrapers-atl",
    clone_locally=True,
    max_scrapers=None  # analyze all scrapers
)

print(f"Success rate: {report['summary']['success_rate']:.1%}")
print(f"Total repair hours: {report['effort_summary']['total_hours_estimated']}")
```

### Analyze Entire Ecosystem

```python
# Analyze all city-scrapers repositories
ecosystem_report = analyzer.analyze_ecosystem(
    repo_names=None,  # auto-discover all repos
    clone_locally=True,
    max_scrapers_per_repo=None
)

print(f"Total scrapers: {ecosystem_report['total_scrapers']}")
print(f"Success rate: {ecosystem_report['ecosystem_health']['overall_success_rate']:.1%}")
```

### API-Only Analysis (No Execution)

```python
# Faster analysis without running scrapers
report = analyzer.analyze_repository(
    repo_name="city-scrapers-det",
    clone_locally=False  # use GitHub API only
)
```

### Check Rate Limits

```python
rate_limit = analyzer.check_rate_limit()
print(f"Remaining: {rate_limit['remaining']}/{rate_limit['limit']}")
```

## Output Schema

### Scraper-Level Assessment

```json
{
  "repo_name": "city-scrapers-atl",
  "scraper_name": "atl_city_council",
  "file_path": "city_scrapers/spiders/atl_city_council.py",
  "agency_name": "Atlanta City Council",
  "start_urls": ["https://atlantacityga.iqm2.com/Citizens/Calendar.aspx"],

  "execution_results": {
    "status": "SUCCESS|SELECTOR_FAILURE|HTTP_ERROR|etc",
    "exit_code": 0,
    "item_count": 15,
    "execution_time_seconds": 12.4,
    "last_run": "2025-11-14T10:30:00Z",
    "log_snippet": "..."
  },

  "complexity_assessment": {
    "lines_of_code": 145,
    "complexity_rating": "simple|medium|complex",
    "dependencies": ["IQM2Mixin"],
    "last_modified": "2024-08-15T14:20:00Z"
  },

  "failure_analysis": {
    "primary_failure_mode": "SELECTOR_FAILURE",
    "root_cause_hypothesis": "Website redesign",
    "evidence": ["selector not found"],
    "confidence": "high"
  },

  "repair_estimate": {
    "total_estimated_hours": 4.5,
    "effort_rating": "LOW|MEDIUM|HIGH|VERY_HIGH",
    "repair_approach": "Update CSS selectors"
  },

  "priority_assessment": {
    "priority_score": 7.2,
    "priority_tier": "CRITICAL|HIGH|MEDIUM|LOW"
  },

  "harambe_candidacy": {
    "recommendation": "CONVENTIONAL_REPAIR|HARAMBE_CONVERSION",
    "reasoning": "..."
  }
}
```

### Repository-Level Report

```json
{
  "repo_name": "city-scrapers-atl",
  "summary": {
    "total_scrapers": 20,
    "functional": 12,
    "failed": 8,
    "success_rate": 0.60
  },
  "failure_breakdown": {
    "SELECTOR_FAILURE": 4,
    "HTTP_ERROR": 2
  },
  "effort_summary": {
    "total_hours_estimated": 42.5
  },
  "strategic_assessment": {
    "overall_health": "MODERATE",
    "recommended_approach": "..."
  }
}
```

### Ecosystem-Level Report

```json
{
  "total_scrapers": 342,
  "ecosystem_health": {
    "functional_scrapers": 201,
    "failed_scrapers": 141,
    "overall_success_rate": 0.588
  },
  "failure_patterns": {
    "SELECTOR_FAILURE": {"count": 67, "percentage": 47.5}
  },
  "total_repair_effort": {
    "hours": 428,
    "parallel_effort_estimate": "4-6 weeks with 2 developers"
  },
  "strategic_insights": [...],
  "recommendations": {...}
}
```

## Status Classifications

| Status | Description | Frequency |
|--------|-------------|-----------|
| **SUCCESS** | Scraper runs and extracts current data | N/A |
| **STALE_SUCCESS** | Runs but extracts old data | Medium |
| **SELECTOR_FAILURE** | CSS/XPath selectors don't match | **High** |
| **HTTP_ERROR** | Cannot access website (404, 403, 500) | Medium |
| **JAVASCRIPT_REQUIRED** | Site requires browser rendering | Medium |
| **EMPTY_RESULT** | Runs but finds no items | Medium |
| **TIMEOUT** | Execution exceeds time limit | Medium |
| **IMPORT_ERROR** | Python dependency issues | Low |
| **ENCODING_ERROR** | Character encoding problems | Low |
| **SSL_ERROR** | Certificate/HTTPS issues | Low |
| **DORMANT** | Repository inactive >90 days | Low |
| **UNKNOWN_FAILURE** | Unclassified error | Medium |

## Priority Scoring

Weighted scoring algorithm:

- **Contractual Risk** (40%): Agencies with contractual obligations
- **Usage Frequency** (30%): Based on Documenters assignments
- **Data Freshness** (20%): Impact of missing/stale data
- **Repair Feasibility** (10%): Ease of repair (lower effort = higher score)

Priority tiers:
- **CRITICAL**: Score ≥ 8.0
- **HIGH**: Score 6.0-7.9
- **MEDIUM**: Score 4.0-5.9
- **LOW**: Score < 4.0

## Harambe Candidacy Scoring

Factors:
- JavaScript requirement: +3
- Existing Reworkd implementation: +4
- High site complexity: +2
- Difficult conventional repair: +1
- Maintenance burden: -2

Recommendations:
- Score ≥ 6: **HARAMBE_CONVERSION** (strong candidate)
- Score 4-5: **CONSIDER_HARAMBE** (viable but not required)
- Score < 4: **CONVENTIONAL_REPAIR** (preferred)

## Repair Effort Estimation

Base effort by failure type (hours):

| Failure Type | Base Hours | Typical Actions |
|--------------|------------|-----------------|
| IMPORT_ERROR | 1.0 | Update dependencies |
| ENCODING_ERROR | 1.5 | Fix character encoding |
| SSL_ERROR | 1.0 | Update certificate handling |
| HTTP_ERROR | 2.0 | Investigate site changes |
| TIMEOUT | 2.0 | Optimize or increase timeout |
| SELECTOR_FAILURE | 3.0 | Update CSS/XPath selectors |
| STALE_SUCCESS | 3.0 | Verify start_urls |
| EMPTY_RESULT | 4.0 | Investigate site structure |
| JAVASCRIPT_REQUIRED | 12.0 | Convert to Harambe |
| UNKNOWN_FAILURE | 4.0 | Debug logs |

Multipliers:
- **Complexity**: Simple (1.0x), Medium (1.5x), Complex (2.5x)
- **Dependencies**: Standalone (1.0x), Shared (1.3x), Coupled (1.5x)

## Architecture

```
RepositoryAnalyzer (main orchestrator)
├── GitHubClient (API access)
├── ScraperExecutor (execution engine)
├── StatusClassifier (failure categorization)
├── PriorityScorer (priority calculation)
├── HarambeScorer (candidacy assessment)
├── EffortEstimator (repair estimation)
└── ReportGenerator (output generation)
```

## Performance

- **GitHub API**: ~4 calls per scraper, 5000/hour limit
- **Execution**: ~15-30 seconds per simple scraper
- **Full Ecosystem**: ~2-4 hours for 342 scrapers (with local execution)
- **API-Only Mode**: ~15-20 minutes for 342 scrapers

## Error Handling

- Graceful degradation: Failed scrapers don't stop analysis
- Comprehensive logging: DEBUG level for troubleshooting
- Intermediate saves: Results saved per-scraper
- Timeout protection: 15-minute default per scraper
- Rate limit monitoring: Built-in rate limit checks

## Best Practices

1. **Use GitHub Token**: Required for >60 requests/hour
2. **Start Small**: Test on 1-2 repos before full ecosystem
3. **Monitor Rate Limits**: Check frequently with large batches
4. **Save Intermediate Results**: Enable incremental processing
5. **API-Only for Quick Scans**: Use local execution for definitive assessment
6. **Allocate Time**: Full ecosystem analysis takes hours

## Limitations

- **Execution Environment**: Requires Python 3.11+, Git, Pipenv
- **Network Access**: Must reach GitHub and scraper target sites
- **Local Storage**: Cloned repos can be 50-100MB each
- **Time**: Full execution analysis is time-intensive
- **Accuracy**: Estimates are heuristic, not definitive

## Troubleshooting

### Rate Limit Exceeded
```python
rate_limit = analyzer.check_rate_limit()
# Wait until rate_limit['reset_at']
```

### Scraper Timeouts
```python
analyzer = RepositoryAnalyzer(timeout_seconds=1800)  # 30 minutes
```

### Import Errors
```bash
cd {repo_path}
pipenv install --skip-lock
```

### Partial Analysis
```python
# Analyze subset for testing
report = analyzer.analyze_repository(
    "city-scrapers-atl",
    max_scrapers=5  # only first 5
)
```

## Integration

### Use with Subagents

```python
# In orchestrator Claude session
def analyze_batch(repo_names):
    for repo in repo_names:
        # Launch subagent with this Skill
        result = subagent.analyze_repository(repo)
        save_result(result)
```

### Use in CI/CD

```bash
# Run as scheduled job
python -m src.analyzer \
  --repos city-scrapers-atl city-scrapers-det \
  --output ./reports \
  --format json,markdown
```

## Future Enhancements

- [ ] Automated repair PRs for simple fixes
- [ ] Continuous monitoring mode
- [ ] Integration with assignment data
- [ ] Real-time dashboard
- [ ] Slack/email notifications
- [ ] Historical trend analysis
- [ ] ML-based failure prediction

## Support

For questions or issues:
- GitHub Issues: [City-Bureau/city-scrapers](https://github.com/City-Bureau/city-scrapers/issues)
- Slack: [Join Documenters Slack](https://airtable.com/shrRv027NLgToRFd6)
- Email: documenters@citybureau.org

## License

Same as city-scrapers project (MIT License)

---

**Version**: 1.0.0
**Last Updated**: 2025-11-14
**Maintained By**: City Bureau / Documenters Network
