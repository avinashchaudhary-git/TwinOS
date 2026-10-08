from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.chroma_client import chroma_client
from app.db.neo4j_client import neo4j_client
from app.db.postgres import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    # 1. Check PostgreSQL / SQLite
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {e}"

    # 2. Check Neo4j
    neo4j_status = "connected" if neo4j_client.is_connected else "in_memory_mock"

    # 3. Check ChromaDB
    chroma_status = "ready"
    try:
        count = chroma_client.count()
        chroma_status = f"ready (records: {count})"
    except Exception as e:
        chroma_status = f"warning: {e}"

    return {
        "status": "healthy" if "unhealthy" not in db_status else "degraded",
        "env": settings.ENV,
        "auth_mode": settings.AUTH_MODE,
        "llm_provider": settings.LLM_PROVIDER,
        "components": {
            "relational_db": db_status,
            "neo4j_graph": neo4j_status,
            "chroma_vector": chroma_status,
            "llm_provider": settings.LLM_PROVIDER,
        },
    }
