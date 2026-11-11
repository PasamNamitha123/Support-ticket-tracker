import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.services import triage


@pytest.fixture()
def client(monkeypatch):
    # fresh in-memory database for every test
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(triage.settings, "llm_api_key", "")  # no AI unless a test turns it on
    yield TestClient(app)  # not used as a context manager, so startup create_all is skipped
    app.dependency_overrides.clear()


def register_and_login(client, email="a@example.com", password="password123"):
    client.post("/api/users/register", json={"email": email, "password": password})
    res = client.post("/api/users/login", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def test_register_login_and_me(client):
    headers = register_and_login(client)
    res = client.get("/api/users/me", headers=headers)
    assert res.status_code == 200
    assert res.json()["email"] == "a@example.com"


def test_duplicate_email_rejected(client):
    register_and_login(client)
    res = client.post(
        "/api/users/register", json={"email": "a@example.com", "password": "password123"}
    )
    assert res.status_code == 400


def test_wrong_password_rejected(client):
    register_and_login(client)
    res = client.post("/api/users/login", data={"username": "a@example.com", "password": "nope"})
    assert res.status_code == 401


def test_tickets_require_login(client):
    assert client.get("/api/tickets").status_code == 401


def test_ticket_uses_rule_based_triage_without_api_key(client):
    headers = register_and_login(client)
    res = client.post(
        "/api/tickets",
        json={"title": "Refund", "description": "I was charged twice, please help urgent"},
        headers=headers,
    )
    assert res.status_code == 201
    body = res.json()
    assert body["category"] == "billing"
    assert body["priority"] == "high"
    assert body["ai_generated"] is False


def test_ticket_uses_llm_when_available(client, monkeypatch):
    monkeypatch.setattr(triage.settings, "llm_api_key", "fake-key")
    monkeypatch.setattr(
        triage,
        "call_llm",
        lambda system, text: '{"category": "bug", "priority": "high", '
        '"summary": "App crashes on save", "suggested_reply": "Sorry, we are looking into it."}',
    )
    headers = register_and_login(client)
    res = client.post(
        "/api/tickets", json={"title": "Crash", "description": "App crashes"}, headers=headers
    )
    body = res.json()
    assert body["ai_generated"] is True
    assert body["category"] == "bug"
    assert body["summary"] == "App crashes on save"


def test_fallback_when_llm_fails(client, monkeypatch):
    monkeypatch.setattr(triage.settings, "llm_api_key", "fake-key")

    def broken(system, text):
        raise RuntimeError("LLM is down")

    monkeypatch.setattr(triage, "call_llm", broken)
    headers = register_and_login(client)
    res = client.post(
        "/api/tickets",
        json={"title": "Login", "description": "I forgot my password"},
        headers=headers,
    )
    assert res.status_code == 201
    assert res.json()["ai_generated"] is False
    assert res.json()["category"] == "account"


def test_fallback_when_llm_returns_invalid_output(client, monkeypatch):
    monkeypatch.setattr(triage.settings, "llm_api_key", "fake-key")
    monkeypatch.setattr(triage, "call_llm", lambda system, text: "sorry, I cannot do that")
    headers = register_and_login(client)
    res = client.post(
        "/api/tickets", json={"title": "Hi", "description": "Some question"}, headers=headers
    )
    assert res.status_code == 201
    assert res.json()["ai_generated"] is False


def test_user_cannot_see_another_users_ticket(client):
    owner = register_and_login(client, "owner@example.com")
    other = register_and_login(client, "other@example.com")
    created = client.post(
        "/api/tickets", json={"title": "Mine", "description": "Private"}, headers=owner
    ).json()
    assert client.get(f"/api/tickets/{created['id']}", headers=other).status_code == 404
    assert client.get("/api/tickets", headers=other).json() == []
    assert client.get(f"/api/tickets/{created['id']}", headers=owner).status_code == 200


def test_update_status(client):
    headers = register_and_login(client)
    ticket = client.post(
        "/api/tickets", json={"title": "T", "description": "D"}, headers=headers
    ).json()
    res = client.patch(
        f"/api/tickets/{ticket['id']}/status", json={"status": "resolved"}, headers=headers
    )
    assert res.status_code == 200
    assert res.json()["status"] == "resolved"
