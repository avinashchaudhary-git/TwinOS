import re
from typing import Any

from neo4j import Driver, GraphDatabase

from app.core.config import settings
from app.core.logging import logger


class InMemoryGraph:
    """In-memory graph store fallback for tests and zero-docker offline execution."""

    def __init__(self):
        self.nodes: dict[str, dict[str, Any]] = {}  # id -> {labels, properties}
        self.relationships: list[
            dict[str, Any]
        ] = []  # list of {start_id, type, end_id, properties}

    def clear(self):
        self.nodes.clear()
        self.relationships.clear()

    def merge_node(self, label: str, properties: dict[str, Any]):
        node_id = properties.get("id")
        if not node_id:
            return
        if node_id in self.nodes:
            self.nodes[node_id]["properties"].update(properties)
            if label not in self.nodes[node_id]["labels"]:
                self.nodes[node_id]["labels"].append(label)
        else:
            self.nodes[node_id] = {
                "id": node_id,
                "labels": [label],
                "properties": properties.copy(),
            }

    def merge_relationship(
        self, start_id: str, rel_type: str, end_id: str, properties: dict[str, Any] | None = None
    ):
        if not start_id or not end_id:
            return
        props = properties or {}
        for r in self.relationships:
            if r["start_id"] == start_id and r["type"] == rel_type and r["end_id"] == end_id:
                r["properties"].update(props)
                return
        self.relationships.append(
            {"start_id": start_id, "type": rel_type, "end_id": end_id, "properties": props}
        )

    def run_query(
        self, query: str, parameters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        # Handle simple pattern matches for in-memory testing
        q = query.strip()

        # Handle MATCH (n) DETACH DELETE n
        if "DETACH DELETE" in q:
            self.clear()
            return []

        # Handle simple node counts: MATCH (n:Label) RETURN count(n) as count
        count_match = re.search(
            r"MATCH\s+\(n:?(\w+)?\)\s+RETURN\s+count\(n\)\s+as\s+(\w+)", q, re.IGNORECASE
        )
        if count_match:
            label, alias = count_match.group(1), count_match.group(2)
            if label:
                count = sum(1 for n in self.nodes.values() if label in n["labels"])
            else:
                count = len(self.nodes)
            return [{alias: count}]

        # Handle relationship count: MATCH ()-[r]->() RETURN count(r) as count
        rel_count_match = re.search(
            r"MATCH\s+\(\)-\[r:?(\w+)?\]->\(\)\s+RETURN\s+count\(r\)\s+as\s+(\w+)", q, re.IGNORECASE
        )
        if rel_count_match:
            r_type, alias = rel_count_match.group(1), rel_count_match.group(2)
            if r_type:
                count = sum(1 for r in self.relationships if r["type"] == r_type)
            else:
                count = len(self.relationships)
            return [{alias: count}]

        # Handle MATCH (p:Project) RETURN p
        if "MATCH (p:Project)" in q and "RETURN" in q:
            results = []
            for n in self.nodes.values():
                if "Project" in n["labels"]:
                    results.append({"p": n["properties"]})
            return results

        # Handle MATCH (t:Task) WHERE t.status != 'done'
        if "MATCH (t:Task)" in q and "WHERE" in q:
            results = []
            for n in self.nodes.values():
                if "Task" in n["labels"]:
                    props = n["properties"]
                    if "t.status != 'done'" in q and props.get("status") == "done":
                        continue
                    results.append(
                        {"t": props, "task_id": props.get("id"), "title": props.get("title")}
                    )
            return results

        # Handle general MATCH (n:Label) RETURN n
        match_label = re.search(r"MATCH\s+\(n:(\w+)\)\s+RETURN\s+n", q, re.IGNORECASE)
        if match_label:
            lbl = match_label.group(1)
            return [{"n": n["properties"]} for n in self.nodes.values() if lbl in n["labels"]]

        return []


class Neo4jClient:
    def __init__(self):
        self.driver: Driver | None = None
        self.in_memory = InMemoryGraph()
        self.is_connected = False
        self._init_driver()

    def _init_driver(self):
        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                max_connection_lifetime=30 * 60,
                connection_timeout=2.0,
            )
            # Verify connectivity
            self.driver.verify_connectivity()
            self.is_connected = True
            logger.info(f"Connected to Neo4j at {settings.NEO4J_URI}")
        except Exception as e:
            self.is_connected = False
            self.driver = None
            if settings.NEO4J_MOCK_FALLBACK:
                logger.warning(
                    f"Neo4j connection failed ({e}). Operating in in-memory fallback graph mode."
                )
            else:
                logger.error(f"Neo4j connection error: {e}")

    def close(self):
        if self.driver:
            self.driver.close()

    def execute_query(
        self, query: str, parameters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        params = parameters or {}
        if self.is_connected and self.driver:
            try:
                with self.driver.session(database=settings.NEO4J_DATABASE) as session:
                    result = session.run(query, params)
                    return [record.data() for record in result]
            except Exception as e:
                logger.error(f"Neo4j query execution failed: {e}")
                if settings.NEO4J_MOCK_FALLBACK:
                    return self.in_memory.run_query(query, params)
                raise
        else:
            return self.in_memory.run_query(query, params)

    def bootstrap_constraints(self):
        """Creates unique constraints and indexes for all 8 entity labels idempotently."""
        constraints = [
            "CREATE CONSTRAINT employee_id IF NOT EXISTS FOR (n:Employee) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT project_id IF NOT EXISTS FOR (n:Project) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT task_id IF NOT EXISTS FOR (n:Task) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT deadline_id IF NOT EXISTS FOR (n:Deadline) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT repository_id IF NOT EXISTS FOR (n:Repository) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT commit_id IF NOT EXISTS FOR (n:Commit) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT email_id IF NOT EXISTS FOR (n:Email) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT event_id IF NOT EXISTS FOR (n:Event) REQUIRE n.id IS UNIQUE",
        ]
        indexes = [
            "CREATE INDEX task_status IF NOT EXISTS FOR (t:Task) ON (t.status)",
            "CREATE INDEX task_due IF NOT EXISTS FOR (t:Task) ON (t.due_date)",
            "CREATE INDEX commit_time IF NOT EXISTS FOR (c:Commit) ON (c.committed_at)",
            "CREATE INDEX employee_email IF NOT EXISTS FOR (e:Employee) ON (e.email)",
        ]

        for stmt in constraints + indexes:
            try:
                self.execute_query(stmt)
            except Exception as e:
                logger.warning(f"Neo4j constraint initialization warning on '{stmt}': {e}")


neo4j_client = Neo4jClient()
