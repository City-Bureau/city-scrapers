# City Scrapers Repository Analysis Orchestrator Guide

## Overview

This guide provides comprehensive instructions for orchestrating large-scale analysis of all `city-scrapers-*` repositories in the City-Bureau organization.

**New in v1.1**: This orchestrator now integrates with the CLI and database features, offering flexible approaches from simple batch processing to full subagent orchestration.

## Three Orchestration Approaches

### Approach 1: CLI-Only Batch Processing ⭐⭐⭐ (Recommended for most users)

**Best for**: Teams who want systematic analysis without the complexity of subagent management

**Advantages**:
- Simpler setup (no subagent coordination)
- Built-in database tracking
- Easy to pause/resume
- Shell script friendly

**Disadvantages**:
- Sequential processing (not parallelized)
- Longer total time for large ecosystems

See `QUICK_START_ORCHESTRATOR.md` for detailed CLI batch processing instructions.

### Approach 2: Hybrid (CLI + Selective Subagents) ⭐⭐

**Best for**: Teams who want quick baseline + deep dives on specific repos

**Workflow**:
1. Use CLI for fast ecosystem baseline
2. Identify high-priority repos from baseline
3. Launch subagents for deep analysis on those repos
4. Use database to track both CLI and subagent results

**Advantages**:
- Best of both worlds
- Efficient use of time
- Targeted deep analysis

### Approach 3: Full Subagent Orchestration ⭐

**Best for**: Comprehensive parallelized analysis when time allows

**Advantages**:
- Maximum parallelization
- Deepest analysis per repo
- Independent subagent sessions

**Disadvantages**:
- Most complex setup
- Requires managing multiple Claude sessions
- Longest total elapsed time

This guide focuses on **Approach 3** (full orchestration). For Approaches 1-2, see `QUICK_START_ORCHESTRATOR.md`.

---

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Python 3.8+ available
- City Scrapers Repository Analyzer Skill installed (from this repo)
- Claude Code CLI installed
- Sufficient disk space for cloning repositories (~5-10 GB recommended)
- GitHub token with repo access: `export GITHUB_TOKEN=$(gh auth token)`

---

## Phase 1: Discovery & Setup

### Step 1.1: Create Working Directory

```bash
mkdir -p ~/city-scrapers-analysis
cd ~/city-scrapers-analysis

# Create directory structure
mkdir -p repos subagent-outputs logs tracking

# Copy the analyzer skill
cp -r /path/to/city-scrapers-analyzer-skill ./analyzer-skill
```

### Step 1.2: Discover Target Repositories

**New in v1.1**: Use the CLI to discover repositories and save to database

```bash
cd analyzer-skill
export GITHUB_TOKEN=$(gh auth token)

# List all repos and save to file
./cli.py list > ../tracking/all_repos.txt

# Save to database for tracking
./cli.py ecosystem --save-db --notes "Initial discovery"
```

Alternatively, use the Python API:

```python
import json
from src.github_client import GitHubClient

client = GitHubClient()
repos = client.list_city_scrapers_repos()

# Save for orchestration
with open('../tracking/target_repos.json', 'w') as f:
    json.dump([{
        'name': repo['name'],
        'url': repo['html_url'],
        'updated_at': repo.get('updated_at', '')
    } for repo in repos], f, indent=2)

print(f"Found {len(repos)} repositories to analyze")
```

### Step 1.3: Initialize Tracking System

**New in v1.1**: Enhanced tracking with database integration

