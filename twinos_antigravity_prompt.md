# TwinOS: Antigravity Build Prompt

> Paste everything below the line into Antigravity (Agent Manager, Planning mode). If it is too long for one message, save this file in the workspace as `BUILD_PROMPT.md` and tell the agent: "Read BUILD_PROMPT.md fully and execute it phase by phase."

---

## 0. ROLE AND WORKING RULES

You are a senior full-stack and ML engineer building **TwinOS: An AI-Powered Digital Twin Operating System for Organizations**, a final-year B.Tech CSE project (SRMCEM Lucknow, AKTU). Build a complete, runnable, well-documented prototype in this workspace.

Working rules (follow strictly):

1. **Plan first.** Produce an implementation plan artifact and wait for no approval; then execute phase by phase (Section 9). After every phase, run the verification commands listed for that phase and fix failures before moving on.
2. **Never commit secrets.** All credentials come from environment variables. Ship `.env.example` only.
3. **Everything must run without paid keys or live third-party accounts.** Every external integration (GitHub, Trello, Gmail, Google Calendar, LLM, Firebase) must have a **mock/dev mode** selectable by env var so the demo and tests work offline. Real mode must also be implemented.
4. **Small, typed, tested code.** Python 3.11+ with type hints and Pydantic v2; TypeScript strict mode on the frontend. Every module gets tests.
5. **Document as you build.** Every non-obvious decision is recorded for `EXPLANATION.md` (Section 10). Do not leave documentation to the end; append to a running `docs/decision_log.md` after each phase, then consolidate it.
6. **Do not invent scope.** Stay inside the scope in Section 2. Out-of-scope items may only appear as clearly marked extension points.
7. When a requirement is ambiguous, pick the simplest option that satisfies the synopsis, and record the choice in the decision log.

---

## 1. PROJECT CONTEXT (from the approved synopsis)

**Problem.** Organizations scatter activity across email, calendars, task boards and code repos. No tool reasons across them, reports are manual and reactive, there is no predictive insight, no natural-language access, and cross-platform data raises access and security concerns.

**Solution.** TwinOS is a synthesis layer above existing tools. It continuously ingests activity data, models it as a **knowledge graph** (employees, projects, tasks, deadlines), answers plain-English questions through a **RAG assistant**, **scores project delay risk** with an explainable ML model, and shows everything in an **executive dashboard** with alerts and recommendations, behind **role-based access control**.

**Objectives (all must be demonstrably met):**
1. Knowledge graph of employees, projects, tasks, deadlines (plus repositories, commits, emails, events).
2. Integrate 4 platforms: Gmail, Google Calendar, GitHub, Trello, with scheduled sync.
3. RAG assistant over graph + vector store of unstructured text, with citations back to graph nodes.
4. Predictive delay/risk model trained on historical activity (synthetic + pilot data).
5. Interactive executive dashboard with risk alerts and recommendations.
6. Secure RBAC (Manager / Employee / Admin).

---

## 2. SCOPE

**In scope:** the 4 integrations via official REST APIs; the 8-entity graph; RAG assistant limited to org-status questions; risk model trained on synthetic and pilot data; web dashboard for 3 roles; notifications (in-app); admin configuration; Docker Compose deployment; tests; docs.

**Out of scope (do NOT build; mention only as extension points):** Slack/Teams/Notion/Jira connectors, native mobile app, multi-tenant SaaS, voice interface, email/push alerts, SHAP explainability (use the simple built-in explanation described below), meeting transcripts.

**Known synopsis inconsistencies, resolved as follows (record in the decision log):**
- DFD figures say "Trello / Jira API"; scope says Jira is out of scope. **Decision: Trello only.**
- Software list says "FastAPI (Python), Node.js". **Decision: Python/FastAPI is the only backend; Node.js is used only for the Next.js toolchain.**
- Synopsis names `users`, `platform_connections`, `audit_log` tables, but the DFD also needs a staging area, risk scores and alerts. **Decision: add `staging_records`, `sync_runs`, `risk_scores`, `risk_config`, `alerts`, `organizations`** (schemas below).

---

## 3. TECH STACK (fixed; do not substitute)

