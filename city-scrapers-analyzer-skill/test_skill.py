#!/usr/bin/env python3
"""
Quick test of the City Scrapers Analyzer Skill.

Tests GitHub API integration and basic analysis without full execution.
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
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def test_github_connection():
    """Test 1: GitHub API connection."""
    print("\n" + "=" * 60)
    print("TEST 1: GitHub API Connection")
    print("=" * 60)

    try:
        from src.github_client import GitHubClient

        github = GitHubClient(token=os.environ.get("GITHUB_TOKEN"))

        # Check rate limit
        rate_limit = github.check_rate_limit()
        print(f"\n✓ GitHub API connected")
        print(f"  Rate limit: {rate_limit['remaining']}/{rate_limit['limit']}")
        print(f"  Reset at: {rate_limit['reset_at']}")

        if rate_limit["remaining"] < 10:
            print("\n⚠ WARNING: Low rate limit remaining")
            return False

        return True

    except Exception as e:
        print(f"\n✗ GitHub API connection failed: {e}")
        return False


def test_discover_repos():
    """Test 2: Discover city-scrapers repositories."""
    print("\n" + "=" * 60)
    print("TEST 2: Discover Repositories")
    print("=" * 60)

    try:
        from src.github_client import GitHubClient

        github = GitHubClient(token=os.environ.get("GITHUB_TOKEN"))

        repos = github.list_city_scrapers_repos()
        print(f"\n✓ Found {len(repos)} city-scrapers repositories")

        # Show first 5
        print("\nFirst 5 repositories:")
        for repo in repos[:5]:
            print(f"  - {repo['name']}")

        return len(repos) > 0

    except Exception as e:
        print(f"\n✗ Repository discovery failed: {e}")
        return False


def test_get_spider_files():
    """Test 3: List spider files in a repository."""
    print("\n" + "=" * 60)
    print("TEST 3: List Spider Files")
    print("=" * 60)

    try:
        from src.github_client import GitHubClient

        github = GitHubClient(token=os.environ.get("GITHUB_TOKEN"))

        repo_name = "city-scrapers-atl"
        spider_files = github.list_spider_files(repo_name)

        print(f"\n✓ Found {len(spider_files)} spider files in {repo_name}")

        # Show first 3
        print("\nFirst 3 spiders:")
        for spider in spider_files[:3]:
            print(f"  - {spider['name']} ({spider['size']} bytes)")

        return len(spider_files) > 0

    except Exception as e:
        print(f"\n✗ Failed to list spider files: {e}")
        return False


def test_get_spider_metadata():
    """Test 4: Extract metadata from a spider file."""
    print("\n" + "=" * 60)
    print("TEST 4: Extract Spider Metadata")
    print("=" * 60)

    try:
        from src.github_client import GitHubClient

        github = GitHubClient(token=os.environ.get("GITHUB_TOKEN"))

        repo_name = "city-scrapers-atl"
        spider_files = github.list_spider_files(repo_name)

        if not spider_files:
            print("No spider files found")
            return False

        # Get metadata for first spider
        spider_file = spider_files[0]
        metadata = github.get_spider_metadata(repo_name, spider_file)

        print(f"\n✓ Extracted metadata for {spider_file['name']}")
        print(f"\nMetadata:")
        print(f"  Spider name: {metadata.get('spider_name', 'N/A')}")
        print(f"  Agency: {metadata.get('agency', 'N/A')}")
        print(f"  Lines of code: {metadata.get('lines_of_code', 'N/A')}")
        print(f"  Mixins: {', '.join(metadata.get('uses_mixins', [])) or 'None'}")
        print(f"  Start URLs: {len(metadata.get('start_urls', []))}")

        return metadata.get("spider_name") is not None

    except Exception as e:
        print(f"\n✗ Failed to extract metadata: {e}")
        return False


def test_status_classifier():
    """Test 5: Status classification logic."""
    print("\n" + "=" * 60)
    print("TEST 5: Status Classifier")
    print("=" * 60)

    try:
        from src.classifier import StatusClassifier

        classifier = StatusClassifier()

        # Test successful execution
        result = classifier.classify(
            exit_code=0, item_count=10, log_content="INFO: Scraped 10 items", execution_time=15.5
        )
        print(f"\n✓ Classify success: {result['status']} (expected SUCCESS)")

        # Test selector failure
        result = classifier.classify(
            exit_code=0,
            item_count=0,
            log_content="ERROR: selector returned no results",
            execution_time=5.0,
        )
        print(f"✓ Classify selector failure: {result['status']} (expected SELECTOR_FAILURE)")

        # Test HTTP error
        result = classifier.classify(
            exit_code=1, item_count=0, log_content="ERROR: 404 Not Found", execution_time=2.0
        )
        print(f"✓ Classify HTTP error: {result['status']} (expected HTTP_ERROR)")

        return True

    except Exception as e:
        print(f"\n✗ Classifier test failed: {e}")
        return False


def test_priority_scorer():
    """Test 6: Priority scoring."""
    print("\n" + "=" * 60)
    print("TEST 6: Priority Scorer")
    print("=" * 60)

    try:
        from src.scorer import PriorityScorer

        scorer = PriorityScorer()

        # Test high priority (contractual risk + high usage)
        priority = scorer.calculate_priority(
            agency_name="San Diego City Council",
            assignment_count=10,
            days_since_last_data=90,
            repair_hours=2.0,
        )
        print(f"\n✓ High priority score: {priority['priority_score']} (tier: {priority['priority_tier']})")

        # Test low priority
        priority = scorer.calculate_priority(
            agency_name="Small Agency",
            assignment_count=0,
            days_since_last_data=5,
            repair_hours=20.0,
        )
        print(f"✓ Low priority score: {priority['priority_score']} (tier: {priority['priority_tier']})")

        return True

    except Exception as e:
        print(f"\n✗ Priority scorer test failed: {e}")
        return False


def test_api_only_analysis():
    """Test 7: Run API-only analysis on a repository."""
    print("\n" + "=" * 60)
    print("TEST 7: API-Only Repository Analysis")
    print("=" * 60)
    print("\nThis test performs analysis using GitHub API only (no execution)")

    try:
        analyzer = RepositoryAnalyzer(
            github_token=os.environ.get("GITHUB_TOKEN"), output_dir="./test_reports"
        )

        # Analyze city-scrapers-atl (API only, limit to 3 scrapers)
        report = analyzer.analyze_repository(
            repo_name="city-scrapers-atl", clone_locally=False, max_scrapers=3
        )

        print(f"\n✓ Analysis completed")
        print(f"\nRepository: {report['repo_name']}")
        print(f"  Total scrapers analyzed: {report['summary']['total_scrapers']}")
        print(f"  Assessment date: {report['assessment_date']}")

        # Show first scraper
        if report.get("scrapers"):
            scraper = report["scrapers"][0]
            print(f"\nFirst scraper: {scraper['scraper_name']}")
            print(f"  Agency: {scraper.get('agency_name', 'N/A')}")
            print(f"  Complexity: {scraper['complexity_assessment']['complexity_rating']}")
            print(f"  Lines of code: {scraper['complexity_assessment']['lines_of_code']}")

        print(f"\nReport saved to: ./test_reports/")

        return True

    except Exception as e:
        print(f"\n✗ API-only analysis failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("City Scrapers Analyzer Skill - Test Suite")
    print("=" * 60)

    # Check for GitHub token
    if not os.environ.get("GITHUB_TOKEN"):
        print("\n⚠ WARNING: GITHUB_TOKEN not set")
        print("Tests will use unauthenticated API (60 requests/hour limit)")
        print("\nTo set token: export GITHUB_TOKEN='your_token'")
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != "y":
            print("Exiting.")
            return

    tests = [
        ("GitHub API Connection", test_github_connection),
        ("Discover Repositories", test_discover_repos),
        ("List Spider Files", test_get_spider_files),
        ("Extract Spider Metadata", test_get_spider_metadata),
        ("Status Classifier", test_status_classifier),
        ("Priority Scorer", test_priority_scorer),
        ("API-Only Analysis", test_api_only_analysis),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            break
        except Exception as e:
            logger.error(f"Unexpected error in {name}: {e}", exc_info=True)
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
