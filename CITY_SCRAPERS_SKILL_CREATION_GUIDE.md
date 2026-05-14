# City Scrapers Repository Analyzer - Claude Skill Creation Guide

## Overview

This guide provides comprehensive instructions for creating a Claude Skill that can analyze city-scrapers repositories across the City Bureau Documenters network, identify non-functional scrapers, categorize failure modes, and assess repair complexity.

## Project Context

### The City Scrapers Ecosystem

- **Purpose**: Scrape public meeting data from local government websites across multiple cities
- **Structure**: Each city has a program with its own repository (e.g., `city-scrapers-atl` for Atlanta, `city-scrapers-det` for Detroit)
- **Template**: All repositories are based on the [city-scrapers-template](https://github.com/City-Bureau/city-scrapers-template)
- **Core Library**: Uses `city-scrapers-core` for shared functionality
- **Framework**: Built on Scrapy framework with Python 3.11+

### Repository Architecture

Each city-scrapers repository contains:

```
city-scrapers-{city}/
├── city_scrapers/
│   ├── spiders/          # Individual scraper files
│   ├── settings/         # Scrapy configuration
│   └── mixins/           # Shared scraper patterns
├── tests/                # Unit tests for each scraper
│   └── files/           # Test HTML fixtures
├── .github/workflows/    # CI/CD pipelines
│   ├── ci.yml           # Pull request checks
│   └── cron.yml         # Daily scraper execution
├── Pipfile              # Python dependencies
├── scrapy.cfg           # Scrapy configuration
└── .deploy.sh           # Deployment script
```

### Scraper Structure

Each scraper inherits from `CityScrapersSpider` and implements:

1. **Required attributes**:
   - `name`: Unique spider identifier
   - `agency`: Government agency name
   - `timezone`: Local timezone
   - `start_urls`: List of URLs to scrape

2. **Core methods**:
   - `parse()`: Main parsing logic, yields Meeting items
   - `_parse_title()`: Extract meeting title
   - `_parse_start()`: Extract meeting datetime
   - `_parse_location()`: Extract meeting location
   - `_parse_links()`: Extract related documents
   - `_get_status()`: Determine meeting status (TENTATIVE, PASSED, CANCELLED)

3. **Output format**: Meeting objects with standardized fields:
   ```python
   {
       "title": str,
       "description": str,
       "classification": str,  # COMMISSION, BOARD, COMMITTEE, etc.
       "start": datetime,
       "end": datetime or None,
       "all_day": bool,
       "location": {"name": str, "address": str},
       "links": [{"title": str, "href": str}],
       "source": str,
       "status": str,
       "id": str
   }
   ```

### Testing Infrastructure

Each scraper has companion tests:
- Uses `freezegun` to freeze time for consistent testing
- Stores HTML fixtures in `tests/files/`
- Validates all meeting fields
- Typical test coverage: 12+ test functions per scraper

### CI/CD Workflows

1. **CI Workflow** (ci.yml):
   - Runs on push/PR
   - Code quality: isort, black, flake8
   - Unit tests: pytest
   - Output validation: scrapy validate

2. **Cron Workflow** (cron.yml):
   - Runs daily at 8:12 AM UTC
   - Executes all scrapers via `.deploy.sh`
   - Stores results in Azure Blob Storage
   - Uses OpenVPN for restricted sites
   - Combines output feeds

## Common Failure Modes

Based on typical web scraper failures:

### 1. **Website Structure Changes** (High frequency)
- HTML selectors no longer match
- Page layout redesign
- CSS class/ID changes
- **Detection**: Parse errors, empty results, assertion failures

### 2. **URL/Endpoint Changes** (Medium frequency)
- Start URL returns 404
- Redirect to new location
- URL pattern changes
- **Detection**: HTTP errors, connection failures

### 3. **Authentication/Access Issues** (Low frequency)
- New login requirements
- CAPTCHA implementation
- IP blocking/rate limiting
- Cloudflare protection
- **Detection**: 403/401 errors, timeout errors

### 4. **Date/Time Parsing Failures** (Medium frequency)
- Date format changes
- Timezone handling issues
- Regex pattern mismatches
- **Detection**: ValueError, parsing exceptions

### 5. **Dynamic Content Loading** (Medium frequency)
- JavaScript-rendered content
- AJAX-loaded meetings
- Pagination changes
- **Detection**: Empty results despite successful page load

### 6. **Data Format Changes** (Low frequency)
- JSON API schema changes
- PDF format changes (for PDF-based scrapers)
- Calendar feed format updates
- **Detection**: KeyError, parsing exceptions

### 7. **Dependency/Environment Issues** (Low frequency)
- Outdated library versions
- Python version incompatibility
- Missing dependencies
- **Detection**: ImportError, runtime errors

## Phase 1: Creating the City Scrapers Analyzer Skill

### Step 1: Initiate Skill Creation Dialogue

Start a new Claude conversation and provide this context:

```
I need to create a Claude Skill called "City Scrapers Repository Analyzer"
that can systematically analyze city-scrapers repositories to identify
non-functional scrapers and categorize their failure modes.

The skill will be used by multiple subagents coordinated by an orchestrator
to analyze hundreds of city-scrapers repositories across the City Bureau
Documenters network.

Here's the project context:
[Provide sections from "Project Context" above]
```

### Step 2: Define Core Skill Capabilities

Explain to Claude that the Skill should be able to:

1. **Repository Setup**
   - Clone a city-scrapers repository
   - Install dependencies via Pipfile/pipenv
   - Verify Python 3.11+ environment
   - Check for required directory structure

2. **Scraper Discovery**
   - List all spider files in `city_scrapers/spiders/`
   - Extract spider metadata (name, agency, start_urls)
   - Identify test files and fixtures

3. **Execution Testing**
   - Run individual scrapers with verbose output
   - Capture stdout, stderr, and exceptions
   - Set timeout limits (e.g., 5 minutes per scraper)
   - Parse Scrapy statistics and logs

4. **Failure Analysis**
   - Categorize errors by type (see Common Failure Modes)
   - Extract relevant error messages and tracebacks
   - Identify specific failing components (selectors, parsers, etc.)
   - Check for empty results vs. errors

5. **GitHub Workflow Analysis** (Alternative approach)
   - Use GitHub CLI to fetch workflow run logs
   - Parse cron.yml execution results
   - Identify failing scrapers from CI logs
   - Extract error patterns from workflow artifacts

6. **Test Execution**
   - Run pytest for specific scraper tests
   - Identify failing test cases
   - Correlate test failures with scraper failures

7. **Complexity Assessment**
   - Estimate repair difficulty (Low/Medium/High)
   - Identify required resources (HTML inspection, API docs, etc.)
   - Suggest repair strategies

8. **Structured Reporting**
   - Generate JSON output with standardized schema
   - Create human-readable markdown reports
   - Aggregate statistics and trends

### Step 3: Define Input/Output Schema

Provide Claude with this schema specification:

**Input Schema** (for each repository analysis):
```json
{
  "repository_url": "https://github.com/City-Bureau/city-scrapers-atl",
  "repository_name": "city-scrapers-atl",
  "branch": "main",
  "analysis_mode": "local_execution|workflow_logs|both",
  "timeout_per_scraper": 300,
  "max_concurrent_scrapers": 5
}
```

**Output Schema**:
```json
{
  "repository_name": "city-scrapers-atl",
  "analysis_timestamp": "2025-01-14T10:00:00Z",
  "total_scrapers": 45,
  "functional_scrapers": 32,
  "non_functional_scrapers": 13,
  "scrapers": [
    {
      "name": "atl_city_council",
      "agency": "Atlanta City Council",
      "status": "functional|non_functional|unknown",
      "execution_time": 12.5,
      "items_scraped": 8,
      "error": {
        "type": "website_structure_change|url_change|authentication|parsing|dynamic_content|data_format|dependency|other",
        "category": "high_frequency|medium_frequency|low_frequency",
        "message": "CSS selector '.meeting-item' returned no results",
        "traceback": "Full traceback...",
        "failing_method": "_parse_title",
        "start_url_status": 200
      },
      "test_results": {
        "total_tests": 12,
        "passed": 0,
        "failed": 12,
        "failing_tests": ["test_title", "test_start"]
      },
      "repair_estimate": {
        "complexity": "low|medium|high",
        "estimated_hours": 2.0,
        "required_resources": ["HTML inspection", "selector update"],
        "suggested_approach": "Update CSS selectors in parse() method"
      }
    }
  ],
  "failure_mode_summary": {
    "website_structure_change": 8,
    "url_change": 2,
    "authentication": 1,
    "parsing": 2,
    "dynamic_content": 0,
    "data_format": 0,
    "dependency": 0,
    "other": 0
  },
  "total_repair_hours": 24.5,
  "priority_repairs": ["atl_city_council", "atl_planning"]
}
```

### Step 4: Request Python Script Templates

Ask Claude to generate reusable Python scripts:

1. **scraper_executor.py**: Execute individual scrapers and capture results
2. **workflow_analyzer.py**: Fetch and parse GitHub workflow logs
3. **failure_classifier.py**: Categorize errors into failure modes
4. **complexity_estimator.py**: Assess repair complexity
5. **report_generator.py**: Generate structured JSON and markdown reports

Example request:
```
Please create a Python script called scraper_executor.py that can:
1. Accept a spider name as input
2. Execute the spider using Scrapy's CrawlerProcess
3. Capture all output, errors, and statistics
4. Handle timeouts gracefully
5. Return a structured result with execution status, items count, and any errors

The script should be reusable across all city-scrapers repositories.
```

### Step 5: Define Skill Workflow

Explain the step-by-step workflow the Skill should follow:

```
When analyzing a repository, the Skill should:

1. SETUP PHASE
   - Clone repository to temporary directory
   - Verify directory structure matches template
   - Install dependencies (pipenv install)
   - Check Python version compatibility

2. DISCOVERY PHASE
   - List all spider files
   - Extract spider metadata
   - Count total scrapers

3. EXECUTION PHASE (for each scraper)
   - Run scraper with timeout
   - Capture output and statistics
   - Run associated tests
   - Record results

4. ANALYSIS PHASE
   - Classify failures by type
   - Estimate repair complexity
   - Identify patterns across failures
   - Prioritize repairs by impact

5. REPORTING PHASE
   - Generate JSON output
   - Create markdown summary
   - Save artifacts to designated location
   - Return structured data to orchestrator

6. CLEANUP PHASE
   - Remove cloned repository
   - Clear temporary files
   - Release resources
```

### Step 6: Provide Example Scenarios

Give Claude concrete examples to train on:

**Example 1: Website Structure Change**
```
Spider: chi_board_elections
Error: CSS selector '.views-row article' returned 0 results
Diagnosis: Website redesign changed HTML structure
Complexity: Low (2 hours)
Approach: Inspect current HTML, update selectors
```

**Example 2: URL Change**
```
Spider: det_planning
Error: HTTP 404 on https://detroitmi.gov/planning/meetings
Diagnosis: URL endpoint changed
Complexity: Low (1 hour)
Approach: Find new URL, update start_urls
```

**Example 3: Dynamic Content**
```
Spider: cle_city_council
Error: 0 meetings found, page loads successfully
Diagnosis: JavaScript-rendered content
Complexity: High (6-8 hours)
Approach: Use Selenium/Playwright or find API endpoint
```

### Step 7: Test the Skill

Before deploying to subagents, test the Skill with:

1. A known-good repository (current city-scrapers)
2. A repository with known failures
3. Edge cases (empty repos, no tests, etc.)

Ask Claude to:
```
Let's test this Skill on the city-scrapers repository. Please:
1. Clone https://github.com/City-Bureau/city-scrapers
2. Analyze the first 5 scrapers
3. Generate a sample report
4. Show me the JSON output
```

## Phase 2: Orchestrator Setup

### Creating the Orchestrator

In a new Claude session, create the orchestrator:

```
I need you to act as an orchestrator that coordinates multiple subagents,
each using the "City Scrapers Repository Analyzer" Skill to analyze
city-scrapers repositories.

You will:
1. Get a list of all city-scrapers-* repositories from City-Bureau
2. Assign each repository to a subagent
3. Manage subagent execution (not all at once, but in manageable batches)
4. Collect reports from all subagents
5. Aggregate results across all repositories
6. Generate a comprehensive analysis report

Here's the Skill definition: [provide Skill details]
```

### Orchestrator Workflow

```python
# Pseudo-code for orchestrator logic

1. Fetch repository list:
   - Use GitHub API or CLI
   - Filter for "city-scrapers-*" pattern
   - Exclude template and core repos
   - Result: ~50-100 repositories

2. Batch processing:
   - Group repos into batches of 5-10
   - For each batch:
     * Launch subagent for each repo
     * Each subagent uses the Skill
     * Wait for all subagents in batch to complete
     * Collect reports
   - Move to next batch

3. Aggregate results:
   - Total scrapers across all cities
   - Total functional vs non-functional
   - Failure mode distribution
   - Total estimated repair hours
   - Priority repositories (highest failure count)

4. Generate master report:
   - Executive summary
   - Repository-by-repository breakdown
   - Failure mode analysis
   - Repair roadmap with priorities
   - Resource allocation recommendations
```

### Orchestrator Commands

The orchestrator should support:

```bash
# Get repository list
gh repo list City-Bureau --topic city-scrapers --limit 100 --json name,url

# Launch subagent (conceptual)
Task: Analyze repository city-scrapers-atl
Skill: City Scrapers Repository Analyzer
Input: {"repository_url": "...", "analysis_mode": "local_execution"}

# Collect results
Subagent report stored in: ./analysis_results/city-scrapers-atl.json
```

## Phase 3: Execution Strategy

### Resource Management

- **Concurrency**: Run 5-10 subagents in parallel
- **Rate limiting**: Respect GitHub API limits
- **Timeout**: 30 minutes per repository analysis
- **Storage**: Organize results by timestamp and repository

### Error Handling

Orchestrator should handle:
- Subagent failures (retry once)
- Repository access issues (skip, log error)
- Timeout scenarios (mark as incomplete)
- Network failures (retry with backoff)

### Progress Tracking

```
Orchestrator Status Report:
========================
Total repositories: 87
Completed: 45 (52%)
In progress: 10 (11%)
Pending: 32 (37%)
Failed: 0 (0%)

Current batch: 5 of 9
Estimated completion: 2.5 hours

Top failures so far:
- Website structure change: 124 scrapers
- URL changes: 38 scrapers
- Parsing errors: 29 scrapers
```

## Phase 4: Analysis and Reporting

### Master Report Structure

```markdown
# City Scrapers Network-Wide Analysis
**Date**: 2025-01-14
**Repositories Analyzed**: 87
**Total Scrapers**: 1,247

## Executive Summary
- Functional: 1,089 (87.3%)
- Non-functional: 158 (12.7%)
- Total estimated repair hours: 342

## Failure Mode Breakdown
1. Website Structure Changes: 94 scrapers (59.5%)
2. URL Changes: 28 scrapers (17.7%)
3. Parsing Errors: 19 scrapers (12.0%)
4. Dynamic Content: 11 scrapers (7.0%)
5. Other: 6 scrapers (3.8%)

## Repository Rankings (by failure count)
1. city-scrapers-det: 23 failures
2. city-scrapers-cle: 18 failures
3. city-scrapers-atl: 15 failures
...

## Repair Roadmap
### Phase 1 (Low complexity, 2-4 weeks)
- 82 scrapers, 164 hours
- Primarily selector updates and URL fixes

### Phase 2 (Medium complexity, 6-8 weeks)
- 51 scrapers, 204 hours
- Date parsing updates, data format changes

### Phase 3 (High complexity, 3-4 months)
- 25 scrapers, 200 hours
- Dynamic content handling, authentication

## Recommendations
1. Prioritize high-traffic cities
2. Batch similar failures for efficiency
3. Update city-scrapers-core for common patterns
4. Implement monitoring for early failure detection
```

### Deliverables

1. **JSON Database**: All structured reports for programmatic access
2. **Master Report**: Comprehensive markdown summary
3. **Per-Repository Reports**: Detailed analysis for each city
4. **Repair Scripts**: Generated fix templates for common issues
5. **Monitoring Dashboard**: (Future) Track scraper health over time

## Advanced Features

### Optional Enhancements

1. **Automated Repair**:
   - For simple selector changes, generate PR with fixes
   - Use LLM to inspect current HTML and suggest selectors

2. **Continuous Monitoring**:
   - Schedule weekly re-analysis
   - Track failure trends over time
   - Alert on new failures

3. **Smart Prioritization**:
   - Weight by city population
   - Consider meeting frequency/importance
   - Factor in historical data usage

4. **Repair Assistance**:
   - Generate repair guides per scraper
   - Create test fixtures from current HTML
   - Draft pull request descriptions

## Example Skill Conversation Starter

Use this to begin creating the Skill:

```
I want to create a Claude Skill for analyzing city-scrapers repositories.
Let me explain the context:

The City Bureau Documenters network maintains ~100 repositories that scrape
public meeting data from local government websites. Each repository follows
the city-scrapers-template pattern and contains dozens of individual scrapers
built with Scrapy.

We need to analyze all repositories to:
1. Identify which scrapers are non-functional
2. Categorize failure types
3. Estimate repair complexity
4. Generate actionable reports

Here's the architecture:
- Each repo: city_scrapers/spiders/*.py (scraper files)
- Tests: tests/test_*.py with HTML fixtures
- CI/CD: .github/workflows/ci.yml and cron.yml
- Dependencies: Pipfile with scrapy, city-scrapers-core
- Python: 3.11+

Common failures include:
- Website HTML structure changes (selectors break)
- URL changes (404 errors)
- Dynamic JavaScript content (empty results)
- Date parsing issues (format changes)

The Skill should be able to:
1. Clone and set up a repository
2. Execute all scrapers and capture results
3. Run tests and correlate failures
4. Analyze errors and categorize by failure mode
5. Estimate repair complexity (low/medium/high)
6. Generate structured JSON reports

Output format should be:
{repository analysis with all scrapers, status, errors, repair estimates}

I'll be using this Skill across many subagents coordinated by an orchestrator
to analyze all ~100 repositories in parallel batches.

Can you help me design this Skill, including creating reusable Python scripts
for scraper execution, error analysis, and report generation?
```

## Success Criteria

The Skill is working correctly when:

✅ It can clone and set up any city-scrapers repository
✅ It executes scrapers and captures all output/errors
✅ It correctly categorizes failures into standard types
✅ Repair complexity estimates are reasonable
✅ JSON output matches the defined schema
✅ Reports are actionable and informative
✅ The Skill can be used by multiple subagents
✅ Orchestrator can aggregate results meaningfully

## Troubleshooting

### Common Issues

1. **Pipenv installation fails**
   - Check Python version (must be 3.11+)
   - Verify Pipfile.lock is present
   - Try `pipenv install --skip-lock`

2. **Scrapers timeout**
   - Increase timeout limit
   - Check for network issues
   - Some sites may require VPN

3. **Empty results vs. errors**
   - Check Scrapy statistics for 'item_scraped_count'
   - Examine response.status
   - Look for redirect responses

4. **Test failures vs. scraper failures**
   - Tests may fail due to outdated fixtures
   - Scraper may work but return different data format
   - Correlate test failures with actual execution

## Next Steps

After creating the Skill:

1. Test on 3-5 repositories manually
2. Refine error categorization based on results
3. Adjust complexity estimation algorithm
4. Create orchestrator in new Claude session
5. Run pilot batch (10 repositories)
6. Review aggregated results
7. Full deployment across all repositories
8. Generate master analysis report
9. Create repair roadmap
10. Begin systematic repairs

---

## Appendix: Reference Commands

### Useful GitHub CLI Commands
```bash
# List all city-scrapers repos
gh repo list City-Bureau --topic city-scrapers --limit 100

# Get workflow runs for a repo
gh run list --repo City-Bureau/city-scrapers-atl --limit 10

# Download workflow logs
gh run download <run-id> --repo City-Bureau/city-scrapers-atl
```

### Useful Scrapy Commands
```bash
# List all spiders
scrapy list

# Run specific spider with verbose output
scrapy crawl chi_board_elections -s LOG_LEVEL=DEBUG

# Validate spider output
scrapy validate chi_board_elections

# Run all spiders
scrapy list | xargs -I {} scrapy crawl {}
```

### Useful Testing Commands
```bash
# Run tests for specific spider
pytest tests/test_chi_board_elections.py -v

# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=city_scrapers
```

---

**Document Version**: 1.0
**Last Updated**: 2025-01-14
**Maintained By**: City Bureau / Documenters Network
