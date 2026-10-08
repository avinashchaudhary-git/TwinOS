from fastapi.testclient import TestClient


def test_tc01_employee_to_admin_endpoint_forbidden(
    client: TestClient, employee_headers, admin_headers
):
    """TC-01: Employee token calls Admin-only endpoint gives HTTP 403 Forbidden."""
    # 1. Employee calling Admin-only users list -> MUST BE 403
    resp = client.get("/api/v1/admin/users", headers=employee_headers)
    assert resp.status_code == 403, (
        f"Expected 403 Forbidden for employee, got {resp.status_code}: {resp.text}"
    )
    assert "Access forbidden" in resp.json()["detail"]

    # 2. Employee calling Admin-only audit log -> MUST BE 403
    resp_audit = client.get("/api/v1/admin/audit", headers=employee_headers)
    assert resp_audit.status_code == 403

    # 3. Admin calling Admin endpoint -> MUST BE 200
    resp_admin = client.get("/api/v1/admin/users", headers=admin_headers)
    assert resp_admin.status_code == 200

    # 4. Unauthenticated -> MUST BE 401
    resp_unauth = client.get("/api/v1/admin/users")
    assert resp_unauth.status_code == 401
