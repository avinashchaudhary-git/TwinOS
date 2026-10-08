from typing import Any

from app.core.logging import logger
from app.db.neo4j_client import neo4j_client


class GraphService:
    """Provides structured Cypher read and write operations for the TwinOS knowledge graph."""

    def merge_employee(self, emp_data: dict[str, Any]):
        cypher = """
        MERGE (e:Employee {id: $id})
        SET e.name = $name,
            e.email = $email,
            e.role_title = $role_title,
            e.org_id = $org_id,
            e.source = $source,
            e.updated_at = datetime()
        ON CREATE SET e.created_at = datetime()
        """
        neo4j_client.execute_query(cypher, emp_data)
        # In-memory sync
        if not neo4j_client.is_connected:
            neo4j_client.in_memory.merge_node("Employee", emp_data)

    def merge_project(self, proj_data: dict[str, Any]):
        cypher = """
        MERGE (p:Project {id: $id})
        SET p.name = $name,
            p.status = $status,
            p.start_date = $start_date,
            p.target_end_date = $target_end_date,
            p.org_id = $org_id,
            p.source = $source,
            p.updated_at = datetime()
        ON CREATE SET p.created_at = datetime()
        """
        neo4j_client.execute_query(cypher, proj_data)
        if not neo4j_client.is_connected:
            neo4j_client.in_memory.merge_node("Project", proj_data)

    def merge_task(self, task_data: dict[str, Any]):
        cypher = """
        MERGE (t:Task {id: $id})
        SET t.title = $title,
            t.description = $description,
            t.status = $status,
            t.due_date = $due_date,
            t.completed_at = $completed_at,
            t.priority = $priority,
            t.external_id = $external_id,
            t.org_id = $org_id,
            t.source = $source,
            t.updated_at = datetime()
        ON CREATE SET t.created_at = datetime()
        """
        neo4j_client.execute_query(cypher, task_data)
        if not neo4j_client.is_connected:
            neo4j_client.in_memory.merge_node("Task", task_data)

        # Relate task to project
        if task_data.get("project_id"):
            self.create_relationship(task_data["id"], "BELONGS_TO", task_data["project_id"])

        # Relate task to assignee
        if task_data.get("assignee_id"):
            self.create_relationship(task_data["id"], "ASSIGNED_TO", task_data["assignee_id"])

    def merge_deadline(self, deadline_data: dict[str, Any]):
        cypher = """
        MERGE (d:Deadline {id: $id})
        SET d.label = $label,
            d.due_at = $due_at,
            d.kind = $kind,
            d.is_met = $is_met,
            d.org_id = $org_id,
            d.source = $source,
            d.updated_at = datetime()
        ON CREATE SET d.created_at = datetime()
        """
        neo4j_client.execute_query(cypher, deadline_data)
        if not neo4j_client.is_connected:
            neo4j_client.in_memory.merge_node("Deadline", deadline_data)

    def merge_repository(self, repo_data: dict[str, Any]):
        cypher = """
        MERGE (r:Repository {id: $id})
        SET r.full_name = $full_name,
            r.url = $url,
            r.default_branch = $default_branch,
            r.org_id = $org_id,
            r.source = $source,
            r.updated_at = datetime()
        ON CREATE SET r.created_at = datetime()
        """
        neo4j_client.execute_query(cypher, repo_data)
        if not neo4j_client.is_connected:
            neo4j_client.in_memory.merge_node("Repository", repo_data)

        if repo_data.get("project_id"):
            self.create_relationship(repo_data["id"], "BELONGS_TO", repo_data["project_id"])

    def merge_commit(self, commit_data: dict[str, Any]):
        cypher = """
        MERGE (c:Commit {id: $sha})
        SET c.sha = $sha,
            c.message = $message,
            c.committed_at = $committed_at,
            c.additions = $additions,
            c.deletions = $deletions,
            c.org_id = $org_id,
            c.source = $source,
            c.updated_at = datetime()
        ON CREATE SET c.created_at = datetime()
        """
        neo4j_client.execute_query(cypher, commit_data)
        if not neo4j_client.is_connected:
            neo4j_client.in_memory.merge_node("Commit", {**commit_data, "id": commit_data["sha"]})

        if commit_data.get("repository_id"):
            self.create_relationship(
                commit_data["sha"], "IN_REPOSITORY", commit_data["repository_id"]
            )
        if commit_data.get("author_id"):
            self.create_relationship(commit_data["sha"], "COMMITTED_BY", commit_data["author_id"])

    def merge_email(self, email_data: dict[str, Any]):
        cypher = """
        MERGE (em:Email {id: $id})
        SET em.subject = $subject,
            em.sent_at = $sent_at,
            em.thread_id = $thread_id,
            em.chroma_id = $chroma_id,
            em.org_id = $org_id,
            em.source = $source,
            em.updated_at = datetime()
        ON CREATE SET em.created_at = datetime()
        """
        neo4j_client.execute_query(cypher, email_data)
        if not neo4j_client.is_connected:
            neo4j_client.in_memory.merge_node("Email", email_data)

        if email_data.get("sender_id"):
            self.create_relationship(email_data["id"], "SENT_BY", email_data["sender_id"])
        for rec_id in email_data.get("recipient_ids", []):
            self.create_relationship(email_data["id"], "RECEIVED_BY", rec_id)

    def merge_event(self, event_data: dict[str, Any]):
        cypher = """
        MERGE (ev:Event {id: $id})
        SET ev.title = $title,
            ev.start_at = $start_at,
            ev.end_at = $end_at,
            ev.is_milestone = $is_milestone,
            ev.location = $location,
            ev.org_id = $org_id,
            ev.source = $source,
            ev.updated_at = datetime()
        ON CREATE SET ev.created_at = datetime()
        """
        neo4j_client.execute_query(cypher, event_data)
        if not neo4j_client.is_connected:
            neo4j_client.in_memory.merge_node("Event", event_data)

        if event_data.get("project_id"):
            self.create_relationship(event_data["id"], "RELATES_TO", event_data["project_id"])
        for att_id in event_data.get("attendee_ids", []):
            self.create_relationship(event_data["id"], "ATTENDED_BY", att_id)

    def create_relationship(self, start_id: str, rel_type: str, end_id: str):
        cypher = f"""
        MATCH (a {{id: $start_id}}), (b {{id: $end_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        """
        try:
            neo4j_client.execute_query(cypher, {"start_id": start_id, "end_id": end_id})
        except Exception:
            pass
        if not neo4j_client.is_connected:
            neo4j_client.in_memory.merge_relationship(start_id, rel_type, end_id)

    def get_overview(self, org_id: str) -> dict[str, Any]:
        """Returns node and relationship summaries for the visual graph explorer."""
        if neo4j_client.is_connected:
            try:
                node_res = neo4j_client.execute_query(
                    "MATCH (n) RETURN n.id as id, labels(n)[0] as label, properties(n) as properties LIMIT 200"
                )
                rel_res = neo4j_client.execute_query(
                    "MATCH (a)-[r]->(b) RETURN a.id as source, b.id as target, type(r) as type LIMIT 300"
                )
                nodes = [
                    {"id": r["id"], "label": r["label"], "properties": r["properties"]}
                    for r in node_res
                ]
                relationships = [
                    {"source": r["source"], "target": r["target"], "type": r["type"]}
                    for r in rel_res
                ]

                # Counts
                node_counts = {}
                for n in nodes:
                    lbl = n["label"]
                    node_counts[lbl] = node_counts.get(lbl, 0) + 1
                rel_counts = {}
                for rel in relationships:
                    rt = rel["type"]
                    rel_counts[rt] = rel_counts.get(rt, 0) + 1

                return {
                    "nodes": nodes,
                    "relationships": relationships,
                    "node_counts": node_counts,
                    "relationship_counts": rel_counts,
                }
            except Exception as e:
                logger.error(f"Failed to query Neo4j overview: {e}")

        # In-memory fallback
        nodes = [
            {"id": n["id"], "label": n["labels"][0], "properties": n["properties"]}
            for n in neo4j_client.in_memory.nodes.values()
        ]
        relationships = neo4j_client.in_memory.relationships
        node_counts = {}
        for n in nodes:
            lbl = n["label"]
            node_counts[lbl] = node_counts.get(lbl, 0) + 1
        rel_counts = {}
        for rel in relationships:
            rt = rel["type"]
            rel_counts[rt] = rel_counts.get(rt, 0) + 1

        return {
            "nodes": nodes,
            "relationships": relationships,
            "node_counts": node_counts,
            "relationship_counts": rel_counts,
        }

    def get_neighbors(self, node_id: str) -> dict[str, Any]:
        """Returns 1-hop connected neighbors for a specific entity node."""
        overview = self.get_overview("any")
        target_node = next((n for n in overview["nodes"] if n["id"] == node_id), None)
        if not target_node:
            return {
                "node": {"id": node_id, "label": "Unknown", "properties": {}},
                "neighbors": [],
                "relationships": [],
            }

        connected_rels = [
            r for r in overview["relationships"] if r["source"] == node_id or r["target"] == node_id
        ]
        neighbor_ids = {
            r["source"] if r["target"] == node_id else r["target"] for r in connected_rels
        }
        neighbors = [n for n in overview["nodes"] if n["id"] in neighbor_ids]

        return {
            "node": target_node,
            "neighbors": neighbors,
            "relationships": connected_rels,
        }


graph_service = GraphService()
