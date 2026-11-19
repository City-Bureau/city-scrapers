#!/usr/bin/env python3
"""
Example usage of City Scrapers Repository Analyzer Skill.

This script demonstrates various ways to use the Skill for analyzing
city-scrapers repositories.
"""

import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.analyzer import RepositoryAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def example_1_single_repository():
    """Example 1: Analyze a single repository."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Analyze Single Repository")
    print("=" * 60)

    # Initialize analyzer
    analyzer = RepositoryAnalyzer(
        github_token=os.environ.get("GITHUB_TOKEN"),
        timeout_seconds=900,
        output_dir="./reports",
    )

    # Check rate limit before starting
    rate_limit = analyzer.check_rate_limit()
    print(f"\nGitHub API Rate Limit: {rate_limit['remaining']}/{rate_limit['limit']}")

    # Analyze city-scrapers-atl
    print("\nAnalyzing city-scrapers-atl...")
    report = analyzer.analyze_repository(
        repo_name="city-scrapers-atl",
        clone_locally=False,  # API-only for speed
        max_scrapers=5,  # Limit to first 5 for demo
    )

    # Print summary
    print("\n--- Repository Summary ---")
    print(f"Total scrapers: {report['summary']['total_scrapers']}")
    print(f"Functional: {report['summary']['functional']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Success rate: {report['summary']['success_rate']:.1%}")

    print("\n--- Failure Breakdown ---")
    for failure, count in report.get("failure_breakdown", {}).items():
        print(f"  {failure}: {count}")

    print("\n--- Effort Summary ---")
    print(f"Total hours: {report['effort_summary']['total_hours_estimated']:.1f}")

    print("\n--- Priority Distribution ---")
    for tier, count in report.get("priority_distribution", {}).items():
        print(f"  {tier}: {count}")

    print(f"\nHarambe candidates: {report.get('harambe_candidates', 0)}")

    return report


def example_2_api_only_quick_scan():
    """Example 2: Quick scan of multiple repos using API only."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Quick Scan (API Only)")
    print("=" * 60)

    analyzer = RepositoryAnalyzer(github_token=os.environ.get("GITHUB_TOKEN"))

    # List of repos to scan
    repos_to_scan = [
        "city-scrapers-atl",
        "city-scrapers-cle",
        "city-scrapers-det",
    ]

    print(f"\nScanning {len(repos_to_scan)} repositories (API only, no execution)...")

    results = []
    for repo_name in repos_to_scan:
        print(f"\n  Scanning {repo_name}...")
        report = analyzer.analyze_repository(
            repo_name=repo_name,
            clone_locally=False,  # API only
            max_scrapers=None,
        )
        results.append(report)

        print(
            f"    {repo_name}: {report['summary']['total_scrapers']} scrapers found"
        )

    # Generate ecosystem report
    print("\nGenerating ecosystem report...")
    ecosystem_report = analyzer.reporter.generate_ecosystem_report(results)

    print("\n--- Ecosystem Summary ---")
    print(f"Total repositories: {ecosystem_report['repos_assessed']}")
    print(f"Total scrapers: {ecosystem_report['total_scrapers']}")
    print(
        f"Overall success rate: {ecosystem_report['ecosystem_health']['overall_success_rate']:.1%}"
    )

    return ecosystem_report


