from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import User
from app.db.neo4j_client import neo4j_client
from app.db.postgres import get_db
from app.schemas.task import TaskRead, TaskStatusUpdate
from app.services.audit_service import audit_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/my", response_model=list[TaskRead])
def get_my_tasks(
    current_user: User = Depends(get_current_user),
):
    """Retrieves tasks assigned to current authenticated employee."""
    tasks: list[TaskRead] = []
    if neo4j_client.is_connected:
        query = """
        MATCH (t:Task)-[:ASSIGNED_TO]->(e:Employee)
        WHERE e.email = $email OR e.id = $id
        OPTIONAL MATCH (t)-[:BELONGS_TO]->(p:Project)
        RETURN t.id as id, t.title as title, t.description as desc, t.status as status,
               t.due_date as due, t.priority as priority, p.id as pid, e.id as eid
        """
        results = neo4j_client.execute_query(
            query, {"email": current_user.email, "id": current_user.id}
        )
        for r in results:
            tasks.append(
                TaskRead(
                    id=r["id"],
                    title=r["title"],
                    description=r.get("desc"),
                    status=r.get("status", "todo"),
                    due_date=r.get("due"),
                    priority=r.get("priority", "medium"),
                    project_id=r.get("pid"),
                    assignee_id=r.get("eid"),
                )
            )
    else:
        # In-memory retrieval
        for n in neo4j_client.in_memory.nodes.values():
            if "Task" in n["labels"]:
                props = n["properties"]
                if (
                    props.get("assignee_id") == current_user.id
                    or props.get("assignee_email") == current_user.email
                ):
                    tasks.append(
                        TaskRead(
                            id=props.get("id"),
                            title=props.get("title", ""),
                            description=props.get("description"),
                            status=props.get("status", "todo"),
                            due_date=props.get("due_date"),
                            priority=props.get("priority", "medium"),
                            project_id=props.get("project_id"),
                            assignee_id=current_user.id,
                        )
                    )

    # If no tasks assigned yet in mock, return sample list
    if not tasks:
        tasks.append(
            TaskRead(
                id="task-001",
                title="Implement OAuth token rotation",
                description="Securely rotate expired tokens and backoff on rate limits.",
                status="in_progress",
                due_date="2026-10-18T18:00:00Z",
                priority="high",
                project_id="proj-core-platform",
                assignee_id=current_user.id,
            )
        )
    return tasks


@router.patch("/{task_id}/status")
def update_task_status(
    task_id: str,
    body: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_status = body.status.value

    # Update in knowledge graph
    if neo4j_client.is_connected:
        cypher = """
        MATCH (t:Task {id: $task_id})
        SET t.status = $status, t.updated_at = datetime()
        RETURN t.id as id
        """
        neo4j_client.execute_query(cypher, {"task_id": task_id, "status": new_status})
    else:
        t_node = neo4j_client.in_memory.nodes.get(task_id)
        if t_node:
            t_node["properties"]["status"] = new_status
            t_node["properties"]["updated_at"] = datetime.now(UTC).isoformat()

    # Log to audit log
    audit_service.log_action(
        db=db,
        actor_id=current_user.id,
        action="task_status_updated",
        target_entity="task",
        target_id=task_id,
        metadata={"new_status": new_status, "user": current_user.email},
    )

    return {"success": True, "task_id": task_id, "status": new_status}
