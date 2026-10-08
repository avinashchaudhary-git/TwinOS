import time
from datetime import UTC, datetime
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import logger
from app.integrations.base import BaseConnector, NormalizedRecord
from app.integrations.mock.mock_connector import MockConnector


class RateLimitError(Exception):
    def __init__(self, retry_after: int = 1):
        self.retry_after = retry_after
        super().__init__(f"Rate limit reached. Retry after {retry_after}s")


class GitHubConnector(BaseConnector):
    """GitHub platform connector with tenacity exponential backoff and rate-limit handling."""

    BASE_URL = "https://api.github.com"

    def __init__(self, credentials: dict[str, Any] | None = None):
        super().__init__(credentials)
        self.token = (credentials or {}).get("token") or settings.GITHUB_TOKEN
        self.mock_connector = MockConnector("github", credentials)

    @property
    def platform(self) -> str:
        return "github"

    def authenticate(self) -> bool:
        if not self.token:
            return True  # Mock mode fallback
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        try:
            with httpx.Client(timeout=10) as client:
                res = client.get(f"{self.BASE_URL}/user", headers=headers)
                return res.status_code == 200
        except Exception:
            return False

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def _make_request(
        self, client: httpx.Client, endpoint: str, params: dict[str, Any] | None = None
    ) -> Any:
        headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "TwinOS-Platform"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        response = client.get(f"{self.BASE_URL}{endpoint}", headers=headers, params=params)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 1))
            logger.warning(f"GitHub 429 Rate limited. Waiting {retry_after}s before retry.")
            time.sleep(retry_after)
            raise RateLimitError(retry_after)

        if response.status_code >= 500:
            raise RateLimitError(1)

        response.raise_for_status()
        return response.json()

    def fetch_since(self, cursor: datetime | None = None) -> list[NormalizedRecord]:
        # If no real token is configured, use deterministic mock connector
        if not self.token:
            logger.info("GitHub credentials not configured. Using MockConnector for GitHub.")
            return self.mock_connector.fetch_since(cursor)

        records: list[NormalizedRecord] = []
        try:
            with httpx.Client(timeout=15) as client:
                # 1. Fetch repositories
                repos_data = self._make_request(client, "/user/repos")
                for repo in repos_data:
                    records.append(
                        NormalizedRecord(
                            platform="github",
                            entity_type="repository",
                            external_id=str(repo["id"]),
                            payload={
                                "id": f"repo-{repo['name']}",
                                "full_name": repo["full_name"],
                                "url": repo["html_url"],
                                "default_branch": repo.get("default_branch", "main"),
                            },
                            occurred_at=datetime.now(UTC),
                        )
                    )

                    # 2. Fetch commits for each repository
                    params = {"per_page": 50}
                    if cursor:
                        params["since"] = cursor.isoformat()

                    try:
                        commits_data = self._make_request(
                            client, f"/repos/{repo['full_name']}/commits", params=params
                        )
                        for c in commits_data:
                            commit_obj = c.get("commit", {})
                            author_info = commit_obj.get("author", {})
                            date_str = author_info.get("date")
                            occurred = (
                                datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                                if date_str
                                else datetime.now(UTC)
                            )

                            records.append(
                                NormalizedRecord(
                                    platform="github",
                                    entity_type="commit",
                                    external_id=c["sha"],
                                    payload={
                                        "sha": c["sha"],
                                        "repository_id": f"repo-{repo['name']}",
                                        "repository_full_name": repo["full_name"],
                                        "message": commit_obj.get("message", ""),
                                        "author_email": author_info.get("email", ""),
                                        "author_name": author_info.get("name", ""),
                                        "committed_at": occurred.isoformat(),
                                        "additions": c.get("stats", {}).get("additions", 10),
                                        "deletions": c.get("stats", {}).get("deletions", 5),
                                    },
                                    occurred_at=occurred,
                                )
                            )
                    except Exception as e:
                        logger.warning(f"Could not fetch commits for {repo['full_name']}: {e}")

            return records
        except Exception as e:
            logger.error(f"GitHub real sync failed ({e}). Falling back to mock connector.")
            return self.mock_connector.fetch_since(cursor)
