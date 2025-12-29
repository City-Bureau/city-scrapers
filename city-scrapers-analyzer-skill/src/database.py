"""
SQLite database for historical tracking of scraper assessments.

Enables trend analysis, comparison across runs, and calibration of estimates.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class AnalysisDatabase:
    """SQLite database for storing and querying analysis results over time."""

    def __init__(self, db_path: str = "./analysis_history.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Return rows as dicts
        self._init_schema()

    def _init_schema(self):
        """Create database schema if it doesn't exist."""
        cursor = self.conn.cursor()

        # Analysis runs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_runs (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_date TEXT NOT NULL,
                analysis_type TEXT NOT NULL,  -- 'repository' or 'ecosystem'
                total_repos INTEGER,
                total_scrapers INTEGER,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Repository assessments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repository_assessments (
                assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                repo_name TEXT NOT NULL,
                total_scrapers INTEGER,
                functional INTEGER,
                failed INTEGER,
                success_rate REAL,
                total_repair_hours REAL,
                overall_health TEXT,
                assessment_json TEXT,  -- Full JSON for detailed analysis
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (run_id) REFERENCES analysis_runs(run_id)
            )
        """)

        # Scraper assessments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraper_assessments (
                assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                repo_name TEXT NOT NULL,
                scraper_name TEXT NOT NULL,
                agency_name TEXT,
                status TEXT NOT NULL,
                item_count INTEGER,
                execution_time_seconds REAL,
                complexity_rating TEXT,
                lines_of_code INTEGER,
                failure_mode TEXT,
                repair_hours REAL,
                effort_rating TEXT,
                priority_score REAL,
                priority_tier TEXT,
                harambe_recommendation TEXT,
                assessment_json TEXT,  -- Full JSON for detailed analysis
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (run_id) REFERENCES analysis_runs(run_id)
            )
        """)

        # Repair tracking table (for calibration)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repair_tracking (
                repair_id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_name TEXT NOT NULL,
                scraper_name TEXT NOT NULL,
                assessment_id INTEGER,
                estimated_hours REAL,
                actual_hours REAL,
                repair_date TEXT,
                repair_notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assessment_id) REFERENCES scraper_assessments(assessment_id)
            )
        """)

        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_repo_scraper
            ON scraper_assessments(repo_name, scraper_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_run_date
            ON analysis_runs(run_date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status
            ON scraper_assessments(status)
        """)

        self.conn.commit()

    def record_analysis_run(
        self,
        analysis_type: str,
        total_repos: int = 0,
        total_scrapers: int = 0,
        notes: Optional[str] = None,
    ) -> int:
        """
        Record a new analysis run.

        Args:
            analysis_type: Type of analysis ('repository' or 'ecosystem')
            total_repos: Total repositories analyzed
            total_scrapers: Total scrapers analyzed
            notes: Optional notes about this run

        Returns:
            run_id for this analysis run
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO analysis_runs (run_date, analysis_type, total_repos, total_scrapers, notes)
            VALUES (?, ?, ?, ?, ?)
        """,
            (datetime.now().isoformat(), analysis_type, total_repos, total_scrapers, notes),
        )
        self.conn.commit()
        return cursor.lastrowid

    def save_repository_assessment(self, run_id: int, repo_report: Dict[str, Any]):
        """
        Save repository-level assessment.

        Args:
            run_id: Analysis run ID
            repo_report: Repository report dictionary
        """
        cursor = self.conn.cursor()
        summary = repo_report.get("summary", {})

        cursor.execute(
            """
            INSERT INTO repository_assessments
            (run_id, repo_name, total_scrapers, functional, failed, success_rate,
             total_repair_hours, overall_health, assessment_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                run_id,
                repo_report.get("repo_name"),
                summary.get("total_scrapers", 0),
                summary.get("functional", 0),
                summary.get("failed", 0),
                summary.get("success_rate", 0.0),
                repo_report.get("effort_summary", {}).get("total_hours_estimated", 0.0),
                repo_report.get("strategic_assessment", {}).get("overall_health", "UNKNOWN"),
                json.dumps(repo_report),
            ),
        )
        self.conn.commit()

    def save_scraper_assessment(self, run_id: int, scraper: Dict[str, Any]):
        """
        Save individual scraper assessment.

        Args:
            run_id: Analysis run ID
            scraper: Scraper assessment dictionary
        """
        cursor = self.conn.cursor()

        exec_results = scraper.get("execution_results", {})
        complexity = scraper.get("complexity_assessment", {})
        repair = scraper.get("repair_estimate", {})
        priority = scraper.get("priority_assessment", {})
        harambe = scraper.get("harambe_candidacy", {})
        failure = scraper.get("failure_analysis", {})

        cursor.execute(
            """
            INSERT INTO scraper_assessments
            (run_id, repo_name, scraper_name, agency_name, status, item_count,
             execution_time_seconds, complexity_rating, lines_of_code, failure_mode,
             repair_hours, effort_rating, priority_score, priority_tier,
             harambe_recommendation, assessment_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                run_id,
                scraper.get("repo_name"),
                scraper.get("scraper_name"),
                scraper.get("agency_name"),
                exec_results.get("status"),
                exec_results.get("item_count", 0),
                exec_results.get("execution_time_seconds", 0.0),
                complexity.get("complexity_rating"),
                complexity.get("lines_of_code", 0),
                failure.get("primary_failure_mode"),
                repair.get("total_estimated_hours", 0.0),
                repair.get("effort_rating"),
                priority.get("priority_score", 0.0),
                priority.get("priority_tier"),
                harambe.get("recommendation"),
                json.dumps(scraper),
            ),
        )
        self.conn.commit()

    def record_repair(
        self,
        repo_name: str,
        scraper_name: str,
        actual_hours: float,
        repair_notes: Optional[str] = None,
    ) -> int:
        """
        Record actual repair time for estimate calibration.

        Args:
            repo_name: Repository name
            scraper_name: Scraper name
            actual_hours: Actual time spent on repair
            repair_notes: Optional notes about the repair

        Returns:
            repair_id
        """
        # Get most recent assessment for this scraper
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT assessment_id, repair_hours
            FROM scraper_assessments
            WHERE repo_name = ? AND scraper_name = ?
            ORDER BY created_at DESC
            LIMIT 1
        """,
            (repo_name, scraper_name),
        )
        row = cursor.fetchone()

        assessment_id = row["assessment_id"] if row else None
        estimated_hours = row["repair_hours"] if row else None

        cursor.execute(
            """
            INSERT INTO repair_tracking
            (repo_name, scraper_name, assessment_id, estimated_hours, actual_hours,
             repair_date, repair_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                repo_name,
                scraper_name,
                assessment_id,
                estimated_hours,
                actual_hours,
                datetime.now().isoformat(),
                repair_notes,
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_scraper_history(
        self, repo_name: str, scraper_name: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get historical assessments for a specific scraper.

        Args:
            repo_name: Repository name
            scraper_name: Scraper name
            limit: Maximum number of records to return

        Returns:
            List of historical assessments
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT sa.*, ar.run_date
            FROM scraper_assessments sa
            JOIN analysis_runs ar ON sa.run_id = ar.run_id
            WHERE sa.repo_name = ? AND sa.scraper_name = ?
            ORDER BY sa.created_at DESC
            LIMIT ?
        """,
            (repo_name, scraper_name, limit),
        )
        return [dict(row) for row in cursor.fetchall()]

    def compare_runs(self, run_id1: int, run_id2: int) -> Dict[str, Any]:
        """
        Compare two analysis runs.

        Args:
            run_id1: First run ID (typically older)
            run_id2: Second run ID (typically newer)

        Returns:
            Comparison report
        """
        cursor = self.conn.cursor()

        # Get scrapers in both runs
        cursor.execute(
            """
            SELECT
                s1.repo_name,
                s1.scraper_name,
                s1.status as old_status,
                s2.status as new_status,
                s1.priority_tier as old_priority,
                s2.priority_tier as new_priority
            FROM scraper_assessments s1
            JOIN scraper_assessments s2
                ON s1.repo_name = s2.repo_name
                AND s1.scraper_name = s2.scraper_name
            WHERE s1.run_id = ? AND s2.run_id = ?
        """,
            (run_id1, run_id2),
        )

        comparisons = [dict(row) for row in cursor.fetchall()]

        # Categorize changes
        improved = []
        degraded = []
        unchanged = []

        for comp in comparisons:
            if comp["old_status"] != "SUCCESS" and comp["new_status"] == "SUCCESS":
                improved.append(comp)
            elif comp["old_status"] == "SUCCESS" and comp["new_status"] != "SUCCESS":
                degraded.append(comp)
            else:
                unchanged.append(comp)

        return {
            "total_compared": len(comparisons),
            "improved": improved,
            "degraded": degraded,
            "unchanged_count": len(unchanged),
            "improvement_rate": len(improved) / len(comparisons) if comparisons else 0,
        }

    def get_failure_trends(self, days: int = 30) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get failure mode trends over time.

        Args:
            days: Number of days to analyze

        Returns:
            Trend data by failure mode
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT
                ar.run_date,
                sa.failure_mode,
                COUNT(*) as count
            FROM scraper_assessments sa
            JOIN analysis_runs ar ON sa.run_id = ar.run_id
            WHERE ar.run_date >= date('now', '-' || ? || ' days')
            GROUP BY ar.run_date, sa.failure_mode
            ORDER BY ar.run_date, sa.failure_mode
        """,
            (days,),
        )

        trends = {}
        for row in cursor.fetchall():
            row_dict = dict(row)
            failure_mode = row_dict["failure_mode"]
            if failure_mode not in trends:
                trends[failure_mode] = []
            trends[failure_mode].append(
                {"date": row_dict["run_date"], "count": row_dict["count"]}
            )

        return trends

    def get_estimate_accuracy(self) -> Dict[str, Any]:
        """
        Analyze accuracy of repair time estimates.

        Returns:
            Accuracy metrics
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT
                estimated_hours,
                actual_hours,
                (actual_hours - estimated_hours) as delta,
                ABS(actual_hours - estimated_hours) / estimated_hours as error_rate
            FROM repair_tracking
            WHERE estimated_hours IS NOT NULL AND actual_hours IS NOT NULL
        """
        )

        repairs = [dict(row) for row in cursor.fetchall()]

        if not repairs:
            return {"total_repairs": 0, "message": "No repair data available"}

        avg_error = sum(r["error_rate"] for r in repairs) / len(repairs)
        over_estimated = sum(1 for r in repairs if r["delta"] < 0)
        under_estimated = sum(1 for r in repairs if r["delta"] > 0)

        return {
            "total_repairs": len(repairs),
            "average_error_rate": round(avg_error, 2),
            "over_estimated_count": over_estimated,
            "under_estimated_count": under_estimated,
            "repairs": repairs,
        }

    def get_summary_stats(self, run_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get summary statistics for a run or all runs.

        Args:
            run_id: Specific run ID, or None for all runs

        Returns:
            Summary statistics
        """
        cursor = self.conn.cursor()

        if run_id:
            where_clause = "WHERE run_id = ?"
            params = (run_id,)
        else:
            where_clause = ""
            params = ()

        cursor.execute(
            f"""
            SELECT
                COUNT(DISTINCT repo_name) as total_repos,
                COUNT(*) as total_scrapers,
                SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as functional,
                SUM(CASE WHEN status != 'SUCCESS' THEN 1 ELSE 0 END) as failed,
                AVG(CASE WHEN status = 'SUCCESS' THEN 1.0 ELSE 0.0 END) as success_rate,
                SUM(repair_hours) as total_repair_hours
            FROM scraper_assessments
            {where_clause}
        """,
            params,
        )

        return dict(cursor.fetchone())

    def export_to_csv(self, output_path: str, run_id: Optional[int] = None):
        """
        Export scraper assessments to CSV.

        Args:
            output_path: Path for CSV file
            run_id: Specific run ID, or None for most recent

        Returns:
            Path to created CSV file
        """
        import csv

        cursor = self.conn.cursor()

        if run_id is None:
            # Get most recent run
            cursor.execute("SELECT MAX(run_id) as max_id FROM analysis_runs")
            run_id = cursor.fetchone()["max_id"]

        cursor.execute(
            """
            SELECT
                repo_name, scraper_name, agency_name, status, item_count,
                execution_time_seconds, complexity_rating, lines_of_code,
                failure_mode, repair_hours, effort_rating, priority_score,
                priority_tier, harambe_recommendation
            FROM scraper_assessments
            WHERE run_id = ?
            ORDER BY repo_name, scraper_name
        """,
            (run_id,),
        )

        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "repo_name",
                    "scraper_name",
                    "agency_name",
                    "status",
                    "item_count",
                    "execution_time_seconds",
                    "complexity_rating",
                    "lines_of_code",
                    "failure_mode",
                    "repair_hours",
                    "effort_rating",
                    "priority_score",
                    "priority_tier",
                    "harambe_recommendation",
                ],
            )
            writer.writeheader()
            for row in cursor.fetchall():
                writer.writerow(dict(row))

        logger.info(f"Exported to CSV: {output_path}")
        return output_path

    def close(self):
        """Close database connection."""
        self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
