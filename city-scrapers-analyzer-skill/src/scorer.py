"""
Priority scoring and Harambe candidacy assessment.

Implements weighted scoring algorithms for prioritizing repairs and
identifying scrapers that should be converted to Harambe.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PriorityScorer:
    """Calculate priority scores for scraper repairs."""

    # Priority tiers
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    # Contractual risk agencies
    CONTRACTUAL_RISK_AGENCIES = [
        "San Diego",
        "Wichita",
        "Columbia Gorge",
        "Columbia River Gorge",
    ]

    def __init__(
        self,
        contractual_weight: float = 0.40,
        usage_weight: float = 0.30,
        freshness_weight: float = 0.20,
        feasibility_weight: float = 0.10,
    ):
        """
        Initialize priority scorer with configurable weights.

        Args:
            contractual_weight: Weight for contractual risk (default: 40%)
            usage_weight: Weight for usage frequency (default: 30%)
            freshness_weight: Weight for data freshness (default: 20%)
            feasibility_weight: Weight for repair feasibility (default: 10%)
        """
        self.contractual_weight = contractual_weight
        self.usage_weight = usage_weight
        self.freshness_weight = freshness_weight
        self.feasibility_weight = feasibility_weight

        # Validate weights sum to 1.0
        total_weight = sum([contractual_weight, usage_weight, freshness_weight, feasibility_weight])
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Weights sum to {total_weight}, expected 1.0")

    def calculate_priority(
        self,
        agency_name: str,
        assignment_count: int = 0,
        days_since_last_data: Optional[int] = None,
        repair_hours: float = 4.0,
        has_documented_issues: bool = False,
        status: str = "UNKNOWN",
    ) -> Dict[str, Any]:
        """
        Calculate weighted priority score for a scraper.

        Args:
            agency_name: Name of the agency
            assignment_count: Number of Documenters assignments
            days_since_last_data: Days since last data (None = no data)
            repair_hours: Estimated repair effort in hours
            has_documented_issues: Whether scraper has known issues
            status: Current scraper status

        Returns:
            Priority assessment with score, tier, and breakdown
        """
        # Contractual Risk Factor (0-10)
        contractual_factor = self._assess_contractual_risk(
            agency_name, has_documented_issues
        )

        # Usage Frequency Factor (0-10)
        usage_factor = self._assess_usage_frequency(assignment_count)

        # Data Freshness Factor (0-10)
        freshness_factor = self._assess_data_freshness(days_since_last_data, status)

        # Repair Feasibility Factor (0-10)
        feasibility_factor = self._assess_repair_feasibility(repair_hours)

        # Calculate weighted score
        priority_score = (
            self.contractual_weight * contractual_factor
            + self.usage_weight * usage_factor
            + self.freshness_weight * freshness_factor
            + self.feasibility_weight * feasibility_factor
        )

        # Determine tier
        priority_tier = self._classify_tier(priority_score)

        return {
            "priority_score": round(priority_score, 2),
            "priority_tier": priority_tier,
            "factors": {
                "contractual_risk": contractual_factor,
                "usage_frequency": usage_factor,
                "data_freshness_impact": freshness_factor,
                "repair_feasibility": feasibility_factor,
            },
            "weights": {
                "contractual_weight": self.contractual_weight,
                "usage_weight": self.usage_weight,
                "freshness_weight": self.freshness_weight,
                "feasibility_weight": self.feasibility_weight,
            },
        }

    def _assess_contractual_risk(
        self, agency_name: str, has_documented_issues: bool
    ) -> float:
        """Assess contractual/political risk level."""
        # Check for explicit contractual risk
        if any(risk_agency.lower() in agency_name.lower()
               for risk_agency in self.CONTRACTUAL_RISK_AGENCIES):
            return 10.0

        # Documented issues
        if has_documented_issues:
            return 7.0

        # Standard agency
        return 3.0

    def _assess_usage_frequency(self, assignment_count: int) -> float:
        """Assess based on Documenters assignment frequency."""
        if assignment_count >= 6:
            return 10.0
        elif assignment_count >= 3:
            return 6.0
        elif assignment_count >= 1:
            return 3.0
        else:
            return 1.0

    def _assess_data_freshness(
        self, days_since_last_data: Optional[int], status: str
    ) -> float:
        """Assess impact of missing/stale data."""
        # No data at all (highest impact)
        if days_since_last_data is None or status in ["EMPTY_RESULT", "SELECTOR_FAILURE"]:
            return 10.0

        # Very stale data
        if days_since_last_data > 90:
            return 10.0

        # Moderately stale
        if days_since_last_data > 30:
            return 7.0

        # Recent data
        return 3.0

    def _assess_repair_feasibility(self, repair_hours: float) -> float:
        """Assess repair feasibility (lower effort = higher score)."""
        if repair_hours <= 2:
            return 10.0  # Quick win
        elif repair_hours <= 8:
            return 6.0  # Medium effort
        else:
            return 3.0  # High effort

    def _classify_tier(self, score: float) -> str:
        """Classify priority tier based on score."""
        if score >= 8.0:
            return self.CRITICAL
        elif score >= 6.0:
            return self.HIGH
        elif score >= 4.0:
            return self.MEDIUM
        else:
            return self.LOW


class HarambeScorer:
    """Assess candidacy for Harambe (browser-based) conversion."""

    HARAMBE_CONVERSION = "HARAMBE_CONVERSION"
    CONSIDER_HARAMBE = "CONSIDER_HARAMBE"
    CONVENTIONAL_REPAIR = "CONVENTIONAL_REPAIR"

    def assess_candidacy(
        self,
        status: str,
        has_reworkd_version: bool = False,
        complexity: str = "medium",
        repair_effort: str = "MEDIUM",
        uses_mixins: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Determine if scraper should be converted to Harambe.

        Scoring factors:
        - JavaScript requirement: +3
        - Existing Reworkd implementation: +4
        - High site complexity: +2
        - High conventional repair difficulty: +1
        - Maintenance burden: -2

        Args:
            status: Current scraper status
            has_reworkd_version: Whether Reworkd scraper exists
            complexity: Scraper complexity (simple/medium/complex)
            repair_effort: Repair difficulty rating
            uses_mixins: List of mixins used by scraper

        Returns:
            Harambe candidacy assessment
        """
        score = 0
        reasoning = []

        # JavaScript requirement (+3)
        if status == "JAVASCRIPT_REQUIRED":
            score += 3
            reasoning.append("Site requires JavaScript rendering")

        # Existing Reworkd implementation (+4)
        if has_reworkd_version:
            score += 4
            reasoning.append("Can reuse existing Reworkd code")

        # Site complexity (+2)
        if complexity == "complex":
            score += 2
            reasoning.append("Complex site structure")

        # Conventional repair difficulty (+1)
        if repair_effort in ["HIGH", "VERY_HIGH"]:
            score += 1
            reasoning.append("High conventional repair difficulty")

        # Maintenance concerns (-2)
        # Per technical team: "significantly harder to maintain"
        score -= 2
        reasoning.append("Harambe has higher maintenance burden")

        # Determine recommendation
        if score >= 6:
            recommendation = self.HARAMBE_CONVERSION
            reasoning.insert(0, "Strong candidate for Harambe conversion")
        elif score >= 4:
            recommendation = self.CONSIDER_HARAMBE
            reasoning.insert(0, "Harambe is viable but not required")
        else:
            recommendation = self.CONVENTIONAL_REPAIR
            reasoning.insert(0, "Conventional Scrapy repair preferred")

        # Additional context
        if not has_reworkd_version and status == "JAVASCRIPT_REQUIRED":
            reasoning.append("Would require building Harambe scraper from scratch")

        if uses_mixins and any("IQM2" in m or "Legistar" in m for m in uses_mixins):
            reasoning.append("Uses standard mixin - conventional repair likely easier")

        return {
            "score": score,
            "recommendation": recommendation,
            "reasoning": " | ".join(reasoning),
            "factors": {
                "javascript_required": status == "JAVASCRIPT_REQUIRED",
                "has_reworkd_version": has_reworkd_version,
                "high_complexity": complexity == "complex",
                "difficult_repair": repair_effort in ["HIGH", "VERY_HIGH"],
                "maintenance_burden": True,  # Always a factor
            },
        }

    def batch_assess(self, scrapers: list) -> Dict[str, Any]:
        """
        Assess Harambe candidacy for multiple scrapers and generate summary.

        Args:
            scrapers: List of scraper assessment dictionaries

        Returns:
            Summary with counts and strong candidates
        """
        results = {
            "total_assessed": len(scrapers),
            "recommendations": {
                self.HARAMBE_CONVERSION: 0,
                self.CONSIDER_HARAMBE: 0,
                self.CONVENTIONAL_REPAIR: 0,
            },
            "strong_candidates": [],
            "javascript_required_count": 0,
            "reworkd_available_count": 0,
        }

        for scraper in scrapers:
            harambe_result = scraper.get("harambe_candidacy", {})
            recommendation = harambe_result.get("recommendation", self.CONVENTIONAL_REPAIR)
            results["recommendations"][recommendation] += 1

            if recommendation == self.HARAMBE_CONVERSION:
                results["strong_candidates"].append(
                    {
                        "scraper_name": scraper.get("scraper_name"),
                        "agency": scraper.get("agency_name"),
                        "score": harambe_result.get("score"),
                        "reasoning": harambe_result.get("reasoning"),
                    }
                )

            if scraper.get("execution_results", {}).get("status") == "JAVASCRIPT_REQUIRED":
                results["javascript_required_count"] += 1

            if scraper.get("has_reworkd_version"):
                results["reworkd_available_count"] += 1

        return results


