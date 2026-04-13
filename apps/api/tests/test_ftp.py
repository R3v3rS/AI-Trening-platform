import pytest
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from domain.metrics.ftp_calculator import (
    calculate_ftp_from_ramp_test,
    calculate_ftp_from_20min_test,
)


# --- Testy kalkulatora ---

def test_ramp_test_basic():
    """180 próbek po 400W → FTP = round(400 * 0.75) = 300"""
    samples = [400] * 180
    result = calculate_ftp_from_ramp_test(samples)
    assert result == 300


def test_ramp_test_last_minute_matters():
    """Pierwsze 120s po 200W, ostatnie 60s po 400W → FTP = 300"""
    samples = [200] * 120 + [400] * 60
    result = calculate_ftp_from_ramp_test(samples)
    assert result == 300


def test_ramp_test_too_few_samples():
    with pytest.raises(ValueError):
        calculate_ftp_from_ramp_test([300] * 30)


def test_ramp_test_empty():
    with pytest.raises(ValueError):
        calculate_ftp_from_ramp_test([])


def test_ramp_test_with_none_values():
    """None values są ignorowane przy obliczeniach"""
    samples = [None] * 50 + [400] * 120
    result = calculate_ftp_from_ramp_test(samples)
    assert result == 300


def test_ramp_test_exactly_60_samples():
    samples = [320] * 60
    result = calculate_ftp_from_ramp_test(samples)
    assert result == round(320 * 0.75)


def test_20min_test_basic():
    result = calculate_ftp_from_20min_test(300.0)
    assert result == 285


def test_20min_test_rounding():
    """300.5 * 0.95 = 285.475 → round = 285"""
    result = calculate_ftp_from_20min_test(300.5)
    assert result == 285


def test_20min_test_zero_raises():
    with pytest.raises(ValueError):
        calculate_ftp_from_20min_test(0)


def test_20min_test_negative_raises():
    with pytest.raises(ValueError):
        calculate_ftp_from_20min_test(-100)


# --- Testy endpointów ---

def test_ftp_manual_ramp(client):
    response = client.post(
        "/api/v1/ftp-test/manual",
        json={"protocol": "ramp", "avg_power": 400}
    )
    assert response.status_code == 200
    assert response.json["suggested_ftp"] == 300
    assert response.json["protocol"] == "ramp"


def test_ftp_manual_20min(client):
    response = client.post(
        "/api/v1/ftp-test/manual",
        json={"protocol": "20min", "avg_power": 300}
    )
    assert response.status_code == 200
    assert response.json["suggested_ftp"] == 285


def test_ftp_manual_invalid_protocol(client):
    response = client.post(
        "/api/v1/ftp-test/manual",
        json={"protocol": "invalid", "avg_power": 300}
    )
    assert response.status_code == 422
    assert response.json["error"] == "invalid_protocol"


def test_ftp_manual_missing_avg_power(client):
    response = client.post(
        "/api/v1/ftp-test/manual",
        json={"protocol": "20min"}
    )
    assert response.status_code == 422


def test_ftp_manual_empty_body(client):
    response = client.post(
        "/api/v1/ftp-test/manual",
        data="not json",
        content_type="application/json"
    )
    assert response.status_code == 400


def test_ftp_accept_updates_profile(client):
    # Najpierw utwórz profil
    client.put(
        "/api/v1/profile",
        json={
            "ftp_watts": 200,
            "weight_kg": 70,
            "hr_max": 200,
            "hr_threshold": 175,
        }
    )
    response = client.post(
        "/api/v1/ftp-test/accept",
        json={"suggested_ftp": 245}
    )
    assert response.status_code == 200
    assert response.json["profile"]["ftp_watts"] == 245


def test_ftp_accept_creates_profile_if_missing(client):
    response = client.post(
        "/api/v1/ftp-test/accept",
        json={"suggested_ftp": 230}
    )
    assert response.status_code == 200
    assert response.json["profile"]["ftp_watts"] == 230


def test_ftp_accept_zero_ftp_returns_422(client):
    response = client.post(
        "/api/v1/ftp-test/accept",
        json={"suggested_ftp": 0}
    )
    assert response.status_code == 422


def test_ftp_accept_missing_field(client):
    response = client.post(
        "/api/v1/ftp-test/accept",
        json={}
    )
    assert response.status_code == 422


def test_ftp_from_fit_no_file(client):
    response = client.post("/api/v1/ftp-test/from-fit")
    assert response.status_code == 400
    assert response.json["error"] == "missing_file"


def test_ftp_from_fit_wrong_extension(client):
    from io import BytesIO
    data = {"file": (BytesIO(b"data"), "test.csv")}
    response = client.post(
        "/api/v1/ftp-test/from-fit",
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 422


def test_ftp_from_fit_invalid_protocol(client):
    from io import BytesIO
    data = {"file": (BytesIO(b"data"), "test.fit")}
    response = client.post(
        "/api/v1/ftp-test/from-fit?protocol=bad",
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 422
    assert response.json["error"] == "invalid_protocol"
