from app.schemas.common import BaseSchema, TaskStatusEnum


class TaskStatusUpdate(BaseSchema):
    status: TaskStatusEnum


class TaskRead(BaseSchema):
    id: str
    title: str
    description: str | None = None
    status: TaskStatusEnum
    due_date: str | None = None
    priority: str | None = None
    project_id: str | None = None
    assignee_id: str | None = None
