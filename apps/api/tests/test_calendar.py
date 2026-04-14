import pytest
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from datetime import date, timedelta


def test_get_calendar_empty(client):
    today = date.today().isoformat()
    response = client.get(f"/api/v1/calendar?from={today}&to={today}")
    assert response.status_code == 200
    assert response.json["planned"] == []
    assert response.json["completed"] == []


def test_get_calendar_missing_params(client):
    response = client.get("/api/v1/calendar")
    assert response.status_code == 400


def test_get_calendar_invalid_range(client):
    response = client.get(
        "/api/v1/calendar?from=2025-01-10&to=2025-01-01"
    )
    assert response.status_code == 422


def test_create_planned_workout(client):
    response = client.post(
        "/api/v1/planned-workouts",
        json={
            "planned_date": "2025-06-01",
            "type": "z2",
            "duration_sec": 5400,
            "notes": "Spokojne Z2"
        }
    )
    assert response.status_code == 201
    assert response.json["type"] == "z2"
    assert response.json["status"] == "planned"
    assert response.json["duration_sec"] == 5400


def test_create_planned_workout_invalid_type(client):
    response = client.post(
        "/api/v1/planned-workouts",
        json={
            "planned_date": "2025-06-01",
            "type": "invalid_type",
        }
    )
    assert response.status_code == 422
    assert "type" in response.json["fields"]


def test_create_planned_workout_invalid_date(client):
    response = client.post(
        "/api/v1/planned-workouts",
        json={"planned_date": "not-a-date"}
    )
    assert response.status_code == 422
    assert "planned_date" in response.json["fields"]


def test_create_planned_workout_missing_date(client):
    response = client.post(
        "/api/v1/planned-workouts",
        json={"type": "z2"}
    )
    assert response.status_code == 422


def test_get_calendar_with_planned(client):
    client.post(
        "/api/v1/planned-workouts",
        json={"planned_date": "2025-06-15", "type": "tempo"}
    )
    response = client.get(
        "/api/v1/calendar?from=2025-06-01&to=2025-06-30"
    )
    assert response.status_code == 200
    assert len(response.json["planned"]) == 1
    assert response.json["planned"][0]["type"] == "tempo"


def test_patch_status_completed(client):
    create = client.post(
        "/api/v1/planned-workouts",
        json={"planned_date": "2025-06-10", "type": "z2"}
    )
    workout_id = create.json["id"]

    response = client.patch(
        f"/api/v1/planned-workouts/{workout_id}/status",
        json={"status": "completed"}
    )
    assert response.status_code == 200
    assert response.json["status"] == "completed"


def test_patch_status_skipped(client):
    create = client.post(
        "/api/v1/planned-workouts",
        json={"planned_date": "2025-06-11", "type": "recovery"}
    )
    workout_id = create.json["id"]

    response = client.patch(
        f"/api/v1/planned-workouts/{workout_id}/status",
        json={"status": "skipped"}
    )
    assert response.status_code == 200
    assert response.json["status"] == "skipped"


def test_patch_status_moved_without_date_returns_422(client):
    create = client.post(
        "/api/v1/planned-workouts",
        json={"planned_date": "2025-06-12", "type": "vo2max"}
    )
    workout_id = create.json["id"]

    response = client.patch(
        f"/api/v1/planned-workouts/{workout_id}/status",
        json={"status": "moved"}
    )
    assert response.status_code == 422
    assert "moved_to_date" in response.json["fields"]


def test_patch_status_moved_with_date(client):
    create = client.post(
        "/api/v1/planned-workouts",
        json={"planned_date": "2025-06-13", "type": "z2"}
    )
    workout_id = create.json["id"]

    response = client.patch(
        f"/api/v1/planned-workouts/{workout_id}/status",
        json={"status": "moved", "moved_to_date": "2025-06-14"}
    )
    assert response.status_code == 200
    assert response.json["status"] == "moved"
    assert response.json["planned_date"] == "2025-06-14"
    assert response.json["moved_from_date"] == "2025-06-13"


def test_patch_status_invalid_status(client):
    create = client.post(
        "/api/v1/planned-workouts",
        json={"planned_date": "2025-06-14", "type": "z2"}
    )
    workout_id = create.json["id"]

    response = client.patch(
        f"/api/v1/planned-workouts/{workout_id}/status",
        json={"status": "invalid"}
    )
    assert response.status_code == 422
    assert "status" in response.json["fields"]


def test_patch_status_not_found(client):
    response = client.patch(
        "/api/v1/planned-workouts/99999/status",
        json={"status": "completed"}
    )
    assert response.status_code == 404
