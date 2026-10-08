from datetime import datetime

from app.schemas.common import BaseSchema, PlatformEnum


class PlatformConnectionCreate(BaseSchema):
    platform: PlatformEnum
    oauth_token_ref: str | None = None
    scopes: list[str] | None = None


class PlatformConnectionRead(BaseSchema):
    id: str
    user_id: str
    organization_id: str
    platform: PlatformEnum
    status: str
    last_synced_at: datetime | None = None


class SyncRunRead(BaseSchema):
    id: str
    connection_id: str
    started_at: datetime
    finished_at: datetime | None = None
    status: str
    records_pulled: int
    error: str | None = None


class SyncTriggerResponse(BaseSchema):
    status: str
    message: str
    records_staged: int
