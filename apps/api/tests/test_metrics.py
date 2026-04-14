import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base
from domain.metrics.load_calculator import (
    calculate_atl,
    calculate_ctl,
    calculate_tsb,
    build_daily_tss_map,
)
from infrastructure.repositories.metrics_repository import MetricsRepository
from infrastructure.db.models import DailyLoadMetric


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_calculate_atl_empty():
    result = calculate_atl({}, date.today())
    assert result == 0.0


def test_calculate_ctl_empty():
    result = calculate_ctl({}, date.today())
    assert result == 0.0


def test_calculate_tsb():
    assert calculate_tsb(80.0, 90.0) == -10.0
    assert calculate_tsb(100.0, 80.0) == 20.0


def test_calculate_ctl_steady_load():
    """
    42 dni po 100 TSS dziennie → CTL bliskie 100
    (nie dokładnie 100 bo EWA, ale > 60)
    """
    today = date.today()
    daily = {today - timedelta(days=i): 100.0 for i in range(42 * 3)}
    ctl = calculate_ctl(daily, today)
    assert ctl > 60.0


def test_calculate_atl_recent_load():
    """
    7 dni po 100 TSS → ATL bliskie 100 (> 50)
    """
    today = date.today()
    daily = {today - timedelta(days=i): 100.0 for i in range(7)}
    atl = calculate_atl(daily, today)
    assert atl > 50.0


def test_calculate_atl_no_recent_load():
    """
    Brak treningu przez 30 dni → ATL bliska 0
    """
    today = date.today()
    old_date = today - timedelta(days=30)
    daily = {old_date: 200.0}
    atl = calculate_atl(daily, today)
    assert atl < 5.0


def test_build_daily_tss_map():
    class FakeWorkout:
        def __init__(self, started_at, tss):
            self.started_at = started_at
            self.tss = tss

    from datetime import datetime
    today = date.today()
    workouts = [
        FakeWorkout(datetime.combine(today, datetime.min.time()), 80.0),
        FakeWorkout(datetime.combine(today, datetime.min.time()), 40.0),
    ]
    result = build_daily_tss_map(workouts, today)
    assert result[today] == 120.0


def test_metrics_repository_upsert(db_session):
    repo = MetricsRepository(db_session)
    today = date.today()

    metric = repo.upsert_daily(today, 100.0, 80.0, 70.0, -10.0)
    assert metric.tss_day == 100.0
    assert metric.atl_7d == 80.0

    updated = repo.upsert_daily(today, 120.0, 90.0, 75.0, -15.0)
    assert updated.tss_day == 120.0

    count = db_session.query(DailyLoadMetric).filter_by(
        metric_date=today
    ).count()
    assert count == 1


def test_metrics_repository_get_range(db_session):
    repo = MetricsRepository(db_session)
    today = date.today()
    yesterday = today - timedelta(days=1)

    repo.upsert_daily(today, 100.0, 80.0, 70.0, -10.0)
    repo.upsert_daily(yesterday, 80.0, 75.0, 68.0, -7.0)

    results = repo.get_range(yesterday, today)
    assert len(results) == 2
    assert results[0].metric_date == yesterday
    assert results[1].metric_date == today


def test_get_load_metrics_endpoint_missing_params(client):
    response = client.get("/api/v1/metrics/load")
    assert response.status_code == 400
    assert response.json["error"] == "missing_params"


def test_get_load_metrics_endpoint_invalid_date(client):
    response = client.get("/api/v1/metrics/load?from=bad&to=date")
    assert response.status_code == 422


def test_get_load_metrics_endpoint_empty_range(client):
    today = date.today().isoformat()
    response = client.get(
        f"/api/v1/metrics/load?from={today}&to={today}"
    )
    assert response.status_code == 200
    assert isinstance(response.json, list)