| Layer | Choice |
|---|---|
| Frontend | React + Next.js (App Router, TypeScript), Tailwind CSS, Recharts (charts), react-force-graph-2d (graph view) |
| Backend | FastAPI (Python 3.11), Pydantic v2, SQLAlchemy 2.0 + Alembic, APScheduler (in-process scheduled sync), httpx, tenacity (retry/backoff) |
| Graph DB | Neo4j 5 (official `neo4j` Python driver) |
| Relational DB | PostgreSQL 16 |
| Vector store | ChromaDB (client/server mode in its own container) |
| AI orchestration | LangChain; LLM provider selectable via `LLM_PROVIDER=openai|gemini|mock` |
| Embeddings | Provider-matched (OpenAI / Gemini) or a local `sentence-transformers` model in `mock` mode |
| ML | scikit-learn (logistic regression baseline + gradient boosting), pandas, joblib |
| Auth | Firebase Auth (ID tokens) verified in FastAPI with `firebase-admin`; `AUTH_MODE=firebase|dev` |
| Containers | Docker, Docker Compose |
| Tests | pytest, pytest-asyncio, respx (HTTP mocking), testcontainers or compose-based integration; Playwright smoke test for the frontend |
| Lint/format | ruff, black, mypy (backend); eslint, prettier (frontend) |

---

## 4. REPOSITORY STRUCTURE (create exactly this, adding files only if justified in the decision log)

```
twinos/
├── README.md
├── EXPLANATION.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── Makefile
├── docs/
│   ├── decision_log.md
│   ├── architecture.md              # layered architecture + Mermaid diagram
│   ├── dfd_level0.mmd / dfd_level1.mmd   # Mermaid DFDs
│   └── usecases.md
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/versions/0001_initial.py
│   ├── app/
│   │   ├── main.py                  # FastAPI app factory, routers, lifespan (scheduler start/stop)
│   │   ├── core/
│   │   │   ├── config.py            # pydantic-settings, all env vars
│   │   │   ├── security.py          # Firebase token verify, dev-mode token, current_user dep
│   │   │   ├── rbac.py              # require_role(...) dependency, permission matrix
│   │   │   └── logging.py           # structured logging, secret redaction filter
│   │   ├── db/
│   │   │   ├── postgres.py          # engine, session
│   │   │   ├── neo4j_client.py      # driver wrapper, constraint bootstrap
│   │   │   ├── chroma_client.py     # collection bootstrap
│   │   │   └── models.py            # SQLAlchemy models
│   │   ├── schemas/                 # Pydantic request/response models per domain
│   │   ├── integrations/
│   │   │   ├── base.py              # BaseConnector ABC + NormalizedRecord
│   │   │   ├── github.py
│   │   │   ├── trello.py
│   │   │   ├── gmail.py
│   │   │   ├── gcalendar.py
│   │   │   ├── oauth.py             # Google OAuth2 flow, token encryption
│   │   │   ├── mock/                # fixtures + MockConnector per platform
│   │   │   └── registry.py          # name -> connector class
│   │   ├── services/
│   │   │   ├── sync_service.py      # Process 1: run connectors -> staging
│   │   │   ├── ingestion_service.py # Process 2: staging -> Neo4j + Chroma
│   │   │   ├── graph_service.py     # Cypher read/write helpers
│   │   │   ├── rag_service.py       # Process 4: retrieval + LLM answer
│   │   │   ├── risk_service.py      # Process 3: features + scoring
│   │   │   ├── dashboard_service.py # Process 5: aggregation
│   │   │   ├── alert_service.py     # threshold monitoring -> alerts
│   │   │   └── audit_service.py
│   │   ├── ml/
│   │   │   ├── features.py          # feature engineering (pure functions)
│   │   │   ├── synthetic.py         # synthetic data generator
│   │   │   ├── train.py             # training script (CLI)
│   │   │   ├── model.py             # load/predict/explain, low-confidence logic
│   │   │   └── artifacts/           # saved model (gitignored, built by `make train`)
│   │   ├── llm/
│   │   │   ├── provider.py          # factory: openai | gemini | mock
│   │   │   ├── prompts.py           # system + RAG prompt templates
│   │   │   └── mock_llm.py          # deterministic offline LLM
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── v1/ auth.py users.py integrations.py sync.py graph.py
│   │   │         assistant.py risk.py dashboard.py alerts.py admin.py tasks.py health.py
│   │   └── scheduler.py             # APScheduler jobs: sync, ingest, risk scoring, alert scan
│   ├── scripts/
│   │   ├── seed_demo.py             # seeds org, users, mock data, runs full pipeline
│   │   └── bootstrap_graph.py
│   └── tests/
│       ├── unit/ integration/ e2e/ security/
│       └── conftest.py
└── frontend/
    ├── Dockerfile
    ├── package.json, tsconfig.json, tailwind.config.ts, next.config.js
    └── src/
        ├── app/
        │   ├── layout.tsx
        │   ├── (auth)/login/page.tsx
        │   ├── dashboard/page.tsx
        │   ├── assistant/page.tsx
        │   ├── graph/page.tsx
        │   ├── projects/page.tsx and projects/[id]/page.tsx
        │   ├── my-work/page.tsx            # Employee: update own task status
        │   ├── alerts/page.tsx
        │   └── admin/ users/page.tsx connections/page.tsx risk-config/page.tsx audit/page.tsx
        ├── components/ RiskBadge, ProjectCard, ChatPanel, GraphView, SourceCitation, RoleGuard, Nav, ...
        ├── lib/ api.ts (typed client), auth.ts (Firebase client + dev login), types.ts
        └── hooks/
```