def example_3_detailed_local_execution():
    """Example 3: Detailed analysis with local execution (slow)."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Detailed Analysis with Local Execution")
    print("=" * 60)
    print("\nWARNING: This will clone the repository and execute scrapers.")
    print("This can take several minutes.")

    response = input("\nContinue? (y/N): ")
    if response.lower() != "y":
        print("Skipped.")
        return None

    analyzer = RepositoryAnalyzer(
        github_token=os.environ.get("GITHUB_TOKEN"),
        timeout_seconds=300,  # 5 minute timeout for demo
    )

    print("\nAnalyzing city-scrapers-atl with local execution...")
    report = analyzer.analyze_repository(
        repo_name="city-scrapers-atl",
        clone_locally=True,  # Clone and execute
        max_scrapers=3,  # Limit to 3 for demo
    )

    print("\n--- Detailed Results ---")
    for scraper in report.get("scrapers", []):
        print(f"\nScraper: {scraper['scraper_name']}")
        print(f"  Status: {scraper['execution_results']['status']}")
        print(f"  Items: {scraper['execution_results']['item_count']}")
        print(f"  Time: {scraper['execution_results']['execution_time_seconds']}s")
        print(f"  Effort: {scraper['repair_estimate']['effort_rating']}")
        print(f"  Priority: {scraper['priority_assessment']['priority_tier']}")

    return report


def example_4_discover_and_prioritize():
    """Example 4: Discover all repos and identify high-priority failures."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Discover Repos and Prioritize")
    print("=" * 60)

    analyzer = RepositoryAnalyzer(github_token=os.environ.get("GITHUB_TOKEN"))

    # Discover all city-scrapers repos
    print("\nDiscovering all city-scrapers repositories...")
    repos = analyzer.github.list_city_scrapers_repos()

    print(f"\nFound {len(repos)} city-scrapers repositories:")
    for repo in repos[:10]:  # Show first 10
        print(f"  - {repo['name']}")
    if len(repos) > 10:
        print(f"  ... and {len(repos) - 10} more")

    # Analyze a subset (for demo)
    print("\nAnalyzing subset for prioritization...")
    subset = [repos[0]["name"], repos[1]["name"]] if len(repos) >= 2 else [repos[0]["name"]]

    ecosystem_report = analyzer.analyze_ecosystem(
        repo_names=subset,
        clone_locally=False,  # API only for speed
        max_scrapers_per_repo=10,
    )

    # Find critical failures
    print("\n--- Critical Priority Scrapers ---")
    critical_count = 0
    for repo_report in ecosystem_report.get("repos", []):
        for scraper in repo_report.get("scrapers", []):
            if (
                scraper.get("priority_assessment", {}).get("priority_tier")
                == "CRITICAL"
            ):
                critical_count += 1
                print(f"\n{scraper['repo_name']}/{scraper['scraper_name']}")
                print(f"  Agency: {scraper['agency_name']}")
                print(f"  Status: {scraper['execution_results']['status']}")
                print(
                    f"  Repair: {scraper['repair_estimate']['total_estimated_hours']:.1f} hours"
                )

    if critical_count == 0:
        print("No critical priority scrapers found in subset.")

    return ecosystem_report


def example_5_harambe_candidates():
    """Example 5: Identify Harambe conversion candidates."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Identify Harambe Candidates")
    print("=" * 60)

    analyzer = RepositoryAnalyzer(github_token=os.environ.get("GITHUB_TOKEN"))

    # Analyze a few repos
    print("\nAnalyzing repositories for Harambe candidates...")
    repos_to_check = ["city-scrapers-atl", "city-scrapers-cle"]

    all_scrapers = []
    for repo_name in repos_to_check:
        report = analyzer.analyze_repository(
            repo_name=repo_name, clone_locally=False, max_scrapers=None
        )
        all_scrapers.extend(report.get("scrapers", []))

    # Find Harambe candidates
    harambe_candidates = [
        s
        for s in all_scrapers
        if s.get("harambe_candidacy", {}).get("recommendation") == "HARAMBE_CONVERSION"
    ]

    print(f"\nFound {len(harambe_candidates)} Harambe conversion candidates:")
    for scraper in harambe_candidates:
        print(f"\n{scraper['repo_name']}/{scraper['scraper_name']}")
        print(f"  Agency: {scraper['agency_name']}")
        print(f"  Score: {scraper['harambe_candidacy']['score']}")
        print(f"  Reason: {scraper['harambe_candidacy']['reasoning']}")

    # Also check for "consider" candidates
    consider_candidates = [
        s
        for s in all_scrapers
        if s.get("harambe_candidacy", {}).get("recommendation") == "CONSIDER_HARAMBE"
    ]

    print(f"\n{len(consider_candidates)} additional 'consider' candidates")

    return {"strong": harambe_candidates, "consider": consider_candidates}


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("City Scrapers Repository Analyzer - Usage Examples")
    print("=" * 60)

    # Check for GitHub token
    if not os.environ.get("GITHUB_TOKEN"):
        print("\nWARNING: GITHUB_TOKEN environment variable not set.")
        print("API rate limits will be very restrictive (60 requests/hour).")
        print("Set token with: export GITHUB_TOKEN='your_token'")
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != "y":
            print("Exiting.")
            return

    # Run examples
    examples = [
        ("Single Repository Analysis", example_1_single_repository),
        ("Quick API Scan", example_2_api_only_quick_scan),
        ("Detailed Local Execution", example_3_detailed_local_execution),
        ("Discover and Prioritize", example_4_discover_and_prioritize),
        ("Harambe Candidates", example_5_harambe_candidates),
    ]

    for i, (name, func) in enumerate(examples, 1):
        print(f"\n\nExample {i}/{len(examples)}: {name}")
        try:
            func()
        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            break
        except Exception as e:
            logger.error(f"Error in {name}: {e}", exc_info=True)
            response = input("\nContinue to next example? (Y/n): ")
            if response.lower() == "n":
                break

    print("\n" + "=" * 60)
    print("Examples completed. Check ./reports/ for generated files.")
    print("=" * 60)


if __name__ == "__main__":
    main()
