import json
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.logging import logger
from app.db.models import EmployeeAlias, Organization, PlatformConnection, User
from app.db.postgres import Base, SessionLocal, engine
from app.services.graph_service import graph_service
from app.services.ingestion_service import ingestion_service
from app.services.risk_service import risk_service
from app.services.sync_service import sync_service

FIXTURES_PATH = (
    Path(__file__).resolve().parent.parent / "app" / "integrations" / "mock" / "fixtures"
)


def seed_demo():
    logger.info("Starting TwinOS demo data seeding...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Load core fixtures
        with open(FIXTURES_PATH / "org_dataset.json", "r") as f:
            base_data = json.load(f)

        org_info = base_data["organization"]
        employees = base_data["employees"]

        # 1. Organization
        org = db.query(Organization).filter(Organization.id == org_info["id"]).first()
        if not org:
            org = Organization(id=org_info["id"], name=org_info["name"])
            db.add(org)
            db.commit()
            logger.info(f"Created Organization: {org.name} ({org.id})")

        # 2. Users & Aliases
        for emp in employees:
            user = db.query(User).filter(User.email == emp["email"].lower()).first()
            if not user:
                user = User(
                    id=emp["id"],
                    organization_id=org.id,
                    name=emp["name"],
                    email=emp["email"].lower(),
                    role=emp["role"],
                    is_active=True,
                )
                db.add(user)
                db.commit()

            # Aliases
            if emp.get("github"):
                gh_alias = (
                    db.query(EmployeeAlias)
                    .filter(
                        EmployeeAlias.platform == "github",
                        EmployeeAlias.external_id == emp["github"],
                    )
                    .first()
                )
                if not gh_alias:
                    db.add(
                        EmployeeAlias(user_id=user.id, platform="github", external_id=emp["github"])
                    )
            if emp.get("trello"):
                tr_alias = (
                    db.query(EmployeeAlias)
                    .filter(
                        EmployeeAlias.platform == "trello",
                        EmployeeAlias.external_id == emp["trello"],
                    )
                    .first()
                )
                if not tr_alias:
                    db.add(
                        EmployeeAlias(user_id=user.id, platform="trello", external_id=emp["trello"])
                    )

            # Also seed Employee node in Knowledge Graph
            graph_service.merge_employee(
                {
                    "id": emp["id"],
                    "name": emp["name"],
                    "email": emp["email"].lower(),
                    "role_title": emp.get("role_title", "Engineer"),
                    "org_id": org.id,
                    "source": "seed",
                }
            )

        db.commit()
        logger.info(f"Seeded {len(employees)} users and knowledge graph Employee nodes.")

        # 3. Create platform connections
        for platform_name in ("github", "trello", "gmail", "gcalendar"):
            conn = (
                db.query(PlatformConnection)
                .filter(
                    PlatformConnection.organization_id == org.id,
                    PlatformConnection.platform == platform_name,
                )
                .first()
            )
            if not conn:
                conn = PlatformConnection(
                    user_id=employees[0]["id"],  # Alice Chen
                    organization_id=org.id,
                    platform=platform_name,
                    status="connected",
                )
                db.add(conn)
        db.commit()

        # 4. Run Process 1: Sync (pull mock records -> staging)
        staged = sync_service.run_all_syncs(db, org.id, use_mock=True)
        logger.info(f"Process 1 completed: {staged} records staged.")

        # 5. Run Process 2: Ingestion (staging -> Neo4j & Chroma)
        ingested = ingestion_service.ingest_pending_records(db, batch_size=500)
        logger.info(f"Process 2 completed: {ingested} records ingested into Neo4j and ChromaDB.")

        # 6. Run Process 3: Risk Evaluation & Alerts
        scores = risk_service.evaluate_all_projects(db, org.id)
        logger.info(f"Process 3 completed: {len(scores)} projects evaluated for delivery risk.")

        logger.info("TwinOS demo seeding completed successfully!")

    except Exception as e:
        db.rollback()
        logger.error(f"Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo()
