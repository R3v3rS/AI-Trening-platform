import pytest
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("SECRET_KEY", "test-secret-key")


def test_get_profile_not_found(client):
    response = client.get("/api/v1/profile")
    assert response.status_code == 404
    assert response.json["error"] == "profile_not_found"


def test_put_creates_profile(client):
    response = client.put(
        "/api/v1/profile",
        json={
            "ftp_watts": 250,
            "weight_kg": 70.0,
            "hr_max": 200,
            "hr_threshold": 175,
        }
    )
    assert response.status_code == 200
    assert response.json["ftp_watts"] == 250
    assert response.json["weight_kg"] == 70.0


def test_put_updates_existing_profile(client):
    client.put(
        "/api/v1/profile",
        json={"ftp_watts": 200, "weight_kg": 70, "hr_max": 200,
              "hr_threshold": 175}
    )
    response = client.put(
        "/api/v1/profile",
        json={"ftp_watts": 230}
    )
    assert response.status_code == 200
    assert response.json["ftp_watts"] == 230
    # Pozostałe pola niezmienione
    assert response.json["weight_kg"] == 70.0


def test_get_profile_after_create(client):
    client.put(
        "/api/v1/profile",
        json={"ftp_watts": 185, "weight_kg": 70, "hr_max": 200,
              "hr_threshold": 175}
    )
    response = client.get("/api/v1/profile")
    assert response.status_code == 200
    assert response.json["ftp_watts"] == 185


def test_put_ftp_zero_returns_422(client):
    response = client.put(
        "/api/v1/profile",
        json={"ftp_watts": 0, "weight_kg": 70, "hr_max": 200,
              "hr_threshold": 175}
    )
    assert response.status_code == 422
    assert "ftp_watts" in response.json["fields"]


def test_put_negative_ftp_returns_422(client):
    response = client.put(
        "/api/v1/profile",
        json={"ftp_watts": -50}
    )
    assert response.status_code == 422


def test_put_hr_max_less_than_threshold_returns_422(client):
    response = client.put(
        "/api/v1/profile",
        json={
            "ftp_watts": 200,
            "weight_kg": 70,
            "hr_max": 160,
            "hr_threshold": 175,
        }
    )
    assert response.status_code == 422
    assert "hr_max" in response.json["fields"]


def test_put_invalid_experience_level(client):
    response = client.put(
        "/api/v1/profile",
        json={"experience_level": "expert"}
    )
    assert response.status_code == 422
    assert "experience_level" in response.json["fields"]


def test_put_invalid_training_days(client):
    response = client.put(
        "/api/v1/profile",
        json={"preferred_training_days": ["mon", "xyz"]}
    )
    assert response.status_code == 422
    assert "preferred_training_days" in response.json["fields"]


def test_put_goals_as_list(client):
    response = client.put(
        "/api/v1/profile",
        json={
            "ftp_watts": 200,
            "weight_kg": 70,
            "hr_max": 200,
            "hr_threshold": 175,
            "goals": ["improve_ftp", "lose_weight"]
        }
    )
    assert response.status_code == 200
    assert isinstance(response.json["goals"], list)
    assert "improve_ftp" in response.json["goals"]


def test_put_empty_body_returns_400(client):
    response = client.put(
        "/api/v1/profile",
        data="not json",
        content_type="application/json"
    )
    assert response.status_code == 400


def test_put_no_fields_returns_400(client):
    response = client.put("/api/v1/profile", json={})
    assert response.status_code == 400
    assert response.json["error"] == "empty_update"
