from typing import Any

from sqlalchemy.orm import Session

from app.core.logging import logger
from app.db.models import AuditLog


class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        actor_id: str | None,
        action: str,
        target_entity: str | None = None,
        target_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Appends an immutable entry to the audit log."""
        try:
            audit_entry = AuditLog(
                actor_id=actor_id,
                action=action,
                target_entity=target_entity,
                target_id=target_id,
                metadata_json=metadata or {},
            )
            db.add(audit_entry)
            db.commit()
            db.refresh(audit_entry)
            logger.info(
                f"Audit: actor={actor_id} action={action} entity={target_entity}:{target_id}"
            )
            return audit_entry
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to record audit log: {e}")
            raise


audit_service = AuditService()
