from enum import Enum

from pydantic import BaseModel, ConfigDict


class RoleEnum(str, Enum):
    MANAGER = "manager"
    EMPLOYEE = "employee"
    ADMIN = "admin"


class RiskBandEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskConfidenceEnum(str, Enum):
    NORMAL = "normal"
    LOW = "low"


class PlatformEnum(str, Enum):
    GITHUB = "github"
    TRELLO = "trello"
    GMAIL = "gmail"
    GCALENDAR = "gcalendar"


class TaskStatusEnum(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


# Base schema with ORM mode
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
