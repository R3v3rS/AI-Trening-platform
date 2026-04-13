import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from core.database import Base
from infrastructure.db.models import (
    AthleteProfile, Workout, PlannedWorkout,
    WorkoutSample, DailyLoadMetric
)
from datetime import datetime, date


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_init_db_creates_all_tables(db):
    from sqlalchemy import inspect
    inspector = inspect(db.bind)
    tables = inspector.get_table_names()
    assert "athlete_profiles" in tables
    assert "workouts" in tables
    assert "workout_samples" in tables
    assert "planned_workouts" in tables
    assert "daily_load_metrics" in tables


def test_athlete_profile_ftp_must_be_positive(db):
    profile = AthleteProfile(
        ftp_watts=-10,
        weight_kg=70,
        hr_max=200,
        hr_threshold=175
    )
    db.add(profile)
    with pytest.raises(IntegrityError):
        db.commit()


def test_athlete_profile_weight_must_be_positive(db):
    profile = AthleteProfile(
        ftp_watts=200,
        weight_kg=0,
        hr_max=200,
        hr_threshold=175
    )
    db.add(profile)
    with pytest.raises(IntegrityError):
        db.commit()


def test_workout_garmin_session_id_unique(db):
    w1 = Workout(
        garmin_session_id="abc123",
        started_at=datetime.utcnow()
    )
    w2 = Workout(
        garmin_session_id="abc123",
        started_at=datetime.utcnow()
    )
    db.add(w1)
    db.commit()
    db.add(w2)
    with pytest.raises(IntegrityError):
        db.commit()


def test_planned_workout_invalid_status(db):
    pw = PlannedWorkout(
        planned_date=date.today(),
        status="invalid_status"
    )
    db.add(pw)
    with pytest.raises(IntegrityError):
        db.commit()


def test_planned_workout_valid_statuses(db):
    for status in ["planned", "completed", "skipped", "moved"]:
        db.rollback()
        pw = PlannedWorkout(
            planned_date=date.today(),
            status=status,
            type="z2"
        )
        db.add(pw)
        db.commit()


def test_workout_samples_cascade_delete(db):
    w = Workout(
        garmin_session_id="del_test",
        started_at=datetime.utcnow()
    )
    db.add(w)
    db.commit()

    sample = WorkoutSample(
        workout_id=w.id,
        ts_offset_sec=0,
        power=200
    )
    db.add(sample)
    db.commit()

    db.delete(w)
    db.commit()

    remaining = db.query(WorkoutSample).filter_by(workout_id=w.id).all()
    assert remaining == []
