import uuid

from app.db.models import StagingRecord
from app.db.neo4j_client import neo4j_client
from app.db.postgres import SessionLocal
from app.services.ingestion_service import ingestion_service
from app.services.sync_service import sync_service


def test_tc04_new_trello_task_creates_task_node_in_graph():
    """TC-04: New Trello task gives Task node in Neo4j within one sync cycle."""
    db = SessionLocal()
    suffix = uuid.uuid4().hex[:6]
    task_ext_id = f"trello_card_tc04_{suffix}"
    task_id = f"task-tc04-{suffix}"
    payload = {
        "id": task_id,
        "title": "Setup distributed caching cluster",
        "description": "Deploy Redis Sentinel with automatic failover.",
        "status": "todo",
        "due_date": "2026-11-01T18:00:00Z",
        "priority": "high",
        "project_id": "proj-core-platform",
    }
    content_hash = sync_service.compute_content_hash("trello", "task", task_ext_id, payload)

    # 1. Stage the record
    staging_rec = StagingRecord(
        organization_id="org-twinos-demo-001",
        platform="trello",
        entity_type="task",
        external_id=task_ext_id,
        payload=payload,
        content_hash=content_hash,
        status="pending",
    )
    db.add(staging_rec)
    db.commit()

    # 2. Run ingestion cycle
    ingested = ingestion_service.ingest_pending_records(db)
    assert ingested >= 1, "Expected at least 1 record to be ingested"

    # 3. Verify Task node is present in knowledge graph
    if neo4j_client.is_connected:
        res = neo4j_client.execute_query(
            "MATCH (t:Task {id: $id}) RETURN properties(t) as props", {"id": task_id}
        )
        assert len(res) == 1, "Task node not found in Neo4j"
        assert res[0]["props"]["title"] == "Setup distributed caching cluster"
    else:
        node = neo4j_client.in_memory.nodes.get(task_id)
        assert node is not None, "Task node not found in in-memory graph"
        assert node["properties"]["title"] == "Setup distributed caching cluster"

    db.close()
