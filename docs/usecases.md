# TwinOS System Use Case Specifications

This document defines the formal operational use cases for the TwinOS platform across the three core security roles: **Project Manager**, **Employee (Engineer)**, and **System Administrator**.

---

## 1. Project Manager Use Cases

### UC-M01: Inspect Org-Wide Project Risk Dashboard & Delay Heatmap
- **Primary Actor:** Project Manager / Engineering Director (`manager` role)
- **Preconditions:**
  - Manager is authenticated with valid credentials or session bearer token.
  - At least one ingestion cycle has executed and seeded data into the knowledge graph and relational database.
- **Trigger:** Manager accesses the TwinOS root URL or navigates to `/dashboard`.
- **Main Success Scenario:**
  1. The system authenticates the manager's role and fetches active organizational projects.
  2. The system queries PostgreSQL/SQLite for the latest ML risk predictions (`score`, `risk_band`, `top_factors`).
  3. The system queries Neo4j for aggregate counts (overdue tasks, impending deadlines, developer commits, active participants).
  4. The frontend renders:
     - High-level metric cards (Total Projects, Critical Projects, Active Watchlist, Risk Trend).
     - Color-coded project cards with dynamic risk badges (`low`, `medium`, `high`, `critical`).
     - Real-time delay risk distribution charts and feature contribution breakdowns.
  5. The manager clicks on a high-risk project to drill down into project details (`/projects/[id]`).
- **Alternative Flows:**
  - *No Projects Seeded (Empty State):* The dashboard renders a prominent banner prompting the manager to trigger a demo seed or manual sync run.
  - *Cold-Start Project Detected:* For projects with fewer than `min_history_days`, the system displays a `LOW CONFIDENCE` badge and baseline risk prior to prevent false alarms.
- **Postconditions:**
  - Manager acquires visibility into project bottlenecks without querying team leads manually.
- **Traceability:** TC-05 (Cold-start handling), Dashboard Service, Risk Engine.

---

### UC-M02: Query Conversational RAG Assistant with Subgraph Citations
- **Primary Actor:** Project Manager (`manager` role)
- **Preconditions:**
  - Manager is authenticated.
  - Vector embeddings have been generated in ChromaDB and knowledge graph nodes are indexed.
- **Trigger:** Manager submits a natural language question (e.g., *"Which projects are at risk of missing their deadlines, and what are the primary root causes?"*) in `/assistant`.
- **Main Success Scenario:**
  1. The system evaluates the prompt using whitelisted Cypher query templates and hybrid vector similarity.
  2. The system detects the manager's role (`manager`) and grants org-wide retrieval scope.
  3. Cypher query executes against Neo4j to retrieve overdue tasks, assigned engineers, upcoming deadlines, and commit velocity.
  4. ChromaDB searches commit diff messages, PR comments, and email headers for semantic overlap.
  5. The Mock/OpenAI LLM provider synthesizes an executive summary grounded in retrieved evidence.
  6. The response is returned to the UI with structured citations (`entity_type`, `entity_id`, `label`, `snippet`).
  7. The frontend renders the response with interactive citation pills that link directly to node details.
- **Alternative Flows:**
  - *Out of Scope / Off-Topic Query:* The system outputs an honest refusal with guidance toward project delivery questions.
  - *No Matching Evidence:* The system states no risk patterns were found for the requested target instead of hallucinating.
- **Postconditions:**
  - Manager receives an audit-logged explanation backed by cryptographic graph references.
- **Traceability:** TC-03 (RAG grounded answers + citations).

---

### UC-M03: Trigger On-Demand Cross-Platform Ingestion Sync Cycle
- **Primary Actor:** Project Manager or Admin
- **Preconditions:**
  - User is authenticated with `manager` or `admin` permissions.
- **Trigger:** User clicks "Sync Now" in the navigation bar or administrative dashboard.
- **Main Success Scenario:**
  1. Frontend dispatches a `POST /api/v1/sync/run?use_mock=true` request.
  2. The ingestion orchestrator queries all configured connectors (GitHub, Trello, Gmail, GCal).
  3. Connectors stage raw payloads in the relational database with SHA-256 deduplication hashing.
  4. Graph service parses staged records, resolves lowercase email identities, and executes parameterized `UNWIND`/`MERGE` Cypher statements.
  5. Vector service updates ChromaDB semantic collections.
  6. Risk service re-extracts the 12 feature vectors and re-evaluates the delay risk classifier.
  7. Alert service evaluates risk thresholds and dispatches transition notifications.
  8. The system returns an execution summary (`records_staged`, `records_ingested`, status `completed`).