```python
# File: setup_tracking.py
import json
from datetime import datetime
from pathlib import Path

def initialize_tracking():
    """Initialize orchestrator tracking system"""

    # Load discovered repos
    with open('tracking/target_repos.json', 'r') as f:
        target_repos = json.load(f)

    # Create tracking state
    tracking_data = {
        "analysis_started": datetime.now().isoformat(),
        "orchestrator_version": "1.1.0",
        "total_repos": len(target_repos),
        "completed": [],
        "in_progress": [],
        "failed": [],
        "pending": [repo['name'] for repo in target_repos],
        "database_run_id": None,  # Will be set when saving to database
        "batch_size": 3,
        "notes": "Full ecosystem orchestration with subagents"
    }

    with open('tracking/progress.json', 'w') as f:
        json.dump(tracking_data, f, indent=2)

    print(f"✅ Tracking initialized for {len(target_repos)} repositories")
    print(f"   Progress will be saved to: tracking/progress.json")

    # Also initialize database tracking
    import sys
    sys.path.insert(0, 'analyzer-skill')
    from src.database import AnalysisDatabase

    with AnalysisDatabase() as db:
        run_id = db.record_analysis_run(
            analysis_type="orchestrated_ecosystem",
            total_repos=len(target_repos),
            total_scrapers=0,  # Will be updated as we go
            notes="Orchestrator-coordinated analysis with subagents"
        )
        tracking_data['database_run_id'] = run_id

        with open('tracking/progress.json', 'w') as f:
            json.dump(tracking_data, f, indent=2)

        print(f"✅ Database tracking initialized (run_id: {run_id})")

if __name__ == "__main__":
    initialize_tracking()
```

Run it:
```bash
cd ~/city-scrapers-analysis
python setup_tracking.py
```

---

## Phase 2: Subagent Orchestration

### Step 2.1: Create Subagent Instructions Generator

**New in v1.1**: Subagent instructions now include CLI usage for efficiency

```python
# File: generate_subagent_instructions.py
import json
import sys
from pathlib import Path

def generate_subagent_instructions(repo_name: str, repo_url: str) -> str:
    """
    Generate instructions for a subagent to analyze a specific repository.

    New in v1.1: Subagents can use CLI for faster execution
    """

    instructions = f"""# Repository Analysis Task: {repo_name}

## Your Assignment

Analyze the repository **{repo_name}** using the City Scrapers Repository Analyzer Skill.

## Repository Details
- Name: {repo_name}
- URL: {repo_url}
- Organization: City-Bureau

---

## Instructions

### Step 1: Clone the Repository

```bash
cd ~/city-scrapers-analysis/repos
git clone {repo_url}
cd {repo_name}
```

### Step 2: Analyze Using the Skill

**Option A: Use the CLI (Recommended - Faster)**

```bash
cd ~/city-scrapers-analysis/analyzer-skill

# Set GitHub token
export GITHUB_TOKEN=$(gh auth token)

# Run analysis with execution
./cli.py analyze {repo_name} \\
    --execute \\
    --save-db \\
    --notes "Orchestrated subagent analysis"

# The results will be in:
# - reports/repository_analysis_{repo_name}_*.json
# - reports/repository_report_{repo_name}_*.md
```

**Option B: Use Python API (More control)**

```python
import sys
sys.path.insert(0, '~/city-scrapers-analysis/analyzer-skill')

from src.analyzer import RepositoryAnalyzer
from src.database import AnalysisDatabase

# Analyze repository
analyzer = RepositoryAnalyzer()
report = analyzer.analyze_repository(
    repo_name="{repo_name}",
    clone_locally=False,  # Already cloned
    execute_scrapers=True,  # Test scrapers
    max_scrapers=None  # Analyze all
)

# Save to database
with AnalysisDatabase() as db:
    run_id = db.record_analysis_run(
        analysis_type="subagent_repository",
        total_repos=1,
        total_scrapers=len(report['scrapers']),
        notes="Subagent analysis of {repo_name}"
    )
    db.save_repository_assessment(run_id, report)
    for scraper in report['scrapers']:
        db.save_scraper_assessment(run_id, scraper)

print(f"Analysis complete! Run ID: {{run_id}}")
```

### Step 3: Copy Results to Orchestrator Output Directory

```bash
cd ~/city-scrapers-analysis

# Copy from CLI reports directory
cp analyzer-skill/reports/repository_analysis_{repo_name}_*.json \\
   subagent-outputs/{repo_name}_analysis.json

cp analyzer-skill/reports/repository_report_{repo_name}_*.md \\
   subagent-outputs/{repo_name}_report.md

# Or if using Python API, save directly:
# (Your Python script should save to subagent-outputs/)
```

### Step 4: Generate Summary

Create a concise summary at `subagent-outputs/{repo_name}_summary.txt`:

```bash
cat > subagent-outputs/{repo_name}_summary.txt << EOF
Repository: {repo_name}
Analysis Date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Status: COMPLETE

Quick Stats:
- Total Scrapers: <count>
- Working: <count>
- Broken: <count>
- Top Failure Mode: <mode>
- Estimated Repair Hours: <hours>