---

## 5. DATA DESIGN (implement exactly)

### 5.1 Neo4j knowledge graph

**Node labels and properties** (every node has `id` (string, unique), `org_id`, `source` (platform), `created_at`, `updated_at`):

| Label | Key properties |
|---|---|
| Employee | name, email, role_title, pg_user_id (nullable) |
| Project | name, status (`planned|active|at_risk|done`), start_date, target_end_date |
| Task | title, description, status (`todo|in_progress|blocked|done`), due_date, completed_at, priority, external_id |
| Deadline | label, due_at, kind (`project|task|milestone`), is_met |
| Repository | full_name, url, default_branch |
| Commit | sha, message, committed_at, additions, deletions |
| Email | subject, sent_at, thread_id, chroma_id (embedding reference); store metadata only, not the full body |
| Event | title, start_at, end_at, is_milestone, location |

**Constraints/indexes (create at startup via `bootstrap_graph.py`, idempotent):**
```cypher
CREATE CONSTRAINT employee_id IF NOT EXISTS FOR (n:Employee) REQUIRE n.id IS UNIQUE;
-- same uniqueness constraint for Project, Task, Deadline, Repository, Commit, Email, Event
CREATE INDEX task_status IF NOT EXISTS FOR (t:Task) ON (t.status);
CREATE INDEX task_due IF NOT EXISTS FOR (t:Task) ON (t.due_date);
CREATE INDEX commit_time IF NOT EXISTS FOR (c:Commit) ON (c.committed_at);
CREATE INDEX employee_email IF NOT EXISTS FOR (e:Employee) ON (e.email);
```

**Relationships (exactly these):**
`(Employee)-[:WORKS_ON]->(Project)`, `(Task)-[:ASSIGNED_TO]->(Employee)`, `(Task)-[:BELONGS_TO]->(Project)`, `(Project|Task)-[:HAS_DEADLINE]->(Deadline)`, `(Commit)-[:COMMITTED_BY]->(Employee)`, `(Commit)-[:IN_REPOSITORY]->(Repository)`, `(Repository)-[:BELONGS_TO]->(Project)` (extra, needed to link code to projects; log it), `(Email)-[:SENT_BY]->(Employee)`, `(Email)-[:RECEIVED_BY]->(Employee)`, `(Event)-[:ATTENDED_BY]->(Employee)`, `(Event)-[:RELATES_TO]->(Project)` (optional).

All writes use `MERGE` on `id` so re-syncing is idempotent.

**Entity resolution rule:** employees from different platforms are unified by lowercase email; fall back to a `employee_aliases` mapping in Postgres (GitHub login, Trello member id) set by Admin. Document this in the decision log.

### 5.2 PostgreSQL schema (Alembic migration `0001_initial`)

