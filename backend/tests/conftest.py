import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Organization, User
from app.db.postgres import Base, get_db
from app.main import app

TEST_DB_URL = "sqlite:///./test_twinos.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    # Create test org
    org = db.query(Organization).filter(Organization.id == "test-org").first()
    if not org:
        org = Organization(id="test-org", name="Test Org")
        db.add(org)

    # Create admin, manager, employee users
    admin = db.query(User).filter(User.email == "admin@test.org").first()
    if not admin:
        admin = User(
            id="user-admin",
            organization_id="test-org",
            name="Admin User",
            email="admin@test.org",
            role="admin",
        )
        db.add(admin)

    manager = db.query(User).filter(User.email == "manager@test.org").first()
    if not manager:
        manager = User(
            id="user-manager",
            organization_id="test-org",
            name="Manager User",
            email="manager@test.org",
            role="manager",
        )
        db.add(manager)

    employee = db.query(User).filter(User.email == "employee@test.org").first()
    if not employee:
        employee = User(
            id="user-employee",
            organization_id="test-org",
            name="Employee User",
            email="employee@test.org",
            role="employee",
        )
        db.add(employee)

    # Seed test project and risk score
    from app.db.models import RiskScore
    from app.services.graph_service import graph_service

    graph_service.merge_project(
        {
            "id": "proj-cloud-migration",
            "name": "Cloud Infrastructure Migration",
            "status": "at_risk",
            "org_id": "test-org",
            "source": "test",
        }
    )
    r_score = db.query(RiskScore).filter(RiskScore.entity_id == "proj-cloud-migration").first()
    if not r_score:
        db.add(
            RiskScore(
                organization_id="test-org",
                entity_type="project",
                entity_id="proj-cloud-migration",
                score=0.82,
                band="critical",
                confidence="normal",
                top_factors=[
                    "3 tasks are overdue past their deadline",
                    "40% of active tasks are marked as blocked",
                ],
            )
        )

    db.commit()
    db.close()
    yield
    # Cleanup if needed


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def admin_headers():
    return {"Authorization": "Bearer dev:admin@test.org"}


@pytest.fixture
def manager_headers():
    return {"Authorization": "Bearer dev:manager@test.org"}


@pytest.fixture
def employee_headers():
    return {"Authorization": "Bearer dev:employee@test.org"}