Key Finding: <one-sentence summary>
EOF
```

### Step 5: Signal Completion

```bash
# Create completion marker
echo "Analysis completed at $(date)" > \\
    ~/city-scrapers-analysis/subagent-outputs/{repo_name}_COMPLETE

# Update tracking (orchestrator will handle this, but you can note it)
echo "✅ {repo_name} analysis complete"
```

---

## Expected Outputs

You should produce these files in `~/city-scrapers-analysis/subagent-outputs/`:

1. **{repo_name}_analysis.json** - Full structured analysis
2. **{repo_name}_report.md** - Human-readable report
3. **{repo_name}_summary.txt** - Quick stats
4. **{repo_name}_COMPLETE** - Completion marker

---

## Error Handling

If you encounter errors:

1. **Document them** in an error file:
   ```bash
   echo "Error details..." > subagent-outputs/{repo_name}_ERROR
   ```

2. **Save partial results** if any analysis was completed

3. **Note the issue** in the summary file

4. **Create the marker** so orchestrator knows you attempted it

---

## Tips for Efficiency

1. **Use CLI when possible** - It's faster and handles edge cases
2. **Execute scrapers selectively** - If repo has 50+ scrapers, consider sampling
3. **Monitor resource usage** - Large repos may need more time
4. **Check database** - Verify results saved: `./cli.py stats`

---

## Questions?

If you're unclear about classification or encounter edge cases:
- Refer to `SKILL.md` in the analyzer-skill directory
- Check failure mode definitions
- Document assumptions in your report

The orchestrator may follow up with additional questions if needed.

---

**Assignment**: Complete analysis of {repo_name}
**Priority**: Standard (unless otherwise specified)
**Deadline**: None (work at sustainable pace)
"""

    return instructions

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_subagent_instructions.py <repo_name> <repo_url>")
        sys.exit(1)

    repo_name = sys.argv[1]
    repo_url = sys.argv[2]

    instructions = generate_subagent_instructions(repo_name, repo_url)

    output_file = f"subagent-outputs/{repo_name}_instructions.md"
    with open(output_file, 'w') as f:
        f.write(instructions)

    print(f"✅ Instructions saved to: {output_file}")
    print(f"\nTo invoke subagent:")
    print(f"  claude-code -f {output_file}")

if __name__ == "__main__":
    main()
```

### Step 2.2: Create Orchestration Loop

**New in v1.1**: Database-aware orchestration with progress tracking

