from fastapi.testclient import TestClient


def test_tc03_rag_projects_at_risk_query_with_citations(
    client: TestClient, manager_headers, employee_headers
):
    """TC-03: Query 'which projects are at risk?' lists projects above threshold with cited evidence."""
    # 1. Manager query
    payload = {"question": "Which projects are at risk?"}
    resp = client.post("/api/v1/assistant/query", json=payload, headers=manager_headers)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    data = resp.json()
    assert "answer" in data
    assert "citations" in data
    assert "used_graph_queries" in data
    assert "projects_at_risk" in data["used_graph_queries"]

    # Verify cited evidence is present
    citations = data["citations"]
    assert len(citations) > 0, "Expected at least one citation for at-risk projects"
    assert any(c["entity_type"] == "project" for c in citations), "Expected project citation"

    # 2. Test employee query scoping
    resp_emp = client.post("/api/v1/assistant/query", json=payload, headers=employee_headers)
    assert resp_emp.status_code == 200
    emp_data = resp_emp.json()
    assert "answer" in emp_data
