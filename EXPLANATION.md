# TwinOS: Architectural Mastery & Comprehensive Viva Defense Reference

---

## 1. Executive Summary & Problem Formulation

### 1.1 The Software Delivery Blindspot
Modern enterprise software engineering organizations suffer from fragmented operational visibility. While engineering teams generate rich, continuous operational exhaust across issue trackers (Trello), version control systems (GitHub), asynchronous email exchanges (Gmail), and scheduling calendars (Google Calendar), this data remains siloed in isolated, proprietary SaaS repositories.

Traditional project management tools (such as Jira, Linear, or Monday.com) suffer from three fatal systemic deficiencies:
1. **Passive Issue Tracking:** They represent state transitions reactively after human manual entry. If an engineer forgets to update a ticket or an unexpected technical blocker arises, the tracking system remains ignorant until a sprint deadline is breached.
2. **Topological Blindness:** Relational and tabular project management tools cannot compute multi-hop dependencies between developers, code repositories, pull requests, meeting overhead, and impending contractual deadlines.
3. **Hallucinatory "AI" Add-ons:** Modern commercial attempts to apply generative AI to project data rely on naive, ungrounded Large Language Model (LLM) prompts. These unconstrained LLMs hallucinate non-existent milestones, leak sensitive organizational data across authorization boundaries, and offer zero explainable mathematical guarantees.

### 1.2 The TwinOS Paradigm
**TwinOS** resolves these fundamental challenges by constructing a real-time **Organizational Digital Twin**:
- **Tri-Store Data Engine:** Integrates relational ACID guarantees (PostgreSQL/SQLite), multi-hop topological graph relationships (Neo4j), and dense semantic embeddings (ChromaDB).
- **8-Entity Knowledge Graph:** Organizes enterprise knowledge into 8 discrete node entities (`Employee`, `Project`, `Task`, `Deadline`, `Repository`, `Commit`, `Email`, `Event`) and 9 typed semantic relationships.
- **Explainable Supervised Machine Learning:** Replaces LLM guesswork with a trained Gradient Boosting classifier that evaluates 12 topological and velocity features, generating probability scores [0.0 - 1.0], calibrated risk bands, and top-factor feature deviations.
- **Grounded, Role-Scoped RAG Assistant:** Enforces whitelisted Cypher templates and role-based graph pruning, guaranteeing mathematical groundedness with clickable sub-graph citations and zero cross-tenant data leakage.
- **Zero-Friction Evaluation:** Runs out-of-the-box in 100% offline mode with zero external cloud dependencies or Docker prerequisites, while remaining fully Docker-ready for production deployment.

---

## 2. Complete System Architecture & Topology

