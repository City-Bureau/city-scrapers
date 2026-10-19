#!/usr/bin/env python3
"""
Command-line interface for City Scrapers Repository Analyzer.

Provides easy command-line access to all Skill functionality.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.analyzer import RepositoryAnalyzer
from src.database import AnalysisDatabase
from src.github_client import GitHubClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def cmd_analyze_repo(args):
    """Analyze a single repository."""
    analyzer = RepositoryAnalyzer(
        github_token=args.token,
        timeout_seconds=args.timeout,
        output_dir=args.output_dir,
    )

    print(f"\n🔍 Analyzing repository: {args.repo}")
    print(f"   Mode: {'Local execution' if args.execute else 'API-only'}")
    if args.max_scrapers:
        print(f"   Limit: First {args.max_scrapers} scrapers")

    report = analyzer.analyze_repository(
        repo_name=args.repo,
        clone_locally=args.execute,
        max_scrapers=args.max_scrapers,
    )

    # Print summary
    print(f"\n📊 Results:")
    print(f"   Total scrapers: {report['summary']['total_scrapers']}")
    print(f"   Functional: {report['summary']['functional']}")
    print(f"   Failed: {report['summary']['failed']}")
    print(f"   Success rate: {report['summary']['success_rate']:.1%}")
    print(f"   Repair hours: {report['effort_summary']['total_hours_estimated']:.1f}")

    # Save to database if requested
    if args.save_db:
        with AnalysisDatabase(args.db_path) as db:
            run_id = db.record_analysis_run(
                analysis_type="repository",
                total_repos=1,
                total_scrapers=report["summary"]["total_scrapers"],
                notes=args.notes,
            )
            db.save_repository_assessment(run_id, report)
            for scraper in report.get("scrapers", []):
                db.save_scraper_assessment(run_id, scraper)
            print(f"\n💾 Saved to database (run_id: {run_id})")

    print(f"\n📄 Full report: {args.output_dir}/{args.repo}_report_*.json")


def cmd_analyze_ecosystem(args):
    """Analyze entire ecosystem."""
    analyzer = RepositoryAnalyzer(
        github_token=args.token,
        timeout_seconds=args.timeout,
        output_dir=args.output_dir,
    )

    print(f"\n🌍 Analyzing ecosystem")
    print(f"   Mode: {'Local execution' if args.execute else 'API-only'}")
    if args.repos:
        print(f"   Repositories: {', '.join(args.repos)}")
    else:
        print(f"   Repositories: Auto-discover all")

    ecosystem = analyzer.analyze_ecosystem(
        repo_names=args.repos if args.repos else None,
        clone_locally=args.execute,
        max_scrapers_per_repo=args.max_scrapers,
    )

    # Print summary
    print(f"\n📊 Results:")
    print(f"   Total repositories: {ecosystem['repos_assessed']}")
    print(f"   Total scrapers: {ecosystem['total_scrapers']}")
    print(
        f"   Success rate: {ecosystem['ecosystem_health']['overall_success_rate']:.1%}"
    )
    print(f"   Repair hours: {ecosystem['total_repair_effort']['hours']:.1f}")

    # Save to database if requested
    if args.save_db:
        with AnalysisDatabase(args.db_path) as db:
            run_id = db.record_analysis_run(
                analysis_type="ecosystem",
                total_repos=ecosystem["repos_assessed"],
                total_scrapers=ecosystem["total_scrapers"],
                notes=args.notes,
            )
            for repo_report in ecosystem.get("repos", []):
                db.save_repository_assessment(run_id, repo_report)
                for scraper in repo_report.get("scrapers", []):
                    db.save_scraper_assessment(run_id, scraper)
            print(f"\n💾 Saved to database (run_id: {run_id})")

    print(f"\n📄 Full report: {args.output_dir}/ecosystem_analysis_*.json")
    print(f"📄 Summary: {args.output_dir}/analysis_summary_*.md")


def cmd_list_repos(args):
    """List all city-scrapers repositories."""
    github = GitHubClient(token=args.token)

    print("\n🔍 Discovering repositories...")
    repos = github.list_city_scrapers_repos()

    print(f"\nFound {len(repos)} city-scrapers repositories:\n")
    for repo in repos:
        print(f"  • {repo['name']}")
        if args.verbose:
            print(f"    Description: {repo.get('description', 'N/A')}")
            print(f"    Updated: {repo.get('updated_at', 'N/A')}")


def cmd_rate_limit(args):
    """Check GitHub API rate limit."""
    github = GitHubClient(token=args.token)
    rate_limit = github.check_rate_limit()

    print("\n⏱️  GitHub API Rate Limit:")
    print(f"   Remaining: {rate_limit['remaining']}/{rate_limit['limit']}")
    print(f"   Used: {rate_limit['used']}")
    print(f"   Reset at: {rate_limit['reset_at']}")

    if rate_limit["remaining"] < 100:
        print(f"\n⚠️  Warning: Low rate limit remaining!")


def cmd_history(args):
    """View scraper history from database."""
    with AnalysisDatabase(args.db_path) as db:
        history = db.get_scraper_history(args.repo, args.scraper, limit=args.limit)

        if not history:
            print(f"\n❌ No history found for {args.repo}/{args.scraper}")
            return

        print(f"\n📜 History for {args.repo}/{args.scraper}:")
        print(f"   (showing last {len(history)} assessments)\n")

        for record in history:
            print(f"   {record['run_date'][:10]}")
            print(f"      Status: {record['status']}")
            print(f"      Priority: {record['priority_tier']}")
            print(f"      Repair: {record['repair_hours']:.1f} hours ({record['effort_rating']})")
            print()


def cmd_compare(args):
    """Compare two analysis runs."""
    with AnalysisDatabase(args.db_path) as db:
        comparison = db.compare_runs(args.run1, args.run2)

        print(f"\n🔄 Comparing run {args.run1} vs run {args.run2}:")
        print(f"   Total compared: {comparison['total_compared']}")
        print(f"   Improved: {len(comparison['improved'])} scrapers")
        print(f"   Degraded: {len(comparison['degraded'])} scrapers")
        print(f"   Improvement rate: {comparison['improvement_rate']:.1%}")

        if comparison["improved"]:
            print(f"\n✅ Improved scrapers:")
            for s in comparison["improved"][:10]:
                print(
                    f"   • {s['repo_name']}/{s['scraper_name']}: {s['old_status']} → {s['new_status']}"
                )

        if comparison["degraded"]:
            print(f"\n❌ Degraded scrapers:")
            for s in comparison["degraded"][:10]:
                print(
                    f"   • {s['repo_name']}/{s['scraper_name']}: {s['old_status']} → {s['new_status']}"
                )


def cmd_export(args):
    """Export data to CSV."""
    with AnalysisDatabase(args.db_path) as db:
        output_path = db.export_to_csv(args.output, run_id=args.run_id)
        print(f"\n✅ Exported to: {output_path}")


def cmd_record_repair(args):
    """Record actual repair time for calibration."""
    with AnalysisDatabase(args.db_path) as db:
        repair_id = db.record_repair(
            args.repo, args.scraper, args.hours, repair_notes=args.notes
        )
        print(
            f"\n✅ Recorded repair: {args.repo}/{args.scraper} took {args.hours} hours (ID: {repair_id})"
        )

        # Show estimate accuracy
        accuracy = db.get_estimate_accuracy()
        if accuracy["total_repairs"] > 0:
            print(f"\n📊 Overall estimate accuracy:")
            print(f"   Average error: {accuracy['average_error_rate']:.1%}")
            print(
                f"   Over-estimated: {accuracy['over_estimated_count']} ({accuracy['over_estimated_count']/accuracy['total_repairs']:.1%})"
            )
            print(
                f"   Under-estimated: {accuracy['under_estimated_count']} ({accuracy['under_estimated_count']/accuracy['total_repairs']:.1%})"
            )


def cmd_stats(args):
    """Show database statistics."""
    with AnalysisDatabase(args.db_path) as db:
        stats = db.get_summary_stats(run_id=args.run_id)

        print(f"\n📊 Statistics{' for run ' + str(args.run_id) if args.run_id else ''}:")
        print(f"   Total repositories: {stats['total_repos']}")
        print(f"   Total scrapers: {stats['total_scrapers']}")
        print(f"   Functional: {stats['functional']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Success rate: {stats['success_rate']:.1%}")
        print(f"   Total repair hours: {stats['total_repair_hours']:.1f}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="City Scrapers Repository Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single repository (API-only, fast)
  %(prog)s analyze city-scrapers-atl

  # Analyze with execution (slow, more accurate)
  %(prog)s analyze city-scrapers-atl --execute

  # Analyze ecosystem
  %(prog)s ecosystem

  # List all repositories
  %(prog)s list

  # Check rate limit
  %(prog)s rate-limit

  # View scraper history
  %(prog)s history city-scrapers-atl atl_city_council

  # Compare two runs
  %(prog)s compare 1 2

  # Export to CSV
  %(prog)s export output.csv

  # Record repair time
  %(prog)s repair city-scrapers-atl atl_city_council 3.5 --notes "Updated selectors"
        """,
    )

    # Global arguments
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN"),
        help="GitHub API token (default: $GITHUB_TOKEN)",
    )
    parser.add_argument(
        "--output-dir", default="./reports", help="Output directory (default: ./reports)"
    )
    parser.add_argument(
        "--db-path",
        default="./analysis_history.db",
        help="Database path (default: ./analysis_history.db)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Analyze repository
    analyze_parser = subparsers.add_parser("analyze", help="Analyze single repository")
    analyze_parser.add_argument("repo", help="Repository name (e.g., city-scrapers-atl)")
    analyze_parser.add_argument(
        "--execute", action="store_true", help="Execute scrapers locally (slow)"
    )
    analyze_parser.add_argument(
        "--max-scrapers", type=int, help="Limit number of scrapers to analyze"
    )
    analyze_parser.add_argument(
        "--timeout", type=int, default=900, help="Scraper timeout in seconds (default: 900)"
    )
    analyze_parser.add_argument(
        "--save-db", action="store_true", help="Save results to database"
    )
    analyze_parser.add_argument("--notes", help="Notes about this analysis run")
    analyze_parser.set_defaults(func=cmd_analyze_repo)

    # Analyze ecosystem
    ecosystem_parser = subparsers.add_parser("ecosystem", help="Analyze entire ecosystem")
    ecosystem_parser.add_argument(
        "--repos", nargs="+", help="Specific repositories to analyze"
    )
    ecosystem_parser.add_argument(
        "--execute", action="store_true", help="Execute scrapers locally (slow)"
    )
    ecosystem_parser.add_argument(
        "--max-scrapers", type=int, help="Limit number of scrapers per repo"
    )
    ecosystem_parser.add_argument(
        "--timeout", type=int, default=900, help="Scraper timeout in seconds"
    )
    ecosystem_parser.add_argument(
        "--save-db", action="store_true", help="Save results to database"
    )
    ecosystem_parser.add_argument("--notes", help="Notes about this analysis run")
    ecosystem_parser.set_defaults(func=cmd_analyze_ecosystem)

    # List repositories
    list_parser = subparsers.add_parser("list", help="List all repositories")
    list_parser.set_defaults(func=cmd_list_repos)

    # Rate limit
    rate_parser = subparsers.add_parser("rate-limit", help="Check GitHub API rate limit")
    rate_parser.set_defaults(func=cmd_rate_limit)

    # History
    history_parser = subparsers.add_parser("history", help="View scraper history")
    history_parser.add_argument("repo", help="Repository name")
    history_parser.add_argument("scraper", help="Scraper name")
    history_parser.add_argument(
        "--limit", type=int, default=10, help="Number of records (default: 10)"
    )
    history_parser.set_defaults(func=cmd_history)

    # Compare
    compare_parser = subparsers.add_parser("compare", help="Compare two analysis runs")
    compare_parser.add_argument("run1", type=int, help="First run ID (older)")
    compare_parser.add_argument("run2", type=int, help="Second run ID (newer)")
    compare_parser.set_defaults(func=cmd_compare)

    # Export
    export_parser = subparsers.add_parser("export", help="Export to CSV")
    export_parser.add_argument("output", help="Output CSV file path")
    export_parser.add_argument("--run-id", type=int, help="Specific run ID (default: latest)")
    export_parser.set_defaults(func=cmd_export)

    # Record repair
    repair_parser = subparsers.add_parser("repair", help="Record repair time")
    repair_parser.add_argument("repo", help="Repository name")
    repair_parser.add_argument("scraper", help="Scraper name")
    repair_parser.add_argument("hours", type=float, help="Actual repair hours")
    repair_parser.add_argument("--notes", help="Repair notes")
    repair_parser.set_defaults(func=cmd_record_repair)

    # Stats
    stats_parser = subparsers.add_parser("stats", help="Show database statistics")
    stats_parser.add_argument("--run-id", type=int, help="Specific run ID")
    stats_parser.set_defaults(func=cmd_stats)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    try:
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        args.func(args)
        return 0

    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=args.verbose)
        return 1


if __name__ == "__main__":
    sys.exit(main())
