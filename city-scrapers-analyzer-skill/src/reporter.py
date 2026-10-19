"""
Report generation for scraper analysis results.

Generates JSON and Markdown reports at scraper, repository, and ecosystem levels.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate comprehensive analysis reports in multiple formats."""

    def __init__(self, output_dir: str = "./reports"):
        """
        Initialize report generator.

        Args:
            output_dir: Directory for saving reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_scraper_report(self, scraper_data: Dict[str, Any]) -> str:
        """
        Generate JSON report for a single scraper.

        Args:
            scraper_data: Complete scraper assessment data

        Returns:
            Path to generated report file
        """
        repo_name = scraper_data.get("repo_name", "unknown")
        scraper_name = scraper_data.get("scraper_name", "unknown")

        filename = f"{repo_name}_{scraper_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(scraper_data, f, indent=2, default=str)

        logger.info(f"Generated scraper report: {filepath}")
        return str(filepath)

    def generate_repository_report(
        self, repo_name: str, scrapers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate aggregate report for a repository.

        Args:
            repo_name: Repository name
            scrapers: List of scraper assessments

        Returns:
            Repository-level report data
        """
        total = len(scrapers)
        functional = sum(
            1 for s in scrapers if s.get("execution_results", {}).get("status") == "SUCCESS"
        )
        failed = total - functional

        # Failure breakdown
        failure_breakdown = {}
        for scraper in scrapers:
            status = scraper.get("execution_results", {}).get("status", "UNKNOWN")
            if status != "SUCCESS":
                failure_breakdown[status] = failure_breakdown.get(status, 0) + 1

        # Effort summary
        effort_by_tier = {"TRIVIAL": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "VERY_HIGH": 0}
        total_hours = 0

        for scraper in scrapers:
            estimate = scraper.get("repair_estimate", {})
            hours = estimate.get("total_estimated_hours", 0) or 0
            tier = estimate.get("effort_rating", "MEDIUM")

            total_hours += hours
            if tier in effort_by_tier:
                effort_by_tier[tier] += hours

        # Priority distribution
        priority_dist = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for scraper in scrapers:
            tier = scraper.get("priority_assessment", {}).get("priority_tier", "MEDIUM")
            if tier in priority_dist:
                priority_dist[tier] += 1

        # Harambe candidates
        harambe_count = sum(
            1
            for s in scrapers
            if s.get("harambe_candidacy", {}).get("recommendation") == "HARAMBE_CONVERSION"
        )

        # Strategic assessment
        blocking_issues = self._identify_blocking_issues(scrapers)
        overall_health = self._assess_overall_health(functional, total)

        report = {
            "repo_name": repo_name,
            "assessment_date": datetime.now().isoformat(),
            "summary": {
                "total_scrapers": total,
                "functional": functional,
                "failed": failed,
                "success_rate": round(functional / total, 3) if total > 0 else 0,
            },
            "failure_breakdown": failure_breakdown,
            "effort_summary": {
                "total_hours_estimated": round(total_hours, 1),
                "by_tier": effort_by_tier,
            },
            "priority_distribution": priority_dist,
            "harambe_candidates": harambe_count,
            "strategic_assessment": {
                "overall_health": overall_health,
                "recommended_approach": self._recommend_approach(scrapers, priority_dist),
                "blocking_issues": blocking_issues,
                "estimated_recovery_time": self._estimate_recovery_time(total_hours),
            },
            "scrapers": scrapers,
        }

        # Save to file
        filename = f"{repo_name}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Generated repository report: {filepath}")
        return report

    def generate_ecosystem_report(
        self, repo_reports: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate cross-repository ecosystem analysis.

        Args:
            repo_reports: List of repository-level reports

        Returns:
            Ecosystem-wide analysis
        """
        total_repos = len(repo_reports)
        total_scrapers = sum(r["summary"]["total_scrapers"] for r in repo_reports)
        functional_scrapers = sum(r["summary"]["functional"] for r in repo_reports)
        failed_scrapers = total_scrapers - functional_scrapers

        # Aggregate failure patterns
        failure_patterns = {}
        for repo in repo_reports:
            for failure_type, count in repo.get("failure_breakdown", {}).items():
                failure_patterns[failure_type] = failure_patterns.get(failure_type, 0) + count

        # Calculate percentages
        failure_patterns_pct = {
            failure: {
                "count": count,
                "percentage": round((count / failed_scrapers) * 100, 1)
                if failed_scrapers > 0
                else 0,
            }
            for failure, count in failure_patterns.items()
        }

        # Total repair effort
        total_hours = sum(
            r["effort_summary"]["total_hours_estimated"] for r in repo_reports
        )

        # Strategic insights
        insights = self._generate_ecosystem_insights(repo_reports, failure_patterns)

        # Recommendations
        recommendations = self._generate_ecosystem_recommendations(
            repo_reports, failure_patterns, total_hours
        )

        report = {
            "analysis_date": datetime.now().isoformat(),
            "repos_assessed": total_repos,
            "total_scrapers": total_scrapers,
            "ecosystem_health": {
                "functional_scrapers": functional_scrapers,
                "failed_scrapers": failed_scrapers,
                "overall_success_rate": round(functional_scrapers / total_scrapers, 3)
                if total_scrapers > 0
                else 0,
            },
            "failure_patterns": failure_patterns_pct,
            "total_repair_effort": {
                "hours": round(total_hours, 1),
                "full_time_weeks": round(total_hours / 40, 1),
                "parallel_effort_estimate": self._estimate_parallel_effort(total_hours),
            },
            "strategic_insights": insights,
            "recommendations": recommendations,
            "repos": repo_reports,
        }

        # Save to file
        filename = f"ecosystem_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Generated ecosystem report: {filepath}")
        return report

    def generate_markdown_summary(
        self, ecosystem_report: Dict[str, Any]
    ) -> str:
        """
        Generate human-readable Markdown summary.

        Args:
            ecosystem_report: Ecosystem analysis data

        Returns:
            Path to generated Markdown file
        """
        lines = []

        # Header
        lines.append("# City Scrapers Network-Wide Analysis")
        lines.append(f"**Date**: {ecosystem_report['analysis_date']}")
        lines.append(f"**Repositories Analyzed**: {ecosystem_report['repos_assessed']}")
        lines.append(f"**Total Scrapers**: {ecosystem_report['total_scrapers']}")
        lines.append("")

        # Executive Summary
        health = ecosystem_report["ecosystem_health"]
        lines.append("## Executive Summary")
        lines.append(
            f"- Functional: {health['functional_scrapers']} ({health['overall_success_rate']:.1%})"
        )
        lines.append(
            f"- Non-functional: {health['failed_scrapers']} ({1-health['overall_success_rate']:.1%})"
        )
        lines.append(
            f"- Total estimated repair hours: {ecosystem_report['total_repair_effort']['hours']}"
        )
        lines.append("")

        # Failure Mode Breakdown
        lines.append("## Failure Mode Breakdown")
        for failure, data in sorted(
            ecosystem_report["failure_patterns"].items(),
            key=lambda x: x[1]["count"],
            reverse=True,
        ):
            lines.append(
                f"{data['count']}. {failure}: {data['count']} scrapers ({data['percentage']}%)"
            )
        lines.append("")

        # Repository Rankings
        lines.append("## Repository Rankings (by failure count)")
        repos_by_failure = sorted(
            ecosystem_report["repos"],
            key=lambda r: r["summary"]["failed"],
            reverse=True,
        )
        for i, repo in enumerate(repos_by_failure[:10], 1):
            lines.append(
                f"{i}. {repo['repo_name']}: {repo['summary']['failed']} failures"
            )
        lines.append("")

        # Strategic Insights
        lines.append("## Strategic Insights")
        for insight in ecosystem_report["strategic_insights"]:
            lines.append(f"- {insight}")
        lines.append("")

        # Recommendations
        lines.append("## Recommendations")
        recs = ecosystem_report["recommendations"]
        if "immediate_actions" in recs:
            lines.append("### Immediate Actions")
            for action in recs["immediate_actions"]:
                lines.append(f"- {action}")
            lines.append("")

        if "parallel_tracks" in recs:
            lines.append("### Parallel Tracks")
            for track in recs["parallel_tracks"]:
                lines.append(f"- {track}")
            lines.append("")

        # Join and save
        content = "\n".join(lines)
        filename = f"analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Generated Markdown summary: {filepath}")
        return str(filepath)

    def _identify_blocking_issues(self, scrapers: List[Dict[str, Any]]) -> List[str]:
        """Identify critical blocking issues."""
        issues = []

        dormant_count = sum(
            1
            for s in scrapers
            if s.get("execution_results", {}).get("status") == "DORMANT"
        )
        if dormant_count > 0:
            issues.append(f"{dormant_count} scrapers in dormant state")

        critical_count = sum(
            1
            for s in scrapers
            if s.get("priority_assessment", {}).get("priority_tier") == "CRITICAL"
        )
        if critical_count > 0:
            issues.append(f"{critical_count} CRITICAL priority scrapers")

        return issues or ["None identified"]

    def _assess_overall_health(self, functional: int, total: int) -> str:
        """Assess overall repository health."""
        if total == 0:
            return "UNKNOWN"

        success_rate = functional / total

        if success_rate >= 0.9:
            return "EXCELLENT"
        elif success_rate >= 0.7:
            return "GOOD"
        elif success_rate >= 0.5:
            return "MODERATE"
        elif success_rate >= 0.3:
            return "POOR"
        else:
            return "CRITICAL"

    def _recommend_approach(
        self, scrapers: List[Dict[str, Any]], priority_dist: Dict[str, int]
    ) -> str:
        """Generate recommended repair approach."""
        critical = priority_dist.get("CRITICAL", 0)
        high = priority_dist.get("HIGH", 0)

        if critical + high == 0:
            return "Focus on medium priority scrapers for steady improvement"
        elif critical > 0:
            return f"Prioritize {critical + high} CRITICAL/HIGH scrapers first"
        else:
            return f"Address {high} HIGH priority scrapers systematically"

    def _estimate_recovery_time(self, total_hours: float) -> str:
        """Estimate time to full recovery."""
        if total_hours < 40:
            return "1 week with focused effort"
        elif total_hours < 160:
            return f"{round(total_hours / 40)} weeks with focused effort"
        else:
            return f"{round(total_hours / 160)} months with sustained effort"

    def _estimate_parallel_effort(self, total_hours: float) -> str:
        """Estimate parallel execution timeline."""
        # Assume 2 developers working in parallel
        weeks = total_hours / (40 * 2)

        if weeks < 2:
            return "1-2 weeks with 2 developers"
        elif weeks < 8:
            return f"{round(weeks)}-{round(weeks)+2} weeks with 2 developers"
        else:
            return f"{round(weeks/4)}-{round(weeks/4)+1} months with 2 developers"

    def _generate_ecosystem_insights(
        self, repo_reports: List[Dict[str, Any]], failure_patterns: Dict[str, int]
    ) -> List[str]:
        """Generate strategic insights from ecosystem data."""
        insights = []

        # Most common failure mode
        if failure_patterns:
            top_failure = max(failure_patterns.items(), key=lambda x: x[1])
            insights.append(
                f"{top_failure[1]} scrapers failing due to {top_failure[0]}"
            )

        # Dormant repos
        dormant_repos = [
            r["repo_name"]
            for r in repo_reports
            if any(
                issue.startswith("dormant")
                for issue in r["strategic_assessment"].get("blocking_issues", [])
            )
        ]
        if dormant_repos:
            insights.append(f"Dormant repos requiring reactivation: {', '.join(dormant_repos[:3])}")

        # Harambe candidates
        total_harambe = sum(r.get("harambe_candidates", 0) for r in repo_reports)
        if total_harambe > 0:
            insights.append(f"{total_harambe} scrapers identified as Harambe candidates")

        return insights

    def _generate_ecosystem_recommendations(
        self,
        repo_reports: List[Dict[str, Any]],
        failure_patterns: Dict[str, int],
        total_hours: float,
    ) -> Dict[str, List[str]]:
        """Generate actionable recommendations."""
        recommendations = {"immediate_actions": [], "parallel_tracks": []}

        # Immediate actions based on failure patterns
        if failure_patterns.get("SELECTOR_FAILURE", 0) > 0:
            recommendations["immediate_actions"].append(
                "Address selector failures - likely quick wins"
            )

        if failure_patterns.get("DORMANT", 0) > 0:
            recommendations["immediate_actions"].append("Reactivate dormant repositories")

        # Parallel tracks
        harambe_total = sum(r.get("harambe_candidates", 0) for r in repo_reports)
        if harambe_total > 0:
            recommendations["parallel_tracks"].append(
                f"Convert {harambe_total} identified Harambe candidates"
            )

        conventional_fixes = sum(
            1
            for r in repo_reports
            for s in r.get("scrapers", [])
            if s.get("repair_estimate", {}).get("effort_rating") in ["TRIVIAL", "LOW"]
        )
        if conventional_fixes > 0:
            recommendations["parallel_tracks"].append(
                f"Repair {conventional_fixes} low-effort conventional scrapers"
            )

        # Resource allocation
        if total_hours > 160:
            recommendations["parallel_tracks"].append(
                "Consider allocating 2+ developers for 4-6 weeks"
            )

        return recommendations