- **Alternative Flows:**
  - *Upstream Rate Limit Encountered (e.g. GitHub 403):* The connector triggers Tenacity exponential backoff, queues remaining requests, and returns partial progress without dropping data.
- **Postconditions:**
  - Knowledge graph, vector collections, and risk predictions reflect the latest external state.
- **Traceability:** TC-02 (Rate limit resilience), TC-04 (Trello sync -> Neo4j task node generation).

---

### UC-M04: Explore Multi-Hop Knowledge Graph Topology & Project Dependencies
- **Primary Actor:** Project Manager (`manager` role)
- **Preconditions:**
  - Manager is authenticated and Neo4j contains active entities and relationships.
- **Trigger:** Manager opens the `/graph` explorer view.
- **Main Success Scenario:**
  1. Frontend fetches graph overview (`GET /api/v1/graph/overview`).
  2. The interactive SVG graph visualizer renders node clusters grouped by entity type (`Project`, `Employee`, `Task`, `Commit`, `Deadline`, `Repository`, `Email`, `Event`).
  3. Manager clicks a specific `Project` node:
     - The visualizer expands 1-hop and 2-hop neighbor connections (`WORKS_ON`, `PART_OF`, `ASSIGNED_TO`, `HAS_DEADLINE`).
     - A side drawer displays complete entity properties, assigned staff, and associated tasks.
  4. Manager filters nodes by entity type using toggle buttons.
- **Alternative Flows:**
  - *Large Graph Volume:* Visualizer samples the top 150 most connected nodes to maintain 60 FPS client performance.
- **Postconditions:**
  - Manager understands cross-project resource bottlenecks and dependency chains.
- **Traceability:** Graph Service, Neo4j Schema.

---

## 2. Employee (Engineer) Use Cases

### UC-E01: Review Scoped Work Queue & Impending Deadlines
- **Primary Actor:** Software Engineer (`employee` role, e.g. Bob Martinez)
- **Preconditions:**
  - Engineer is authenticated with `employee` role.
- **Trigger:** Engineer navigates to `/my-work`.
- **Main Success Scenario:**
  1. Frontend requests `GET /api/v1/tasks/my`.
  2. System resolves the engineer's employee profile via their authenticated email address.
  3. Relational database returns only tasks where `assignee_id == current_user.id` or `assignee_email == current_user.email`.
  4. UI renders the engineer's assigned Kanban columns (`todo`, `in_progress`, `review`, `done`), highlighting overdue tasks in amber/rose.
- **Alternative Flows:**
  - *No Tasks Assigned:* UI displays a clean message indicating all queues are clear.
- **Postconditions:**
  - Engineer has clear operational visibility into their sprint responsibilities.
- **Traceability:** Tasks API, RBAC Scoping.

---

### UC-E02: Update Card/Task Progress & Trigger Real-Time Risk Recomputation
- **Primary Actor:** Software Engineer (`employee` role)
- **Preconditions:**
  - Engineer is assigned to the target task.
- **Trigger:** Engineer transitions a task from `in_progress` to `done` on `/my-work`.
- **Main Success Scenario:**
  1. Frontend sends `PATCH /api/v1/tasks/{task_id}/status` with `{"status": "done"}`.
  2. Backend updates task status in PostgreSQL/SQLite and commits transaction.
  3. Backend updates the corresponding `Task` node property in Neo4j (`n.status = 'done'`).
  4. System asynchronously schedules risk score recomputation for the parent project.
  5. Subsequent dashboard and RAG queries immediately reflect the reduced backlog risk.
- **Alternative Flows:**
  - *Employee Attempts to Modify Unassigned Task in Another Project:* Backend denies request if cross-project mutation is restricted.
- **Postconditions:**
  - Graph node state matches relational task state; project risk drops.
- **Traceability:** TC-04 (Task sync), E2E Pipeline Test.

---

### UC-E03: Query RAG Assistant with Role-Restricted Knowledge Scoping
- **Primary Actor:** Software Engineer (`employee` role)
- **Preconditions:**
  - Engineer is authenticated with `employee` role.