```sql
organizations(id UUID PK, name TEXT NOT NULL, created_at TIMESTAMPTZ DEFAULT now());

users(id UUID PK, organization_id UUID FK organizations, name TEXT NOT NULL,
      email CITEXT UNIQUE NOT NULL, role TEXT NOT NULL CHECK (role IN ('manager','employee','admin')),
      firebase_uid TEXT UNIQUE, is_active BOOLEAN DEFAULT true, created_at TIMESTAMPTZ DEFAULT now());

employee_aliases(id UUID PK, user_id UUID FK users, platform TEXT, external_id TEXT,
                 UNIQUE(platform, external_id));

platform_connections(id UUID PK, user_id UUID FK users, organization_id UUID FK organizations,
      platform TEXT CHECK (platform IN ('github','trello','gmail','gcalendar')),
      oauth_token_ref TEXT,          -- reference/ciphertext only; tokens encrypted with Fernet (ENCRYPTION_KEY)
      scopes TEXT[], status TEXT DEFAULT 'connected', last_synced_at TIMESTAMPTZ,
      UNIQUE(user_id, platform));

sync_runs(id UUID PK, connection_id UUID FK, started_at, finished_at, status TEXT,
          records_pulled INT, error TEXT);

staging_records(id UUID PK, organization_id UUID, platform TEXT, entity_type TEXT,
      external_id TEXT, payload JSONB NOT NULL, content_hash TEXT NOT NULL,
      status TEXT DEFAULT 'pending' CHECK (status IN ('pending','ingested','failed')),
      created_at TIMESTAMPTZ DEFAULT now(), UNIQUE(platform, entity_type, external_id, content_hash));

risk_scores(id UUID PK, organization_id UUID, entity_type TEXT CHECK (entity_type IN ('project','task')),
      entity_id TEXT NOT NULL, score NUMERIC(4,3) NOT NULL, band TEXT CHECK (band IN ('low','medium','high','critical')),
      confidence TEXT CHECK (confidence IN ('normal','low')), top_factors JSONB,
      model_version TEXT, computed_at TIMESTAMPTZ DEFAULT now());
CREATE INDEX ON risk_scores(entity_type, entity_id, computed_at DESC);

risk_config(organization_id UUID PK, medium_threshold NUMERIC DEFAULT 0.35, high_threshold NUMERIC DEFAULT 0.60,
      critical_threshold NUMERIC DEFAULT 0.80, min_history_days INT DEFAULT 14, sync_interval_minutes INT DEFAULT 15,
      updated_by UUID, updated_at TIMESTAMPTZ);

alerts(id UUID PK, organization_id UUID, recipient_user_id UUID FK users, entity_type TEXT, entity_id TEXT,
      from_band TEXT, to_band TEXT, message TEXT, is_read BOOLEAN DEFAULT false, created_at TIMESTAMPTZ DEFAULT now());

audit_log(id UUID PK, actor_id UUID, action TEXT NOT NULL, target_entity TEXT, target_id TEXT,
      metadata JSONB, timestamp TIMESTAMPTZ DEFAULT now());   -- append-only; no UPDATE/DELETE endpoints
```

### 5.3 ChromaDB

One collection `twinos_content`. Each record: `id` = `{entity_type}:{entity_id}`, `document` = text (email body/snippet, commit message, task description), `embedding`, and **metadata**: `org_id, source_platform, entity_type, entity_id, timestamp, project_id (optional)`. Retrieval always filters by `org_id`. Metadata `entity_id` lets every answer cite its originating graph node.

---

## 6. BACKEND BEHAVIOUR (implement all)

### 6.1 Auth and RBAC
- `AUTH_MODE=firebase`: verify Firebase ID token, map `firebase_uid` to a `users` row. `AUTH_MODE=dev`: accept `Authorization: Bearer dev:<email>` for seeded users (never enabled when `ENV=production`).
- Roles live in Postgres, not in the token. `require_role("manager","admin")` dependency on every protected route.
- Permission matrix (enforce and test): 
  - **Employee:** query assistant (scoped to projects they work on), view graph (scoped), update own task status, view own alerts.
  - **Manager:** everything Employee has org-wide, plus trigger sync, view risk dashboard, view all projects.
  - **Admin:** manage users/roles, configure risk model thresholds, manage connections, view audit log, trigger sync.
- Every state-changing and admin action writes to `audit_log`.
- **Scoping for the assistant:** Employee retrieval is restricted to graph nodes connected to their projects; this is enforced in the Cypher/Chroma filter, **not** by prompt instructions.

