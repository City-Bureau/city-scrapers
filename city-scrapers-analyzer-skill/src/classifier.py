"""
Status classification and failure mode detection for scrapers.

Implements the classification logic for determining scraper health status
and identifying specific failure modes.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class StatusClassifier:
    """Classifies scraper execution results into standardized status categories."""

    # Status constants
    SUCCESS = "SUCCESS"
    STALE_SUCCESS = "STALE_SUCCESS"
    EMPTY_RESULT = "EMPTY_RESULT"
    SELECTOR_FAILURE = "SELECTOR_FAILURE"
    HTTP_ERROR = "HTTP_ERROR"
    TIMEOUT = "TIMEOUT"
    IMPORT_ERROR = "IMPORT_ERROR"
    ENCODING_ERROR = "ENCODING_ERROR"
    SSL_ERROR = "SSL_ERROR"
    JAVASCRIPT_REQUIRED = "JAVASCRIPT_REQUIRED"
    DORMANT = "DORMANT"
    UNKNOWN_FAILURE = "UNKNOWN_FAILURE"

    # Failure frequency categories
    FREQUENCY_HIGH = "high_frequency"
    FREQUENCY_MEDIUM = "medium_frequency"
    FREQUENCY_LOW = "low_frequency"

    # Map failure types to frequency
    FAILURE_FREQUENCIES = {
        SELECTOR_FAILURE: FREQUENCY_HIGH,
        HTTP_ERROR: FREQUENCY_MEDIUM,
        EMPTY_RESULT: FREQUENCY_MEDIUM,
        TIMEOUT: FREQUENCY_MEDIUM,
        JAVASCRIPT_REQUIRED: FREQUENCY_MEDIUM,
        ENCODING_ERROR: FREQUENCY_LOW,
        IMPORT_ERROR: FREQUENCY_LOW,
        SSL_ERROR: FREQUENCY_LOW,
        DORMANT: FREQUENCY_LOW,
        UNKNOWN_FAILURE: FREQUENCY_MEDIUM,
    }

    def __init__(self, stale_threshold_days: int = 30):
        """
        Initialize status classifier.

        Args:
            stale_threshold_days: Days after which data is considered stale
        """
        self.stale_threshold_days = stale_threshold_days

    def classify(
        self,
        exit_code: int,
        item_count: int,
        log_content: str,
        execution_time: float,
        items: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Classify scraper execution status.

        Args:
            exit_code: Process exit code (0 = success)
            item_count: Number of items scraped
            log_content: Full log output from scraper
            execution_time: Execution time in seconds
            items: Actual scraped items (optional, for staleness check)

        Returns:
            Classification result with status, confidence, and evidence
        """
        logger.debug(f"Classifying: exit={exit_code}, items={item_count}, time={execution_time}s")

        # Priority 1: Check for specific error types
        if exit_code != 0:
            return self._classify_error(log_content, execution_time)

        # Priority 2: Check for empty results
        if item_count == 0:
            return self._classify_empty_result(log_content)

        # Priority 3: Success cases
        if item_count > 0:
            return self._classify_success(items, log_content)

        # Fallback
        return {
            "status": self.UNKNOWN_FAILURE,
            "confidence": "low",
            "evidence": ["Unexpected execution state"],
            "category": self.FREQUENCY_MEDIUM,
        }

    def _classify_error(self, log_content: str, execution_time: float) -> Dict[str, Any]:
        """Classify execution errors based on log content."""

        # Import errors
        if self._contains_any(log_content, ["ImportError", "ModuleNotFoundError", "No module named"]):
            return {
                "status": self.IMPORT_ERROR,
                "confidence": "high",
                "evidence": self._extract_error_snippets(log_content, ["ImportError", "ModuleNotFoundError"]),
                "category": self.FREQUENCY_LOW,
            }

        # Timeout errors
        if self._contains_any(log_content, ["timeout", "timed out"]) or execution_time > 900:
            return {
                "status": self.TIMEOUT,
                "confidence": "high",
                "evidence": [f"Execution time: {execution_time}s"] + self._extract_error_snippets(log_content, ["timeout"]),
                "category": self.FREQUENCY_MEDIUM,
            }

        # SSL/Certificate errors
        if self._contains_any(log_content, ["SSL", "certificate", "CERTIFICATE_VERIFY_FAILED"]):
            return {
                "status": self.SSL_ERROR,
                "confidence": "high",
                "evidence": self._extract_error_snippets(log_content, ["SSL", "certificate"]),
                "category": self.FREQUENCY_LOW,
            }

        # HTTP errors
        http_codes = ["404", "403", "500", "502", "503"]
        if self._contains_any(log_content, http_codes):
            matching_codes = [code for code in http_codes if code in log_content]
            return {
                "status": self.HTTP_ERROR,
                "confidence": "high",
                "evidence": [f"HTTP {code} detected" for code in matching_codes]
                + self._extract_error_snippets(log_content, matching_codes),
                "category": self.FREQUENCY_MEDIUM,
            }

        # Encoding errors
        if self._contains_any(log_content, ["UnicodeDecodeError", "UnicodeEncodeError", "codec"]):
            return {
                "status": self.ENCODING_ERROR,
                "confidence": "high",
                "evidence": self._extract_error_snippets(log_content, ["Unicode", "codec"]),
                "category": self.FREQUENCY_LOW,
            }

        # Unknown error
        return {
            "status": self.UNKNOWN_FAILURE,
            "confidence": "medium",
            "evidence": self._extract_error_snippets(log_content, ["Error", "Exception", "Traceback"]),
            "category": self.FREQUENCY_MEDIUM,
        }

    def _classify_empty_result(self, log_content: str) -> Dict[str, Any]:
        """Classify cases where scraper runs but produces no items."""

        # Selector failures
        selector_indicators = [
            "selector returned no results",
            "returned 0 results",
            "no elements found",
            "empty selector",
        ]
        if self._contains_any(log_content, selector_indicators):
            return {
                "status": self.SELECTOR_FAILURE,
                "confidence": "high",
                "evidence": self._extract_error_snippets(log_content, selector_indicators),
                "category": self.FREQUENCY_HIGH,
            }

        # JavaScript-heavy sites
        if self._is_javascript_heavy(log_content):
            return {
                "status": self.JAVASCRIPT_REQUIRED,
                "confidence": "medium",
                "evidence": ["Site appears to require JavaScript rendering"],
                "category": self.FREQUENCY_MEDIUM,
            }

        # Generic empty result
        return {
            "status": self.EMPTY_RESULT,
            "confidence": "medium",
            "evidence": ["No items scraped, no specific error detected"],
            "category": self.FREQUENCY_MEDIUM,
        }

    def _classify_success(
        self, items: Optional[List[Dict]], log_content: str
    ) -> Dict[str, Any]:
        """Classify successful executions, checking for data staleness."""

        # Check if data is stale
        if items and self._is_data_stale(items):
            newest_date = self._get_newest_item_date(items)
            return {
                "status": self.STALE_SUCCESS,
                "confidence": "high",
                "evidence": [f"Latest meeting date: {newest_date}"],
                "category": self.FREQUENCY_MEDIUM,
            }

        # Normal success
        return {
            "status": self.SUCCESS,
            "confidence": "high",
            "evidence": ["Scraper executed successfully with current data"],
            "category": None,  # Not a failure
        }

    def _is_javascript_heavy(self, log_content: str) -> bool:
        """Detect if site likely requires JavaScript rendering."""
        indicators = [
            "empty response body",
            "no items found on page",
            "<script>window.__INITIAL_STATE__",
            "React",
            "Vue.js",
            "Angular",
            "data-reactroot",
            "__NEXT_DATA__",
        ]
        return any(indicator in log_content for indicator in indicators)

    def _is_data_stale(self, items: List[Dict]) -> bool:
        """Check if scraped meeting dates are old."""
        if not items:
            return False

        newest_date = self._get_newest_item_date(items)
        if not newest_date:
            return False

        threshold = datetime.now() - timedelta(days=self.stale_threshold_days)
        return newest_date < threshold

    def _get_newest_item_date(self, items: List[Dict]) -> Optional[datetime]:
        """Extract newest meeting date from items."""
        dates = []
        for item in items:
            # Try various date fields
            for field in ["start", "start_time", "date", "meeting_date"]:
                if field in item and item[field]:
                    try:
                        if isinstance(item[field], datetime):
                            dates.append(item[field])
                        elif isinstance(item[field], str):
                            # Try parsing ISO format
                            dates.append(datetime.fromisoformat(item[field].replace("Z", "+00:00")))
                    except (ValueError, AttributeError):
                        continue

        return max(dates) if dates else None

    def _contains_any(self, text: str, patterns: List[str]) -> bool:
        """Check if text contains any of the patterns (case-insensitive)."""
        text_lower = text.lower()
        return any(pattern.lower() in text_lower for pattern in patterns)

    def _extract_error_snippets(
        self, log_content: str, keywords: List[str], context_lines: int = 2
    ) -> List[str]:
        """Extract relevant snippets from logs containing keywords."""
        snippets = []
        lines = log_content.split("\n")

        for i, line in enumerate(lines):
            if any(keyword.lower() in line.lower() for keyword in keywords):
                # Get context around the match
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                snippet = "\n".join(lines[start:end])

                # Truncate if too long
                if len(snippet) > 200:
                    snippet = snippet[:200] + "..."

                snippets.append(snippet)

                # Limit number of snippets
                if len(snippets) >= 3:
                    break

        return snippets or [log_content[:500] + "..." if len(log_content) > 500 else log_content]

    def classify_dormancy(
        self, last_commit_date: Optional[str], last_workflow_run: Optional[str]
    ) -> Dict[str, Any]:
        """
        Classify repository dormancy status.

        Args:
            last_commit_date: ISO timestamp of last commit
            last_workflow_run: ISO timestamp of last workflow execution

        Returns:
            Classification result
        """
        if not last_commit_date and not last_workflow_run:
            return {
                "status": self.DORMANT,
                "confidence": "high",
                "evidence": ["No commit or workflow history found"],
                "category": self.FREQUENCY_LOW,
            }

        # Check most recent activity
        most_recent = None
        if last_commit_date:
            try:
                commit_dt = datetime.fromisoformat(last_commit_date.replace("Z", "+00:00"))
                most_recent = commit_dt
            except ValueError:
                pass

        if last_workflow_run:
            try:
                workflow_dt = datetime.fromisoformat(last_workflow_run.replace("Z", "+00:00"))
                if not most_recent or workflow_dt > most_recent:
                    most_recent = workflow_dt
            except ValueError:
                pass

        if most_recent:
            days_inactive = (datetime.now(most_recent.tzinfo) - most_recent).days

            if days_inactive > 90:
                return {
                    "status": self.DORMANT,
                    "confidence": "high",
                    "evidence": [f"No activity for {days_inactive} days"],
                    "category": self.FREQUENCY_LOW,
                }

        return {
            "status": "ACTIVE",
            "confidence": "high",
            "evidence": ["Recent activity detected"],
            "category": None,
        }

    def get_failure_category(self, status: str) -> str:
        """Get frequency category for a failure status."""
        return self.FAILURE_FREQUENCIES.get(status, self.FREQUENCY_MEDIUM)
