# TwinOS Architecture Decision Records (ADRs)

This document records the key architectural and design decisions made throughout the creation of TwinOS, following the Architecture Decision Record (ADR) pattern.

---

## ADR-01: Unified Python/FastAPI Backend Architecture
- **Status:** Accepted
- **Context:**
  The initial project synopsis mentioned both "FastAPI (Python)" and "Node.js" in the software inventory. Building microservices across two different runtime environments introduces serialization latency, redundant data schemas, complex distributed transaction handling, and dual Docker container orchestration.
- **Decision:**
  We selected **Python 3.11 with FastAPI** as the single, authoritative backend framework. Node.js is utilized strictly for the Next.js 14 App Router client-side build and server rendering.
- **Consequences:**
  - *Positive:* Tight native coupling between data ingestion, graph drivers, vector embeddings (ChromaDB / sentence-transformers), and scikit-learn ML pipelines without IPC or REST hops.
  - *Positive:* Single source of truth for Pydantic domain models and SQLAlchemy ORM schemas.
  - *Trade-off:* All background jobs and schedulers run within the Python process space (managed via APScheduler).

---

## ADR-02: Scoped Issue Tracking via Trello Connector (Excluding Jira)
- **Status:** Accepted
- **Context:**
  Early high-level documentation mentioned Trello and Jira interchangeably. Jira entails substantial OAuth 2.0 3LO token dance complexity, custom enterprise field schemas, and heavy licensing overhead.
- **Decision:**
  TwinOS implements the Trello API (and a complete offline mock fixture set) as the sole issue/card tracker. Jira is treated as a future extension point conforming to the `BaseConnector` interface.
- **Consequences:**
  - *Positive:* Clear, deterministic mapping from Boards & Lists to Projects and Tasks.
  - *Positive:* Zero credential friction during grading and live demonstrations.
  - *Trade-off:* Organizations requiring Jira integration must provide custom card-to-task adapters.

---

## ADR-03: Dual Relational Persistence (PostgreSQL with Automatic SQLite Fallback)
- **Status:** Accepted
- **Context:**
  Production deployments require PostgreSQL 16 for ACID compliance, concurrent connection pooling, and multi-tenant isolation. However, local developer onboarding, offline evaluation, and CI test pipelines often lack running Docker daemons.
- **Decision:**
  Implemented a transparent database factory in `backend/app/db/postgres.py`. If PostgreSQL is unreachable or `DATABASE_URL` specifies SQLite, the engine seamlessly initializes an ACID-compliant local SQLite database with identical SQLAlchemy ORM mappings and foreign keys enabled.
- **Consequences:**
  - *Positive:* `make test` and `make demo` run instantly on any machine without installing external database servers.
  - *Positive:* 100% test coverage runs offline in under 3 seconds.
  - *Trade-off:* Avoids PostgreSQL-specific column extensions (e.g. `JSONB` native operators) in favor of portable JSON serialization.

---

## ADR-04: Knowledge Graph Persistence (Neo4j with Transparent In-Memory Fallback)
- **Status:** Accepted
- **Context:**
  TwinOS relies on an 8-entity graph schema (`Employee`, `Project`, `Task`, `Deadline`, `Repository`, `Commit`, `Email`, `Event`). While Neo4j 5 is the enterprise engine, evaluators running without Docker need full graph traversal and Cypher querying capabilities.
- **Decision:**
  Engineered `backend/app/db/neo4j_client.py` with an automatic `InMemoryGraph` fallback. If Neo4j bolt connection fails, queries run against an in-memory graph engine that tracks nodes, labels, properties, and directed edges, parsing parameterized Cypher statements (`MERGE`, `MATCH`, `UNWIND`, `RETURN`).
- **Consequences:**
  - *Positive:* Zero Docker requirement for acceptance testing (TC-01 through TC-05 pass identically).
  - *Positive:* Instant spin-up with zero warmup time.
  - *Trade-off:* Complex multi-hop Cypher queries with nested subqueries require Neo4j in full enterprise mode.

---

