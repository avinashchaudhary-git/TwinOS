import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Deterministic seed
random.seed(42)

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "app" / "integrations" / "mock" / "fixtures"
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

with open(FIXTURES_DIR / "org_dataset.json", "r") as f:
    base_data = json.load(f)

org = base_data["organization"]
employees = base_data["employees"]
projects = base_data["projects"]
repos = base_data["repositories"]

base_date = datetime(2026, 10, 6, 12, 0, 0, tzinfo=UTC)

# 1. Generate ~60 Tasks
tasks = []
task_verbs = [
    "Implement",
    "Refactor",
    "Deploy",
    "Debug",
    "Configure",
    "Audit",
    "Write unit tests for",
    "Optimize query performance in",
    "Migrate database schema for",
    "Update documentation for",
    "Benchmark",
    "Secure endpoint for",
]
task_nouns = [
    "OAuth token rotation",
    "Redis caching layer",
    "GraphQL federation gateway",
    "PostgreSQL partition maintenance",
    "Kubernetes cluster autoscaler",
    "Ingress TLS certificates",
    "Kafka event consumer",
    "CI/CD staging pipeline",
    "Telemetry metrics exporter",
    "RBAC permission evaluator",
    "Rate limiting middleware",
    "S3 bucket replication",
    "CloudWatch alert policy",
    "Grafana dashboards",
]

