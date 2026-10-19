# Quick Start Guide: City Scrapers Ecosystem Analysis

## 🚀 Analyze All Repositories in 3 Ways

You have **three options** for analyzing the entire city-scrapers ecosystem, from simplest to most advanced:

---

## Option 1: CLI Single Command (Easiest) ⭐⭐⭐

**Best for**: Quick ecosystem health check, weekly monitoring, CI/CD

```bash
cd city-scrapers-analyzer-skill

# Set GitHub token
export GITHUB_TOKEN=$(gh auth token)

# Analyze entire ecosystem (API-only, fast ~15-20 minutes)
./cli.py ecosystem --save-db --notes "Weekly health check"

# Export results
./cli.py export ecosystem_analysis.csv
./cli.py stats

# View reports
cat reports/analysis_summary_*.md
```

**What you get**:
- JSON report: `reports/ecosystem_analysis_*.json`
- Markdown summary: `reports/analysis_summary_*.md`
- CSV export: `ecosystem_analysis.csv`
- SQLite database: `analysis_history.db`

**Limitations**:
- API-only (no scraper execution)
- Single process (not parallelized)
- Limited to what GitHub API can provide

**Time**: 15-20 minutes for full ecosystem

---

## Option 2: CLI Batch Processing (Recommended) ⭐⭐

**Best for**: Detailed analysis with execution, manageable batches

```bash
cd city-scrapers-analyzer-skill
export GITHUB_TOKEN=$(gh auth token)

# Get list of all repos
./cli.py list > all_repos.txt

# Process in batches (with execution for accuracy)
for repo in city-scrapers-atl city-scrapers-cle city-scrapers-det; do
    echo "Analyzing $repo..."
    ./cli.py analyze $repo --execute --save-db --notes "Batch 1"
done

# Aggregate results
./cli.py stats
./cli.py export batch_1_results.csv
```

**Shell script version**:
```bash
#!/bin/bash
# batch_analyze.sh

export GITHUB_TOKEN=$(gh auth token)

# Define batches
BATCH1="city-scrapers-atl city-scrapers-cle city-scrapers-det"
BATCH2="city-scrapers-akr city-scrapers-phil city-scrapers-roc"

for repo in $BATCH1; do
    echo "=========================================="
    echo "Analyzing: $repo"
    echo "=========================================="

    ./cli.py analyze $repo --execute --save-db --notes "Systematic review"

    # Brief pause between repos
    sleep 5
done

# Generate summary
echo "Batch complete! Generating summary..."
./cli.py stats
./cli.py export batch_results.csv
```

**What you get**:
- Scraper execution results (actual success/failure)
- Historical database tracking
- CSV exports for each batch
- Comparison across batches

**Time**: ~5-10 minutes per repository (execution included)

---

## Option 3: Orchestrator with Subagents (Advanced) ⭐

**Best for**: Parallelized processing, maximum detail, long-running analysis

See `ORCHESTRATOR_GUIDE.md` for complete instructions.

**Summary**:
1. Orchestrator discovers all repos
2. Launches Claude subagents in parallel batches
3. Each subagent analyzes one repository independently
4. Orchestrator aggregates all results
5. Generates comprehensive meta-analysis

**Time**: 2-4 hours total (but parallelized across subagents)

---

## Comparison Table

| Feature | CLI Single | CLI Batch | Orchestrator |
|---------|------------|-----------|--------------|
| **Ease of use** | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Speed** | 15-20 min | Varies | 2-4 hours |
| **Parallelization** | No | Manual | Yes |
| **Scraper execution** | Optional | Yes | Yes |
| **Detail level** | Medium | High | Highest |
| **Database tracking** | Yes | Yes | Yes |
| **CSV export** | Yes | Yes | Yes |
| **Comparison tools** | Yes | Yes | Yes |
| **Best for** | Quick checks | Systematic analysis | Full ecosystem deep dive |

---

## Recommended Workflow

### Week 1: Initial Baseline
```bash
# Quick baseline
./cli.py ecosystem --save-db --notes "Initial baseline"
./cli.py export baseline.csv

# This is run_id 1
```

### Week 2+: Detailed Analysis
```bash
# Pick top priority repos (from baseline)
# Analyze with execution
./cli.py analyze city-scrapers-atl --execute --save-db
./cli.py analyze city-scrapers-det --execute --save-db
./cli.py analyze city-scrapers-cle --execute --save-db

# Compare to baseline
./cli.py compare 1 2
```

### Ongoing: Weekly Monitoring
```bash
# Weekly quick check
./cli.py ecosystem --save-db --notes "Week $(date +%U) check"

# Compare to last week
CURRENT=$(python3 -c "from src.database import AnalysisDatabase; db = AnalysisDatabase(); print(db.conn.execute('SELECT MAX(run_id) FROM analysis_runs').fetchone()[0])")
PREVIOUS=$((CURRENT - 1))
./cli.py compare $PREVIOUS $CURRENT
```

---

## Setting Up GitHub Actions (Optional)

For automated weekly checks:

```yaml
# .github/workflows/scraper-health.yml
name: Weekly Scraper Health Check

on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday
  workflow_dispatch:

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd city-scrapers-analyzer-skill
          pip install -r requirements.txt

      - name: Run analysis
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          cd city-scrapers-analyzer-skill
          ./cli.py ecosystem --save-db --notes "Automated weekly check"
          ./cli.py export weekly_report.csv

      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: weekly-scraper-health
          path: |
            city-scrapers-analyzer-skill/reports/
            city-scrapers-analyzer-skill/weekly_report.csv
```

---

## Troubleshooting

### "Permission denied" running CLI
```bash
chmod +x cli.py
```

### "No module named 'src'"
```bash
# Make sure you're in the right directory
cd city-scrapers-analyzer-skill

# Try with python3 explicitly
python3 cli.py --help
```

### "GitHub rate limit exceeded"
```bash
# Check rate limit
./cli.py rate-limit

# Use token
export GITHUB_TOKEN=$(gh auth token)
./cli.py rate-limit  # Should show 5000/hour now
```

### "Database locked"
```bash
# Close any open database connections
# Check if another process is using it
lsof analysis_history.db

# If needed, create fresh database
mv analysis_history.db analysis_history_backup.db
./cli.py ecosystem --save-db  # Creates new database
```

---

## Next Steps

1. **Try the quick analysis first**:
   ```bash
   ./cli.py list
   ./cli.py analyze city-scrapers-atl
   ```

2. **Review the output**:
   ```bash
   ls -la reports/
   cat reports/*_summary*.md
   ```

3. **Save to database**:
   ```bash
   ./cli.py analyze city-scrapers-atl --save-db
   ./cli.py stats
   ```

4. **For full ecosystem**:
   - Start with CLI single command (Option 1)
   - Move to batch processing for detail (Option 2)
   - Use orchestrator for parallelization (Option 3)

---

## Documentation

- **CLI Reference**: `QUICK_REFERENCE.md`
- **Database Guide**: `ENHANCEMENTS.md` (section 1)
- **Orchestrator Guide**: `ORCHESTRATOR_GUIDE.md`
- **Full Skill Docs**: `SKILL.md`

---

**Version**: 1.1.0
**Last Updated**: 2025-11-14
