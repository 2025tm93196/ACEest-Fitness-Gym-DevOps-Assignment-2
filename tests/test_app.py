
import pytest
from app import app, init_db

@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test_fitness.db"
    monkeypatch.setattr("app.DATABASE", str(db_path))
    init_db()

    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client

def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Fitness Management Dashboard" in response.data

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "UP"

def test_member_registration(client):
    response = client.post("/members", data={
        "name": "Test Member",
        "email": "test@example.com",
        "age": 25
    })
    assert response.status_code == 302

    dashboard = client.get("/")
    assert b"Test Member" in dashboard.data

def test_duplicate_member_registration(client):
    data = {
        "name": "Test Member",
        "email": "test@example.com",
        "age": 25
    }

    client.post("/members", data=data)
    response = client.post("/members", data=data)

    assert response.status_code == 409

def test_invalid_member_registration(client):
    response = client.post("/members", data={
        "name": "",
        "email": "invalid@example.com",
        "age": 25
    })
    assert response.status_code == 400

def test_workout_recording(client):
    client.post("/members", data={
        "name": "Test Member",
        "email": "workout@example.com",
        "age": 25
    })

    response = client.post("/workouts", data={
        "member_id": 1,
        "activity": "Running",
        "duration": 30
    })

    assert response.status_code == 302

    dashboard = client.get("/")
    assert b"Running" in dashboard.data

def test_invalid_workout(client):
    response = client.post("/workouts", data={
        "member_id": 999,
        "activity": "Running",
        "duration": 30
    })
    assert response.status_code == 404