```python
# File: orchestrate.py
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
import sys

# Add analyzer skill to path
sys.path.insert(0, 'analyzer-skill')
from src.database import AnalysisDatabase

def load_tracking():
    """Load current tracking state"""
    with open('tracking/progress.json', 'r') as f:
        return json.load(f)

def save_tracking(tracking_data):
    """Save tracking state"""
    with open('tracking/progress.json', 'w') as f:
        json.dump(tracking_data, f, indent=2)

def check_completion(repo_name):
    """Check if subagent completed analysis"""
    base_path = Path('subagent-outputs')

    complete_marker = base_path / f'{repo_name}_COMPLETE'
    error_marker = base_path / f'{repo_name}_ERROR'
    json_output = base_path / f'{repo_name}_analysis.json'

    if error_marker.exists():
        return 'error'
    elif complete_marker.exists() and json_output.exists():
        return 'complete'
    else:
        return 'incomplete'

def update_database_from_subagent(repo_name, run_id):
    """
    Update orchestrator database with subagent results.

    New in v1.1: Sync subagent analysis into orchestrator's database run
    """
    json_file = Path(f'subagent-outputs/{repo_name}_analysis.json')

    if not json_file.exists():
        print(f"⚠️  No JSON output found for {repo_name}")
        return

    try:
        with open(json_file, 'r') as f:
            analysis = json.load(f)

        with AnalysisDatabase('analyzer-skill/analysis_history.db') as db:
            # Save repository assessment
            db.save_repository_assessment(run_id, analysis)

            # Save individual scraper assessments
            for scraper in analysis.get('scrapers', []):
                db.save_scraper_assessment(run_id, scraper)

        print(f"✅ Database updated with {repo_name} results")

    except Exception as e:
        print(f"❌ Error updating database for {repo_name}: {e}")

def process_batch(batch_size=3):
    """Process next batch of repositories"""
    tracking = load_tracking()

    if not tracking['pending']:
        print("\n🎉 All repositories processed!")
        return False

    # Load repository info
    with open('tracking/target_repos.json', 'r') as f:
        target_repos = json.load(f)

    repo_map = {r['name']: r for r in target_repos}

    # Take next batch
    batch = tracking['pending'][:batch_size]

    print(f"\n{'='*80}")
    print(f"📦 Processing Batch: {len(batch)} repositories")
    print(f"   Remaining after batch: {len(tracking['pending']) - len(batch)}")
    print(f"{'='*80}\n")

    for repo_name in batch:
        repo_info = repo_map[repo_name]

        # Update tracking: pending → in_progress
        tracking['pending'].remove(repo_name)
        tracking['in_progress'].append(repo_name)
        save_tracking(tracking)

        print(f"\n🔹 {repo_name}")
        print(f"   Generating subagent instructions...")

        # Generate instructions
        subprocess.run([
            'python', 'generate_subagent_instructions.py',
            repo_name, repo_info['url']
        ])

        print(f"\n   ⚠️  ACTION REQUIRED:")
        print(f"   Open a new terminal and run:")
        print(f"   ")
        print(f"     cd ~/city-scrapers-analysis")
        print(f"     claude-code -f subagent-outputs/{repo_name}_instructions.md")
        print(f"   ")
        print(f"   Press Enter when subagent completes...")

        input()

        # Check completion
        status = check_completion(repo_name)

        if status == 'complete':
            tracking['in_progress'].remove(repo_name)
            tracking['completed'].append(repo_name)

            # Update database with results
            run_id = tracking.get('database_run_id')
            if run_id:
                update_database_from_subagent(repo_name, run_id)

            print(f"   ✅ {repo_name} completed successfully")

        elif status == 'error':
            tracking['in_progress'].remove(repo_name)
            tracking['failed'].append(repo_name)
            print(f"   ❌ {repo_name} encountered errors")

        else:
            print(f"   ⚠️  {repo_name} status unclear")
            print(f"      Keeping in 'in_progress' state")

        save_tracking(tracking)
        time.sleep(1)

    return True

def show_status():
    """Display current orchestration status"""
    tracking = load_tracking()

    print(f"\n{'='*80}")
    print(f"📊 ORCHESTRATION STATUS")
    print(f"{'='*80}")
    print(f"Started: {tracking['analysis_started']}")
    print(f"Total Repositories: {tracking['total_repos']}")
    print(f"")
    print(f"  ✅ Completed:   {len(tracking['completed']):3d} ({len(tracking['completed'])/tracking['total_repos']*100:5.1f}%)")
    print(f"  ❌ Failed:      {len(tracking['failed']):3d} ({len(tracking['failed'])/tracking['total_repos']*100:5.1f}%)")
    print(f"  ⏳ In Progress: {len(tracking['in_progress']):3d}")
    print(f"  ⏸️  Pending:     {len(tracking['pending']):3d}")
    print(f"{'='*80}\n")

def main():
    """Main orchestration loop"""
    print("\n" + "="*80)
    print("🎯 CITY SCRAPERS ORCHESTRATOR v1.1")
    print("="*80)

    while True:
        show_status()
        tracking = load_tracking()

        if not tracking['pending'] and not tracking['in_progress']:
            print("✅ All repositories processed!\n")
            break

        print("Commands:")
        print("  [n] Process next batch")
        print("  [s] Show detailed status")
        print("  [d] Database stats")
        print("  [q] Quit (save & resume later)")
        print("")

        choice = input("➤ ").strip().lower()

        if choice == 'n':
            if not process_batch(batch_size=tracking.get('batch_size', 3)):
                break

        elif choice == 's':
            tracking = load_tracking()
            if tracking['completed']:
                print("\n✅ Completed:")
                for repo in tracking['completed']:
                    print(f"   - {repo}")
            if tracking['failed']:
                print("\n❌ Failed:")
                for repo in tracking['failed']:
                    print(f"   - {repo}")
            if tracking['in_progress']:
                print("\n⏳ In Progress:")
                for repo in tracking['in_progress']:
                    print(f"   - {repo}")

        elif choice == 'd':
            # Show database statistics
            run_id = tracking.get('database_run_id')
            if run_id:
                print(f"\n📊 Database Stats (Run ID: {run_id})")
                subprocess.run(['./analyzer-skill/cli.py', 'stats'])
            else:
                print("\n⚠️  No database run_id found")

        elif choice == 'q':
            print("\n💾 Saving progress...")
            print("   You can resume by running this script again.")
            break

        else:
            print("❓ Unknown command")

if __name__ == "__main__":
    main()
```