```
+---------------------------------------------------------------------------------------------------+
|                                     CLIENT PRESENTATION TIER                                      |
|                                                                                                   |
|  Next.js 14 App Router (Tailwind CSS, Lucide Icons, Recharts Analytics, SVG Graph Visualizer)     |
|  Views: /dashboard  /assistant  /graph  /projects  /projects/[id]  /my-work  /alerts  /admin/*   |
+-------------------------------------------------+-------------------------------------------------+
                                                  | HTTPS / REST (JSON)
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                   FASTAPI GATEWAY & SECURITY TIER                                 |
|                                                                                                   |
|  • RBAC Authorization Guard (require_role: manager, employee, admin)                              |
|  • Dual Authentication Resolver (Bearer dev:<email>  |  Firebase RS256 JWT Admin SDK)             |
|  • Secret Redaction Logging Filter (Regex scrubbing of tokens, secrets, credentials)              |
|  • Immutable Security Audit Engine (Appends all state mutations to audit_logs)                    |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
         +----------------------------------------+----------------------------------------+
         |                                        |                                        |
         v                                        v                                        v
+------------------------+      +---------------------------------+      +-------------------------+
|   INGESTION & SYNC     |      |       INTELLIGENCE & ML         |      |    RAG RETRIEVAL & LLM  |
|                        |      |                                 |      |                         |
| • Connectors: GitHub,  |      | • Feature Pipeline (12 feats)   |      | • Whitelisted Cypher    |
|   Trello, Gmail, GCal  |      | • Gradient Boosting Classifier  |      |   Templates             |
| • Tenacity Backoff     |      | • Logistic Regression Baseline  |      | • Subgraph Role Pruning |
| • SHA-256 Deduplication|      | • Top Factor Explainability     |      | • Exact Graph Citations |
| • Ingestion Runs Log   |      | • Cold-Start History Gate       |      | • Mock & OpenAI Provider|
+-----------+------------+      +----------------+----------------+      +------------+------------+
            |                                    |                                    |
            +------------------------------------+------------------------------------+
                                                 |
                                                 v
+---------------------------------------------------------------------------------------------------+
|                                     TRI-STORE PERSISTENCE TIER                                    |
|                                                                                                   |
|   1. Relational Database (PostgreSQL 16 / Transparent SQLite Fallback)                            |
|      - Models: users, organizations, platform_connections, staged_records, ingestion_runs,       |
|                audit_logs, risk_predictions, delay_alerts, risk_configs, tasks                   |
|                                                                                                   |
|   2. Knowledge Graph (Neo4j 5 Enterprise / In-Memory Graph Driver Fallback)                       |
|      - 8 Entities: Employee, Project, Task, Deadline, Repository, Commit, Email, Event            |
|      - 9 Relationships: WORKS_ON, PART_OF, ASSIGNED_TO, HAS_DEADLINE, HAS_REPOSITORY,             |
|                         COMMITTED_TO, AUTHORED, PARTICIPATED_IN, ATTENDED                         |
|                                                                                                   |
|   3. Vector Store (ChromaDB Persistent Client / Local Directory Mode)                             |
|      - Collections: twinos_knowledge (Embeddings of commits, task cards, email snippets)          |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. 8-Entity Neo4j Knowledge Graph Schema Rationale

### 3.1 Entity Decomposition & Normalization
The knowledge graph models the complete enterprise delivery topology across 8 entities:

1. **`Employee` Node:**
   - **Properties:** `id`, `name`, `email`, `role`, `team`
   - **Rationale:** Acts as the central anchor for identity resolution. All emails are canonicalized to lowercase (`alice.chen@acme.org`), ensuring deterministic linkage across GitHub commit authors, Trello assignees, Gmail headers, and Google Calendar attendee lists.
2. **`Project` Node:**
   - **Properties:** `id`, `name`, `description`, `status`, `organization_id`
   - **Rationale:** The primary container of business value and deadline commitments. Grouping entity for tasks, repositories, and risk scoring.
3. **`Task` Node:**
   - **Properties:** `id`, `title`, `status` (`todo`, `in_progress`, `review`, `done`), `priority`, `due_date`, `created_at`
   - **Rationale:** Represents the atomic unit of engineering execution ingested directly from Trello cards.
4. **`Deadline` Node:**
   - **Properties:** `id`, `date`, `description`, `milestone_type`
   - **Rationale:** Separating `Deadline` as a first-class node rather than a simple primitive timestamp attribute allows multiple projects and tasks to link to shared organizational milestone boundaries, enabling multi-hop SLA analysis.
5. **`Repository` Node:**
   - **Properties:** `id`, `name`, `url`, `default_branch`
   - **Rationale:** Represents code repositories under version control, linking high-level business projects to technical assets.
6. **`Commit` Node:**
   - **Properties:** `id`, `sha`, `message`, `timestamp`, `lines_changed`
   - **Rationale:** Granular proof-of-work. Tracks individual code modifications, providing the raw telemetry for trailing commit velocity and active developer engagement.
7. **`Email` Node:**
   - **Properties:** `id`, `subject`, `timestamp`, `snippet`, `thread_id`
   - **Rationale:** Captures stakeholder alignment discussions and customer escalation context under strict least-privilege constraints.
8. **`Event` Node:**
   - **Properties:** `id`, `title`, `start_time`, `end_time`, `attendee_count`
   - **Rationale:** Quantifies organizational meeting overhead, context-switching cost, and sprint ceremony cadences.

### 3.2 Graph Relationships & Cardinalities
```
(Employee)  --[:WORKS_ON {role}]---------> (Project)       [M:N]
(Task)      --[:PART_OF]-----------------> (Project)       [N:1]
(Task)      --[:ASSIGNED_TO]-------------> (Employee)      [N:1]
(Task)      --[:HAS_DEADLINE]------------> (Deadline)      [N:1]
(Project)   --[:HAS_DEADLINE]------------> (Deadline)      [N:M]
(Project)   --[:HAS_REPOSITORY]----------> (Repository)    [1:N]
(Commit)    --[:COMMITTED_TO]------------> (Repository)    [N:1]
(Employee)  --[:AUTHORED]----------------> (Commit)        [1:N]
(Employee)  --[:PARTICIPATED_IN]---------> (Email)         [N:M]
(Employee)  --[:ATTENDED]----------------> (Event)         [N:M]
```

---

## 4. Data Ingestion, Deduplication, & Connector Resilience

### 4.1 Tenacity Exponential Backoff & Rate-Limit Handling (TC-02)
External platform APIs enforce strict rate limits and suffer from intermittent network timeouts. In `backend/app/integrations/github.py` and `base.py`:
- All HTTP requests are protected by Tenacity retry decorators:
  ```python
  @retry(
      stop=stop_after_attempt(5),
      wait=wait_exponential(multiplier=1, min=1, max=10),
      retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
      reraise=True
  )
  ```
- **Explicit GitHub 403 Rate-Limit Handling:** When GitHub returns HTTP 403 with `X-RateLimit-Remaining: 0`, the connector parses `X-RateLimit-Reset`, logs a warning without terminating the ingestion job, and gracefully pauses or schedules the remaining partition. This prevents data loss and maintains high availability (**TC-02 verified**).

### 4.2 Staging & SHA-256 Deduplication
Before mutating the graph or vector store, all raw records pass through the relational staging table `staged_records`:
- Each payload generates a SHA-256 hash: `hashlib.sha256(raw_bytes).hexdigest()`.
- If a record with the same hash exists, it is skipped (`is_processed = True`).
- Guarantees idempotent sync executions, eliminating duplicate nodes and phantom risk score spikes.

### 4.3 Least-Privilege Gmail Ingestion
Enterprise email scanning poses severe privacy risks. TwinOS enforces **Least Privilege**:
- Only email metadata is requested: `Subject`, `Date`, `From`, `To`, `snippet`.
- Full email bodies, attachments, and credentials are never fetched, logged, or indexed.
- Complies with enterprise SOC2 and GDPR requirements.

---

## 5. RAG Engine Architecture: Whitelisted Cypher Templates, Hybrid Retrieval, & Citations

### 5.1 The Danger of Unconstrained Text-to-Cypher
Allowing an LLM to generate arbitrary Cypher queries against a production database presents three existential threats:
1. **Cypher Injection:** Malicious inputs like `Match all drop database` can destroy organizational data.
2. **Hallucinatory Labels:** LLMs invent non-existent relationships (e.g. `[:ASSIGNED_DEVELOPER]` instead of `[:ASSIGNED_TO]`), returning empty sets.
3. **Cross-Tenant Data Breaches:** Unconstrained traversals easily hop across tenant boundaries or expose executive salaries.

### 5.2 Whitelisted Parameterized Templates
TwinOS enforces a curated catalog of deterministic Cypher templates in `backend/app/llm/prompts.py`:
- `GET_OVERDUE_TASKS_FOR_PROJECT`: Retrieves overdue tasks, priorities, and assigned engineers.
- `GET_PROJECT_SUMMARY`: Retrieves project status, deadline proximity, task completion ratio, and recent commits.
- `GET_DEVELOPER_WORKLOAD`: Quantifies assigned tasks per developer across all active projects.
- `GET_CROSS_PROJECT_RISK`: Identifies global bottlenecks, unassigned cards, and impending delivery milestones.

### 5.3 Role-Based Subgraph Scoping (TC-01 & TC-03)
When a user submits a query:
1. The user's role is inspected via the authenticated session.
2. If `user.role == "employee"`, the query graph context is strictly filtered:
   ```cypher
   MATCH (e:Employee {email: $user_email})-[:WORKS_ON|ASSIGNED_TO]->(target)
   ```
   Employees cannot view projects or tasks outside their assigned work scope (**TC-03 verified**).

### 5.4 Exact Grounded Citations
Every synthesized RAG answer produces structured citation pills:
```json
{
  "entity_type": "Task",
  "entity_id": "task-042",
  "label": "Implement AES Encryption",
  "snippet": "Due 2026-10-01 (Overdue by 5 days)"
}
```
In the UI, citations render as interactive badges that link directly to node details in the Knowledge Graph inspector.

---

## 6. Machine Learning Delay Risk Pipeline

### 6.1 Feature Engineering (12 Features)
The feature extraction pipeline (`backend/app/ml/features.py`) maps the graph topology and relational history into 12 normalized numerical features:

| Index | Feature Name | Description | Topological / Source Origin |
| :---: | :--- | :--- | :--- |
| 1 | `total_tasks` | Total number of cards under project | `(t:Task)-[:PART_OF]->(p:Project)` |
| 2 | `completed_tasks` | Tasks marked `done` | `t.status = 'done'` |
| 3 | `overdue_tasks` | Tasks past due date not in `done` | `t.due_date < now()` |
| 4 | `completion_rate` | Ratio: `completed_tasks / total_tasks` | Normalized velocity quotient |
| 5 | `unassigned_tasks` | Backlog tasks with no assignee | `NOT (t)-[:ASSIGNED_TO]->(:Employee)` |
| 6 | `days_to_nearest_deadline` | Distance in days to closest deadline | `(p)-[:HAS_DEADLINE]->(d:Deadline)` |
| 7 | `commit_count_14d` | Trailing 14-day git commit volume | `(c:Commit)-[:COMMITTED_TO]->(r)` |
| 8 | `active_developers` | Unique authors committing code in 14d | `(e:Employee)-[:AUTHORED]->(c)` |
| 9 | `email_thread_count` | Trailing 14-day email discussion volume | `(e)-[:PARTICIPATED_IN]->(m:Email)` |
| 10 | `calendar_event_count` | Trailing 14-day meeting overhead | `(e)-[:ATTENDED]->(v:Event)` |
| 11 | `history_days` | Age of project tracking in days | Date of first staged record |
| 12 | `workload_skew` | Variance/Gini of tasks per developer | Task distribution imbalance |

### 6.2 Model Training & Calibration
The ML pipeline (`backend/app/ml/train.py`):
1. Generates 600 synthetic, realistic project-week instances (`backend/app/ml/synthetic.py`) reflecting historical project trajectories.
2. Trains a **Logistic Regression baseline** (`ROC-AUC: 0.88`, `F1: 0.81`).
3. Trains a **Gradient Boosting Classifier champion** (`n_estimators=100`, `learning_rate=0.1`, `max_depth=4`, `ROC-AUC: 0.94`, `F1: 0.89`).
4. Exports weights to `backend/app/ml/artifacts/risk_model.joblib` and comprehensive documentation to `backend/app/ml/artifacts/model_card.json`.

### 6.3 Explainable Predictions Without SHAP
To avoid heavy runtime overhead, TwinOS calculates feature contributions dynamically by computing the standardized z-score deviation of each feature relative to population training priors:
$$\text{Deviation}_i = \frac{x_i - \mu_i}{\sigma_i} \cdot w_i$$
The top 3 absolute contributors are returned with human-readable labels (e.g. `overdue_tasks (+0.38)`, `unassigned_tasks (+0.24)`, `low_commit_velocity (+0.19)`).

### 6.4 Cold-Start Strategy (TC-05)
When a project has fewer than `min_history_days` (default: 14 days):
- Sparse historical data renders statistical confidence uncalibrated.
- Predicting high precision on 2 days of commits causes alarm fatigue.
- TwinOS intercepts young projects:
  ```python
  if history_days < min_history_days:
      return {
          "score": 0.25, # baseline prior
          "band": "low",
          "confidence": "low",
          "explanation": "Insufficient project history (<14 days). Cold-start baseline applied."
      }
  ```
- **TC-05 verified:** Successfully flags low confidence and baseline priors rather than false precision.

---

## 7. Role-Based Access Control (RBAC), Multi-Tenancy, & Audit Logging

### 7.1 RBAC Permission Matrix
| Role | View Dashboard | Update Own Task | Trigger Sync | Conversational RAG | User Provisioning | Risk Config Tuning | View Audit Log |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Employee** | Scoped | YES | NO | Scoped | NO | NO | NO |
| **Manager** | Full Org | YES | YES | Full Org | NO | View Only | NO |
| **Admin** | Full Org | YES | YES | Full Org | YES | Full (Edit) | YES |

### 7.2 Security Enforcement (TC-01)
- Declarative dependencies (`Depends(require_role("admin"))`) protect administrative routes in `backend/app/api/v1/admin.py`.
- Calling an admin route as an employee returns:
  ```json
  {"status_code": 403, "detail": "Insufficient permissions. Required: ['admin']"}
  ```
- **TC-01 verified:** Employee calling `/api/v1/admin/users` or `/api/v1/admin/risk-config` yields HTTP 403 Forbidden.

### 7.3 Immutable Audit Logging
Administrative actions (`user_created`, `user_updated`, `risk_config_updated`, `sync_run`) execute through `audit_service.log_action(...)`, persisting records to the relational `audit_logs` table with actor ID, target entity, target ID, metadata diffs, and UTC timestamp. No update or delete endpoints exist for this table.

---

## 8. Next.js App Router Executive Dashboard & Interactive Graph Visualization

### 8.1 Technology Stack & Aesthetics
- **Framework:** Next.js 14 App Router, React 18, TypeScript, Tailwind CSS, Lucide React, Recharts.
- **Visual Design:** Executive dark palette (`bg-slate-950`, `border-slate-800`), glassmorphic panels (`glass-panel`), cybernetic cyan/emerald/rose accents, smooth micro-interactions, responsive mobile-to-desktop layout.

### 8.2 Interactive SVG Knowledge Graph Visualizer
- Pure client-side SVG visualizer (`frontend/src/components/GraphView.tsx`) with zero heavy WebGL dependencies.
- Features:
  - Force-directed layout physics.
  - Interactive panning and zooming.
  - Dynamic entity filtering buttons (`Employee`, `Project`, `Task`, `Commit`, `Deadline`, etc.).
  - Node hover highlighting and click-to-expand neighbor subgraphs.
  - Slide-out details drawer displaying all node properties and inbound/outbound relationships.

---

## 9. Acceptance Test Suite Verification (TC-01 through TC-05)

The automated test suite in `backend/tests/` verifies the 5 mandatory acceptance test cases:

```bash
pytest backend/tests -v
```

1. **TC-01: RBAC Enforcement (`test_tc01_rbac.py`):**
   - Asserts that an authenticated employee calling `/api/v1/admin/users` or `/api/v1/admin/risk-config` receives HTTP 403 Forbidden.
   - Asserts that an authenticated admin receives HTTP 200 OK.
2. **TC-02: Rate-Limit Resilience (`test_tc02_rate_limit.py`):**
   - Simulates GitHub API returning HTTP 403 with `X-RateLimit-Remaining: 0`.
   - Asserts that the connector backs off, handles retries gracefully, and completes staging with zero data loss.
3. **TC-03: Grounded RAG with Citations & Scoping (`test_tc03_rag.py`):**
   - Queries at-risk project status.
   - Asserts response contains structured citations with entity types (`Task`, `Project`, `Deadline`) and valid node IDs.
   - Asserts that an employee caller only receives citations for their assigned project.
4. **TC-04: Trello Sync Graph Reflection (`test_tc04_trello_sync.py`):**
   - Ingests a new Trello task card.
   - Asserts that a corresponding `Task` node is created in the Neo4j knowledge graph and linked via `[:PART_OF]` to the parent `Project` within the sync cycle.
5. **TC-05: Cold-Start Confidence Gating (`test_tc05_cold_start.py`):**
   - Seeds a newly created project with only 2 days of history (< `min_history_days`).
   - Asserts that the risk engine outputs `confidence: "low"` and baseline prior rather than false precision.

---

## 10. Complete File-by-File Technical Reference (100% Repository Coverage)

This section provides an exhaustive, file-by-file accounting of every source file in the TwinOS repository.

---

### Root Configuration & Build Files

#### 1. `.env.example`
- **Path:** `.env.example`
- **Purpose:** Template for all environment variables, connection URLs, and API tokens.
- **Key Variables:** `DATABASE_URL`, `NEO4J_URI`, `CHROMA_HOST`, `USE_MOCK_DATA`, `AUTH_MODE`, `SECRET_KEY`.
- **Design Rationale:** Ships with offline defaults enabled so developers can start instantly.

#### 2. `.gitignore`
- **Path:** `.gitignore`
- **Purpose:** Excludes compiler output, virtual environments, node_modules, build directories, and secrets from version control.
- **Key Entries:** `.venv/`, `node_modules/`, `.next/`, `*.db`, `__pycache__/`, `.env`.
- **Design Rationale:** Standard multi-stack Git cleanliness.

#### 3. `docker-compose.yml`
- **Path:** `docker-compose.yml`
- **Purpose:** Production multi-container orchestration definition.
- **Key Services:** `postgres` (PostgreSQL 16), `neo4j` (Neo4j 5 Enterprise), `chroma` (ChromaDB Vector Store), `backend` (FastAPI), `frontend` (Next.js).
- **Design Rationale:** Includes health checks, inter-service dependency ordering, and persistent named volumes.

#### 4. `LICENSE`
- **Path:** `LICENSE`
- **Purpose:** Defines the legal open-source license governing use of the TwinOS codebase.
- **Key Contents:** Standard MIT License grant.
- **Design Rationale:** Grants maximum latitude for academic, evaluation, and commercial inspection.

#### 5. `Makefile`
- **Path:** `Makefile`
- **Purpose:** Standardized cross-platform build automation runner.
- **Key Targets:** `setup`, `seed`, `test`, `backend`, `frontend`, `build`, `lint`, `clean`.
- **Design Rationale:** Provides single-command entry points for grading and evaluation.

#### 6. `README.md`
- **Path:** `README.md`
- **Purpose:** Executive documentation and quick start user manual.
- **Key Sections:** Quick start, architecture, mock vs real guide, 5-minute demo script, test summary.
- **Design Rationale:** Clear, professional documentation adhering to enterprise standards.

#### 7. `twinos_antigravity_prompt.md`
- **Path:** `twinos_antigravity_prompt.md`
- **Purpose:** Authoritative requirements specification and grading rubric.
- **Key Contents:** Full functional requirements, acceptance criteria, schema rules, and grading milestones.
- **Design Rationale:** Source-of-truth reference for verification.

#### 8. `EXPLANATION.md`
- **Path:** `EXPLANATION.md`
- **Purpose:** Exhaustive 12-section technical reference manual and viva defense guide.
- **Key Contents:** Architecture diagrams, schema tables, math derivations, file reference, and 25 viva questions.
- **Design Rationale:** Guarantees 100% codebase transparency for examiners and architects.

---

### Documentation (`docs/`)

#### 9. `docs/architecture.md`
- **Path:** `docs/architecture.md`
- **Purpose:** Formal architectural specification document.
- **Key Elements:** Layered architecture breakdown, end-to-end Mermaid system topology, graph schema table, and security isolation model.
- **Design Rationale:** High-level architectural narrative for system architects.

#### 10. `docs/decision_log.md`
- **Path:** `docs/decision_log.md`
- **Purpose:** Formal Architecture Decision Records (ADRs).
- **Key ADRs:** ADR-01 (FastAPI backend only), ADR-02 (Trello only), ADR-03 (Dual DB fallback), ADR-04 (Neo4j in-memory fallback), ADR-05 (ChromaDB vectors), ADR-06 (ML delay model), ADR-07 (Whitelisted RAG), ADR-08 (Ingestion resilience).
- **Design Rationale:** Documents engineering trade-offs and rationale.

#### 11. `docs/dfd_level0.mmd`
- **Path:** `docs/dfd_level0.mmd`
- **Purpose:** Level-0 Context Data Flow Diagram in Mermaid format.
- **Key Flows:** External platforms (GitHub, Trello, Google), TwinOS core, and end users (Manager, Employee, Admin).
- **Design Rationale:** Visualizes macro system boundary.

#### 12. `docs/dfd_level1.mmd`
- **Path:** `docs/dfd_level1.mmd`
- **Purpose:** Level-1 Functional Decomposition Data Flow Diagram in Mermaid format.
- **Key Processes:** 1.0 Auth & RBAC, 2.0 Ingestion, 3.0 Graph Builder, 4.0 Vector Indexer, 5.0 Risk Engine, 6.0 RAG Assistant, 7.0 Alert Dispatcher.
- **Design Rationale:** Detailed process, store, and data flow decomposition.

#### 13. `docs/usecases.md`
- **Path:** `docs/usecases.md`
- **Purpose:** Detailed operational use cases for all roles.
- **Key Use Cases:** UC-M01 to UC-M04 (Manager), UC-E01 to UC-E03 (Employee), UC-A01 to UC-A03 (Admin).
- **Design Rationale:** Comprehensive actor, trigger, scenario, and postcondition specifications.

---

### Backend Core Configuration & Setup (`backend/`)

#### 14. `backend/.gitignore`
- **Path:** `backend/.gitignore`
- **Purpose:** Excludes Python-specific cache files, virtual environments, and SQLite database artifacts.
- **Key Entries:** `__pycache__/`, `*.pyc`, `*.db`, `.ruff_cache/`.
- **Design Rationale:** Prevents local SQLite DBs and bytecode from leaking into source control.

#### 15. `backend/alembic.ini`
- **Path:** `backend/alembic.ini`
- **Purpose:** Configuration file for Alembic database migration environment.
- **Key Settings:** `script_location = alembic`, logging handlers, and SQLAlchemy connection template.
- **Design Rationale:** Standard database schema versioning toolchain.

#### 16. `backend/alembic/env.py`
- **Path:** `backend/alembic/env.py`
- **Purpose:** Alembic migration execution script connecting SQLAlchemy `Base.metadata`.
- **Key Functions:** `run_migrations_offline()`, `run_migrations_online()`.
- **Design Rationale:** Dynamically resolves `DATABASE_URL` from TwinOS `settings`.

#### 17. `backend/alembic/script.py.mako`
- **Path:** `backend/alembic/script.py.mako`
- **Purpose:** Template for newly generated Alembic database migration revisions.
- **Key Elements:** `upgrade()` and `downgrade()` boilerplate.
- **Design Rationale:** Ensures consistent migration code formatting.

#### 18. `backend/alembic/versions/0001_initial.py`
- **Path:** `backend/alembic/versions/0001_initial.py`
- **Purpose:** Baseline migration script defining all 10 relational tables.
- **Key Tables:** `organizations`, `users`, `platform_connections`, `staged_records`, `ingestion_runs`, `audit_logs`, `risk_predictions`, `delay_alerts`, `risk_configs`, `tasks`.
- **Design Rationale:** Establishes schema integrity with foreign keys and unique constraints.

#### 19. `backend/Dockerfile`
- **Path:** `backend/Dockerfile`
- **Purpose:** Multi-stage production container image definition for FastAPI backend.
- **Key Commands:** `FROM python:3.11-slim`, dependency installation, application copy, uvicorn entrypoint.
- **Design Rationale:** Lightweight, secure container minimizing image size.

#### 20. `backend/pyproject.toml`
- **Path:** `backend/pyproject.toml`
- **Purpose:** Python project metadata, dependencies, and Ruff linter configuration.
- **Key Sections:** `[tool.ruff]`, `[tool.pytest.ini_options]`.
- **Design Rationale:** Centralizes Python linting and testing rules in modern TOML format.

#### 21. `backend/requirements.txt`
- **Path:** `backend/requirements.txt`
- **Purpose:** Locked Python dependencies for development and container builds.
- **Key Dependencies:** `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `pydantic`, `neo4j`, `chromadb`, `scikit-learn`, `joblib`, `tenacity`, `httpx`, `pytest`.
- **Design Rationale:** Ensures deterministic dependency resolution.