class EffortEstimator:
    """Estimate repair effort for failed scrapers."""

    # Base effort hours by failure type
    BASE_EFFORT_HOURS = {
        "IMPORT_ERROR": 1.0,
        "ENCODING_ERROR": 1.5,
        "SSL_ERROR": 1.0,
        "HTTP_ERROR": 2.0,
        "TIMEOUT": 2.0,
        "SELECTOR_FAILURE": 3.0,
        "STALE_SUCCESS": 3.0,
        "EMPTY_RESULT": 4.0,
        "JAVASCRIPT_REQUIRED": 12.0,
        "UNKNOWN_FAILURE": 4.0,
        "DORMANT": None,  # Requires repo reactivation first
    }

    # Complexity multipliers
    COMPLEXITY_MULTIPLIERS = {
        "simple": 1.0,
        "medium": 1.5,
        "complex": 2.5,
    }

    # Dependency factors
    DEPENDENCY_FACTORS = {
        "standalone": 1.0,
        "shared_base": 1.3,
        "tightly_coupled": 1.5,
    }

    # Effort rating thresholds
    TRIVIAL = "TRIVIAL"  # < 1 hour
    LOW = "LOW"  # 1-4 hours
    MEDIUM = "MEDIUM"  # 4-8 hours
    HIGH = "HIGH"  # 8-16 hours
    VERY_HIGH = "VERY_HIGH"  # 16+ hours

    def estimate_effort(
        self,
        failure_mode: str,
        complexity: str = "medium",
        dependency_type: str = "standalone",
    ) -> Dict[str, Any]:
        """
        Calculate repair effort estimate.

        Args:
            failure_mode: Type of failure
            complexity: Scraper complexity (simple/medium/complex)
            dependency_type: Dependency coupling (standalone/shared_base/tightly_coupled)

        Returns:
            Effort estimate with hours and rating
        """
        base_hours = self.BASE_EFFORT_HOURS.get(failure_mode)

        if base_hours is None:
            return {
                "base_effort_hours": None,
                "complexity_multiplier": None,
                "dependency_factor": None,
                "total_estimated_hours": None,
                "effort_rating": "REQUIRES_REPO_REACTIVATION",
                "repair_approach": "Repository must be reactivated before assessment",
            }

        complexity_mult = self.COMPLEXITY_MULTIPLIERS.get(complexity, 1.5)
        dependency_mult = self.DEPENDENCY_FACTORS.get(dependency_type, 1.0)

        total_hours = base_hours * complexity_mult * dependency_mult

        # Round to nearest 0.5 hours
        total_hours = round(total_hours * 2) / 2

        # Classify effort
        if total_hours < 1:
            effort_rating = self.TRIVIAL
        elif total_hours <= 4:
            effort_rating = self.LOW
        elif total_hours <= 8:
            effort_rating = self.MEDIUM
        elif total_hours <= 16:
            effort_rating = self.HIGH
        else:
            effort_rating = self.VERY_HIGH

        # Generate repair approach
        repair_approach = self._suggest_repair_approach(failure_mode, complexity)

        return {
            "base_effort_hours": base_hours,
            "complexity_multiplier": complexity_mult,
            "dependency_factor": dependency_mult,
            "total_estimated_hours": total_hours,
            "effort_rating": effort_rating,
            "repair_approach": repair_approach,
        }

    def _suggest_repair_approach(self, failure_mode: str, complexity: str) -> str:
        """Suggest repair approach based on failure mode."""
        approaches = {
            "IMPORT_ERROR": "Update dependencies in Pipfile",
            "ENCODING_ERROR": "Fix character encoding in parser",
            "SSL_ERROR": "Update SSL certificate handling",
            "HTTP_ERROR": "Investigate site changes, update URLs if needed",
            "TIMEOUT": "Optimize scraper performance or increase timeout",
            "SELECTOR_FAILURE": "Inspect current HTML and update CSS/XPath selectors",
            "STALE_SUCCESS": "Verify start_urls point to current meetings",
            "EMPTY_RESULT": "Investigate site structure for changes",
            "JAVASCRIPT_REQUIRED": "Convert to Harambe or use Selenium/Playwright",
            "UNKNOWN_FAILURE": "Debug execution logs to identify root cause",
        }

        approach = approaches.get(failure_mode, "Manual investigation required")

        if complexity == "complex":
            approach += " (Complex scraper - may require significant refactoring)"

        return approach
