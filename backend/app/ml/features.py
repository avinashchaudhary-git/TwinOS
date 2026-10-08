from datetime import UTC, datetime
from typing import Any

import numpy as np

FEATURE_NAMES = [
    "commit_frequency_7d",
    "commit_frequency_28d",
    "commit_trend",
    "task_velocity",
    "open_task_ratio",
    "overdue_task_count",
    "deadline_slippage_days",
    "blocked_task_ratio",
    "days_to_deadline",
    "workload_concentration",
    "email_activity_trend",
    "meeting_load",
]


def extract_project_features(
    project: dict[str, Any],
    tasks: list[dict[str, Any]],
    commits: list[dict[str, Any]],
    emails: list[dict[str, Any]],
    events: list[dict[str, Any]],
    reference_date: datetime | None = None,
) -> dict[str, float]:
    """Pure function extracting 12 risk features from project activity artifacts."""
    ref_time = reference_date or datetime.now(UTC)
    if ref_time.tzinfo is None:
        ref_time = ref_time.replace(tzinfo=UTC)

    # 1 & 2. Commits 7d & 28d
    commits_7d = 0
    commits_28d = 0
    for c in commits:
        t_str = c.get("committed_at")
        if t_str:
            dt = datetime.fromisoformat(t_str.replace("Z", "+00:00"))
            age_days = (ref_time - dt).total_seconds() / 86400.0
            if 0 <= age_days <= 7:
                commits_7d += 1
            if 0 <= age_days <= 28:
                commits_28d += 1

    commit_frequency_7d = float(commits_7d)
    commit_frequency_28d = float(commits_28d)

    # 3. Commit trend (7d normalized rate vs 28d weekly rate)
    weekly_28d_rate = commit_frequency_28d / 4.0
    commit_trend = (commit_frequency_7d - weekly_28d_rate) if weekly_28d_rate > 0 else 0.0

    # Tasks stats
    total_tasks = len(tasks)
    open_tasks = [t for t in tasks if t.get("status") in ("todo", "in_progress", "blocked")]
    done_tasks = [t for t in tasks if t.get("status") == "done"]
    blocked_tasks = [t for t in tasks if t.get("status") == "blocked"]

    # 4. Task velocity (tasks completed per week over past 4 weeks)
    recent_done = 0
    slippage_days_list = []
    for t in done_tasks:
        comp_str = t.get("completed_at")
        if comp_str:
            c_dt = datetime.fromisoformat(comp_str.replace("Z", "+00:00"))
            if (ref_time - c_dt).total_seconds() <= 28 * 86400:
                recent_done += 1
        # Slippage: completed_at - due_date
        due_str = t.get("due_date")
        if comp_str and due_str:
            c_dt = datetime.fromisoformat(comp_str.replace("Z", "+00:00"))
            d_dt = datetime.fromisoformat(due_str.replace("Z", "+00:00"))
            diff = (c_dt - d_dt).total_seconds() / 86400.0
            if diff > 0:
                slippage_days_list.append(diff)

    task_velocity = float(recent_done) / 4.0

    # 5. Open task ratio
    open_task_ratio = float(len(open_tasks)) / float(total_tasks) if total_tasks > 0 else 0.0

    # 6. Overdue task count
    overdue_count = 0
    for t in open_tasks:
        due_str = t.get("due_date")
        if due_str:
            d_dt = datetime.fromisoformat(due_str.replace("Z", "+00:00"))
            if ref_time > d_dt:
                overdue_count += 1
    overdue_task_count = float(overdue_count)

    # 7. Deadline slippage days (mean slippage)
    deadline_slippage_days = float(np.mean(slippage_days_list)) if slippage_days_list else 0.0

    # 8. Blocked task ratio
    blocked_task_ratio = float(len(blocked_tasks)) / float(len(open_tasks)) if open_tasks else 0.0

    # 9. Days to deadline
    target_end = project.get("target_end_date")
    if target_end:
        end_dt = datetime.fromisoformat(target_end.replace("Z", "+00:00"))
        days_to_deadline = max(0.0, (end_dt - ref_time).total_seconds() / 86400.0)
    else:
        days_to_deadline = 30.0

    # 10. Workload concentration (share of open tasks held by top assignee)
    assignee_counts: dict[str, int] = {}
    for t in open_tasks:
        a_id = t.get("assignee_id") or t.get("assignee_email") or "unassigned"
        assignee_counts[a_id] = assignee_counts.get(a_id, 0) + 1
    max_held = max(assignee_counts.values()) if assignee_counts else 0
    workload_concentration = float(max_held) / float(len(open_tasks)) if open_tasks else 0.0

    # 11. Email activity trend
    recent_emails = 0
    for em in emails:
        s_str = em.get("sent_at")
        if s_str:
            e_dt = datetime.fromisoformat(s_str.replace("Z", "+00:00"))
            if (ref_time - e_dt).total_seconds() <= 14 * 86400:
                recent_emails += 1
    email_activity_trend = float(recent_emails) / 2.0  # emails per week

    # 12. Meeting load
    meeting_load = float(len(events))

    return {
        "commit_frequency_7d": commit_frequency_7d,
        "commit_frequency_28d": commit_frequency_28d,
        "commit_trend": commit_trend,
        "task_velocity": task_velocity,
        "open_task_ratio": open_task_ratio,
        "overdue_task_count": overdue_task_count,
        "deadline_slippage_days": deadline_slippage_days,
        "blocked_task_ratio": blocked_task_ratio,
        "days_to_deadline": days_to_deadline,
        "workload_concentration": workload_concentration,
        "email_activity_trend": email_activity_trend,
        "meeting_load": meeting_load,
    }