- **Trigger:** Engineer asks a question in `/assistant` (e.g., *"What deadlines do I have coming up this sprint?"*).
- **Main Success Scenario:**
  1. Backend RAG service detects caller role is `employee`.
  2. Cypher query injection applies strict employee scoping: filters graph traversals to tasks and projects where `(e:Employee {email: user.email})-[:WORKS_ON|ASSIGNED_TO]->(target)`.
  3. Sensitive org-wide financial or executive management queries return only the employee's accessible context.
  4. Assistant answers with citations strictly within the employee's authorized boundary.
- **Alternative Flows:**
  - *Employee Inquires About Another Project's Confidential Data:* Assistant returns scoped message: *"You do not have access to unassigned project data per company RBAC policy."*
- **Postconditions:**
  - Confidential cross-team data is protected from unauthorized prompt extraction.
- **Traceability:** TC-01 (RBAC Security), TC-03 (Scoped RAG).

---

## 3. System Administrator Use Cases

### UC-A01: Provision User Accounts, Deactivate Staff, & Assign RBAC Roles
- **Primary Actor:** System Administrator (`admin` role, e.g. Laura Croft)
- **Preconditions:**
  - Administrator is authenticated with `admin` role.
- **Trigger:** Administrator navigates to `/admin/users`.
- **Main Success Scenario:**
  1. System queries all users within the admin's organization (`GET /api/v1/admin/users`).
  2. Administrator clicks "Add User", inputs Name, Email, and selects Role (`employee`, `manager`, `admin`).
  3. System creates the user record, normalizes email to lowercase, and commits to PostgreSQL.
  4. Immutable audit service records `action="user_created"`, `actor_id=admin.id`, `target_id=new_user.id`.
  5. UI immediately lists the new user.
- **Alternative Flows:**
  - *Non-Admin Attempts User Creation:* System halts execution with HTTP 403 Forbidden.
  - *Duplicate Email Submitted:* System returns HTTP 400 with clear message: *"User with this email already exists."*
- **Postconditions:**
  - User can immediately authenticate and inherit appropriate RBAC permissions.
- **Traceability:** TC-01 (Admin RBAC Gate), Audit Service.

---

### UC-A02: Calibrate ML Risk Thresholds, Cold-Start Gating, & Ingestion Cadence
- **Primary Actor:** System Administrator (`admin` role)
- **Preconditions:**
  - Administrator is authenticated.
- **Trigger:** Administrator navigates to `/admin/risk-config`.
- **Main Success Scenario:**
  1. Frontend retrieves active risk parameters (`GET /api/v1/admin/risk-config`).
  2. Admin adjusts Medium Threshold slider (e.g. from 0.35 to 0.40), High Threshold (from 0.60 to 0.65), and Cold-Start Floor (from 14 to 21 days).
  3. Admin clicks "Save Changes" (`PUT /api/v1/admin/risk-config`).
  4. Backend validates invariant: `medium_threshold < high_threshold < critical_threshold`.
  5. Updates are written to the database; audit trail records `risk_config_updated`.
  6. Subsequent risk evaluation runs adhere to the newly calibrated thresholds.
- **Alternative Flows:**
  - *Invalid Threshold Bounds (e.g. Medium > High):* UI and backend reject mutation with validation error.
- **Postconditions:**
  - Project risk classifications reflect executive organizational tolerances.
- **Traceability:** TC-05 (Configurable history days), Risk Config API.

---

### UC-A03: Audit Administrative Mutations via Immutable Security Ledger
- **Primary Actor:** System Administrator (`admin` role)
- **Preconditions:**
  - Administrator is authenticated.
- **Trigger:** Administrator navigates to `/admin/audit`.
- **Main Success Scenario:**
  1. System fetches recent audit log entries (`GET /api/v1/admin/audit?limit=100`).
  2. UI displays a chronological tabular ledger with timestamps, actors, action types (`user_created`, `risk_config_updated`, `sync_run`), and entity IDs.
  3. Admin searches for a specific action or clicks "View Meta" to inspect the JSON payload containing the exact before/after state diff.
- **Alternative Flows:**
  - *Unauthorized User (Employee) Requests Audit API:* Request is blocked with HTTP 403 Forbidden.
- **Postconditions:**
  - Complete compliance trail is verified without capability to alter historical logs.
- **Traceability:** TC-01 (Admin Protection), Audit Trail Architecture.
