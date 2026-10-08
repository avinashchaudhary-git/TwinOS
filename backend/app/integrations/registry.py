from typing import Any

from app.integrations.base import BaseConnector
from app.integrations.gcalendar import GoogleCalendarConnector
from app.integrations.github import GitHubConnector
from app.integrations.gmail import GmailConnector
from app.integrations.mock.mock_connector import MockConnector
from app.integrations.trello import TrelloConnector

CONNECTOR_REGISTRY: dict[str, type[BaseConnector]] = {
    "github": GitHubConnector,
    "trello": TrelloConnector,
    "gmail": GmailConnector,
    "gcalendar": GoogleCalendarConnector,
}


def get_connector(
    platform: str, credentials: dict[str, Any] | None = None, use_mock: bool = False
) -> BaseConnector:
    """Returns an initialized connector instance for the given platform."""
    if use_mock:
        return MockConnector(platform=platform, credentials=credentials)

    connector_cls = CONNECTOR_REGISTRY.get(platform)
    if not connector_cls:
        raise ValueError(f"Unsupported platform: {platform}")

    return connector_cls(credentials=credentials)
