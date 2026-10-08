from typing import Any

from app.schemas.common import BaseSchema


class GraphNode(BaseSchema):
    id: str
    label: str
    properties: dict[str, Any]


class GraphRelationship(BaseSchema):
    source: str
    target: str
    type: str
    properties: dict[str, Any] | None = None


class GraphOverviewResponse(BaseSchema):
    nodes: list[GraphNode]
    relationships: list[GraphRelationship]
    node_counts: dict[str, int]
    relationship_counts: dict[str, int]


class NeighborsResponse(BaseSchema):
    node: GraphNode
    neighbors: list[GraphNode]
    relationships: list[GraphRelationship]