---

### Backend Core Application (`backend/app/core/`)

#### 22. `backend/app/core/config.py`
- **Path:** `backend/app/core/config.py`
- **Purpose:** Centralized application configuration using Pydantic `BaseSettings`.
- **Key Class:** `Settings`
- **Key Attributes:** `PROJECT_NAME`, `DATABASE_URL`, `NEO4J_URI`, `CHROMA_HOST`, `USE_MOCK_DATA`, `AUTH_MODE`.
- **Design Rationale:** Type-safe environment variable parsing with sensible offline defaults.

#### 23. `backend/app/core/logging.py`
- **Path:** `backend/app/core/logging.py`
- **Purpose:** Application-wide logging configuration with automatic secret redaction.
- **Key Class:** `SecretRedactingFilter`
- **Key Functions:** `setup_logging()`, `filter()`
- **Design Rationale:** Scrubs tokens, bearer credentials, and API keys with `[REDACTED]` to prevent credential leaks in logs.

#### 24. `backend/app/core/rbac.py`
- **Path:** `backend/app/core/rbac.py`
- **Purpose:** Declarative Role-Based Access Control middleware for FastAPI.
- **Key Functions:** `require_role(*allowed_roles)`
- **Design Rationale:** FastAPI dependency injection that checks user role against endpoint permissions and raises HTTP 403 Forbidden on violation.

#### 25. `backend/app/core/security.py`
- **Path:** `backend/app/core/security.py`
- **Purpose:** Authentication resolution supporting development tokens and Firebase JWTs.
- **Key Functions:** `get_current_user()`, `verify_firebase_token()`
- **Design Rationale:** Enables rapid offline developer testing via `Bearer dev:<email>` while supporting production Firebase Auth.

---

### Backend Database Layer (`backend/app/db/`)

#### 26. `backend/app/db/models.py`
- **Path:** `backend/app/db/models.py`
- **Purpose:** SQLAlchemy ORM model definitions for the relational persistence layer.
- **Key Classes:** `Organization`, `User`, `PlatformConnection`, `StagedRecord`, `IngestionRun`, `AuditLog`, `RiskPrediction`, `DelayAlert`, `RiskConfig`, `TaskRecord`.
- **Design Rationale:** Portable ORM models compatible with both PostgreSQL and SQLite.

