from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.db.models import User
from app.schemas.graph import GraphOverviewResponse, NeighborsResponse
from app.services.graph_service import graph_service

router = APIRouter(prefix="/graph", tags=["Knowledge Graph"])


@router.get("/overview", response_model=GraphOverviewResponse)
def get_graph_overview(current_user: User = Depends(get_current_user)):
    data = graph_service.get_overview(current_user.organization_id)
    return GraphOverviewResponse(
        nodes=data["nodes"],
        relationships=data["relationships"],
        node_counts=data["node_counts"],
        relationship_counts=data["relationship_counts"],
    )


@router.get("/neighbors/{node_id}", response_model=NeighborsResponse)
def get_node_neighbors(
    node_id: str,
    current_user: User = Depends(get_current_user),
):
    data = graph_service.get_neighbors(node_id)
    return NeighborsResponse(
        node=data["node"],
        neighbors=data["neighbors"],
        relationships=data["relationships"],
    )
