from datetime import UTC, datetime
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import logger
from app.integrations.base import BaseConnector, NormalizedRecord
from app.integrations.mock.mock_connector import MockConnector


class TrelloConnector(BaseConnector):
    """Trello platform connector mapping boards to Projects and cards to Tasks."""

    BASE_URL = "https://api.trello.com/1"

    def __init__(self, credentials: dict[str, Any] | None = None):
        super().__init__(credentials)
        self.api_key = (credentials or {}).get("api_key") or settings.TRELLO_API_KEY
        self.token = (credentials or {}).get("token") or settings.TRELLO_TOKEN
        self.mock_connector = MockConnector("trello", credentials)

    @property
    def platform(self) -> str:
        return "trello"

    def authenticate(self) -> bool:
        if not (self.api_key and self.token):
            return True  # Mock mode
        try:
            with httpx.Client(timeout=10) as client:
                res = client.get(
                    f"{self.BASE_URL}/members/me", params={"key": self.api_key, "token": self.token}
                )
                return res.status_code == 200
        except Exception:
            return False

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        reraise=False,
    )
    def fetch_since(self, cursor: datetime | None = None) -> list[NormalizedRecord]:
        if not (self.api_key and self.token):
            logger.info("Trello credentials not configured. Using MockConnector for Trello.")
            return self.mock_connector.fetch_since(cursor)

        records: list[NormalizedRecord] = []
        try:
            auth_params = {"key": self.api_key, "token": self.token}
            with httpx.Client(timeout=15) as client:
                # 1. Fetch user boards
                boards_res = client.get(f"{self.BASE_URL}/members/me/boards", params=auth_params)
                boards_res.raise_for_status()
                boards = boards_res.json()

                for b in boards:
                    records.append(
                        NormalizedRecord(
                            platform="trello",
                            entity_type="project",
                            external_id=b["id"],
                            payload={
                                "id": f"proj-{b['id']}",
                                "name": b["name"],
                                "status": "active" if not b.get("closed") else "done",
                                "start_date": datetime.now(UTC).isoformat(),
                                "target_end_date": None,
                            },
                            occurred_at=datetime.now(UTC),
                        )
                    )

                    # 2. Fetch cards per board
                    cards_res = client.get(
                        f"{self.BASE_URL}/boards/{b['id']}/cards", params=auth_params
                    )
                    cards_res.raise_for_status()
                    cards = cards_res.json()

                    for c in cards:
                        due = c.get("due")
                        status = (
                            "done"
                            if c.get("dueComplete")
                            else ("blocked" if "block" in c["name"].lower() else "in_progress")
                        )
                        records.append(
                            NormalizedRecord(
                                platform="trello",
                                entity_type="task",
                                external_id=c["id"],
                                payload={
                                    "id": f"task-{c['id']}",
                                    "project_id": f"proj-{b['id']}",
                                    "title": c["name"],
                                    "description": c.get("desc", ""),
                                    "status": status,
                                    "due_date": due,
                                    "priority": "high"
                                    if "urgent" in c["name"].lower()
                                    else "medium",
                                    "external_id": c["id"],
                                },
                                occurred_at=datetime.now(UTC),
                            )
                        )

            return records
        except Exception as e:
            logger.error(f"Trello real sync failed ({e}). Falling back to mock connector.")
            return self.mock_connector.fetch_since(cursor)