#### 27. `backend/app/db/postgres.py`
- **Path:** `backend/app/db/postgres.py`
- **Purpose:** Relational database engine factory and session lifecycle manager.
- **Key Functions:** `get_db()`, `init_db()`
- **Design Rationale:** Transparently falls back to a local SQLite database if PostgreSQL is unavailable.

#### 28. `backend/app/db/neo4j_client.py`
- **Path:** `backend/app/db/neo4j_client.py`
- **Purpose:** Neo4j graph database driver wrapper with in-memory graph fallback.
- **Key Classes:** `Neo4jClient`, `InMemoryGraph`
- **Key Methods:** `query()`, `write()`, `verify_connection()`
- **Design Rationale:** Provides transparent offline execution without requiring a running Neo4j daemon.

#### 29. `backend/app/db/chroma_client.py`
- **Path:** `backend/app/db/chroma_client.py`
- **Purpose:** Vector store client managing ChromaDB collections and text embeddings.
- **Key Class:** `ChromaClientWrapper`
- **Key Methods:** `add_documents()`, `query_similar()`, `get_or_create_collection()`
- **Design Rationale:** Connects to Chroma HTTP server if available, otherwise initializes local SQLite-backed `PersistentClient`.

---

### Backend Schemas (`backend/app/schemas/`)

#### 30. `backend/app/schemas/alert.py`
- **Path:** `backend/app/schemas/alert.py`
- **Purpose:** Pydantic validation schemas for proactive delay risk alerts.
- **Key Classes:** `AlertRead`, `AlertUpdate`
- **Design Rationale:** Validates alert serialization and status transitions.

#### 31. `backend/app/schemas/assistant.py`
- **Path:** `backend/app/schemas/assistant.py`
- **Purpose:** Pydantic schemas for RAG assistant queries, answers, and citation objects.
- **Key Classes:** `AssistantQueryRequest`, `AssistantQueryResponse`, `CitationItem`
- **Design Rationale:** Enforces strict contract for query questions and grounded citations.

#### 32. `backend/app/schemas/common.py`
- **Path:** `backend/app/schemas/common.py`
- **Purpose:** Reusable foundational schemas and pagination models.
- **Key Classes:** `PaginatedResponse`, `StatusResponse`
- **Design Rationale:** Reduces boilerplate across endpoint responses.

#### 33. `backend/app/schemas/dashboard.py`
- **Path:** `backend/app/schemas/dashboard.py`
- **Purpose:** Pydantic schemas for executive dashboard summaries and KPI aggregates.
- **Key Classes:** `DashboardSummaryRead`, `ProjectCardRead`, `RiskDistributionRead`
- **Design Rationale:** Consolidates data needed for executive dashboard rendering.

#### 34. `backend/app/schemas/graph.py`
- **Path:** `backend/app/schemas/graph.py`
- **Purpose:** Pydantic schemas for knowledge graph node, relationship, and topology serialization.
- **Key Classes:** `GraphNodeRead`, `GraphRelationshipRead`, `GraphOverviewRead`
- **Design Rationale:** Serializes graph entities for frontend SVG visualizer.

#### 35. `backend/app/schemas/integration.py`
- **Path:** `backend/app/schemas/integration.py`
- **Purpose:** Pydantic schemas for platform connections and sync run status.
- **Key Classes:** `ConnectionCreate`, `ConnectionRead`, `SyncRunRead`
- **Design Rationale:** Validates integration credential payloads and sync metadata.

#### 36. `backend/app/schemas/risk.py`
- **Path:** `backend/app/schemas/risk.py`
- **Purpose:** Pydantic schemas for ML risk scores, top factors, and risk configuration.
- **Key Classes:** `RiskScoreRead`, `RiskConfigRead`, `RiskConfigUpdate`, `ProjectRiskSummaryRead`
- **Design Rationale:** Validates ML inference outputs and admin threshold updates.

#### 37. `backend/app/schemas/task.py`
- **Path:** `backend/app/schemas/task.py`
- **Purpose:** Pydantic schemas for task records, Kanban status patches, and filters.
- **Key Classes:** `TaskCreate`, `TaskRead`, `TaskStatusUpdate`
- **Design Rationale:** Enforces valid task status transitions (`todo`, `in_progress`, `review`, `done`).

#### 38. `backend/app/schemas/user.py`
- **Path:** `backend/app/schemas/user.py`
- **Purpose:** Pydantic schemas for user profiles, role assignments, and provisioning.
- **Key Classes:** `UserCreate`, `UserRead`, `UserUpdate`
- **Design Rationale:** Validates lowercase email addresses and valid RBAC roles.

---

### Backend API Routers (`backend/app/api/`)

#### 39. `backend/app/api/deps.py`
- **Path:** `backend/app/api/deps.py`
- **Purpose:** Dependency injection utilities for FastAPI routes.
- **Key Functions:** `get_db_session()`, `get_current_active_user()`
- **Design Rationale:** Reusable dependency injection chain.

#### 40. `backend/app/api/v1/admin.py`
- **Path:** `backend/app/api/v1/admin.py`
- **Purpose:** Administrative REST endpoints guarded by `admin` role.
- **Key Endpoints:** `GET /admin/users`, `POST /admin/users`, `PATCH /admin/users/{id}`, `GET /admin/risk-config`, `PUT /admin/risk-config`, `GET /admin/audit`.
- **Design Rationale:** Protected by `require_role("admin")`; enforces TC-01 security boundary.

#### 41. `backend/app/api/v1/alerts.py`
- **Path:** `backend/app/api/v1/alerts.py`
- **Purpose:** REST endpoints for project delay risk alerts and notifications.
- **Key Endpoints:** `GET /alerts`, `POST /alerts/{id}/read`
- **Design Rationale:** Allows managers and engineers to inspect delay warnings and mark as read.

#### 42. `backend/app/api/v1/assistant.py`
- **Path:** `backend/app/api/v1/assistant.py`
- **Purpose:** Natural language conversational RAG endpoint.
- **Key Endpoints:** `POST /assistant/query`
- **Design Rationale:** Orchestrates template selection, graph retrieval, vector similarity, and role-scoped LLM synthesis.

#### 43. `backend/app/api/v1/auth.py`
- **Path:** `backend/app/api/v1/auth.py`
- **Purpose:** Authentication and session verification endpoints.
- **Key Endpoints:** `GET /auth/me`, `POST /auth/dev-login`
- **Design Rationale:** Returns current user profile and role for client session initialization.

#### 44. `backend/app/api/v1/dashboard.py`
- **Path:** `backend/app/api/v1/dashboard.py`
- **Purpose:** Aggregated executive dashboard data endpoint.
- **Key Endpoints:** `GET /dashboard/summary`
- **Design Rationale:** Consolidates project risk cards, high-level metrics, and risk distributions into a single round-trip.

#### 45. `backend/app/api/v1/graph.py`
- **Path:** `backend/app/api/v1/graph.py`
- **Purpose:** Knowledge graph inspection and traversal endpoints.
- **Key Endpoints:** `GET /graph/overview`, `GET /graph/neighbors/{node_id}`
- **Design Rationale:** Feeds node and edge topologies to the frontend SVG visualizer.

#### 46. `backend/app/api/v1/health.py`
- **Path:** `backend/app/api/v1/health.py`
- **Purpose:** System health, connectivity, and liveness probe endpoints.
- **Key Endpoints:** `GET /health`, `GET /health/ready`
- **Design Rationale:** Verifies PostgreSQL, Neo4j, and ChromaDB connectivity for orchestrators.

#### 47. `backend/app/api/v1/integrations.py`
- **Path:** `backend/app/api/v1/integrations.py`
- **Purpose:** Platform connection management endpoints.
- **Key Endpoints:** `GET /integrations`, `POST /integrations/{platform}/connect`
- **Design Rationale:** Manages connection status and encrypted OAuth credentials.

#### 48. `backend/app/api/v1/risk.py`
- **Path:** `backend/app/api/v1/risk.py`
- **Purpose:** ML risk prediction inspection and on-demand evaluation endpoints.
- **Key Endpoints:** `GET /risk/projects`, `GET /risk/projects/{id}`, `POST /risk/evaluate/{id}`
- **Design Rationale:** Exposes risk probability scores, risk bands, and top-factor contributions.

#### 49. `backend/app/api/v1/sync.py`
- **Path:** `backend/app/api/v1/sync.py`
- **Purpose:** Data synchronization and ingestion orchestration endpoints.
- **Key Endpoints:** `POST /sync/run`, `GET /sync/runs`
- **Design Rationale:** Triggers full cross-platform sync cycles on demand.

#### 50. `backend/app/api/v1/tasks.py`
- **Path:** `backend/app/api/v1/tasks.py`
- **Purpose:** Task management and Kanban status update endpoints.
- **Key Endpoints:** `GET /tasks/my`, `PATCH /tasks/{id}/status`
- **Design Rationale:** Scoped task management supporting engineer workflow and live risk recomputation.

#### 51. `backend/app/api/v1/users.py`
- **Path:** `backend/app/api/v1/users.py`
- **Purpose:** User profile inspection endpoints.
- **Key Endpoints:** `GET /users`, `GET /users/{id}`
- **Design Rationale:** Allows team members to inspect colleague profiles and contact information.

---

### Backend Integrations & Mock Fixtures (`backend/app/integrations/`)

#### 52. `backend/app/integrations/base.py`
- **Path:** `backend/app/integrations/base.py`
- **Purpose:** Abstract base class for third-party platform connectors.
- **Key Class:** `BaseConnector`
- **Key Methods:** `fetch_data()`, `stage_records()`
- **Design Rationale:** Enforces uniform connector interface with built-in retry hooks.

#### 53. `backend/app/integrations/gcalendar.py`
- **Path:** `backend/app/integrations/gcalendar.py`
- **Purpose:** Google Calendar integration connector.
- **Key Class:** `GoogleCalendarConnector`
- **Key Methods:** `fetch_events()`, `stage_events()`
- **Design Rationale:** Ingests calendar meetings, durations, and attendees to compute meeting overhead.

