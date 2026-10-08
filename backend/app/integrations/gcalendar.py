from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.logging import logger
from app.integrations.base import BaseConnector, NormalizedRecord
from app.integrations.mock.mock_connector import MockConnector


class GoogleCalendarConnector(BaseConnector):
    """Google Calendar connector extracting events, times, attendees, and milestone flags."""

    BASE_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

    def __init__(self, credentials: dict[str, Any] | None = None):
        super().__init__(credentials)
        self.access_token = (credentials or {}).get("access_token")
        self.mock_connector = MockConnector("gcalendar", credentials)

    @property
    def platform(self) -> str:
        return "gcalendar"

    def authenticate(self) -> bool:
        return True

    def fetch_since(self, cursor: datetime | None = None) -> list[NormalizedRecord]:
        if not self.access_token:
            logger.info(
                "Google Calendar access token not provided. Using MockConnector for Calendar."
            )
            return self.mock_connector.fetch_since(cursor)

        records: list[NormalizedRecord] = []
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            params = {
                "maxResults": 100,
                "singleEvents": "true",
                "orderBy": "startTime",
            }
            if cursor:
                params["timeMin"] = cursor.isoformat()

            with httpx.Client(timeout=15) as client:
                res = client.get(self.BASE_URL, headers=headers, params=params)
                res.raise_for_status()
                items = res.json().get("items", [])

                for item in items:
                    start_dt = item.get("start", {}).get("dateTime") or item.get("start", {}).get(
                        "date"
                    )
                    end_dt = item.get("end", {}).get("dateTime") or item.get("end", {}).get("date")
                    summary = item.get("summary", "Untitled Meeting")
                    attendees = [
                        a.get("email") for a in item.get("attendees", []) if a.get("email")
                    ]

                    records.append(
                        NormalizedRecord(
                            platform="gcalendar",
                            entity_type="event",
                            external_id=item["id"],
                            payload={
                                "id": f"event-{item['id']}",
                                "title": summary,
                                "start_at": start_dt,
                                "end_at": end_dt,
                                "attendees": attendees,
                                "is_milestone": "milestone" in summary.lower(),
                                "location": item.get("location", "Google Meet"),
                            },
                            occurred_at=datetime.now(UTC),
                        )
                    )

            return records
        except Exception as e:
            logger.error(f"Google Calendar sync failed ({e}). Falling back to mock connector.")
            return self.mock_connector.fetch_since(cursor)