### Step 2.3: Monitor Progress

```python
# File: monitor.py
import json
from pathlib import Path
from datetime import datetime

def monitor():
    """Display orchestration progress dashboard"""

    with open('tracking/progress.json', 'r') as f:
        tracking = json.load(f)

    total = tracking['total_repos']
    completed = len(tracking['completed'])
    failed = len(tracking['failed'])
    in_progress = len(tracking['in_progress'])
    pending = len(tracking['pending'])

    print("\n" + "="*80)
    print("📊 CITY SCRAPERS ORCHESTRATOR - PROGRESS DASHBOARD")
    print("="*80)
    print(f"Started: {tracking['analysis_started']}")
    print(f"Version: {tracking.get('orchestrator_version', 'unknown')}")

    if tracking.get('database_run_id'):
        print(f"Database Run ID: {tracking['database_run_id']}")

    print(f"\n🎯 Overall Progress")
    print(f"   Total: {total}")

    # Progress bar
    progress = (completed + failed) / total if total > 0 else 0
    bar_length = 50
    filled = int(bar_length * progress)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"   [{bar}] {progress*100:.1f}%")

    print(f"\n📈 Status Breakdown")
    print(f"   ✅ Completed:   {completed:3d} ({completed/total*100:5.1f}%)")
    print(f"   ❌ Failed:      {failed:3d} ({failed/total*100:5.1f}%)")
    print(f"   ⏳ In Progress: {in_progress:3d}")
    print(f"   ⏸️  Pending:     {pending:3d} ({pending/total*100:5.1f}%)")

    # Output files created
    output_dir = Path('subagent-outputs')
    if output_dir.exists():
        json_files = list(output_dir.glob('*_analysis.json'))
        report_files = list(output_dir.glob('*_report.md'))

        print(f"\n📁 Output Files")
        print(f"   JSON analyses:  {len(json_files)}")
        print(f"   Markdown reports: {len(report_files)}")

    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    monitor()
```

---

## Phase 3: Aggregation & Analysis

### Step 3.1: Aggregate Subagent Results

**New in v1.1**: Use database for aggregation, fallback to JSON parsing