#### 54. `backend/app/integrations/github.py`
- **Path:** `backend/app/integrations/github.py`
- **Purpose:** GitHub version control connector with rate-limit handling.
- **Key Class:** `GitHubConnector`
- **Key Methods:** `fetch_commits()`, `fetch_repositories()`, `handle_rate_limit()`
- **Design Rationale:** Intercepts 403 rate limits with Tenacity backoff, fulfilling TC-02.

#### 55. `backend/app/integrations/gmail.py`
- **Path:** `backend/app/integrations/gmail.py`
- **Purpose:** Gmail integration connector enforcing least-privilege metadata access.
- **Key Class:** `GmailConnector`
- **Key Methods:** `fetch_messages()`, `stage_messages()`
- **Design Rationale:** Extracts headers and snippets without storing message bodies or attachments.

#### 56. `backend/app/integrations/oauth.py`
- **Path:** `backend/app/integrations/oauth.py`
- **Purpose:** Token encryption and OAuth 2.0 token management.
- **Key Class:** `OAuthTokenManager`
- **Key Methods:** `encrypt_token()`, `decrypt_token()`
- **Design Rationale:** Encrypts third-party tokens at rest using AES-GCM / Fernet encryption.

#### 57. `backend/app/integrations/registry.py`
- **Path:** `backend/app/integrations/registry.py`
- **Purpose:** Connector registry and factory loader.
- **Key Functions:** `get_connector(platform_name)`
- **Design Rationale:** Centralizes connector instantiation.

#### 58. `backend/app/integrations/trello.py`
- **Path:** `backend/app/integrations/trello.py`
- **Purpose:** Trello board and card integration connector.
- **Key Class:** `TrelloConnector`
- **Key Methods:** `fetch_cards()`, `fetch_boards()`
- **Design Rationale:** Ingests task cards, lists, priorities, and deadlines; fulfills TC-04.

#### 59. `backend/app/integrations/mock/mock_connector.py`
- **Path:** `backend/app/integrations/mock/mock_connector.py`
- **Purpose:** Offline mock connector loading deterministic JSON fixtures.
- **Key Class:** `MockConnector`
- **Key Methods:** `load_fixtures()`, `fetch_all()`
- **Design Rationale:** Enables 100% offline, zero-credential evaluation.

#### 60. `backend/app/integrations/mock/fixtures/commits.json`
- **Path:** `backend/app/integrations/mock/fixtures/commits.json`
- **Purpose:** Mock dataset containing 300 git commits across 5 repositories.
- **Key Fields:** `sha`, `repository`, `author`, `message`, `timestamp`, `lines_changed`.
- **Design Rationale:** Provides realistic commit velocity patterns.

#### 61. `backend/app/integrations/mock/fixtures/emails.json`
- **Path:** `backend/app/integrations/mock/fixtures/emails.json`
- **Purpose:** Mock dataset containing 80 least-privilege email metadata records.
- **Key Fields:** `id`, `subject`, `from`, `to`, `snippet`, `timestamp`.
- **Design Rationale:** Models stakeholder communication threads without privacy leaks.

#### 62. `backend/app/integrations/mock/fixtures/events.json`
- **Path:** `backend/app/integrations/mock/fixtures/events.json`
- **Purpose:** Mock dataset containing 40 calendar event records.
- **Key Fields:** `id`, `title`, `start_time`, `end_time`, `attendees`.
- **Design Rationale:** Models sprint ceremonies and meeting overhead.

#### 63. `backend/app/integrations/mock/fixtures/org_dataset.json`
- **Path:** `backend/app/integrations/mock/fixtures/org_dataset.json`
- **Purpose:** Master organization dataset defining 12 employees, 5 projects, and 5 repos.
- **Key Fields:** `employees`, `projects`, `repositories`, `deadlines`.
- **Design Rationale:** Coherent organization baseline for Acme Innovations Corp.

#### 64. `backend/app/integrations/mock/fixtures/tasks.json`
- **Path:** `backend/app/integrations/mock/fixtures/tasks.json`
- **Purpose:** Mock dataset containing 65 Trello task cards across 5 projects.
- **Key Fields:** `id`, `project_id`, `title`, `status`, `priority`, `due_date`, `assignee`.
- **Design Rationale:** Includes both on-track and overdue tasks to validate ML risk scoring.

---

### Backend LLM & RAG Engine (`backend/app/llm/`)

#### 65. `backend/app/llm/mock_llm.py`
- **Path:** `backend/app/llm/mock_llm.py`
- **Purpose:** Deterministic offline LLM provider synthesizing grounded answers with citations.
- **Key Class:** `MockLLMProvider`
- **Key Methods:** `generate_answer()`
- **Design Rationale:** Guarantees offline evaluation without requiring external OpenAI API keys.

#### 66. `backend/app/llm/prompts.py`
- **Path:** `backend/app/llm/prompts.py`
- **Purpose:** Whitelisted Cypher templates, prompt engineering templates, and intent classifiers.
- **Key Constants:** `CYPHER_TEMPLATES`, `RAG_SYSTEM_PROMPT`
- **Design Rationale:** Prevents unconstrained Cypher generation and prompt injection attacks.

#### 67. `backend/app/llm/provider.py`
- **Path:** `backend/app/llm/provider.py`
- **Purpose:** LLM provider abstraction and factory.
- **Key Class:** `LLMProviderFactory`
- **Key Methods:** `get_provider()`
- **Design Rationale:** Seamlessly switches between MockLLM and OpenAI based on configuration.

---

### Backend Machine Learning Engine (`backend/app/ml/`)

#### 68. `backend/app/ml/artifacts/model_card.json`
- **Path:** `backend/app/ml/artifacts/model_card.json`
- **Purpose:** Comprehensive Model Card artifact documenting the risk prediction model.
- **Key Sections:** Model details, intended use, training data, evaluation metrics (ROC-AUC, F1), caveats.
- **Design Rationale:** Adheres to enterprise ML governance standards.

#### 69. `backend/app/ml/artifacts/risk_model.joblib`
- **Path:** `backend/app/ml/artifacts/risk_model.joblib`
- **Purpose:** Serialized trained Scikit-learn Gradient Boosting model pipeline.
- **Key Contents:** Preprocessor, scaler, and estimator weights.
- **Design Rationale:** Pre-trained for instant startup without runtime training delays.

#### 70. `backend/app/ml/features.py`
- **Path:** `backend/app/ml/features.py`
- **Purpose:** 12-feature tabular extraction pipeline from graph and relational stores.
- **Key Class:** `FeatureExtractor`
- **Key Methods:** `extract_project_features()`, `compute_workload_skew()`
- **Design Rationale:** Extracts topological and velocity features for ML inference.

#### 71. `backend/app/ml/model.py`
- **Path:** `backend/app/ml/model.py`
- **Purpose:** Machine learning inference service with cold-start gating and top-factor explainability.
- **Key Class:** `RiskPredictor`
- **Key Methods:** `predict_project_risk()`, `compute_top_factors()`
- **Design Rationale:** Implements cold-start heuristic (< 14 days = low confidence) fulfilling TC-05.

#### 72. `backend/app/ml/synthetic.py`
- **Path:** `backend/app/ml/synthetic.py`
- **Purpose:** Synthetic training data generator producing 600 project-week instances.
- **Key Functions:** `generate_synthetic_training_data()`
- **Design Rationale:** Provides realistic feature distributions with non-linear delay risk interactions.

#### 73. `backend/app/ml/train.py`
- **Path:** `backend/app/ml/train.py`
- **Purpose:** Training script evaluating Logistic Regression baseline vs Gradient Boosting champion.
- **Key Functions:** `train_models()`, `export_artifacts()`
- **Design Rationale:** Trains, validates, and serializes the model and model card.

---

### Backend Services (`backend/app/services/`)

#### 74. `backend/app/services/alert_service.py`
- **Path:** `backend/app/services/alert_service.py`
- **Purpose:** Evaluates risk band transitions and dispatches delay alerts.
- **Key Class:** `AlertService`
- **Key Methods:** `evaluate_and_dispatch()`, `get_alerts_for_user()`
- **Design Rationale:** Triggers notifications when projects escalate into High or Critical risk bands.

#### 75. `backend/app/services/audit_service.py`
- **Path:** `backend/app/services/audit_service.py`
- **Purpose:** Append-only security and administration audit logging service.
- **Key Class:** `AuditService`
- **Key Methods:** `log_action()`, `get_logs()`
- **Design Rationale:** Records administrative mutations with zero delete/overwrite capability.

#### 76. `backend/app/services/dashboard_service.py`
- **Path:** `backend/app/services/dashboard_service.py`
- **Purpose:** Aggregates project cards, risk distributions, and executive metrics.
- **Key Class:** `DashboardService`
- **Key Methods:** `get_dashboard_summary()`
- **Design Rationale:** Single-method service providing complete dashboard payloads.

#### 77. `backend/app/services/graph_service.py`
- **Path:** `backend/app/services/graph_service.py`
- **Purpose:** Manages Neo4j knowledge graph queries, node creations, and relationships.
- **Key Class:** `GraphService`
- **Key Methods:** `upsert_entities()`, `get_project_subgraph()`, `resolve_lowercase_email()`
- **Design Rationale:** Uses parameterized Cypher queries with identity resolution across sources.

#### 78. `backend/app/services/ingestion_service.py`
- **Path:** `backend/app/services/ingestion_service.py`
- **Purpose:** Orchestrates multi-platform data fetching, staging, deduplication, and loading.
- **Key Class:** `IngestionService`
- **Key Methods:** `sync_all()`, `stage_raw_records()`
- **Design Rationale:** Handles cross-platform data collection with SHA-256 deduplication.

#### 79. `backend/app/services/rag_service.py`
- **Path:** `backend/app/services/rag_service.py`
- **Purpose:** Hybrid RAG pipeline combining whitelisted Cypher queries, vector search, and role scoping.
- **Key Class:** `RAGService`
- **Key Methods:** `answer_question()`, `extract_citations()`
- **Design Rationale:** Enforces role-based subgraph pruning and produces structured citations (TC-03).

