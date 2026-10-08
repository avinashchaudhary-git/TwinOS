from datetime import UTC, datetime

from app.ml.features import FEATURE_NAMES, extract_project_features


def test_extract_project_features_known_inputs():
    ref_date = datetime(2026, 10, 6, 12, 0, 0, tzinfo=UTC)
    project = {
        "id": "proj-test",
        "name": "Test Project",
        "target_end_date": "2026-11-06T18:00:00Z",
    }
    tasks = [
        {
            "id": "t1",
            "status": "todo",
            "due_date": "2026-10-01T12:00:00Z",
            "assignee_id": "emp-1",
        },  # overdue
        {
            "id": "t2",
            "status": "in_progress",
            "due_date": "2026-10-20T12:00:00Z",
            "assignee_id": "emp-1",
        },
        {
            "id": "t3",
            "status": "blocked",
            "due_date": "2026-10-25T12:00:00Z",
            "assignee_id": "emp-2",
        },
        {
            "id": "t4",
            "status": "done",
            "due_date": "2026-10-02T12:00:00Z",
            "completed_at": "2026-10-04T12:00:00Z",
        },
    ]
    commits = [
        {"sha": "c1", "committed_at": "2026-10-05T10:00:00Z"},  # 1 day ago (7d & 28d)
        {"sha": "c2", "committed_at": "2026-09-20T10:00:00Z"},  # 16 days ago (28d only)
    ]
    emails = [{"id": "em1", "sent_at": "2026-10-04T10:00:00Z"}]
    events = [{"id": "ev1", "title": "Standup"}]

    feats = extract_project_features(
        project, tasks, commits, emails, events, reference_date=ref_date
    )

    assert set(feats.keys()) == set(FEATURE_NAMES)
    assert feats["commit_frequency_7d"] == 1.0
    assert feats["commit_frequency_28d"] == 2.0
    assert feats["overdue_task_count"] == 1.0  # t1 is past due
    assert feats["blocked_task_ratio"] == (1.0 / 3.0)  # 1 blocked out of 3 open
    assert feats["meeting_load"] == 1.0