### 6.2 Integrations (Process 1)
`BaseConnector` interface: `authenticate()`, `fetch_since(cursor) -> list[NormalizedRecord]`, `platform`. `NormalizedRecord`: `platform, entity_type, external_id, payload (common schema), occurred_at`. Implement:
- **GitHub:** repos, commits (author email, message, additions/deletions), issues (map to Task when linked to a project). Auth via PAT or OAuth app token.
- **Trello:** boards (to Project), cards (to Task), due dates (to Deadline), members. API key + token.
- **Gmail:** message metadata + snippet only (least-privilege `gmail.readonly`), sender/recipients, thread id.
- **Google Calendar:** events, attendees, times, `calendar.readonly`.
- Use `tenacity` exponential backoff on 429/5xx and honor `Retry-After`; incremental sync using stored cursors (`last_synced_at`); a rate-limit error must never lose data (test TC-02).
- Mock connectors read JSON fixtures in `integrations/mock/` that form a coherent fictional org (about 12 employees, 5 projects, 60 tasks, 300 commits, 80 emails, 40 events, with some intentionally slipping projects).

### 6.3 Ingestion (Process 2)
Staging rows to Neo4j `MERGE` operations in batches (UNWIND) + embeddings to Chroma. Mark staging rows `ingested`/`failed`. Idempotent via `content_hash`. A new Trello task must appear as a Task node within one sync cycle (TC-04).

### 6.4 RAG assistant (Process 4)
Pipeline in `rag_service.py`:
1. **Intent/entity step:** classify question (status, risk, workload, who/what/when) and extract entities (project, person, date range).
2. **Graph retrieval:** pick from a *whitelisted set of parameterized Cypher templates* (e.g., overdue tasks per project, workload per employee, projects with high-risk score, recent commits per repo). **Never execute LLM-generated Cypher.** Document this as a security decision.
3. **Vector retrieval:** top-k from Chroma filtered by `org_id` (+ project/entity filters).
4. **Context assembly:** merge, dedupe, trim to token budget, tag each item with `[source: entity_type:entity_id]`.
5. **Generation** via the provider factory, system prompt forces: answer only from supplied context, say "I don't have data on that" when absent, cite sources, refuse out-of-scope questions (non-org-status).
6. **Response:** `{answer, citations:[{entity_type, entity_id, label}], used_graph_queries:[...], confidence}`.
`mock` LLM must return deterministic, context-derived answers so tests (TC-03) pass offline.

### 6.5 Risk prediction (Process 3)
- **Features per project (and task rollup):** commit_frequency_7d and 28d, commit_trend, task_velocity (tasks done/week), open_task_ratio, overdue_task_count, deadline_slippage_days (mean of completed-vs-due), blocked_task_ratio, days_to_deadline, workload_concentration (share of open tasks held by the top contributor), email_activity_trend, meeting_load.
- **Model:** logistic regression baseline + gradient boosting; choose by cross-validated ROC-AUC; save with `joblib` plus `model_card.json` (features, metrics, training data description, version).
- **Training data:** `synthetic.py` generates a few thousand project-weeks with realistic correlations and noise, plus optional pilot CSV; fixed random seed.
- **Explainability (simple, no SHAP):** return the top-3 contributing features per score (coefficient x standardized value for logistic; permutation-importance-weighted deviation from baseline for boosting) as plain-English `top_factors`.
- **Cold start (TC-05):** if history < `min_history_days` or too few events, return `confidence="low"` and a banded "insufficient data" flag instead of a falsely precise number.
- Bands from `risk_config` thresholds. Persist to `risk_scores`; scheduler recomputes after each ingestion.

### 6.6 Alerts (Notification module)
After scoring, compare with the previous band; when a project/task moves to a higher band, create an `alerts` row for the project's manager and owner. In-app only. Include a one-line recommendation (rule-based templates keyed by dominant risk factor, e.g., "Reassign 2 tasks from X").

### 6.7 Dashboard aggregation (Process 5)
`GET /api/v1/dashboard/summary`: counts by band, top 5 at-risk projects with factors, overdue tasks, workload heatmap data, recent alerts, sync health. Cache for 30s.