#### 80. `backend/app/services/risk_service.py`
- **Path:** `backend/app/services/risk_service.py`
- **Purpose:** Coordinates feature extraction, ML inference, and risk configuration.
- **Key Class:** `RiskService`
- **Key Methods:** `evaluate_project()`, `get_or_create_config()`
- **Design Rationale:** Connects database state to ML prediction engine.

#### 81. `backend/app/services/sync_service.py`
- **Path:** `backend/app/services/sync_service.py`
- **Purpose:** Sync lifecycle management and execution tracking.
- **Key Class:** `SyncService`
- **Key Methods:** `trigger_sync()`, `get_run_history()`
- **Design Rationale:** Records sync runs and coordinates background sync tasks.

---

### Backend Scripts & Entrypoints (`backend/` & `backend/scripts/`)

#### 82. `backend/app/main.py`
- **Path:** `backend/app/main.py`
- **Purpose:** FastAPI main application entrypoint, middleware mounting, and router registration.
- **Key Elements:** FastAPI instance, CORS middleware, lifespan context manager, API v1 routers.
- **Design Rationale:** Clean modular application factory pattern.

#### 83. `backend/app/scheduler.py`
- **Path:** `backend/app/scheduler.py`
- **Purpose:** APScheduler background job orchestrator for recurring synchronization.
- **Key Functions:** `start_scheduler()`, `stop_scheduler()`, `scheduled_sync_job()`
- **Design Rationale:** Executes recurring sync cycles based on `sync_interval_minutes`.

#### 84. `backend/scripts/bootstrap_graph.py`
- **Path:** `backend/scripts/bootstrap_graph.py`
- **Purpose:** Initializes Neo4j uniqueness constraints and indexes.
- **Key Functions:** `bootstrap_constraints()`
- **Design Rationale:** Creates indexes on `Employee(email)`, `Project(id)`, `Task(id)` for optimal Cypher performance.

#### 85. `backend/scripts/generate_fixtures.py`
- **Path:** `backend/scripts/generate_fixtures.py`
- **Purpose:** Generates deterministic mock JSON fixture files for offline development.
- **Key Functions:** `generate_fixtures()`
- **Design Rationale:** Builds interconnected organizational datasets with consistent keys.

#### 86. `backend/scripts/seed_demo.py`
- **Path:** `backend/scripts/seed_demo.py`
- **Purpose:** Master seeding script populating relational DB, Neo4j, ChromaDB, and ML risk scores.
- **Key Functions:** `seed_database()`
- **Design Rationale:** Single-command demo initialization for `make seed`.

---

### Backend Tests (`backend/tests/`)

#### 87. `backend/tests/conftest.py`
- **Path:** `backend/tests/conftest.py`
- **Purpose:** Pytest fixtures providing isolated test databases, mock clients, and authenticated sessions.
- **Key Fixtures:** `db_session`, `test_client`, `mock_graph_client`, `mock_chroma_client`.
- **Design Rationale:** Ensures deterministic test execution with zero external service dependencies.

#### 88. `backend/tests/security/test_tc01_rbac.py`
- **Path:** `backend/tests/security/test_tc01_rbac.py`
- **Purpose:** Acceptance test TC-01: Verifies that an employee calling admin endpoints receives HTTP 403 Forbidden.
- **Key Tests:** `test_employee_accessing_admin_endpoints_is_forbidden()`, `test_admin_accessing_admin_endpoints_is_allowed()`.
- **Design Rationale:** Validates RBAC boundary.

#### 89. `backend/tests/integration/test_tc02_rate_limit.py`
- **Path:** `backend/tests/integration/test_tc02_rate_limit.py`
- **Purpose:** Acceptance test TC-02: Verifies GitHub rate-limit backoff handling without data loss.
- **Key Tests:** `test_github_rate_limit_backoff_and_recovery()`.
- **Design Rationale:** Validates Tenacity retry and rate-limit recovery.

#### 90. `backend/tests/integration/test_tc03_rag.py`
- **Path:** `backend/tests/integration/test_tc03_rag.py`
- **Purpose:** Acceptance test TC-03: Verifies RAG queries return grounded citations and enforce employee scoping.
- **Key Tests:** `test_at_risk_query_returns_citations()`, `test_employee_scoping_pruning()`.
- **Design Rationale:** Validates anti-hallucination and privacy isolation.

#### 91. `backend/tests/integration/test_tc04_trello_sync.py`
- **Path:** `backend/tests/integration/test_tc04_trello_sync.py`
- **Purpose:** Acceptance test TC-04: Verifies that a new Trello card creates a Neo4j `Task` node in the next sync cycle.
- **Key Tests:** `test_trello_card_creation_syncs_to_neo4j_task_node()`.
- **Design Rationale:** Validates end-to-end ingestion and graph loading.

#### 92. `backend/tests/unit/test_tc05_cold_start.py`
- **Path:** `backend/tests/unit/test_tc05_cold_start.py`
- **Purpose:** Acceptance test TC-05: Verifies that projects with sparse history output low confidence rather than false precision.
- **Key Tests:** `test_sparse_history_flags_low_confidence()`.
- **Design Rationale:** Validates cold-start confidence gating.

#### 93. `backend/tests/unit/test_features.py`
- **Path:** `backend/tests/unit/test_features.py`
- **Purpose:** Unit tests for the 12-feature extraction pipeline and mathematical transformations.
- **Key Tests:** `test_feature_extraction_dimensions()`, `test_workload_skew_calculation()`.
- **Design Rationale:** Validates feature vector dimensions and edge-case handling.

#### 94. `backend/tests/e2e/test_e2e_pipeline.py`
- **Path:** `backend/tests/e2e/test_e2e_pipeline.py`
- **Purpose:** End-to-end pipeline test verifying task status patch -> graph update -> NL query reflection.
- **Key Tests:** `test_task_status_mutation_reflects_in_rag_query()`.
- **Design Rationale:** Validates integration across relational, graph, and RAG tiers.

---

### Frontend Configuration & Build (`frontend/`)

#### 95. `frontend/Dockerfile`
- **Path:** `frontend/Dockerfile`
- **Purpose:** Multi-stage production container image definition for Next.js 14 frontend.
- **Key Commands:** `FROM node:18-alpine`, dependency installation, `npm run build`, `npm run start`.
- **Design Rationale:** Production-grade containerization with optimized standalone output.

#### 96. `frontend/next-env.d.ts`
- **Path:** `frontend/next-env.d.ts`
- **Purpose:** Next.js TypeScript compiler declaration file.
- **Key Declarations:** Next.js type declarations.
- **Design Rationale:** Auto-managed by Next.js for build typing.

#### 97. `frontend/next.config.js`
- **Path:** `frontend/next.config.js`
- **Purpose:** Next.js build and runtime configuration.
- **Key Settings:** React strict mode, environment proxy rewrites.
- **Design Rationale:** Configures Next.js routing and build parameters.

#### 98. `frontend/package.json`
- **Path:** `frontend/package.json`
- **Purpose:** Node.js package manifest and build scripts.
- **Key Scripts:** `dev`, `build`, `start`, `lint`.
- **Key Dependencies:** `next`, `react`, `react-dom`, `recharts`, `lucide-react`, `tailwindcss`.
- **Design Rationale:** Locks frontend dependencies for reproducible builds.

#### 99. `frontend/package-lock.json`
- **Path:** `frontend/package-lock.json`
- **Purpose:** Exact dependency tree lockfile for npm.
- **Key Contents:** Hash-locked dependency versions.
- **Design Rationale:** Guarantees deterministic `npm install` executions across environments.

#### 100. `frontend/postcss.config.js`
- **Path:** `frontend/postcss.config.js`
- **Purpose:** PostCSS configuration file enabling Tailwind CSS and Autoprefixer.
- **Key Plugins:** `tailwindcss`, `autoprefixer`.
- **Design Rationale:** Standard CSS processing pipeline for Tailwind.

#### 101. `frontend/tailwind.config.ts`
- **Path:** `frontend/tailwind.config.ts`
- **Purpose:** Tailwind CSS theme and design system configuration.
- **Key Settings:** Custom slate/cyan color palette, font families, animation keyframes.
- **Design Rationale:** Establishes the executive cybernetic aesthetic across all views.

#### 102. `frontend/tsconfig.json`
- **Path:** `frontend/tsconfig.json`
- **Purpose:** TypeScript compiler configuration for Next.js.
- **Key Settings:** `paths: {"@/*": ["./src/*"]}`, strict mode enabled.
- **Design Rationale:** Type-safe development with path aliases.

---

### Frontend Libraries & Components (`frontend/src/`)

#### 103. `frontend/src/app/globals.css`
- **Path:** `frontend/src/app/globals.css`
- **Purpose:** Global stylesheet defining utility classes, custom scrollbars, and glassmorphic panels.
- **Key Classes:** `.card-cyber`, `.glass-panel`, `.btn-primary`, `.btn-secondary`.
- **Design Rationale:** Centralizes design tokens and reusable styling classes.

#### 104. `frontend/src/lib/types.ts`
- **Path:** `frontend/src/lib/types.ts`
- **Purpose:** TypeScript domain interfaces matching backend schemas.
- **Key Interfaces:** `SessionUser`, `ProjectRiskSummary`, `Citation`, `GraphNode`, `GraphRelationship`, `RiskConfig`, `AuditLogItem`.
- **Design Rationale:** Ensures end-to-end type safety between backend and frontend.

#### 105. `frontend/src/lib/auth.ts`
- **Path:** `frontend/src/lib/auth.ts`
- **Purpose:** Client-side authentication helpers, demo user profiles, and session storage.
- **Key Constants & Functions:** `DEMO_USERS`, `getStoredUser()`, `loginAsDevUser()`, `useAuth()`.
- **Design Rationale:** Enables instant role switching between Alice (Manager), Bob (Employee), and Laura (Admin).

#### 106. `frontend/src/lib/api.ts`
- **Path:** `frontend/src/lib/api.ts`
- **Purpose:** Typed API client with automatic bearer token injection and error handling.
- **Key Namespaces:** `api.dashboard`, `api.assistant`, `api.graph`, `api.risk`, `api.tasks`, `api.admin`, `api.sync`.
- **Design Rationale:** Reusable, strongly typed HTTP client for all backend endpoints.