task_counter = 1
for proj in projects:
    p_id = proj["id"]
    is_at_risk = proj["status"] == "at_risk"
    # At risk projects get 15-18 tasks with high blocked/overdue
    count = 16 if is_at_risk else 11

    for _ in range(count):
        t_id = f"task-{task_counter:03d}"
        assignee = random.choice(employees)
        verb = random.choice(task_verbs)
        noun = random.choice(task_nouns)
        title = f"{verb} {noun}"

        # Deadlines and status
        if is_at_risk:
            # High probability of blocked or overdue
            status = random.choices(
                ["todo", "in_progress", "blocked", "done"], weights=[0.2, 0.3, 0.35, 0.15]
            )[0]
            # Some past due dates
            days_offset = random.randint(-20, 15)
        else:
            status = random.choices(
                ["todo", "in_progress", "blocked", "done"], weights=[0.2, 0.35, 0.05, 0.4]
            )[0]
            days_offset = random.randint(-5, 30)

        due_date = (base_date + timedelta(days=days_offset)).strftime("%Y-%m-%dT18:00:00Z")
        completed_at = (
            (base_date - timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%dT18:00:00Z")
            if status == "done"
            else None
        )
        priority = random.choice(["low", "medium", "high", "critical"])

        tasks.append(
            {
                "id": t_id,
                "project_id": p_id,
                "title": title,
                "description": f"Detailed task specifications for {title.lower()} within {proj['name']}.",
                "status": status,
                "due_date": due_date,
                "completed_at": completed_at,
                "priority": priority,
                "assignee_email": assignee["email"],
                "assignee_id": assignee["id"],
                "external_id": f"trello_card_{task_counter:03d}",
                "created_at": (base_date - timedelta(days=random.randint(25, 60))).strftime(
                    "%Y-%m-%dT09:00:00Z"
                ),
            }
        )
        task_counter += 1

# 2. Generate ~300 Commits
commits = []
commit_msgs = [
    "fix(api): resolve race condition in token refresh",
    "feat(auth): add MFA verification challenge",
    "chore(deps): bump cryptography to latest secure patch",
    "refactor(db): optimize connection pool parameters",
    "perf(query): add composite index on task status and deadline",
    "fix(k8s): increase memory limits on ingress controller",
    "test(e2e): add automated test scenario for RBAC access",
    "feat(logging): redact sensitive credentials in log interceptor",
    "docs(arch): update Mermaid diagrams in architecture specs",
    "fix(staging): handle intermittent 429 backoff gracefully",
    "feat(metrics): publish latency histogram to telemetry pipeline",
    "refactor(clean): remove deprecated legacy endpoints",
]

repo_map = {r["project_id"]: r for r in repos}
commit_counter = 1
for _ in range(300):
    proj = random.choice(projects)
    repo = repo_map[proj["id"]]
    author = random.choice(employees)
    msg = random.choice(commit_msgs)
    days_ago = random.randint(1, 75)
    commit_time = (
        base_date
        - timedelta(days=days_ago, hours=random.randint(1, 12), minutes=random.randint(1, 59))
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    commits.append(
        {
            "sha": f"a{commit_counter:03d}f8c{random.randint(1000, 9999)}bc{random.randint(1000, 9999)}",
            "repository_id": repo["id"],
            "repository_full_name": repo["full_name"],
            "project_id": proj["id"],
            "message": msg,
            "author_email": author["email"],
            "author_name": author["name"],
            "committed_at": commit_time,
            "additions": random.randint(5, 180),
            "deletions": random.randint(1, 75),
        }
    )
    commit_counter += 1

# 3. Generate ~80 Emails
emails = []
email_subjects = [
    "Sprint Planning Updates & Blockers",
    "Incident Report: High latency on telemetry ingestion",
    "Milestone Slippage Warning: Cloud Infrastructure Migration",
    "Security Audit: OAuth2 token rotation checklist",
    "Weekly Sync: Architectural alignment across core teams",
    "Status Update: SSO federation readiness",
    "Risk Mitigation Proposal: Workload rebalancing for sprint 14",
    "RFC: Moving telemetry pipeline to asynchronous buffering",
    "Release Candidate v2.0 sign-off checklist",
    "Urgent: Database deadlocks detected on staging replica",
]

for i in range(1, 81):
    sender = random.choice(employees)
    recipients = [e["email"] for e in random.sample(employees, k=random.randint(2, 5))]
    proj = random.choice(projects)
    subject = random.choice(email_subjects)
    days_ago = random.randint(1, 60)
    sent_at = (base_date - timedelta(days=days_ago, hours=random.randint(1, 8))).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    snippet = f"Hi team, regarding {proj['name']}: We noticed blockers on recent deliverables. Specifically, {subject.lower()}. Please review the assigned tickets on Trello and verify the latest commits."

    emails.append(
        {
            "id": f"email-{i:03d}",
            "thread_id": f"thread-{(i % 25) + 1:03d}",
            "subject": f"[{proj['name']}] {subject}",
            "sender_email": sender["email"],
            "sender_name": sender["name"],
            "recipient_emails": recipients,
            "sent_at": sent_at,
            "snippet": snippet,
            "project_id": proj["id"],
        }
    )

# 4. Generate ~40 Events
events = []
event_titles = [
    "Sprint Retrospective",
    "Cross-Team Architecture Review",
    "Cloud Migration Readiness Check",
    "Executive Operational Review",
    "Bi-weekly Security Council",
    "Telemetry Performance Review",
    "Milestone Milestone: Release Candidate Beta",
    "Engineering Standup",
]

for i in range(1, 41):
    proj = random.choice(projects)
    title = f"{proj['name']}: {random.choice(event_titles)}"
    days_offset = random.randint(-30, 20)
    start_time = base_date + timedelta(days=days_offset, hours=random.randint(9, 16))
    end_time = start_time + timedelta(minutes=random.choice([30, 45, 60]))
    attendees = [e["email"] for e in random.sample(employees, k=random.randint(3, 7))]
    is_milestone = "Milestone" in title or (i % 7 == 0)

    events.append(
        {
            "id": f"event-{i:03d}",
            "title": title,
            "start_at": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_at": end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "attendees": attendees,
            "project_id": proj["id"],
            "is_milestone": is_milestone,
            "location": "Google Meet / Conference Room Alpha",
        }
    )

# Save individual fixture files
with open(FIXTURES_DIR / "tasks.json", "w") as f:
    json.dump(tasks, f, indent=2)

with open(FIXTURES_DIR / "commits.json", "w") as f:
    json.dump(commits, f, indent=2)

with open(FIXTURES_DIR / "emails.json", "w") as f:
    json.dump(emails, f, indent=2)

with open(FIXTURES_DIR / "events.json", "w") as f:
    json.dump(events, f, indent=2)

print(
    f"Generated fixtures: {len(tasks)} tasks, {len(commits)} commits, {len(emails)} emails, {len(events)} events."
)