```python
# File: aggregate.py
import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

sys.path.insert(0, 'analyzer-skill')
from src.database import AnalysisDatabase

def aggregate_from_database(run_id):
    """
    Aggregate results from database (preferred method).

    New in v1.1: Use database for cleaner aggregation
    """
    with AnalysisDatabase('analyzer-skill/analysis_history.db') as db:
        # Get all repository assessments for this run
        repos = db.conn.execute("""
            SELECT repo_name, total_scrapers, working_scrapers, broken_scrapers,
                   health_score, priority_score
            FROM repository_assessments
            WHERE run_id = ?
        """, (run_id,)).fetchall()

        # Get all scraper assessments
        scrapers = db.conn.execute("""
            SELECT repo_name, scraper_name, status, failure_mode,
                   estimated_hours, priority_score, harambe_score
            FROM scraper_assessments
            WHERE run_id = ?
        """, (run_id,)).fetchall()

        # Aggregate by failure mode
        failure_modes = defaultdict(lambda: {
            'count': 0,
            'total_hours': 0,
            'repos': set()
        })

        for scraper in scrapers:
            if scraper[3]:  # failure_mode
                mode = scraper[3]
                failure_modes[mode]['count'] += 1
                failure_modes[mode]['total_hours'] += scraper[4] or 0
                failure_modes[mode]['repos'].add(scraper[0])

        # Convert sets to lists for JSON serialization
        for mode in failure_modes:
            failure_modes[mode]['repos'] = list(failure_modes[mode]['repos'])

        return {
            'source': 'database',
            'run_id': run_id,
            'total_repos': len(repos),
            'total_scrapers': sum(r[1] for r in repos),
            'total_working': sum(r[2] for r in repos),
            'total_broken': sum(r[3] for r in repos),
            'repositories': [
                {
                    'name': r[0],
                    'total_scrapers': r[1],
                    'working': r[2],
                    'broken': r[3],
                    'health_score': r[4],
                    'priority_score': r[5]
                }
                for r in repos
            ],
            'failure_modes': dict(failure_modes),
            'scrapers': [
                {
                    'repo': s[0],
                    'name': s[1],
                    'status': s[2],
                    'failure_mode': s[3],
                    'estimated_hours': s[4],
                    'priority_score': s[5],
                    'harambe_score': s[6]
                }
                for s in scrapers
            ]
        }

def aggregate_from_json_files():
    """
    Aggregate from JSON files (fallback method).

    Used when database aggregation not available
    """
    output_dir = Path('subagent-outputs')
    analyses = []

    for json_file in output_dir.glob('*_analysis.json'):
        try:
            with open(json_file, 'r') as f:
                analyses.append(json.load(f))
        except Exception as e:
            print(f"⚠️  Error loading {json_file}: {e}")

    # Build aggregated structure
    aggregated = {
        'source': 'json_files',
        'total_repos': len(analyses),
        'total_scrapers': 0,
        'total_working': 0,
        'total_broken': 0,
        'repositories': [],
        'failure_modes': defaultdict(lambda: {
            'count': 0,
            'total_hours': 0,
            'repos': []
        })
    }

    for analysis in analyses:
        repo_name = analysis['repository']

        aggregated['total_scrapers'] += analysis.get('total_scrapers', 0)
        aggregated['total_working'] += analysis.get('working_scrapers', 0)
        aggregated['total_broken'] += analysis.get('broken_scrapers', 0)

        aggregated['repositories'].append({
            'name': repo_name,
            'total_scrapers': analysis.get('total_scrapers', 0),
            'working': analysis.get('working_scrapers', 0),
            'broken': analysis.get('broken_scrapers', 0)
        })

        # Aggregate failure modes
        for mode, details in analysis.get('failure_modes', {}).items():
            aggregated['failure_modes'][mode]['count'] += 1
            aggregated['failure_modes'][mode]['total_hours'] += details.get('repair_estimate_hours', 0)
            aggregated['failure_modes'][mode]['repos'].append(repo_name)

    # Convert defaultdict to dict
    aggregated['failure_modes'] = dict(aggregated['failure_modes'])

    return aggregated

def generate_markdown_report(aggregated):
    """Generate comprehensive markdown report"""

    lines = []
    lines.append("# City Scrapers Ecosystem - Aggregated Analysis")
    lines.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Source**: {aggregated['source']}")

    if aggregated['source'] == 'database':
        lines.append(f"**Run ID**: {aggregated['run_id']}")

    lines.append("\n---\n")

    # Executive Summary
    lines.append("## Executive Summary\n")
    lines.append(f"- **Repositories Analyzed**: {aggregated['total_repos']}")
    lines.append(f"- **Total Scrapers**: {aggregated['total_scrapers']}")

    total = aggregated['total_scrapers']
    working = aggregated['total_working']
    broken = aggregated['total_broken']

    if total > 0:
        lines.append(f"- **Working**: {working} ({working/total*100:.1f}%)")
        lines.append(f"- **Broken**: {broken} ({broken/total*100:.1f}%)")

    lines.append("\n---\n")

    # Failure Modes
    lines.append("## Failure Modes\n")

    sorted_modes = sorted(
        aggregated['failure_modes'].items(),
        key=lambda x: x[1]['total_hours'],
        reverse=True
    )

    for mode, details in sorted_modes:
        lines.append(f"### {mode}\n")
        lines.append(f"- Scrapers affected: {details['count']}")
        lines.append(f"- Estimated repair hours: {details['total_hours']:.1f}")
        lines.append(f"- Repositories: {', '.join(details['repos'][:5])}")
        if len(details['repos']) > 5:
            lines.append(f"  (+ {len(details['repos']) - 5} more)")
        lines.append("")

    lines.append("\n---\n")

    # Repository Breakdown
    lines.append("## Repository Breakdown\n")
    lines.append("| Repository | Total | Working | Broken | % Working |")
    lines.append("|------------|-------|---------|--------|-----------|")

    sorted_repos = sorted(
        aggregated['repositories'],
        key=lambda x: x.get('broken', 0),
        reverse=True
    )

    for repo in sorted_repos:
        total_s = repo['total_scrapers']
        working_s = repo['working']
        broken_s = repo['broken']
        pct = (working_s / total_s * 100) if total_s > 0 else 0

        lines.append(f"| {repo['name']} | {total_s} | {working_s} | {broken_s} | {pct:.1f}% |")

    lines.append("\n---\n")

    return "\n".join(lines)

def main():
    """Main aggregation logic"""

    print("\n🔄 Aggregating subagent results...\n")

    # Try database method first
    tracking_file = Path('tracking/progress.json')
    run_id = None

    if tracking_file.exists():
        with open(tracking_file, 'r') as f:
            tracking = json.load(f)
            run_id = tracking.get('database_run_id')

    if run_id:
        print(f"📊 Using database aggregation (Run ID: {run_id})")
        aggregated = aggregate_from_database(run_id)
    else:
        print("📄 Using JSON file aggregation (fallback)")
        aggregated = aggregate_from_json_files()

    # Save aggregated JSON
    with open('aggregated_analysis.json', 'w') as f:
        json.dump(aggregated, f, indent=2)
    print("✅ Saved: aggregated_analysis.json")

    # Generate markdown report
    report = generate_markdown_report(aggregated)
    with open('AGGREGATED_REPORT.md', 'w') as f:
        f.write(report)
    print("✅ Saved: AGGREGATED_REPORT.md")

    print("\n✨ Aggregation complete!\n")

if __name__ == "__main__":
    main()
```

