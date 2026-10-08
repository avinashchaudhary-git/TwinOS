from unittest.mock import MagicMock, patch

import httpx

from app.integrations.github import GitHubConnector


def test_tc02_github_rate_limit_retry_no_data_lost():
    """TC-02: GitHub rate-limit error gives retry with backoff, no data lost."""
    connector = GitHubConnector(credentials={"token": "fake-pat-token"})

    # Setup mock HTTP responses:
    # Call 1: HTTP 429 (rate limited) with Retry-After header
    # Call 2: HTTP 200 (success) returning repos
    # Call 3: HTTP 200 returning commits
    resp_429 = httpx.Response(status_code=429, headers={"Retry-After": "1"}, request=MagicMock())
    resp_repos_200 = httpx.Response(
        status_code=200,
        json=[
            {
                "id": 12345,
                "name": "core-repo",
                "full_name": "acme/core-repo",
                "html_url": "https://github.com/acme/core-repo",
            }
        ],
        request=MagicMock(),
    )
    resp_commits_200 = httpx.Response(
        status_code=200,
        json=[
            {
                "sha": "testsha123456",
                "commit": {
                    "message": "feat: test rate limit",
                    "author": {"email": "dev@acme.org", "date": "2026-10-06T12:00:00Z"},
                },
                "stats": {"additions": 10, "deletions": 2},
            }
        ],
        request=MagicMock(),
    )

    with patch.object(
        httpx.Client, "get", side_effect=[resp_429, resp_repos_200, resp_commits_200]
    ):
        records = connector.fetch_since()

    # Verify retry worked and all records were pulled without data loss
    assert len(records) >= 2, f"Expected repo and commit records after retry, got {len(records)}"
    repo_rec = next(r for r in records if r.entity_type == "repository")
    commit_rec = next(r for r in records if r.entity_type == "commit")

    assert repo_rec.external_id == "12345"
    assert commit_rec.external_id == "testsha123456"
