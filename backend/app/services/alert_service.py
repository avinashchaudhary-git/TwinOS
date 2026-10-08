from sqlalchemy.orm import Session

from app.core.logging import logger
from app.db.models import Alert, User


class AlertService:
    """Manages in-app alert notifications for risk band escalations."""

    def trigger_risk_alert(
        self,
        db: Session,
        organization_id: str,
        entity_type: str,
        entity_id: str,
        from_band: str | None,
        to_band: str,
        message: str,
        recommendation: str | None = None,
        recipient_user_id: str | None = None,
    ) -> Alert | None:
        """Creates an in-app alert when a project or task transitions to a higher risk band."""
        # Find recipient: designated manager/owner or all managers in the org
        target_recipients = []
        if recipient_user_id:
            target_recipients.append(recipient_user_id)
        else:
            managers = (
                db.query(User)
                .filter(
                    User.organization_id == organization_id,
                    User.role.in_(["manager", "admin"]),
                    User.is_active.is_(True),
                )
                .all()
            )
            target_recipients = [m.id for m in managers]

        if not target_recipients:
            logger.warning(f"No manager found to receive risk alert for {entity_type} {entity_id}")
            return None

        created_alert = None
        for r_id in target_recipients:
            alert = Alert(
                organization_id=organization_id,
                recipient_user_id=r_id,
                entity_type=entity_type,
                entity_id=entity_id,
                from_band=from_band,
                to_band=to_band,
                message=message,
                recommendation=recommendation,
                is_read=False,
            )
            db.add(alert)
            created_alert = alert

        db.commit()
        logger.info(
            f"Triggered risk escalation alert for {entity_type} {entity_id} to {len(target_recipients)} recipient(s)."
        )
        return created_alert

    def get_user_alerts(self, db: Session, user_id: str, unread_only: bool = False) -> list[Alert]:
        query = db.query(Alert).filter(Alert.recipient_user_id == user_id)
        if unread_only:
            query = query.filter(Alert.is_read.is_(False))
        return query.order_by(Alert.created_at.desc()).all()

    def mark_as_read(self, db: Session, alert_id: str, user_id: str) -> bool:
        alert = (
            db.query(Alert).filter(Alert.id == alert_id, Alert.recipient_user_id == user_id).first()
        )
        if alert:
            alert.is_read = True
            db.commit()
            return True
        return False


alert_service = AlertService()
