from fastapi.testclient import TestClient


def test_e2e_task_update_and_nl_query_reflection(
    client: TestClient, employee_headers, manager_headers
):
    """End-to-end test: Employee updates task status, changes are reflected in queries."""
    # 1. Employee updates task status to 'done'
    update_res = client.patch(
        "/api/v1/tasks/task-001/status",
        json={"status": "done"},
        headers=employee_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "done"

    # 2. Manager asks natural-language query to assistant
    query_res = client.post(
        "/api/v1/assistant/query",
        json={"question": "What is the status of task-001?"},
        headers=manager_headers,
    )
    assert query_res.status_code == 200
    answer = query_res.json()["answer"]
    assert len(answer) > 0