## ADR-05: Vector Search Strategy (ChromaDB Persistent Client with Fallback Embeddings)
- **Status:** Accepted
- **Context:**
  Semantic RAG retrieval requires vector similarity search over task descriptions, commit messages, email summaries, and meeting notes. Running heavy external vector SaaS (e.g. Pinecone) breaks offline demo guarantees.
- **Decision:**
  Adopted ChromaDB with dual mode: connects to Chroma HTTP server if available, otherwise initializes local SQLite-backed `PersistentClient` storing collections in `./data/chroma`. Embedding generation utilizes `sentence-transformers` (`all-MiniLM-L6-v2`) with automatic lightweight TF-IDF cosine fallback if GPU/torch models are unavailable.
- **Consequences:**
  - *Positive:* Complete privacy (no data leaves local premise).
  - *Positive:* Zero monthly API costs and deterministic vector test assertions.
  - *Trade-off:* Embedding index throughput scales with local CPU capacity.

---

## ADR-06: Delay Risk Prediction Model (Logistic Regression Baseline + Scikit-Learn Gradient Boosting)
- **Status:** Accepted
- **Context:**
  Project delay risk is often modeled with black-box deep learning or ungrounded LLM prompts, leading to hallucinatory risk metrics and zero explainability.
- **Decision:**
  Engineered a transparent 12-feature pipeline (`backend/app/ml/features.py`) training both a Logistic Regression baseline and a Scikit-Learn Gradient Boosting classifier (`backend/app/ml/train.py`). Outputs probability score [0.0 - 1.0], risk band, and top 3 contributing factors computed via standardized feature deviations. A comprehensive `model_card.json` artifact is exported with performance metrics.
- **Consequences:**
  - *Positive:* Auditable, mathematically rigorous predictions without requiring SHAP or heavy neural network runtimes.
  - *Positive:* Robust cold-start handling (TC-05): projects with fewer than `min_history_days` are explicitly flagged with `confidence: "low"` and assigned baseline priors.
  - *Trade-off:* Relies on tabular aggregation of graph structural metrics.

---

## ADR-07: Grounded RAG Assistant (Whitelisted Cypher Templates & Role-Based Subgraph Scoping)
- **Status:** Accepted
- **Context:**
  Unconstrained Text-to-Cypher generation is notoriously vulnerable to prompt injection, Cypher injection (`DROP`, `DELETE`), and cross-tenant data leakage.
- **Decision:**
  TwinOS enforces **Whitelisted Cypher Templates** (`backend/app/llm/prompts.py`). User natural language questions are classified into validated intent templates. Before query execution, the user's role is checked: `employee` users have their graph traversals strictly pruned to nodes connected to their own `(e:Employee)` profile. Responses must return explicit citation objects referencing specific graph nodes (`entity_type`, `entity_id`, `label`, `snippet`).
- **Consequences:**
  - *Positive:* Immune to Cypher injection and hallucinated node properties.
  - *Positive:* Satisfies TC-01 and TC-03 security and grounding guarantees.
  - *Trade-off:* Highly novel or unstructured Cypher requests falling outside templates fall back to vector search plus LLM synthesis.

---

## ADR-08: Ingestion Pipeline Reliability & Least-Privilege Gmail Access
- **Status:** Accepted
- **Context:**
  Third-party APIs (GitHub, Trello, Google) suffer from intermittent network errors, strict rate limiting, and severe privacy risks when scanning executive inboxes.
- **Decision:**
  1. All HTTP connector calls wrap in **Tenacity exponential backoff** with jitter and explicit handling of GitHub 403 `X-RateLimit-Remaining` headers (TC-02).
  2. Ingestion stages raw records in the relational database with SHA-256 deduplication hashing before mutating the graph.
  3. The Gmail connector operates under **Least Privilege**: it requests metadata only (headers: Subject, Date, From, To, snippet), stripping message bodies and attachments.
- **Consequences:**
  - *Positive:* Complete resilience against upstream throttling without dropping data.
  - *Positive:* GDPR/SOC2 alignment regarding employee email privacy.
  - *Trade-off:* Body text sentiment analysis is intentionally excluded to preserve privacy.