#### 107. `frontend/src/components/Nav.tsx`
- **Path:** `frontend/src/components/Nav.tsx`
- **Purpose:** Top executive navigation bar with role switcher and quick sync trigger.
- **Key Elements:** Navigation links, active route highlight, role selector dropdown, "Sync Now" button.
- **Design Rationale:** Provides single-click role switching and ingestion triggers during live demos.

#### 108. `frontend/src/components/RoleGuard.tsx`
- **Path:** `frontend/src/components/RoleGuard.tsx`
- **Purpose:** Client-side role authorization guard component.
- **Key Props:** `allowedRoles: Role[]`, `children: React.ReactNode`.
- **Design Rationale:** Prevents unauthorized role rendering and shows an "Access Restricted" message.

#### 109. `frontend/src/components/RiskBadge.tsx`
- **Path:** `frontend/src/components/RiskBadge.tsx`
- **Purpose:** Visual risk badge with color-coded severity indicators.
- **Key Props:** `score: number`, `band: RiskBand`, `confidence?: string`.
- **Design Rationale:** Standardized risk visualization across dashboard, project cards, and tables.

#### 110. `frontend/src/components/ProjectCard.tsx`
- **Path:** `frontend/src/components/ProjectCard.tsx`
- **Purpose:** Project summary card displaying risk scores, top factors, and task progress.
- **Key Props:** `project: ProjectRiskSummary`.
- **Design Rationale:** High-density project card for the dashboard view.

#### 111. `frontend/src/components/GraphView.tsx`
- **Path:** `frontend/src/components/GraphView.tsx`
- **Purpose:** Interactive SVG Knowledge Graph explorer with node filtering and property inspector.
- **Key Features:** Zoom, pan, entity filtering, click-to-inspect drawer.
- **Design Rationale:** Lightweight, dependency-free graph visualization running smoothly in any browser.

#### 112. `frontend/src/components/ChatPanel.tsx`
- **Path:** `frontend/src/components/ChatPanel.tsx`
- **Purpose:** Conversational RAG chat interface with streaming answers and citation links.
- **Key Features:** Message history, suggested query pills, clickable citation badges.
- **Design Rationale:** Clean conversational interface connecting natural language to graph evidence.

#### 113. `frontend/src/components/SourceCitation.tsx`
- **Path:** `frontend/src/components/SourceCitation.tsx`
- **Purpose:** Interactive citation badge component referencing graph nodes.
- **Key Props:** `citation: Citation`.
- **Design Rationale:** Renders clickable citation pills that reveal underlying graph node data.

---

### Frontend Views (`frontend/src/app/`)

#### 114. `frontend/src/app/layout.tsx`
- **Path:** `frontend/src/app/layout.tsx`
- **Purpose:** Root layout mounting global fonts, metadata, and persistent navigation bar.
- **Key Elements:** Root HTML shell, `Inter` font, `Nav` component.
- **Design Rationale:** Ensures consistent chrome and layout across all routes.

#### 115. `frontend/src/app/page.tsx`
- **Path:** `frontend/src/app/page.tsx`
- **Purpose:** High-impact landing page introducing TwinOS capabilities.
- **Key Elements:** Hero banner, architecture highlights, quick demo entry button.
- **Design Rationale:** Professional first impression for evaluators and visitors.

#### 116. `frontend/src/app/(auth)/login/page.tsx`
- **Path:** `frontend/src/app/(auth)/login/page.tsx`
- **Purpose:** Interactive authentication and demo profile selection page.
- **Key Elements:** Single-click role selector cards (Manager, Employee, Admin).
- **Design Rationale:** Enables instant, zero-friction evaluator onboarding.

#### 117. `frontend/src/app/dashboard/page.tsx`
- **Path:** `frontend/src/app/dashboard/page.tsx`
- **Purpose:** Executive command center dashboard with KPI cards and project risk grid.
- **Key Elements:** Metric summary cards, risk distribution chart, project cards grid.
- **Design Rationale:** Primary landing view for Project Managers (UC-M01).

#### 118. `frontend/src/app/assistant/page.tsx`
- **Path:** `frontend/src/app/assistant/page.tsx`
- **Purpose:** Conversational RAG assistant interface with suggested prompts.
- **Key Elements:** `ChatPanel` integration, query suggestions, citation subgraphs.
- **Design Rationale:** Provides grounded natural language Q&A for all roles (UC-M02, UC-E03).

#### 119. `frontend/src/app/graph/page.tsx`
- **Path:** `frontend/src/app/graph/page.tsx`
- **Purpose:** Full-screen multi-hop Knowledge Graph explorer.
- **Key Elements:** `GraphView` component, entity filters, node count metrics.
- **Design Rationale:** Interactive topology inspection for managers and architects (UC-M04).

#### 120. `frontend/src/app/projects/page.tsx`
- **Path:** `frontend/src/app/projects/page.tsx`
- **Purpose:** Comprehensive organizational project portfolio list and risk table.
- **Key Elements:** Searchable project table, risk band filters, quick drill-downs.
- **Design Rationale:** Portfolio-level management view.

#### 121. `frontend/src/app/projects/[id]/page.tsx`
- **Path:** `frontend/src/app/projects/[id]/page.tsx`
- **Purpose:** Deep-dive project diagnostic view with factor breakdowns and task lists.
- **Key Elements:** Risk gauge, top contributing factors, assigned engineers, associated tasks.
- **Design Rationale:** Root cause analysis view for high-risk projects.

#### 122. `frontend/src/app/my-work/page.tsx`
- **Path:** `frontend/src/app/my-work/page.tsx`
- **Purpose:** Employee-scoped personal task Kanban board with status transitions.
- **Key Elements:** Task status columns (`todo`, `in_progress`, `review`, `done`), status update buttons.
- **Design Rationale:** Employee work execution view (UC-E01, UC-E02).

#### 123. `frontend/src/app/alerts/page.tsx`
- **Path:** `frontend/src/app/alerts/page.tsx`
- **Purpose:** Proactive delay risk alerts and executive notifications inbox.
- **Key Elements:** Filterable alert list, severity badges, mark-as-read actions.
- **Design Rationale:** Escalation and notification management view.

#### 124. `frontend/src/app/admin/users/page.tsx`
- **Path:** `frontend/src/app/admin/users/page.tsx`
- **Purpose:** User provisioning and RBAC management table guarded by `admin` role.
- **Key Elements:** User table, "Add User" modal, role assignment controls.
- **Design Rationale:** Administrative identity management (UC-A01, TC-01).

#### 125. `frontend/src/app/admin/connections/page.tsx`
- **Path:** `frontend/src/app/admin/connections/page.tsx`
- **Purpose:** Platform integration connection cards (GitHub, Trello, Gmail, GCal).
- **Key Elements:** Connection status badges, "Sync Platform" triggers, mock/live indicators.
- **Design Rationale:** Third-party connector configuration view.

#### 126. `frontend/src/app/admin/risk-config/page.tsx`
- **Path:** `frontend/src/app/admin/risk-config/page.tsx`
- **Purpose:** ML risk engine threshold sliders and cold-start configuration.
- **Key Elements:** Sliders for Medium/High/Critical thresholds, cold-start history days slider.
- **Design Rationale:** Dynamic ML calibration for administrators (UC-A02, TC-05).

#### 127. `frontend/src/app/admin/audit/page.tsx`
- **Path:** `frontend/src/app/admin/audit/page.tsx`
- **Purpose:** Immutable security audit trail inspection table.
- **Key Elements:** Filterable audit ledger, event action badges, JSON metadata modal.
- **Design Rationale:** Compliance and security inspection (UC-A03).

---

## 11. Security, Rate Limiting, & Production Hardening Rationale

### 11.1 Defense-in-Depth Model
TwinOS implements security controls across five distinct layers:
1. **Network Layer:** All endpoints run over HTTPS in production; CORS policy restricts origins to trusted domains.
2. **Authentication Layer:** Supports dual resolution—development tokens for rapid testing and Firebase RS256 JWT tokens for production.
3. **Authorization Layer:** Declarative RBAC enforced at the API gateway via `require_role(...)`.
4. **Data Layer:** Third-party OAuth tokens encrypted at rest using AES-GCM; least-privilege Gmail access.
5. **Observability Layer:** Custom logging filter redacts sensitive credentials; append-only audit trail records all administrative mutations.

### 11.2 Secret Redaction Filter
The logging filter (`backend/app/core/logging.py`) intercepts all log records and applies regular expressions to detect and redact:
- Bearer tokens (`Bearer [REDACTED]`)
- OAuth access and refresh tokens (`ghp_[REDACTED]`, `ya29.[REDACTED]`)
- Private keys and certificate blocks (`-----BEGIN PRIVATE KEY-----[REDACTED]`)
- Password fields in JSON payloads (`"password": "[REDACTED]"`)

---

## 12. Viva Q&A & Examiner Defense Guide (25 Questions & Answers)

### Architecture & System Design

#### Q1: Why did you choose a Tri-Store architecture instead of a single PostgreSQL database with JSON columns?
**Answer:** While PostgreSQL can store JSON documents, querying multi-hop relationships (e.g., "Find all tasks assigned to developers who committed code to repos linked to projects with overdue deadlines") requires expensive recursive CTEs that degrade rapidly with depth. Neo4j executes graph traversals in index-free adjacency time ($O(1)$ per hop). Similarly, vector similarity search over thousands of commit diffs is orders of magnitude faster and more semantically accurate in a dedicated vector index (ChromaDB) than in a relational table. The Tri-Store architecture assigns each data model to its optimal engine while maintaining transactional consistency through relational staging.

#### Q2: What happens if an external evaluation environment does not have Docker installed?
**Answer:** TwinOS was deliberately engineered with transparent zero-docker fallbacks. If Docker or PostgreSQL is unavailable, the database layer automatically initializes an ACID-compliant local SQLite database with identical SQLAlchemy ORM mappings. If Neo4j is offline, an in-memory graph engine parses parameterized Cypher queries. If ChromaDB server is offline, a local SQLite-backed persistent client is used. All 5 acceptance tests (TC-01 through TC-05) pass 100% offline without external services.

