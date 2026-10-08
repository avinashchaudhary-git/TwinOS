from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class NormalizedRecord(BaseModel):
    platform: str
    entity_type: str  # employee, project, task, deadline, repository, commit, email, event
    external_id: str
    payload: dict[str, Any]
    occurred_at: datetime = Field(default_factory=datetime.utcnow)


class BaseConnector(ABC):
    """Abstract base class for all external platform connectors."""

    def __init__(self, credentials: dict[str, Any] | None = None):
        self.credentials = credentials or {}

    @property
    @abstractmethod
    def platform(self) -> str:
        """The platform identifier (github, trello, gmail, gcalendar)."""

    @abstractmethod
    def authenticate(self) -> bool:
        """Validates or refreshes authentication credentials."""

    @abstractmethod
    def fetch_since(self, cursor: datetime | None = None) -> list[NormalizedRecord]:
        """Pulls incremental activity updates since the given cursor timestamp."""