### Step 3.2: Generate Final Report

```python
# File: final_report.py
import json
from datetime import datetime
from pathlib import Path

def generate_final_report():
    """Generate ultimate comprehensive report"""

    # Load aggregated data
    with open('aggregated_analysis.json', 'r') as f:
        agg = json.load(f)

    # Load tracking
    with open('tracking/progress.json', 'r') as f:
        tracking = json.load(f)

    lines = []

    lines.append("# City Scrapers Ecosystem: Final Comprehensive Report")
    lines.append(f"\n**Analysis Period**: {tracking['analysis_started']} to {datetime.now().isoformat()}")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Orchestrator Version**: {tracking.get('orchestrator_version', 'unknown')}\n")

    lines.append("---\n")

    lines.append("## 🎯 Mission Accomplished\n")
    lines.append(f"This orchestrated analysis processed **{agg['total_repos']} repositories** ")
    lines.append(f"containing **{agg['total_scrapers']} scrapers** across the City Bureau ")
    lines.append("Documenters Network.\n")

    lines.append("### Analysis Completion")
    total = tracking['total_repos']
    completed = len(tracking['completed'])
    failed = len(tracking['failed'])

    lines.append(f"- Successfully analyzed: {completed}/{total} ({completed/total*100:.1f}%)")
    lines.append(f"- Failed/skipped: {failed}\n")

    lines.append("---\n")

    lines.append("## 📊 Key Findings\n")

    working_pct = (agg['total_working'] / agg['total_scrapers'] * 100) if agg['total_scrapers'] > 0 else 0

    lines.append(f"### Health Status")
    lines.append(f"- **{working_pct:.1f}%** of scrapers are functional")
    lines.append(f"- **{100-working_pct:.1f}%** require attention ({agg['total_broken']} scrapers)\n")

    # Calculate total repair effort
    total_hours = sum(
        details['total_hours']
        for details in agg['failure_modes'].values()
    )

    lines.append(f"### Repair Effort")
    lines.append(f"- Total estimated hours: **{total_hours:.0f}**")
    lines.append(f"- Person-days (8hr): **{total_hours/8:.1f}**")
    lines.append(f"- Person-weeks (40hr): **{total_hours/40:.1f}**\n")

    lines.append("---\n")

    # Include aggregated report content
    with open('AGGREGATED_REPORT.md', 'r') as f:
        lines.append(f.read())

    lines.append("\n---\n")

    lines.append("## 📁 Appendices\n")
    lines.append("### A. Detailed Repository Reports")
    lines.append("Individual analyses available in `subagent-outputs/`:\n")

    for repo in sorted(tracking['completed']):
        lines.append(f"- `{repo}_analysis.json`")
        lines.append(f"- `{repo}_report.md`")

    lines.append("\n### B. Database")
    if tracking.get('database_run_id'):
        lines.append(f"Analysis stored in database (Run ID: {tracking['database_run_id']})\n")
        lines.append("Query using:")
        lines.append("```bash")
        lines.append("cd analyzer-skill")
        lines.append(f"./cli.py stats")
        lines.append(f"./cli.py export ../ecosystem_results.csv")
        lines.append("```\n")

    lines.append("### C. Data Files")
    lines.append("- `aggregated_analysis.json` - Combined results")
    lines.append("- `tracking/progress.json` - Orchestration state")
    lines.append("- `tracking/target_repos.json` - Repository list\n")

    lines.append("---\n")
    lines.append("*Generated by City Scrapers Orchestrator v1.1*")

    return "\n".join(lines)

