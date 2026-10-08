import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import User
from app.db.postgres import get_db
from app.schemas.assistant import AssistantQueryRequest, AssistantQueryResponse
from app.services.rag_service import rag_service

router = APIRouter(prefix="/assistant", tags=["RAG Assistant"])

# Simple in-process token-bucket rate limiter: max 30 requests / 60 seconds per user
RATE_LIMIT_STORE: dict[str, list[float]] = {}


def check_rate_limit(user_id: str, limit: int = 30, window: int = 60):
    now = time.time()
    history = RATE_LIMIT_STORE.get(user_id, [])
    history = [t for t in history if (now - t) < window]
    if len(history) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: maximum {limit} queries per minute.",
        )
    history.append(now)
    RATE_LIMIT_STORE[user_id] = history


@router.post("/query", response_model=AssistantQueryResponse)
def ask_assistant(
    request: AssistantQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    check_rate_limit(current_user.id)

    response = rag_service.query(
        db=db,
        question=request.question,
        user=current_user,
        project_id_filter=request.project_id,
    )
    return response
