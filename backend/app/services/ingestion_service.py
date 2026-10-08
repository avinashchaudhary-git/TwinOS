from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.logging import logger
from app.db.chroma_client import chroma_client
from app.db.models import EmployeeAlias, StagingRecord, User
from app.services.graph_service import graph_service


class IngestionService:
    """Process 2: Ingests staged records into the Neo4j knowledge graph and Chroma vector store."""

    def resolve_employee_id(
        self, db: Session, email: str | None, platform: str | None, external_id: str | None
    ) -> str | None:
        """Resolves employee identifier via lowercase email, falling back to employee_aliases."""
        if email:
            clean_email = email.strip().lower()
            user = db.query(User).filter(User.email == clean_email).first()
            if user:
                return user.id

        if platform and external_id:
            alias = (
                db.query(EmployeeAlias)
                .filter(
                    EmployeeAlias.platform == platform,
                    EmployeeAlias.external_id == str(external_id),
                )
                .first()
            )
            if alias:
                return alias.user_id

        return None

    def ingest_pending_records(self, db: Session, batch_size: int = 100) -> int:
        pending_records = (
            db.query(StagingRecord)
            .filter(StagingRecord.status == "pending")
            .limit(batch_size)
            .all()
        )
        if not pending_records:
            return 0

        ingested_count = 0
        chroma_ids: list[str] = []
        chroma_docs: list[str] = []
        chroma_metas: list[dict[str, Any]] = []

        for record in pending_records:
            try:
                payload = record.payload
                platform = record.platform
                entity_type = record.entity_type
                org_id = record.organization_id

                if entity_type == "project":
                    graph_service.merge_project(
                        {
                            "id": payload.get("id", record.external_id),
                            "name": payload.get("name", "Untitled Project"),
                            "status": payload.get("status", "active"),
                            "start_date": payload.get("start_date"),
                            "target_end_date": payload.get("target_end_date"),
                            "org_id": org_id,
                            "source": platform,
                        }
                    )

                elif entity_type == "task":
                    assignee_email = payload.get("assignee_email")
                    assignee_id = payload.get("assignee_id") or self.resolve_employee_id(
                        db, assignee_email, platform, payload.get("assignee_external_id")
                    )
                    task_id = payload.get("id", record.external_id)

                    graph_service.merge_task(
                        {
                            "id": task_id,
                            "title": payload.get("title", ""),
                            "description": payload.get("description", ""),
                            "status": payload.get("status", "todo"),
                            "due_date": payload.get("due_date"),
                            "completed_at": payload.get("completed_at"),
                            "priority": payload.get("priority", "medium"),
                            "external_id": record.external_id,
                            "project_id": payload.get("project_id"),
                            "assignee_id": assignee_id,
                            "org_id": org_id,
                            "source": platform,
                        }
                    )

                    # Vector embedding for task description
                    desc = payload.get("description") or payload.get("title")
                    if desc:
                        chroma_ids.append(f"task:{task_id}")
                        chroma_docs.append(f"Task: {payload.get('title')}. Description: {desc}")
                        chroma_metas.append(
                            {
                                "org_id": org_id,
                                "source_platform": platform,
                                "entity_type": "task",
                                "entity_id": task_id,
                                "project_id": payload.get("project_id", ""),
                                "timestamp": record.created_at.isoformat(),
                            }
                        )

                elif entity_type == "repository":
                    graph_service.merge_repository(
                        {
                            "id": payload.get("id", record.external_id),
                            "full_name": payload.get("full_name", ""),
                            "url": payload.get("url", ""),
                            "default_branch": payload.get("default_branch", "main"),
                            "project_id": payload.get("project_id"),
                            "org_id": org_id,
                            "source": platform,
                        }
                    )

                elif entity_type == "commit":
                    sha = payload.get("sha", record.external_id)
                    author_id = self.resolve_employee_id(
                        db, payload.get("author_email"), platform, None
                    )
                    graph_service.merge_commit(
                        {
                            "sha": sha,
                            "message": payload.get("message", ""),
                            "committed_at": payload.get(
                                "committed_at", datetime.now(UTC).isoformat()
                            ),
                            "additions": payload.get("additions", 0),
                            "deletions": payload.get("deletions", 0),
                            "repository_id": payload.get("repository_id"),
                            "author_id": author_id,
                            "org_id": org_id,
                            "source": platform,
                        }
                    )

                    # Vector embedding for commit message
                    msg = payload.get("message", "")
                    if msg:
                        chroma_ids.append(f"commit:{sha}")
                        chroma_docs.append(f"Commit [{sha[:7]}]: {msg}")
                        chroma_metas.append(
                            {
                                "org_id": org_id,
                                "source_platform": platform,
                                "entity_type": "commit",
                                "entity_id": sha,
                                "project_id": payload.get("project_id", ""),
                                "timestamp": payload.get(
                                    "committed_at", record.created_at.isoformat()
                                ),
                            }
                        )

                elif entity_type == "email":
                    email_id = payload.get("id", record.external_id)
                    sender_id = self.resolve_employee_id(
                        db, payload.get("sender_email"), platform, None
                    )
                    graph_service.merge_email(
                        {
                            "id": email_id,
                            "subject": payload.get("subject", ""),
                            "sent_at": payload.get("sent_at", datetime.now(UTC).isoformat()),
                            "thread_id": payload.get("thread_id", ""),
                            "chroma_id": f"email:{email_id}",
                            "sender_id": sender_id,
                            "recipient_ids": [],
                            "org_id": org_id,
                            "source": platform,
                        }
                    )

                    # Vector embedding for email snippet
                    snippet = payload.get("snippet", "")
                    if snippet:
                        chroma_ids.append(f"email:{email_id}")
                        chroma_docs.append(f"Subject: {payload.get('subject')}\nSnippet: {snippet}")
                        chroma_metas.append(
                            {
                                "org_id": org_id,
                                "source_platform": platform,
                                "entity_type": "email",
                                "entity_id": email_id,
                                "project_id": payload.get("project_id", ""),
                                "timestamp": payload.get("sent_at", record.created_at.isoformat()),
                            }
                        )

                elif entity_type == "event":
                    event_id = payload.get("id", record.external_id)
                    graph_service.merge_event(
                        {
                            "id": event_id,
                            "title": payload.get("title", ""),
                            "start_at": payload.get("start_at", datetime.now(UTC).isoformat()),
                            "end_at": payload.get("end_at", datetime.now(UTC).isoformat()),
                            "is_milestone": payload.get("is_milestone", False),
                            "location": payload.get("location", ""),
                            "project_id": payload.get("project_id"),
                            "attendee_ids": [],
                            "org_id": org_id,
                            "source": platform,
                        }
                    )

                record.status = "ingested"
                ingested_count += 1

            except Exception as e:
                logger.error(f"Failed to ingest staging record {record.id}: {e}")
                record.status = "failed"

        # Batch upsert to ChromaDB
        if chroma_ids:
            try:
                chroma_client.add_documents(
                    ids=chroma_ids,
                    documents=chroma_docs,
                    metadatas=chroma_metas,
                )
                logger.info(f"Ingested {len(chroma_ids)} text records into ChromaDB collection.")
            except Exception as e:
                logger.error(f"Chroma batch upsert failed: {e}")

        db.commit()
        return ingested_count


ingestion_service = IngestionService()
