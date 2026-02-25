"""
GitHub API client for city-scrapers repository analysis.

Handles repository discovery, file access, and metadata retrieval
without requiring local clones.
"""

import base64
import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)


class GitHubClient:
    """Client for interacting with GitHub API for city-scrapers repositories."""

    BASE_URL = "https://api.github.com"
    ORG_NAME = "City-Bureau"
    REPO_PATTERN = r"city-scrapers-.*"

    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub client.

        Args:
            token: GitHub personal access token. If None, uses GITHUB_TOKEN env var.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.session = requests.Session()

        if self.token:
            self.session.headers.update({"Authorization": f"token {self.token}"})
        else:
            logger.warning(
                "No GitHub token provided. API rate limits will be restrictive."
            )

        self.session.headers.update(
            {"Accept": "application/vnd.github.v3+json", "User-Agent": "city-scrapers-analyzer"}
        )

    def list_city_scrapers_repos(self) -> List[Dict[str, Any]]:
        """
        List all city-scrapers-* repositories in the City-Bureau organization.

        Returns:
            List of repository metadata dictionaries.
        """
        logger.info(f"Discovering city-scrapers repositories in {self.ORG_NAME}")

        repos = []
        page = 1
        per_page = 100

        while True:
            url = f"{self.BASE_URL}/orgs/{self.ORG_NAME}/repos"
            params = {"type": "public", "per_page": per_page, "page": page}

            response = self.session.get(url, params=params)
            response.raise_for_status()

            page_repos = response.json()
            if not page_repos:
                break

            # Filter for city-scrapers pattern
            pattern = re.compile(self.REPO_PATTERN)
            matching = [r for r in page_repos if pattern.match(r["name"])]
            repos.extend(matching)

            logger.debug(f"Page {page}: Found {len(matching)} matching repos")

            # Check if there are more pages
            if len(page_repos) < per_page:
                break

            page += 1

        logger.info(f"Found {len(repos)} city-scrapers repositories")
        return repos

    def get_repository_info(self, repo_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a repository.

        Args:
            repo_name: Name of the repository (e.g., 'city-scrapers-atl')

        Returns:
            Repository metadata including last commit, default branch, etc.
        """
        url = f"{self.BASE_URL}/repos/{self.ORG_NAME}/{repo_name}"
        response = self.session.get(url)
        response.raise_for_status()

        repo_data = response.json()

        # Get latest workflow run
        workflow_run = self.get_latest_workflow_run(repo_name)

        return {
            "repo_name": repo_name,
            "full_name": repo_data["full_name"],
            "description": repo_data.get("description", ""),
            "default_branch": repo_data["default_branch"],
            "last_commit": repo_data["pushed_at"],
            "last_workflow_run": workflow_run.get("created_at") if workflow_run else None,
            "workflow_status": workflow_run.get("conclusion") if workflow_run else None,
            "is_archived": repo_data.get("archived", False),
            "is_disabled": repo_data.get("disabled", False),
            "clone_url": repo_data["clone_url"],
            "html_url": repo_data["html_url"],
        }

    def get_latest_workflow_run(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest workflow run for a repository.

        Args:
            repo_name: Name of the repository

        Returns:
            Workflow run metadata or None if no runs found
        """
        url = f"{self.BASE_URL}/repos/{self.ORG_NAME}/{repo_name}/actions/runs"
        params = {"per_page": 1}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            runs = response.json().get("workflow_runs", [])
            return runs[0] if runs else None
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not fetch workflow runs for {repo_name}: {e}")
            return None

    def list_spider_files(self, repo_name: str, branch: str = "main") -> List[Dict[str, Any]]:
        """
        List all spider files in a repository's spiders directory.

        Args:
            repo_name: Name of the repository
            branch: Branch name (default: 'main')

        Returns:
            List of spider file metadata
        """
        path = "city_scrapers/spiders"
        url = f"{self.BASE_URL}/repos/{self.ORG_NAME}/{repo_name}/contents/{path}"
        params = {"ref": branch}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            contents = response.json()

            # Filter for Python files (excluding __init__.py)
            spider_files = [
                f
                for f in contents
                if f["type"] == "file"
                and f["name"].endswith(".py")
                and f["name"] != "__init__.py"
            ]

            logger.info(f"Found {len(spider_files)} spider files in {repo_name}")
            return spider_files

        except requests.exceptions.RequestException as e:
            logger.error(f"Error listing spider files in {repo_name}: {e}")
            return []

    def get_file_content(
        self, repo_name: str, file_path: str, branch: str = "main"
    ) -> Optional[str]:
        """
        Get the content of a file from a repository.

        Args:
            repo_name: Name of the repository
            file_path: Path to the file within the repo
            branch: Branch name (default: 'main')

        Returns:
            File content as string, or None if error
        """
        url = f"{self.BASE_URL}/repos/{self.ORG_NAME}/{repo_name}/contents/{file_path}"
        params = {"ref": branch}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            content_data = response.json()

            # Decode base64 content
            content_b64 = content_data["content"]
            content_bytes = base64.b64decode(content_b64)
            return content_bytes.decode("utf-8")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {file_path} from {repo_name}: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Error decoding content from {file_path}: {e}")
            return None

    def get_file_last_modified(
        self, repo_name: str, file_path: str, branch: str = "main"
    ) -> Optional[str]:
        """
        Get the last modified date of a file.

        Args:
            repo_name: Name of the repository
            file_path: Path to the file within the repo
            branch: Branch name (default: 'main')

        Returns:
            ISO timestamp of last commit affecting this file
        """
        url = f"{self.BASE_URL}/repos/{self.ORG_NAME}/{repo_name}/commits"
        params = {"path": file_path, "per_page": 1, "sha": branch}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            commits = response.json()

            if commits:
                return commits[0]["commit"]["committer"]["date"]
            return None

        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not fetch last modified for {file_path}: {e}")
            return None

    def get_spider_metadata(
        self, repo_name: str, spider_file: Dict[str, Any], branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Extract metadata from a spider file.

        Args:
            repo_name: Name of the repository
            spider_file: Spider file metadata from list_spider_files
            branch: Branch name (default: 'main')

        Returns:
            Spider metadata including name, agency, etc.
        """
        file_path = spider_file["path"]
        content = self.get_file_content(repo_name, file_path, branch)

        metadata = {
            "file_name": spider_file["name"],
            "file_path": file_path,
            "file_size": spider_file["size"],
            "spider_name": None,
            "agency": None,
            "start_urls": [],
            "timezone": None,
            "uses_mixins": [],
            "lines_of_code": 0,
            "last_modified": self.get_file_last_modified(repo_name, file_path, branch),
        }

        if not content:
            return metadata

        lines = content.split("\n")
        metadata["lines_of_code"] = len([l for l in lines if l.strip() and not l.strip().startswith("#")])

        # Extract spider class attributes using regex
        for line in lines:
            # Spider name
            if match := re.search(r'name\s*=\s*["\']([^"\']+)["\']', line):
                metadata["spider_name"] = match.group(1)

            # Agency name
            if match := re.search(r'agency\s*=\s*["\']([^"\']+)["\']', line):
                metadata["agency"] = match.group(1)

            # Timezone
            if match := re.search(r'timezone\s*=\s*["\']([^"\']+)["\']', line):
                metadata["timezone"] = match.group(1)

            # Start URLs (simplified)
            if match := re.search(r'start_urls\s*=\s*\[(.*?)\]', line):
                urls = re.findall(r'["\']([^"\']+)["\']', match.group(1))
                metadata["start_urls"].extend(urls)

        # Detect mixins from class definition
        class_def_pattern = r'class\s+\w+\((.*?)\):'
        for line in lines:
            if match := re.search(class_def_pattern, line):
                bases = match.group(1).split(',')
                mixins = [b.strip() for b in bases if 'Mixin' in b or 'mixin' in b.lower()]
                metadata["uses_mixins"].extend(mixins)

        return metadata

    def check_rate_limit(self) -> Dict[str, Any]:
        """
        Check current GitHub API rate limit status.

        Returns:
            Rate limit information
        """
        url = f"{self.BASE_URL}/rate_limit"
        response = self.session.get(url)
        response.raise_for_status()

        data = response.json()
        core_limit = data["resources"]["core"]

        return {
            "limit": core_limit["limit"],
            "remaining": core_limit["remaining"],
            "reset_at": datetime.fromtimestamp(core_limit["reset"]).isoformat(),
            "used": core_limit["limit"] - core_limit["remaining"],
        }
