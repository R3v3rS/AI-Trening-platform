from datetime import datetime, date
from sqlalchemy import (
    Integer, Float, String, Text, DateTime,
    Date, ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base


class AthleteProfile(Base):
    __tablename__ = "athlete_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ftp_watts: Mapped[int] = mapped_column(
        Integer, nullable=False,
        info={"check": "ftp_watts > 0"}
    )
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    hr_max: Mapped[int] = mapped_column(Integer, nullable=False)
    hr_threshold: Mapped[int] = mapped_column(Integer, nullable=False)
    experience_level: Mapped[str] = mapped_column(String(20), nullable=True)
    weekly_hours: Mapped[float] = mapped_column(Float, nullable=True)
    goals: Mapped[str] = mapped_column(Text, nullable=True)
    preferred_training_days: Mapped[str] = mapped_column(Text, nullable=True)
    max_ride_time_per_day_min: Mapped[int] = mapped_column(Integer, nullable=True)
    indoor_vs_outdoor_preference: Mapped[str] = mapped_column(
        String(10), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        CheckConstraint("ftp_watts > 0", name="ck_ftp_positive"),
        CheckConstraint("weight_kg > 0", name="ck_weight_positive"),
        CheckConstraint("hr_max > hr_threshold", name="ck_hr_max_gt_threshold"),
        CheckConstraint(
            "experience_level IN ('beginner','intermediate','advanced')",
            name="ck_experience_level"
        ),
        CheckConstraint(
            "indoor_vs_outdoor_preference IN ('indoor','outdoor','mixed')",
            name="ck_indoor_outdoor"
        ),
    )


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(50), default="garmin")
    garmin_session_id: Mapped[str] = mapped_column(String(64), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration_sec: Mapped[int] = mapped_column(Integer, nullable=True)
    distance_m: Mapped[float] = mapped_column(Float, nullable=True)
    avg_power: Mapped[float] = mapped_column(Float, nullable=True)
    np_power: Mapped[float] = mapped_column(Float, nullable=True)
    if_value: Mapped[float] = mapped_column(Float, nullable=True)
    tss: Mapped[float] = mapped_column(Float, nullable=True)
    avg_hr: Mapped[int] = mapped_column(Integer, nullable=True)
    max_hr: Mapped[int] = mapped_column(Integer, nullable=True)
    avg_cadence: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    samples: Mapped[list["WorkoutSample"]] = relationship(
        "WorkoutSample", back_populates="workout",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("garmin_session_id", name="uq_garmin_session_id"),
    )


class WorkoutSample(Base):
    __tablename__ = "workout_samples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workout_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False
    )
    ts_offset_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    power: Mapped[int] = mapped_column(Integer, nullable=True)
    hr: Mapped[int] = mapped_column(Integer, nullable=True)
    cadence: Mapped[int] = mapped_column(Integer, nullable=True)
    speed: Mapped[float] = mapped_column(Float, nullable=True)

    workout: Mapped["Workout"] = relationship("Workout", back_populates="samples")


class PlannedWorkout(Base):
    __tablename__ = "planned_workouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    planned_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=True)
    duration_sec: Mapped[int] = mapped_column(Integer, nullable=True)
    target_zone: Mapped[str] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="planned")
    moved_from_date: Mapped[date] = mapped_column(Date, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('planned','completed','skipped','moved')",
            name="ck_status"
        ),
        CheckConstraint(
            "type IN ('z2','tempo','vo2max','recovery','long_ride','ftp_test')",
            name="ck_type"
        ),
    )


class DailyLoadMetric(Base):
    __tablename__ = "daily_load_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    metric_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False, index=True)
    tss_day: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    atl_7d: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    ctl_42d: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    tsb: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