### 6.8 API surface (all under `/api/v1`, OpenAPI documented)
`POST /auth/session` · `GET /users/me` · `GET/POST/PATCH /admin/users` · `GET/POST/DELETE /integrations`, `GET /integrations/{platform}/oauth/start|callback` · `POST /sync/run`, `GET /sync/runs` · `GET /graph/overview`, `GET /graph/neighbors/{id}` · `POST /assistant/query` · `GET /risk/projects`, `GET /risk/projects/{id}` · `GET /dashboard/summary` · `GET /alerts`, `POST /alerts/{id}/read` · `PATCH /tasks/{id}/status` · `GET/PUT /admin/risk-config` · `GET /admin/audit` · `GET /health` (checks Postgres, Neo4j, Chroma, LLM provider).

---

## 7. FRONTEND BEHAVIOUR

- Login (Firebase; dev-mode user picker when `AUTH_MODE=dev`). Role-aware navigation via `RoleGuard`.
- **Dashboard:** KPI cards, risk distribution chart, top at-risk projects (RiskBadge + top factors + recommendation), workload heatmap, alert feed, sync status.
- **Assistant:** chat UI with streaming-style rendering, citation chips that open the underlying node in the graph view, suggested starter questions (e.g., "Which of my team's projects are most likely to slip this month, and why?").
- **Graph:** interactive force graph with filters by node type and project; click shows node details.
- **Projects / Project detail:** tasks, deadlines, commits timeline, risk history sparkline.
- **My Work (Employee):** list own tasks, update status.
- **Admin:** user and role management, platform connections with last sync status, risk threshold sliders, audit log table.
- Clean executive styling, responsive, accessible (labels, contrast, keyboard nav), loading/empty/error states everywhere.

---

## 8. DEPLOYMENT

`docker-compose.yml` services: `backend` (FastAPI, uvicorn), `frontend` (Next.js), `postgres`, `neo4j`, `chroma`. Health checks, named volumes, dependency ordering, env via `.env`. Commands via `Makefile`: `make up`, `make down`, `make migrate`, `make seed`, `make train`, `make test`, `make lint`, `make demo` (up + migrate + train + seed). The whole stack must start with `make demo` and be usable with **zero external credentials** (mock mode).

---

## 9. PHASES (execute in order; verify before advancing)

1. **Scaffold & infra:** repo tree, Compose, configs, health endpoint. *Verify:* `docker compose up` all healthy; `/health` green.
2. **Data layer:** Alembic migration, Neo4j bootstrap, Chroma bootstrap. *Verify:* migration applies; constraints exist.
3. **Auth & RBAC:** dev + Firebase modes, permission matrix, audit logging. *Verify:* TC-01 (Employee to Admin endpoint = 403).
4. **Connectors + mocks + sync + staging:** *Verify:* TC-02 (rate limit retried, no data loss) and mock sync fills staging.
5. **Ingestion to graph + vector:** *Verify:* TC-04, node/relationship counts match fixtures.
6. **Risk pipeline:** features, synthetic data, training, scoring, alerts. *Verify:* TC-05; model metrics in `model_card.json`.
7. **RAG assistant:** retrieval templates, scoping, citations, providers. *Verify:* TC-03, employee scoping test.
8. **Dashboard API + frontend:** all pages. *Verify:* Playwright smoke (login, dashboard loads, ask a question, see citation).
9. **Hardening:** secret-redaction logging, input validation, CORS, rate limiting on `/assistant/query`, dependency pinning. *Verify:* security tests pass.
10. **Docs:** finish `README.md`, `EXPLANATION.md`, architecture and DFD diagrams. *Verify:* checklist in Section 10.

Required test cases (name tests `test_tc01_...` etc.): **TC-01** Employee token calls Admin-only endpoint gives 403. **TC-02** GitHub rate-limit error gives retry with backoff, no data lost. **TC-03** Query "which projects are at risk?" lists projects above threshold with cited evidence. **TC-04** New Trello task gives Task node in Neo4j within one sync cycle. **TC-05** Sparse history gives low-confidence flag, not a false-precise score. Add further unit tests for connectors (mocked responses), feature engineering (known inputs/outputs), and an end-to-end flow (mock Trello change, sync, NL query reflects it).

---

## 10. DOCUMENTATION DELIVERABLES (these two files are mandatory and graded)

