from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.db.models import RiskConfig, RiskScore
from app.db.neo4j_client import neo4j_client
from app.ml.features import extract_project_features
from app.ml.model import risk_model_engine
from app.services.alert_service import alert_service

BAND_SEVERITY = {"low": 1, "medium": 2, "high": 3, "critical": 4}


class RiskService:
    """Process 3: Computes ML project risk scores, monitors escalation thresholds, and records alerts."""

    def get_or_create_config(self, db: Session, org_id: str) -> RiskConfig:
        config = db.query(RiskConfig).filter(RiskConfig.organization_id == org_id).first()
        if not config:
            config = RiskConfig(
                organization_id=org_id,
                medium_threshold=0.35,
                high_threshold=0.60,
                critical_threshold=0.80,
                min_history_days=14,
                sync_interval_minutes=15,
            )
            db.add(config)
            db.commit()
            db.refresh(config)
        return config

    def evaluate_project_risk(self, db: Session, org_id: str, project_id: str) -> RiskScore | None:
        config = self.get_or_create_config(db, org_id)

        # Retrieve project and its artifacts from knowledge graph
        nodes_overview = neo4j_client.execute_query(
            "MATCH (p:Project {id: $id}) RETURN properties(p) as props", {"id": project_id}
        )
        if not nodes_overview and not neo4j_client.is_connected:
            p_node = neo4j_client.in_memory.nodes.get(project_id)
            project_props = (
                p_node["properties"] if p_node else {"id": project_id, "name": project_id}
            )
        elif nodes_overview:
            project_props = nodes_overview[0].get("props", {"id": project_id})
        else:
            project_props = {"id": project_id, "name": project_id}

        # Gather related tasks, commits, emails, events
        if neo4j_client.is_connected:
            task_records = neo4j_client.execute_query(
                "MATCH (t:Task)-[:BELONGS_TO]->(p:Project {id: $id}) RETURN properties(t) as props",
                {"id": project_id},
            )
            tasks = [r["props"] for r in task_records]

            commit_records = neo4j_client.execute_query(
                "MATCH (c:Commit)-[:IN_REPOSITORY]->(r:Repository)-[:BELONGS_TO]->(p:Project {id: $id}) RETURN properties(c) as props",
                {"id": project_id},
            )
            commits = [r["props"] for r in commit_records]

            email_records = neo4j_client.execute_query(
                "MATCH (em:Email) WHERE em.subject CONTAINS $name RETURN properties(em) as props",
                {"name": project_props.get("name", "")},
            )
            emails = [r["props"] for r in email_records]

            event_records = neo4j_client.execute_query(
                "MATCH (ev:Event)-[:RELATES_TO]->(p:Project {id: $id}) RETURN properties(ev) as props",
                {"id": project_id},
            )
            events = [r["props"] for r in event_records]
        else:
            # In-memory retrieval
            tasks = []
            commits = []
            emails = []
            events = []
            for r in neo4j_client.in_memory.relationships:
                if r["type"] == "BELONGS_TO" and r["end_id"] == project_id:
                    src = neo4j_client.in_memory.nodes.get(r["start_id"])
                    if src and "Task" in src["labels"]:
                        tasks.append(src["properties"])
                    elif src and "Repository" in src["labels"]:
                        repo_id = src["id"]
                        for cr in neo4j_client.in_memory.relationships:
                            if cr["type"] == "IN_REPOSITORY" and cr["end_id"] == repo_id:
                                c_node = neo4j_client.in_memory.nodes.get(cr["start_id"])
                                if c_node:
                                    commits.append(c_node["properties"])

            for n in neo4j_client.in_memory.nodes.values():
                if "Email" in n["labels"] and project_props.get("name", "") in n["properties"].get(
                    "subject", ""
                ):
                    emails.append(n["properties"])
                if "Event" in n["labels"]:
                    events.append(n["properties"])

        # Extract features
        features = extract_project_features(project_props, tasks, commits, emails, events)

        # Run prediction with cold-start evaluation
        history_days = 30 if (commits or tasks) else 5
        pred_res = risk_model_engine.predict(
            features=features,
            min_history_days=int(config.min_history_days or 14),
            history_days=history_days,
            thresholds={
                "medium": float(config.medium_threshold or 0.35),
                "high": float(config.high_threshold or 0.60),
                "critical": float(config.critical_threshold or 0.80),
            },
        )

        # Check previous score to detect escalation
        last_score = (
            db.query(RiskScore)
            .filter(RiskScore.entity_type == "project", RiskScore.entity_id == project_id)
            .order_by(RiskScore.computed_at.desc())
            .first()
        )
        prev_band = last_score.band if last_score else None

        new_score = RiskScore(
            organization_id=org_id,
            entity_type="project",
            entity_id=project_id,
            score=pred_res["score"],
            band=pred_res["band"],
            confidence=pred_res["confidence"],
            top_factors=pred_res["top_factors"],
            model_version="1.0.0",
            computed_at=datetime.now(UTC),
        )
        db.add(new_score)
        db.commit()
        db.refresh(new_score)

        # Escalate alert if band transitioned upward
        if prev_band and BAND_SEVERITY.get(pred_res["band"], 0) > BAND_SEVERITY.get(prev_band, 0):
            alert_service.trigger_risk_alert(
                db=db,
                organization_id=org_id,
                entity_type="project",
                entity_id=project_id,
                from_band=prev_band,
                to_band=pred_res["band"],
                message=f"Risk for project '{project_props.get('name', project_id)}' escalated from {prev_band.upper()} to {pred_res['band'].upper()} (score: {pred_res['score']:.2f}).",
                recommendation=pred_res.get("recommendation"),
            )

        return new_score

    def evaluate_all_projects(self, db: Session, org_id: str) -> list[RiskScore]:
        if neo4j_client.is_connected:
            p_res = neo4j_client.execute_query("MATCH (p:Project) RETURN p.id as id")
            project_ids = [r["id"] for r in p_res]
        else:
            project_ids = [
                n["id"] for n in neo4j_client.in_memory.nodes.values() if "Project" in n["labels"]
            ]

        scores = []
        for p_id in project_ids:
            score = self.evaluate_project_risk(db, org_id, p_id)
            if score:
                scores.append(score)
        return scores


risk_service = RiskService()
