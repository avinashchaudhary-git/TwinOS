from apscheduler.schedulers.background import BackgroundScheduler

from app.core.logging import logger
from app.db.models import Organization
from app.db.postgres import SessionLocal
from app.services.ingestion_service import ingestion_service
from app.services.risk_service import risk_service
from app.services.sync_service import sync_service

scheduler = BackgroundScheduler()


def scheduled_pipeline_job():
    """Runs scheduled sync, ingestion, risk recalculation, and alert scanning."""
    db = SessionLocal()
    try:
        org = db.query(Organization).first()
        if not org:
            return
        logger.info(f"Running scheduled sync pipeline for org: {org.id}")
        staged = sync_service.run_all_syncs(db, org.id, use_mock=True)
        if staged > 0:
            ingested = ingestion_service.ingest_pending_records(db)
            scores = risk_service.evaluate_all_projects(db, org.id)
            logger.info(
                f"Scheduled pipeline finished: {staged} staged, {ingested} ingested, {len(scores)} projects scored."
            )
    except Exception as e:
        logger.error(f"Scheduled pipeline job error: {e}")
    finally:
        db.close()


def start_scheduler():
    try:
        if not scheduler.running:
            # Run every 15 minutes by default
            scheduler.add_job(
                scheduled_pipeline_job,
                "interval",
                minutes=15,
                id="twinos_sync_job",
                replace_existing=True,
            )
            scheduler.start()
            logger.info("APScheduler background scheduler started.")
    except Exception as e:
        logger.warning(f"Could not start APScheduler: {e}")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped.")
