from app.schemas.common import BaseSchema


class CitationDto(BaseSchema):
    entity_type: str
    entity_id: str
    label: str
    snippet: str | None = None


class AssistantQueryRequest(BaseSchema):
    question: str
    project_id: str | None = None


class AssistantQueryResponse(BaseSchema):
    answer: str
    citations: list[CitationDto]
    used_graph_queries: list[str]
    confidence: str = "high"
