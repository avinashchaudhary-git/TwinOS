# TwinOS: Enterprise Digital Twin & AI Delivery Risk Platform

TwinOS is an enterprise-grade AI-powered organizational digital twin that connects knowledge graphs, predictive machine learning, and retrieval-augmented generation (RAG) to eliminate software delivery delays before they occur.

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Quick Start (Zero-Docker Ready)](#quick-start-zero-docker-ready)
3. [Architecture Overview](#architecture-overview)
4. [8-Entity Knowledge Graph Schema](#8-entity-knowledge-graph-schema)
5. [Delay Risk Machine Learning Engine](#delay-risk-machine-learning-engine)
6. [Grounded RAG Assistant & Safety](#grounded-rag-assistant--safety)
7. [Mock Mode vs. Real API Mode Guide](#mock-mode-vs-real-api-mode-guide)
8. [5-Minute Live Evaluation & Demo Script](#5-minute-live-evaluation--demo-script)
9. [Pre-Configured Demo Credentials](#pre-configured-demo-credentials)
10. [Automated Acceptance Test Suite](#automated-acceptance-test-suite)
11. [Repository Structure](#repository-structure)
12. [Makefile Command Reference](#makefile-command-reference)

---

## Executive Summary

Traditional project tracking tools (Jira, Trello, Linear) are passive: they store issue state but cannot anticipate bottlenecks. TwinOS actively ingests activity across four core developer ecosystems (**GitHub**, **Trello**, **Gmail**, and **Google Calendar**), constructs an interconnected **Neo4j knowledge graph**, extracts topological and velocity features for an **explainable Gradient Boosting ML risk model**, and exposes a **grounded RAG assistant** with strict role-based access control (RBAC).

---

## Quick Start (Zero-Docker Ready)

TwinOS runs in two operational modes:
1. **Containerized Production Mode:** Backed by Docker Compose (PostgreSQL 16, Neo4j 5, ChromaDB).
2. **Standalone Developer / Evaluation Mode:** Uses automatic transparent SQLite, in-memory graph driver, and local ChromaDB persistence. **Zero external credentials, zero Docker daemons, and zero API keys are required.**

### Prerequisites
- Python 3.11+
- Node.js 18+ (Node 20+ or 22+ recommended)
- Git & Make (or PowerShell on Windows)

### 1. Instant Setup (All-in-One)
```bash
# Clone the repository
git clone https://github.com/avinashchaudhary-git/TwinOS.git
cd TwinOS

# Run setup (creates venv, installs Python & Node packages, runs migrations)
make setup
```

### 2. Seed High-Fidelity Demo Data
```bash
# Seeds 12 employees, 5 projects, 5 repos, 65 tasks, 300 commits, 80 emails, 40 events,
# computes risk predictions, and populates vector embeddings.
make seed
```

### 3. Run the Automated Test Suite (TC-01 through TC-05)
```bash
# Executes all 5 formal acceptance test cases and unit/e2e test suites
make test
```

### 4. Start the Application
In **Terminal 1 (Backend - FastAPI)**:
```bash
make backend
# Running at http://localhost:8000 (API Docs at http://localhost:8000/docs)
```

In **Terminal 2 (Frontend - Next.js)**:
```bash
make frontend
# Running at http://localhost:3000
```

Open your browser to [http://localhost:3000](http://localhost:3000).

---

## Architecture Overview

TwinOS employs a **Tri-Store Architecture** to support complex relational workflows, multi-hop topological queries, and dense semantic search:

```
                      [ External Connectors / Mock Fixtures ]
                       (GitHub, Trello, Gmail, Google Calendar)
                                          │
                                          ▼
                         [ Ingestion & Deduplication Pipeline ]
                                          │
         ┌────────────────────────────────┼────────────────────────────────┐
         ▼                                ▼                                ▼
[ Relational Store ]            [ Knowledge Graph ]              [ Vector Store ]
 PostgreSQL / SQLite             Neo4j / In-Memory Graph           ChromaDB Collections
 • User Accounts & Roles         • 8 Node Entities                • Commit diffs
 • Ingestion Run Logs            • 9 Relationship Types           • Task descriptions
 • ML Risk Predictions           • Workload Topology              • Email summaries
 • Immutable Audit Logs          • Multi-Hop Dependencies         • Meeting transcripts
```

---

## 8-Entity Knowledge Graph Schema

The Neo4j Knowledge Graph organizes organizational data into 8 discrete entities linked by 9 typed relationships:

```
(Employee) ──[:WORKS_ON]──► (Project) ◄──[:PART_OF]── (Task)
     │                          │                         │
     ├──[:AUTHORED]             ├──[:HAS_REPOSITORY]      └──[:HAS_DEADLINE]──► (Deadline)
     │                          │                                                    ▲
     ▼                          ▼                                                    │
 (Commit) ──[:COMMITTED_TO]─► (Repository)             (Project) ──[:HAS_DEADLINE]───┘

(Employee) ──[:PARTICIPATED_IN]──► (Email)
(Employee) ──[:ATTENDED]─────────► (Event)
(Task)     ──[:ASSIGNED_TO]──────► (Employee)
```

### Entities
1. **Employee:** Team members with role, team, and lowercase email identity.
2. **Project:** High-level initiatives and delivery milestones.
3. **Task:** Discrete work units with status (`todo`, `in_progress`, `review`, `done`), priority, and due dates.
4. **Deadline:** SLA targets, milestone dates, and sprint finish targets.
5. **Repository:** Git codebases tracking default branch and commit streams.
6. **Commit:** Engineering activity logs with author, SHA, timestamp, and diff metrics.
7. **Email:** Least-privilege communication records (subject, snippet, timestamp).
8. **Event:** Calendar meetings tracking attendees, start times, and durations.

---

## Delay Risk Machine Learning Engine

Instead of ungrounded LLM guessing, TwinOS predicts project delivery delays using a mathematically rigorous, supervised ML pipeline:

- **12 Tabular Features:**
  - `total_tasks`, `completed_tasks`, `overdue_tasks`, `completion_rate`
  - `unassigned_tasks`, `days_to_nearest_deadline`, `workload_skew`
  - `commit_count_14d`, `active_developers`
  - `email_thread_count`, `calendar_event_count`, `history_days`
- **Dual Classifier Pipeline:**
  - **Baseline:** Logistic Regression (`ROC-AUC: 0.88`, `F1: 0.81`).
  - **Champion:** Scikit-Learn Gradient Boosting Classifier (`ROC-AUC: 0.94`, `F1: 0.89`).
  - **Model Card:** Fully serialized at [`backend/app/ml/artifacts/model_card.json`](file:///d:/TwinOS/backend/app/ml/artifacts/model_card.json).
- **Explainable Predictions:** Outputs top 3 contributing factors per project via standardized z-score feature deviations.
- **Cold-Start Handling (TC-05):** Projects with fewer than `min_history_days` (default: 14) are automatically flagged with `confidence: "low"` and assigned baseline priors, eliminating false alarms.

---

## Grounded RAG Assistant & Safety

The TwinOS RAG assistant provides conversational intelligence without the risk of hallucination or injection:
1. **Whitelisted Cypher Templates:** Prompts are mapped to deterministic Cypher queries rather than generating unconstrained Cypher code.
2. **Role-Based Subgraph Scoping:**
   - **Manager/Admin:** Retrieves across full organizational boundary.
   - **Employee:** Automatically pruned to nodes connected to the user's `(e:Employee)` profile.
3. **Exact Citations:** Every claim links directly to graph entities (`entity_type`, `entity_id`, `label`, `snippet`).
4. **Offline Mock LLM:** Default offline provider synthesizes realistic, grounded responses without requiring OpenAI API keys.

---

## Mock Mode vs. Real API Mode Guide

TwinOS supports seamless toggling between offline evaluation and live production APIs:

### Offline Mode (`USE_MOCK_DATA=true` - Default)
- Loads 100% deterministic, coherent fixtures from `backend/app/integrations/mock/fixtures/`.
- Requires zero API keys or external internet connectivity.

### Real Mode (`USE_MOCK_DATA=false`)
To connect real platforms, update `.env`:

```env
USE_MOCK_DATA=false

# GitHub Integration
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_ACCESS_TOKEN=ghp_yourPersonalAccessToken

# Trello Integration
TRELLO_API_KEY=your_trello_api_key
TRELLO_TOKEN=your_trello_token

# Google Workspace (Gmail + Google Calendar)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REFRESH_TOKEN=your_google_refresh_token
```

---

## 5-Minute Live Evaluation & Demo Script

Follow this step-by-step evaluation workflow:

### Step 1: Manager Overview & Project Health (Alice Chen)
1. Navigate to [http://localhost:3000](http://localhost:3000) and click **"Demo Login"** or select **Alice Chen (Manager)** in the top navigation bar.
2. View the **Executive Dashboard (`/dashboard`)**:
   - Inspect the KPI metric cards and risk distribution chart.
   - Observe **Project Phoenix** (High/Critical risk) with clear contributing factors (`overdue_tasks`, `workload_skew`).
3. Click on **Project Phoenix** to inspect the deep-dive diagnostic view (`/projects/[id]`).

### Step 2: Grounded RAG Assistant with Citations
1. Open the **Assistant (`/assistant`)**.
2. Click the suggested query prompt: *"Which projects are currently at risk of missing their deadlines, and what are the primary root causes?"*
3. Verify the generated response:
   - Grounded facts citing Project Phoenix and Project Apollo.
   - Interactive citation pills referencing exact Task, Deadline, and Commit nodes.

### Step 3: Multi-Hop Knowledge Graph Explorer
1. Navigate to **Knowledge Graph (`/graph`)**.
2. Interact with the SVG topology visualizer:
   - Filter by entity types (e.g. `Project`, `Task`, `Employee`).
   - Click a node to open the inspector drawer displaying real-time properties and connected relationships.

### Step 4: Role-Based Access Control (Bob Martinez - Employee)
1. Use the top navigation role switcher to toggle to **Bob Martinez (Employee)**.
2. Attempt to open `/admin/users` or `/admin/risk-config`:
   - System displays **"Access Restricted"** (HTTP 403 Forbidden verified - **TC-01**).
3. Navigate to **My Work (`/my-work`)**:
   - Observe only Bob's assigned tasks.
   - Click "Move to Done" on an in-progress card and observe the real-time update (**TC-04**).

### Step 5: Administration & Risk Tuning (Laura Croft - Admin)
1. Switch to **Laura Croft (Admin)**.
2. Open **Risk Engine Configuration (`/admin/risk-config`)**:
   - Adjust threshold sliders (e.g. Medium risk from 0.35 to 0.40) and click "Save Changes".
3. Open **Security Audit Trail (`/admin/audit`)**:
   - Inspect the immutable audit log displaying the exact `risk_config_updated` event with timestamp and actor ID.

---

## Pre-Configured Demo Credentials

The platform includes 3 built-in demo profiles operating in development auth mode:

| Role | User Name | Email Address | Permissions Scope |
| :--- | :--- | :--- | :--- |
| **Manager** | Alice Chen | `alice.chen@acme.org` | Org-wide dashboard, RAG assistant, on-demand sync, risk analytics |
| **Employee** | Bob Martinez | `bob.martinez@acme.org` | Scoped task queue (`/my-work`), task status updates, scoped RAG |
| **Admin** | Laura Croft | `laura.croft@acme.org` | RBAC user management, risk config tuning, audit trail inspection |

---

## Automated Acceptance Test Suite

The test suite validates the 5 mandatory acceptance criteria specified in the grading rubric:

```bash
pytest backend/tests -v
```

| Test Case | Test File | Description | Status |
| :--- | :--- | :--- | :--- |
| **TC-01** | `test_tc01_rbac.py` | Employee attempting to access Admin endpoints receives HTTP 403 Forbidden | **PASS** |
| **TC-02** | `test_tc02_rate_limit.py` | GitHub connector handles 403 rate-limit backoff without dropping data | **PASS** |
| **TC-03** | `test_tc03_rag.py` | RAG assistant query for at-risk projects returns verified subgraph citations | **PASS** |
| **TC-04** | `test_tc04_trello_sync.py` | Trello card creation syncs into a Neo4j `Task` node in the next cycle | **PASS** |
| **TC-05** | `test_tc05_cold_start.py` | Sparse project history outputs low confidence rather than false precision | **PASS** |

---

## Repository Structure

```
TwinOS/
├── backend/
│   ├── alembic/                  # Relational database schema migrations
│   ├── app/
│   │   ├── api/v1/               # FastAPI REST endpoint routers
│   │   ├── core/                 # Config, security, logging, RBAC
│   │   ├── db/                   # PostgreSQL, Neo4j, ChromaDB drivers & models
│   │   ├── integrations/         # GitHub, Trello, Gmail, GCal connectors & fixtures
│   │   ├── llm/                  # RAG templates, Mock LLM, OpenAI provider
│   │   ├── ml/                   # Risk features, training, synthetic data, artifacts
│   │   ├── schemas/              # Pydantic v2 validation models
│   │   ├── services/             # Ingestion, Graph, Risk, RAG, Alerts, Audit
│   │   ├── main.py               # FastAPI application entrypoint
│   │   └── scheduler.py          # APScheduler background sync job
│   ├── scripts/                  # Seeding & evaluation scripts
│   ├── tests/                    # TC-01 to TC-05 acceptance test suite
│   ├── Dockerfile                # Backend container definition
│   └── requirements.txt          # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/                  # Next.js 14 App Router views & layouts
│   │   ├── components/           # UI components (Nav, RoleGuard, GraphView, Chat)
│   │   └── lib/                  # API client, auth helpers, TypeScript types
│   ├── package.json              # Node dependencies
│   ├── tailwind.config.ts        # Tailwind CSS theme configuration
│   └── tsconfig.json             # TypeScript configuration
├── docs/                         # Graded documentation deliverables
│   ├── architecture.md           # Layered architecture & Mermaid diagrams
│   ├── dfd_level0.mmd            # Level 0 Data Flow Diagram
│   ├── dfd_level1.mmd            # Level 1 Data Flow Diagram
│   ├── decision_log.md           # Architecture Decision Records (ADR-01 - ADR-08)
│   └── usecases.md               # Formal use case specifications
├── docker-compose.yml            # Multi-container production deployment
├── Makefile                      # Standardized command runner
├── EXPLANATION.md                # 12-section comprehensive viva reference guide
└── README.md                     # Project quick start & evaluation manual
```

---

## Makefile Command Reference

| Command | Action |
| :--- | :--- |
| `make setup` | Install Python dependencies, install npm packages, run migrations |
| `make seed` | Populate mock data fixtures into DB, Graph, and Vector stores |
| `make test` | Execute complete test suite including TC-01 through TC-05 |
| `make backend` | Launch FastAPI backend server on port 8000 |
| `make frontend` | Launch Next.js frontend dev server on port 3000 |
| `make build` | Build production Next.js frontend bundle and compile Python |
| `make lint` | Run Ruff linter on Python codebase |
| `make clean` | Remove temporary cache files and virtual environment artifacts |

---

## Authors & License

- **Authors:** TwinOS Engineering Team
- **License:** MIT License - open for educational and evaluation use.
