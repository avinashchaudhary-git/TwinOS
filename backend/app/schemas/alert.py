from datetime import datetime

from app.schemas.common import BaseSchema


class AlertRead(BaseSchema):
    id: str
    organization_id: str
    recipient_user_id: str
    entity_type: str
    entity_id: str
    from_band: str | None = None
    to_band: str
    message: str
    recommendation: str | None = None
    is_read: bool
    created_at: datetime


class AlertActionResponse(BaseSchema):
    success: bool
    message: str
