import hashlib
import json
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.logging import logger
from app.db.models import PlatformConnection, StagingRecord, SyncRun
from app.integrations.base import NormalizedRecord
from app.integrations.registry import get_connector


class SyncService:
    """Process 1: Runs external connectors and stages normalized records into PostgreSQL."""

    @staticmethod
    def compute_content_hash(
        platform: str, entity_type: str, external_id: str, payload: dict
    ) -> str:
        serialized = json.dumps(payload, sort_keys=True)
        raw_key = f"{platform}:{entity_type}:{external_id}:{serialized}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def run_sync_for_connection(
        self, db: Session, connection: PlatformConnection, use_mock: bool = False
    ) -> int:
        sync_run = SyncRun(
            connection_id=connection.id,
            started_at=datetime.now(UTC),
            status="running",
            records_pulled=0,
        )
        db.add(sync_run)
        db.commit()
        db.refresh(sync_run)

        try:
            connector = get_connector(platform=connection.platform, use_mock=use_mock)
            records: list[NormalizedRecord] = connector.fetch_since(
                cursor=connection.last_synced_at
            )

            staged_count = 0
            for r in records:
                content_hash = self.compute_content_hash(
                    platform=r.platform,
                    entity_type=r.entity_type,
                    external_id=r.external_id,
                    payload=r.payload,
                )

                # Check if this exact record version exists
                existing = (
                    db.query(StagingRecord)
                    .filter(
                        StagingRecord.platform == r.platform,
                        StagingRecord.entity_type == r.entity_type,
                        StagingRecord.external_id == r.external_id,
                        StagingRecord.content_hash == content_hash,
                    )
                    .first()
                )

                if not existing:
                    staging_record = StagingRecord(
                        organization_id=connection.organization_id,
                        platform=r.platform,
                        entity_type=r.entity_type,
                        external_id=r.external_id,
                        payload=r.payload,
                        content_hash=content_hash,
                        status="pending",
                        created_at=datetime.now(UTC),
                    )
                    db.add(staging_record)
                    staged_count += 1

            connection.last_synced_at = datetime.now(UTC)
            sync_run.finished_at = datetime.now(UTC)
            sync_run.status = "success"
            sync_run.records_pulled = len(records)

            db.commit()
            logger.info(
                f"Sync complete for {connection.platform}: {len(records)} pulled, {staged_count} new staged."
            )
            return staged_count

        except Exception as e:
            db.rollback()
            sync_run.finished_at = datetime.now(UTC)
            sync_run.status = "failed"
            sync_run.error = str(e)
            db.commit()
            logger.error(f"Sync failed for connection {connection.id} ({connection.platform}): {e}")
            raise

    def run_all_syncs(self, db: Session, org_id: str, use_mock: bool = False) -> int:
        connections = (
            db.query(PlatformConnection).filter(PlatformConnection.organization_id == org_id).all()
        )
        total_staged = 0
        for conn in connections:
            try:
                total_staged += self.run_sync_for_connection(db, conn, use_mock=use_mock)
            except Exception as e:
                logger.error(f"Error syncing {conn.platform}: {e}")
        return total_staged


sync_service = SyncService()