def main():
    print("\n📝 Generating final comprehensive report...\n")

    report = generate_final_report()

    with open('FINAL_REPORT.md', 'w') as f:
        f.write(report)

    print("✅ Saved: FINAL_REPORT.md")
    print("\n🎉 All done! Review FINAL_REPORT.md for complete findings.\n")

if __name__ == "__main__":
    main()
```

---

## Complete Workflow

### Initial Setup

```bash
cd ~/city-scrapers-analysis

# Install dependencies
cd analyzer-skill
pip install -r requirements.txt
cd ..

# Set GitHub token
export GITHUB_TOKEN=$(gh auth token)
```

### Phase 1: Discovery

```bash
python setup_tracking.py
```

### Phase 2: Orchestration

```bash
# Start orchestrator
python orchestrate.py

# In another terminal, monitor progress
python monitor.py
```

### Phase 3: Aggregation

```bash
# Once all subagents complete
python aggregate.py
python final_report.py
```

### Export Results

```bash
# Export from database
cd analyzer-skill
./cli.py export ../ecosystem_analysis.csv
./cli.py stats

# Compare to earlier runs if available
./cli.py compare <run_id_1> <run_id_2>
```

---

## Tips for Success

### 1. Batch Size

Adjust in `tracking/progress.json`:
```json
{
  "batch_size": 3  // Start with 2-3, increase if comfortable
}
```

### 2. Pause & Resume

The orchestrator saves state continuously. You can quit anytime:
- Run `orchestrate.py` again to resume
- All progress is preserved in `tracking/progress.json`

### 3. Parallel Processing (Advanced)

For faster processing, run multiple orchestrators in parallel with different repo subsets:

```bash
# Terminal 1
python orchestrate.py --repos "city-scrapers-a* city-scrapers-b*"

# Terminal 2
python orchestrate.py --repos "city-scrapers-c* city-scrapers-d*"
```

### 4. Database Integration

All subagent results are synced to the database:
- Query across runs
- Track trends over time
- Export for stakeholders

---

## Troubleshooting

### Subagent Hangs

1. Check the terminal running the subagent
2. Look for errors in `subagent-outputs/*_ERROR`
3. If needed, mark as failed in `tracking/progress.json`
4. Continue with other repos

### Database Issues

```bash
# Check database integrity
cd analyzer-skill
./cli.py stats

# If corrupted, the JSON files are the source of truth
# Re-aggregate from JSON: python aggregate.py
```

### Missing Outputs

If a subagent completes but files are missing:
1. Check `reports/` directory in analyzer-skill
2. Copy manually to `subagent-outputs/`
3. Ensure proper naming: `{repo_name}_analysis.json`

---

## Success Criteria

✅ All repositories discovered
✅ Tracking system initialized
✅ Subagents invoked for all repos
✅ Results collected in `subagent-outputs/`
✅ Database updated with all results
✅ Aggregated analysis generated
✅ Final comprehensive report created

---

## Next Steps After Orchestration

1. **Review FINAL_REPORT.md** - Strategic insights
2. **Export database** - Share with stakeholders
3. **Prioritize repairs** - Use priority scores
4. **Track progress** - Run follow-up analyses
5. **Automate** - Set up recurring orchestration

---

**Version**: 1.1.0
**Last Updated**: 2025-11-14
**Integration**: CLI + Database + Orchestrator
