"""
Main repository analyzer orchestration.

Coordinates GitHub API access, scraper execution, classification,
scoring, and report generation.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from .classifier import StatusClassifier
from .executor import ScraperExecutor
from .github_client import GitHubClient
from .reporter import ReportGenerator
from .scorer import PriorityScorer, HarambeScorer, EffortEstimator

logger = logging.getLogger(__name__)


class RepositoryAnalyzer:
    """Main analyzer for city-scrapers repositories."""

    def __init__(
        self,
        github_token: Optional[str] = None,
        timeout_seconds: int = 900,
        output_dir: str = "./reports",
        stale_threshold_days: int = 30,
    ):
        """
        Initialize repository analyzer.

        Args:
            github_token: GitHub API token
            timeout_seconds: Scraper execution timeout
            output_dir: Output directory for reports
            stale_threshold_days: Days for staleness threshold
        """
        self.github = GitHubClient(token=github_token)
        self.executor = ScraperExecutor(timeout_seconds=timeout_seconds)
        self.classifier = StatusClassifier(stale_threshold_days=stale_threshold_days)
        self.priority_scorer = PriorityScorer()
        self.harambe_scorer = HarambeScorer()
        self.effort_estimator = EffortEstimator()
        self.reporter = ReportGenerator(output_dir=output_dir)

    def analyze_repository(
        self,
        repo_name: str,
        clone_locally: bool = True,
        max_scrapers: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a single repository.

        Args:
            repo_name: Repository name (e.g., 'city-scrapers-atl')
            clone_locally: Whether to clone repo locally for execution
            max_scrapers: Maximum number of scrapers to analyze (for testing)

        Returns:
            Repository-level analysis report
        """
        logger.info(f"Analyzing repository: {repo_name}")

        # Get repository info
        repo_info = self.github.get_repository_info(repo_name)

        # Check for dormancy at repo level
        dormancy = self.classifier.classify_dormancy(
            repo_info.get("last_commit"), repo_info.get("last_workflow_run")
        )

        if dormancy["status"] == "DORMANT":
            logger.warning(f"Repository {repo_name} is dormant")
            # Still analyze, but note the dormancy

        # Get spider files
        spider_files = self.github.list_spider_files(repo_name)

        if not spider_files:
            logger.warning(f"No spider files found in {repo_name}")
            return {
                "repo_name": repo_name,
                "error": "No spider files found",
                "repo_info": repo_info,
            }

        # Limit for testing
        if max_scrapers:
            spider_files = spider_files[:max_scrapers]

        # Analyze each scraper
        scraper_assessments = []

        if clone_locally:
            # Clone and execute locally
            repo_path = None
            try:
                repo_path = self.executor.setup_repository(repo_info["clone_url"])

                for spider_file in spider_files:
                    assessment = self._analyze_scraper_local(
                        repo_name, repo_path, spider_file, repo_info
                    )
                    scraper_assessments.append(assessment)

            finally:
                if repo_path:
                    self.executor.cleanup_repository(repo_path)

        else:
            # API-only analysis (no execution)
            for spider_file in spider_files:
                assessment = self._analyze_scraper_api_only(
                    repo_name, spider_file, repo_info
                )
                scraper_assessments.append(assessment)

        # Generate repository report
        repo_report = self.reporter.generate_repository_report(
            repo_name, scraper_assessments
        )

        return repo_report

    def _analyze_scraper_local(
        self,
        repo_name: str,
        repo_path: str,
        spider_file: Dict[str, Any],
        repo_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze scraper with local execution."""
        # Get spider metadata from GitHub API
        metadata = self.github.get_spider_metadata(repo_name, spider_file)

        spider_name = metadata.get("spider_name")
        if not spider_name:
            logger.warning(f"Could not extract spider name from {spider_file['name']}")
            spider_name = spider_file["name"].replace(".py", "")

        logger.info(f"Analyzing scraper: {spider_name}")

        # Execute scraper
        execution_results = self.executor.execute_scraper(repo_path, spider_name)

        # Classify status
        classification = self.classifier.classify(
            exit_code=execution_results.get("exit_code", -1),
            item_count=execution_results.get("item_count", 0),
            log_content=execution_results.get("log_content", ""),
            execution_time=execution_results.get("execution_time_seconds", 0),
            items=execution_results.get("items"),
        )

        # Assess complexity
        complexity = self._assess_complexity(
            metadata["lines_of_code"], metadata.get("uses_mixins", [])
        )

        # Estimate repair effort
        repair_estimate = self.effort_estimator.estimate_effort(
            failure_mode=classification["status"],
            complexity=complexity,
            dependency_type="shared_base"
            if metadata.get("uses_mixins")
            else "standalone",
        )

        # Calculate priority
        priority = self.priority_scorer.calculate_priority(
            agency_name=metadata.get("agency", "Unknown"),
            assignment_count=0,  # Would need external data
            days_since_last_data=None,  # Could calculate from items
            repair_hours=repair_estimate.get("total_estimated_hours", 4.0) or 4.0,
            has_documented_issues=False,  # Would need external data
            status=classification["status"],
        )

        # Assess Harambe candidacy
        harambe = self.harambe_scorer.assess_candidacy(
            status=classification["status"],
            has_reworkd_version=False,  # Would need external data
            complexity=complexity,
            repair_effort=repair_estimate.get("effort_rating", "MEDIUM"),
            uses_mixins=metadata.get("uses_mixins", []),
        )

        # Compile full assessment
        return {
            "repo_name": repo_name,
            "scraper_name": spider_name,
            "file_path": metadata["file_path"],
            "agency_name": metadata.get("agency", "Unknown"),
            "start_urls": metadata.get("start_urls", []),
            "execution_results": {
                "status": classification["status"],
                "exit_code": execution_results.get("exit_code", -1),
                "item_count": execution_results.get("item_count", 0),
                "execution_time_seconds": execution_results.get(
                    "execution_time_seconds", 0
                ),
                "last_run": datetime.now().isoformat(),
                "log_snippet": execution_results.get("log_content", "")[:500],
            },
            "complexity_assessment": {
                "lines_of_code": metadata["lines_of_code"],
                "parse_methods": len(
                    [m for m in metadata.get("uses_mixins", []) if "parse" in m.lower()]
                ),
                "complexity_rating": complexity,
                "dependencies": metadata.get("uses_mixins", []),
                "last_modified": metadata.get("last_modified"),
            },
            "failure_analysis": {
                "primary_failure_mode": classification["status"],
                "root_cause_hypothesis": classification.get("evidence", ["Unknown"])[0],
                "evidence": classification.get("evidence", []),
                "confidence": classification.get("confidence", "unknown"),
            },
            "repair_estimate": repair_estimate,
            "priority_assessment": priority,
            "harambe_candidacy": harambe,
            "strategic_notes": self._generate_strategic_notes(
                classification, priority, harambe
            ),
        }

    def _analyze_scraper_api_only(
        self, repo_name: str, spider_file: Dict[str, Any], repo_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze scraper using only GitHub API (no execution)."""
        # Get spider metadata
        metadata = self.github.get_spider_metadata(repo_name, spider_file)

        spider_name = metadata.get("spider_name") or spider_file["name"].replace(
            ".py", ""
        )

        # Can't execute, so mark as unknown
        complexity = self._assess_complexity(
            metadata["lines_of_code"], metadata.get("uses_mixins", [])
        )

        return {
            "repo_name": repo_name,
            "scraper_name": spider_name,
            "file_path": metadata["file_path"],
            "agency_name": metadata.get("agency", "Unknown"),
            "start_urls": metadata.get("start_urls", []),
            "execution_results": {
                "status": "NOT_EXECUTED",
                "note": "API-only analysis, no execution performed",
            },
            "complexity_assessment": {
                "lines_of_code": metadata["lines_of_code"],
                "complexity_rating": complexity,
                "dependencies": metadata.get("uses_mixins", []),
                "last_modified": metadata.get("last_modified"),
            },
        }

    def _assess_complexity(self, lines_of_code: int, uses_mixins: List[str]) -> str:
        """Assess scraper complexity based on code metrics."""
        # Mixins typically indicate simpler scrapers
        if uses_mixins and any("IQM2" in m or "Legistar" in m for m in uses_mixins):
            return "simple"

        if lines_of_code > 200:
            return "complex"
        elif lines_of_code > 100:
            return "medium"
        else:
            return "simple"

    def _generate_strategic_notes(
        self,
        classification: Dict[str, Any],
        priority: Dict[str, Any],
        harambe: Dict[str, Any],
    ) -> str:
        """Generate strategic notes for scraper."""
        notes = []

        # Priority-based notes
        tier = priority.get("priority_tier", "MEDIUM")
        if tier == "CRITICAL":
            notes.append("CRITICAL priority - immediate attention required")
        elif tier == "HIGH":
            notes.append("High priority repair")

        # Harambe notes
        if harambe.get("recommendation") == "HARAMBE_CONVERSION":
            notes.append("Strong candidate for Harambe conversion")

        # Status-based notes
        status = classification.get("status", "UNKNOWN")
        if status == "SELECTOR_FAILURE":
            notes.append("Likely quick fix - update selectors")
        elif status == "JAVASCRIPT_REQUIRED":
            notes.append("Requires browser automation")
        elif status == "DORMANT":
            notes.append("Repository must be reactivated first")

        return " | ".join(notes) if notes else "Standard repair needed"

    def analyze_ecosystem(
        self,
        repo_names: Optional[List[str]] = None,
        clone_locally: bool = True,
        max_scrapers_per_repo: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Analyze multiple repositories across the ecosystem.

        Args:
            repo_names: List of repo names (or None to discover all)
            clone_locally: Whether to clone and execute locally
            max_scrapers_per_repo: Limit scrapers per repo (for testing)

        Returns:
            Ecosystem-wide analysis report
        """
        logger.info("Starting ecosystem-wide analysis")

        # Discover repositories if not provided
        if repo_names is None:
            repos = self.github.list_city_scrapers_repos()
            repo_names = [r["name"] for r in repos]
            logger.info(f"Discovered {len(repo_names)} repositories")

        # Analyze each repository
        repo_reports = []
        for i, repo_name in enumerate(repo_names, 1):
            logger.info(f"Analyzing repository {i}/{len(repo_names)}: {repo_name}")

            try:
                report = self.analyze_repository(
                    repo_name,
                    clone_locally=clone_locally,
                    max_scrapers=max_scrapers_per_repo,
                )
                repo_reports.append(report)

            except Exception as e:
                logger.error(f"Error analyzing {repo_name}: {e}", exc_info=True)
                # Continue with next repo

        # Generate ecosystem report
        ecosystem_report = self.reporter.generate_ecosystem_report(repo_reports)

        # Generate Markdown summary
        self.reporter.generate_markdown_summary(ecosystem_report)

        return ecosystem_report

    def check_rate_limit(self) -> Dict[str, Any]:
        """Check GitHub API rate limit status."""
        return self.github.check_rate_limit()