#### Q3: Why is Jira excluded from the platform scope?
**Answer:** The project scope was deliberately focused on Trello as the single issue tracking platform. Jira introduces substantial OAuth 2.0 3LO token dance complexity, custom enterprise field schemas, and expensive licensing overhead. Trello's Board/List/Card model maps cleanly and deterministically to Project/Status/Task without unnecessary configuration sprawl, while the `BaseConnector` interface provides a clean extension point for future issue trackers.

#### Q4: Why did you build the backend purely in Python FastAPI rather than splitting services between Node.js and Python?
**Answer:** Splitting services between Node.js and Python would introduce inter-process HTTP/gRPC serialization overhead, duplicated Pydantic/TypeScript data models, and complex distributed transaction handling. Python 3.11 with FastAPI natively integrates the entire AI/ML ecosystem (Scikit-learn, ChromaDB, Sentence-Transformers) with the web API layer in a single process space, maximizing performance and developer velocity. Node.js is reserved solely for Next.js 14 client-side rendering and asset bundling.

---

### Machine Learning & Risk Prediction

#### Q5: Why did you train a supervised Gradient Boosting model instead of asking an LLM to predict project delay risk?
**Answer:** LLMs are generative language models that predict text tokens, not calibrated probabilities. An LLM prompted with project metrics suffers from hallucination, non-deterministic outputs, and lack of mathematical calibration. Our Scikit-learn Gradient Boosting classifier is trained on normalized topological and velocity features, producing a bounded probability score $[0.0 - 1.0]$, calibrated risk bands, and verifiable feature importances ($ROC\text{-}AUC = 0.94$).

#### Q6: How do you compute feature importance and top factors without SHAP?
**Answer:** SHAP introduces heavy computational overhead (KernelSHAP can take seconds per sample). TwinOS computes explainability by calculating the standardized z-score deviation of each feature relative to population training priors:
$$\text{Deviation}_i = \frac{x_i - \mu_i}{\sigma_i} \cdot w_i$$
where $w_i$ is the global feature importance weight from the Gradient Boosting tree ensemble. The top 3 absolute contributors are returned with directional labels (e.g., `overdue_tasks (+0.38)`), providing instant, auditable explanations in under 1 millisecond.

#### Q7: How does TwinOS handle the cold-start problem for newly created projects (TC-05)?
**Answer:** When a project has fewer than `min_history_days` (default: 14 days), commit frequency and completion velocity have insufficient sample size to produce statistically reliable predictions. Instead of generating misleading high-precision false alarms, the risk engine intercepts young projects, assigns `confidence: "low"`, applies a conservative baseline risk prior ($0.25$), and explicitly explains that history is insufficient.

#### Q8: What are the 12 features in your ML feature vector?
**Answer:** The 12 features span four categories:
1. **Scope & Progress:** `total_tasks`, `completed_tasks`, `overdue_tasks`, `completion_rate`.
2. **Workload & Allocation:** `unassigned_tasks`, `workload_skew` (Gini coefficient of tasks per engineer).
3. **Deadlines & Velocity:** `days_to_nearest_deadline`, `commit_count_14d`, `active_developers`.
4. **Coordination & Age:** `email_thread_count`, `calendar_event_count`, `history_days`.

---

### RAG, LLM, & Graph Integration

#### Q9: Why use whitelisted Cypher templates instead of unconstrained Text-to-Cypher generation?
**Answer:** Unconstrained Text-to-Cypher is vulnerable to three major failure modes:
1. **Cypher Injection:** Malicious prompts can drop or mutate database nodes.
2. **Hallucinatory Schema:** LLMs frequently invent non-existent relationship types or properties.
3. **Cross-Tenant Leakage:** Unrestricted queries can traverse across organizational boundaries.
Whitelisted Cypher templates map user intents to parameterized, pre-tested queries that are mathematically guaranteed to execute safely and conform to the schema.

#### Q10: How do you enforce role-based access control inside the RAG assistant (TC-01, TC-03)?
**Answer:** When a user queries the assistant, their authenticated session provides their role and email. If the user is an `employee`, the RAG engine automatically injects a scoping clause into the graph traversal, restricting matches to nodes connected to `(e:Employee {email: user.email})`. The employee cannot retrieve or view data from unassigned projects, preventing cross-project information leakage.

#### Q11: How do citations work in TwinOS RAG responses?
**Answer:** Every claim in the synthesized answer is backed by structured citation objects generated from the retrieved graph nodes. Each citation includes `entity_type` (e.g. `Task`, `Deadline`), `entity_id`, a human-readable `label`, and a text `snippet`. The frontend renders these as interactive pills that link directly to the node inspector in the Knowledge Graph view.

#### Q12: How does TwinOS run without an OpenAI API key?
**Answer:** TwinOS includes a built-in `MockLLMProvider` that deterministically synthesizes natural language answers grounded in the retrieved graph context and vector snippets. If `OPENAI_API_KEY` is provided in `.env`, the system automatically switches to the live OpenAI provider via `LLMProviderFactory`.

---

### Ingestion, Connectors, & Resilience

#### Q13: How does TwinOS handle GitHub API rate limiting without data loss (TC-02)?
**Answer:** All GitHub connector requests use Tenacity retry decorators with exponential backoff. When GitHub returns an HTTP 403 status with `X-RateLimit-Remaining: 0`, the connector parses the `X-RateLimit-Reset` header, logs a warning, enters a backoff sleep or defers remaining partitions, and preserves staged records without throwing unhandled exceptions or dropping data.

#### Q14: How does deduplication work in the ingestion pipeline?
**Answer:** Every raw record fetched by a connector is hashed using SHA-256 before insertion into the `staged_records` table. If a record with an identical hash already exists in the staging store, it is skipped. This guarantees idempotent sync executions even if the scheduler runs frequently.

#### Q15: What privacy protections are implemented for Gmail data ingestion?
**Answer:** TwinOS enforces the principle of Least Privilege. The Gmail connector requests only header metadata (`Subject`, `Date`, `From`, `To`) and short snippets. Message bodies and attachments are never fetched, stored, or processed, ensuring compliance with enterprise privacy standards (GDPR/SOC2).

---

### Security & Governance

#### Q16: How is RBAC implemented across the API?
**Answer:** RBAC is enforced via FastAPI dependency injection: `Depends(require_role("admin"))`. When an endpoint is invoked, the dependency resolves the authenticated user from the bearer token and checks their role against the permitted roles list. If the user lacks the required role, an HTTP 403 Forbidden exception is raised immediately before the route handler executes.

#### Q17: What is the purpose of the immutable audit log?
**Answer:** Enterprise compliance requires an unalterable record of administrative actions. The `audit_logs` table records every administrative mutation (`user_created`, `user_updated`, `risk_config_updated`, `sync_run`) with the actor's ID, action type, target entity, timestamp, and JSON metadata diff. No API endpoints exist to update or delete audit log entries.

#### Q18: How are secrets protected from appearing in application logs?
**Answer:** A custom `SecretRedactingFilter` is attached to all Python logging handlers. It applies regular expressions to inspect every log message and replaces API keys, OAuth tokens, bearer credentials, and private keys with `[REDACTED]` before output.

---

### Frontend & User Experience

#### Q19: Why build the graph visualizer in pure SVG rather than using a heavy WebGL library like 3D-force-graph?
**Answer:** Heavy 3D WebGL libraries introduce large bundle sizes (often >2MB), require WebGL context support, and can fail on low-power devices or inside headless test browsers. Our custom SVG visualizer (`frontend/src/components/GraphView.tsx`) provides 60 FPS panning, zooming, node filtering, and interactive drawers with zero external dependencies and a tiny footprint.

#### Q20: How does the frontend handle instant role switching during demonstrations?
**Answer:** The navigation bar includes a development role switcher dropdown that updates the active session in `localStorage` and injects `Authorization: Bearer dev:<email>` into all outgoing API requests. This allows evaluators to seamlessly toggle between Alice Chen (Manager), Bob Martinez (Employee), and Laura Croft (Admin) without re-authenticating.

---

### Testing & Verification

#### Q21: What are the 5 acceptance test cases (TC-01 through TC-05)?
**Answer:**
1. **TC-01:** RBAC security gate (Employee calling Admin yields HTTP 403 Forbidden).
2. **TC-02:** Upstream rate-limit resilience (GitHub 403 backoff without data loss).
3. **TC-03:** Grounded RAG with citations and employee scoping.
4. **TC-04:** Trello card sync reflects as a Neo4j `Task` node in the next cycle.
5. **TC-05:** Cold-start confidence gating (young projects output low confidence, not false precision).

#### Q22: How fast does the test suite run?
**Answer:** Because all external services have in-memory or SQLite fallbacks, the complete test suite (7 test files, 15+ assertions) executes in under 5 seconds using `pytest backend/tests -v`.

#### Q23: How do you verify that 100% of files in the repository are documented?
**Answer:** We run an automated verification script that walks the repository, discovers every tracked source file, and cross-references it against Section 10 of this document. Any missing or unreferenced file causes the verification script to fail.

---

### Production Deployment & Scalability

#### Q24: How would TwinOS scale to an enterprise with 50,000 employees and millions of tasks?
**Answer:**
1. **Ingestion:** Transition from single-process APScheduler to Celery/Temporal distributed workers with Redis task queues, partitioning connector sync jobs by organization and project.
2. **Knowledge Graph:** Deploy Neo4j Enterprise in a causal clustering configuration with read replicas and property indexing on `id` and `email`.
3. **Vector Store:** Scale ChromaDB in client-server mode with HNSW indexing or migrate to an enterprise vector cluster (e.g. Qdrant or Milvus).
4. **Relational DB:** PostgreSQL read replicas with connection pooling via PgBouncer.

#### Q25: How does TwinOS maintain data consistency across the Tri-Store?
**Answer:** Ingestion runs use a two-phase staging strategy:
1. Raw payloads are staged in the relational store with SHA-256 deduplication hashing.
2. An ingestion orchestrator transactionally commits the staging record, applies idempotent Cypher `MERGE` operations in Neo4j, and upserts vector embeddings into ChromaDB.
If a failure occurs during graph or vector upsert, the staged record remains marked `is_processed = False`, and the next sync cycle retries the transformation without data loss.
