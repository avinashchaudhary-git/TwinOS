from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.logging import logger
from app.integrations.base import BaseConnector, NormalizedRecord
from app.integrations.mock.mock_connector import MockConnector


class GmailConnector(BaseConnector):
    """Gmail connector adhering strictly to least-privilege (metadata & snippet only)."""

    BASE_URL = "https://gmail.googleapis.com/gmail/v1/users/me"

    def __init__(self, credentials: dict[str, Any] | None = None):
        super().__init__(credentials)
        self.access_token = (credentials or {}).get("access_token")
        self.mock_connector = MockConnector("gmail", credentials)

    @property
    def platform(self) -> str:
        return "gmail"

    def authenticate(self) -> bool:
        return True

    def fetch_since(self, cursor: datetime | None = None) -> list[NormalizedRecord]:
        if not self.access_token:
            logger.info("Gmail access token not provided. Using MockConnector for Gmail.")
            return self.mock_connector.fetch_since(cursor)

        records: list[NormalizedRecord] = []
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            with httpx.Client(timeout=15) as client:
                query = "newer_than:14d"
                res = client.get(
                    f"{self.BASE_URL}/messages",
                    headers=headers,
                    params={"q": query, "maxResults": 50},
                )
                res.raise_for_status()
                messages = res.json().get("messages", [])

                for m in messages:
                    # Fetch metadata format only (no full body download - least privilege)
                    detail = client.get(
                        f"{self.BASE_URL}/messages/{m['id']}",
                        headers=headers,
                        params={
                            "format": "metadata",
                            "metadataHeaders": ["Subject", "From", "To", "Date"],
                        },
                    ).json()

                    payload_headers = {
                        h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])
                    }
                    subject = payload_headers.get("Subject", "No Subject")
                    sender = payload_headers.get("From", "")
                    snippet = detail.get("snippet", "")

                    records.append(
                        NormalizedRecord(
                            platform="gmail",
                            entity_type="email",
                            external_id=m["id"],
                            payload={
                                "id": f"email-{m['id']}",
                                "thread_id": m.get("threadId"),
                                "subject": subject,
                                "sender_email": sender,
                                "snippet": snippet,
                                "sent_at": datetime.now(UTC).isoformat(),
                            },
                            occurred_at=datetime.now(UTC),
                        )
                    )

            return records
        except Exception as e:
            logger.error(f"Gmail sync failed ({e}). Falling back to mock connector.")
            return self.mock_connector.fetch_since(cursor)
