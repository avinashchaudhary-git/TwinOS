import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.logging import logger
from app.integrations.base import BaseConnector, NormalizedRecord

FIXTURES_PATH = Path(__file__).resolve().parent / "fixtures"


class MockConnector(BaseConnector):
    """Mock platform connector providing realistic fixture data for zero-credential demos & tests."""

    def __init__(self, platform: str, credentials: dict[str, Any] | None = None):
        super().__init__(credentials)
        self._platform = platform
        self.rate_limit_counter = 0

    @property
    def platform(self) -> str:
        return self._platform

    def authenticate(self) -> bool:
        return True

    def fetch_since(self, cursor: datetime | None = None) -> list[NormalizedRecord]:
        records: list[NormalizedRecord] = []

        # Load core fixtures
        with open(FIXTURES_PATH / "org_dataset.json", "r") as f:
            org_data = json.load(f)

        if self._platform == "github":
            # Repositories
            for repo in org_data.get("repositories", []):
                records.append(
                    NormalizedRecord(
                        platform="github",
                        entity_type="repository",
                        external_id=repo["id"],
                        payload=repo,
                        occurred_at=datetime.now(UTC),
                    )
                )
            # Commits
            commits_file = FIXTURES_PATH / "commits.json"
            if commits_file.exists():
                with open(commits_file, "r") as f:
                    commits = json.load(f)
                for c in commits:
                    records.append(
                        NormalizedRecord(
                            platform="github",
                            entity_type="commit",
                            external_id=c["sha"],
                            payload=c,
                            occurred_at=datetime.fromisoformat(
                                c["committed_at"].replace("Z", "+00:00")
                            ),
                        )
                    )

        elif self._platform == "trello":
            # Projects (boards)
            for proj in org_data.get("projects", []):
                records.append(
                    NormalizedRecord(
                        platform="trello",
                        entity_type="project",
                        external_id=proj["id"],
                        payload=proj,
                        occurred_at=datetime.now(UTC),
                    )
                )
            # Tasks (cards)
            tasks_file = FIXTURES_PATH / "tasks.json"
            if tasks_file.exists():
                with open(tasks_file, "r") as f:
                    tasks = json.load(f)
                for t in tasks:
                    created_at = datetime.fromisoformat(t["created_at"].replace("Z", "+00:00"))
                    records.append(
                        NormalizedRecord(
                            platform="trello",
                            entity_type="task",
                            external_id=t["id"],
                            payload=t,
                            occurred_at=created_at,
                        )
                    )

        elif self._platform == "gmail":
            emails_file = FIXTURES_PATH / "emails.json"
            if emails_file.exists():
                with open(emails_file, "r") as f:
                    emails = json.load(f)
                for em in emails:
                    records.append(
                        NormalizedRecord(
                            platform="gmail",
                            entity_type="email",
                            external_id=em["id"],
                            payload=em,
                            occurred_at=datetime.fromisoformat(
                                em["sent_at"].replace("Z", "+00:00")
                            ),
                        )
                    )

        elif self._platform == "gcalendar":
            events_file = FIXTURES_PATH / "events.json"
            if events_file.exists():
                with open(events_file, "r") as f:
                    events = json.load(f)
                for ev in events:
                    records.append(
                        NormalizedRecord(
                            platform="gcalendar",
                            entity_type="event",
                            external_id=ev["id"],
                            payload=ev,
                            occurred_at=datetime.fromisoformat(
                                ev["start_at"].replace("Z", "+00:00")
                            ),
                        )
                    )

        # Apply cursor filtering if provided
        if cursor:
            # Ensure cursor has timezone info
            if cursor.tzinfo is None:
                cursor = cursor.replace(tzinfo=UTC)
            records = [r for r in records if r.occurred_at >= cursor]

        logger.info(f"MockConnector[{self._platform}]: produced {len(records)} normalized records.")
        return records
