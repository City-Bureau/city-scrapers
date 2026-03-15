"""
Scraper execution engine with timeout handling and output capture.

Executes Scrapy spiders in isolated processes with comprehensive logging
and error handling.
"""

import json
import logging
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ScraperExecutor:
    """Execute Scrapy spiders and capture results."""

    def __init__(
        self,
        timeout_seconds: int = 900,  # 15 minutes default
        max_log_size: int = 50000,  # 50KB max log capture
    ):
        """
        Initialize scraper executor.

        Args:
            timeout_seconds: Maximum execution time per scraper
            max_log_size: Maximum log size to capture (characters)
        """
        self.timeout_seconds = timeout_seconds
        self.max_log_size = max_log_size

    def execute_scraper(
        self,
        repo_path: str,
        spider_name: str,
        output_format: str = "json",
    ) -> Dict[str, Any]:
        """
        Execute a single scraper and capture results.

        Args:
            repo_path: Path to cloned repository
            spider_name: Name of the spider to execute
            output_format: Output format (json/jl/csv)

        Returns:
            Execution results including status, output, and logs
        """
        logger.info(f"Executing scraper: {spider_name}")

        # Create temporary output file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=f".{output_format}", delete=False
        ) as tmp_output:
            output_file = tmp_output.name

        # Create temporary log file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as tmp_log:
            log_file = tmp_log.name

        try:
            # Build scrapy command
            cmd = [
                "scrapy",
                "crawl",
                spider_name,
                "-s",
                "LOG_LEVEL=DEBUG",
                "-o",
                output_file,
            ]

            # Execute with timeout
            start_time = time.time()

            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )

            execution_time = time.time() - start_time

            # Read output file
            items = self._read_output_file(output_file, output_format)

            # Capture logs (stdout + stderr)
            log_content = result.stdout + "\n" + result.stderr
            if len(log_content) > self.max_log_size:
                log_content = log_content[: self.max_log_size] + "\n... [truncated]"

            # Parse Scrapy statistics
            stats = self._parse_scrapy_stats(log_content)

            return {
                "status": "completed",
                "exit_code": result.returncode,
                "execution_time_seconds": round(execution_time, 2),
                "item_count": len(items) if items else 0,
                "items": items,
                "log_content": log_content,
                "stats": stats,
                "command": " ".join(cmd),
            }

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            logger.warning(f"Scraper {spider_name} timed out after {execution_time}s")

            return {
                "status": "timeout",
                "exit_code": -1,
                "execution_time_seconds": round(execution_time, 2),
                "item_count": 0,
                "items": None,
                "log_content": f"Execution timed out after {self.timeout_seconds} seconds",
                "stats": {},
                "command": " ".join(cmd),
            }

        except Exception as e:
            logger.error(f"Error executing {spider_name}: {e}")

            return {
                "status": "error",
                "exit_code": -1,
                "execution_time_seconds": 0,
                "item_count": 0,
                "items": None,
                "log_content": f"Execution error: {str(e)}",
                "stats": {},
                "command": " ".join(cmd) if "cmd" in locals() else "N/A",
            }

        finally:
            # Cleanup temporary files
            for filepath in [output_file, log_file]:
                try:
                    if os.path.exists(filepath):
                        os.unlink(filepath)
                except Exception as e:
                    logger.warning(f"Could not delete temp file {filepath}: {e}")

    def _read_output_file(
        self, filepath: str, format_type: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Read and parse scraper output file."""
        try:
            if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                return []

            with open(filepath, "r", encoding="utf-8") as f:
                if format_type == "json":
                    return json.load(f)
                elif format_type == "jl":  # JSON Lines
                    return [json.loads(line) for line in f if line.strip()]
                else:
                    # For other formats, just return raw content
                    return [{"content": f.read()}]

        except json.JSONDecodeError as e:
            logger.warning(f"Could not parse output file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading output file: {e}")
            return None

    def _parse_scrapy_stats(self, log_content: str) -> Dict[str, Any]:
        """Extract Scrapy statistics from log output."""
        stats = {}

        # Common Scrapy stat patterns
        patterns = {
            "item_scraped_count": r"'item_scraped_count':\s*(\d+)",
            "response_received_count": r"'response_received_count':\s*(\d+)",
            "request_bytes": r"'request_bytes':\s*(\d+)",
            "response_bytes": r"'response_bytes':\s*(\d+)",
            "finish_reason": r"'finish_reason':\s*'([^']+)'",
            "downloader/exception_count": r"'downloader/exception_count':\s*(\d+)",
            "downloader/response_status_count/200": r"'downloader/response_status_count/200':\s*(\d+)",
            "downloader/response_status_count/404": r"'downloader/response_status_count/404':\s*(\d+)",
        }

        import re

        for key, pattern in patterns.items():
            match = re.search(pattern, log_content)
            if match:
                value = match.group(1)
                # Try to convert to int if possible
                try:
                    stats[key] = int(value)
                except ValueError:
                    stats[key] = value

        return stats

    def setup_repository(self, repo_url: str, target_dir: Optional[str] = None) -> str:
        """
        Clone repository and install dependencies.

        Args:
            repo_url: GitHub repository URL
            target_dir: Target directory for clone (optional)

        Returns:
            Path to cloned repository
        """
        if target_dir is None:
            target_dir = tempfile.mkdtemp(prefix="city-scrapers-")

        logger.info(f"Cloning {repo_url} to {target_dir}")

        try:
            # Clone repository
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, target_dir],
                check=True,
                capture_output=True,
            )

            # Install dependencies with pipenv
            logger.info("Installing dependencies...")
            subprocess.run(
                ["pipenv", "install", "--skip-lock"],
                cwd=target_dir,
                check=True,
                capture_output=True,
                timeout=300,  # 5 minute timeout for install
            )

            return target_dir

        except subprocess.CalledProcessError as e:
            logger.error(f"Error setting up repository: {e}")
            raise
        except subprocess.TimeoutExpired:
            logger.error("Dependency installation timed out")
            raise

    def cleanup_repository(self, repo_path: str):
        """Remove cloned repository."""
        import shutil

        try:
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
                logger.info(f"Cleaned up {repo_path}")
        except Exception as e:
            logger.warning(f"Could not clean up {repo_path}: {e}")

    def list_available_spiders(self, repo_path: str) -> List[str]:
        """
        List all available spiders in a repository.

        Args:
            repo_path: Path to repository

        Returns:
            List of spider names
        """
        try:
            result = subprocess.run(
                ["scrapy", "list"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                spiders = [
                    line.strip() for line in result.stdout.split("\n") if line.strip()
                ]
                logger.info(f"Found {len(spiders)} spiders in repository")
                return spiders
            else:
                logger.error(f"Error listing spiders: {result.stderr}")
                return []

        except Exception as e:
            logger.error(f"Error listing spiders: {e}")
            return []

    def validate_spider_output(
        self, repo_path: str, spider_name: str
    ) -> Dict[str, Any]:
        """
        Validate spider output using Scrapy's validate command.

        Args:
            repo_path: Path to repository
            spider_name: Name of spider to validate

        Returns:
            Validation results
        """
        try:
            result = subprocess.run(
                ["scrapy", "validate", spider_name],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            return {
                "is_valid": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
            }

        except Exception as e:
            logger.error(f"Error validating spider: {e}")
            return {"is_valid": False, "output": "", "errors": str(e)}


class RemoteExecutor(ScraperExecutor):
    """
    Execute scrapers without local cloning using GitHub API.

    This executor downloads only the necessary files via GitHub API
    and constructs a minimal execution environment.
    """

    def __init__(self, github_client, *args, **kwargs):
        """
        Initialize remote executor.

        Args:
            github_client: Initialized GitHubClient instance
        """
        super().__init__(*args, **kwargs)
        self.github = github_client

    def execute_remote_scraper(
        self, repo_name: str, spider_name: str
    ) -> Dict[str, Any]:
        """
        Execute scraper remotely without full clone.

        Note: This is a simplified approach that may not work for all scrapers.
        For production use, consider using the full clone approach.

        Args:
            repo_name: Repository name
            spider_name: Spider name

        Returns:
            Execution results
        """
        logger.warning(
            "Remote execution is experimental and may not work for complex scrapers"
        )

        # For now, recommend using full clone approach
        return {
            "status": "not_implemented",
            "exit_code": -1,
            "execution_time_seconds": 0,
            "item_count": 0,
            "items": None,
            "log_content": "Remote execution not fully implemented. Use local clone approach.",
            "stats": {},
            "command": "N/A",
        }