### 10.1 `README.md`
Concise and practical. Sections: project title and one-paragraph pitch; key features; architecture diagram (Mermaid); tech stack table; prerequisites; **Quick Start** (`cp .env.example .env`, `make demo`, URLs and demo logins per role); environment variables table (name, purpose, required?, default); mock vs real mode instructions for each integration (how to get GitHub PAT, Trello key/token, Google OAuth credentials, Firebase project, LLM keys); common commands (`Makefile`); running tests; API overview with link to `/docs`; folder structure summary; demo script (5-minute walkthrough with sample questions); limitations; roadmap/extension points; credits (authors Avinash Chaudhary and Ayush Dubey, guide Er. M.B. Singh, SRMCEM Lucknow, AKTU); license placeholder.

### 10.2 `EXPLANATION.md`
Long-form engineering document for a viva/evaluation reader. Required structure:

1. **Purpose and how to read this document.**
2. **Architectural decisions.** For *each* decision use this template: **Decision**, **Context/problem**, **Options considered**, **Why this option**, **Trade-offs/risks**, **Where it lives in the code**. Cover at minimum: polyglot persistence (Neo4j vs PostgreSQL vs Chroma, what goes where and why); layered service architecture; FastAPI choice; in-process APScheduler vs Celery; staging table pattern; MERGE-based idempotent ingestion and content hashing; whitelisted Cypher templates instead of LLM-generated Cypher; RAG design (graph + vector hybrid, citation tagging, token budget); provider factory and mock LLM; Firebase Auth with roles in Postgres; scoping enforced in queries not prompts; OAuth token encryption; least-privilege API scopes and metadata-only email storage; model choice, features, cold-start handling and explainability approach; synthetic training data and its honest limitations; mock mode strategy; Docker Compose topology; each synopsis inconsistency resolved in Section 2.
3. **Data schemas in full, with rationale.** Reproduce the Neo4j node/relationship tables, the full PostgreSQL DDL, and the Chroma record/metadata schema, and for **each table, label and relationship explain what it stores, who writes it, who reads it, why it exists, and why the columns/constraints/indexes were chosen.** Include an ER-style Mermaid diagram of the graph and of the relational tables.
4. **File-by-file reference.** Walk the **entire** repository tree. For **every file** give: purpose, key classes/functions, who calls it / what it depends on, and *why it is a separate file* (the design reason). Group by directory with a short directory-level rationale first. Do not skip config, scripts, migrations, or test files.
5. **Request and data flows.** Step-by-step traces with Mermaid sequence diagrams for: (a) a scheduled sync end to end, (b) a natural-language question end to end, (c) a risk-score recompute and alert generation, (d) a login and RBAC check. Map each step to files and functions.
6. **Security model.** Threats, controls, and where implemented (RBAC matrix, audit log, secrets handling, token encryption, injection avoidance, rate limiting, data minimization).
7. **ML model card.** Features (with formulas and why each is a risk signal), training data generation, models compared, metrics, thresholds/bands, explainability method, known failure modes.
8. **Testing strategy mapped to code.** Table of tests to what they verify to which synopsis requirement/TC.
9. **Synopsis traceability matrix.** Table: each objective/module/scope item from the synopsis to the implementing files to how to demo/verify it.
10. **Known limitations and honest gaps** (what is mocked, what is approximated, what was left out of scope).
11. **Future work** mapped to concrete extension points in the code.
12. **Glossary** (digital twin, RAG, knowledge graph, polyglot persistence, etc.).

Quality bar: no placeholder text, no "TBD", no file left undocumented; every claim in the document must match the actual code. At the end of Phase 10, run a script that lists all files in the repo and asserts each appears in section 4 of `EXPLANATION.md`; fix any omissions.

---

## 11. ACCEPTANCE CRITERIA (final check; report results as a short checklist)

- [ ] `make demo` brings up the full stack with no external credentials.
- [ ] Three demo logins (manager, employee, admin) behave per the permission matrix.
- [ ] Mock sync populates Neo4j, Chroma and Postgres; counts match fixtures.
- [ ] Assistant answers the sample questions with citations; employee answers are scoped.
- [ ] Risk dashboard shows banded scores with top factors; a slipping project triggers an alert.
- [ ] TC-01 to TC-05 pass; `make test` and `make lint` are green.
- [ ] Real-mode code paths for GitHub, Trello, Gmail, Calendar, Firebase, OpenAI/Gemini exist and are documented (even if untested live).
- [ ] No secrets in the repo; `.env.example` complete.
- [ ] `README.md` and `EXPLANATION.md` complete per Section 10, with the file-coverage script passing.

Begin with Phase 1. Produce the implementation plan artifact first, then proceed.
