from datetime import datetime, date
from sqlalchemy import Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base


class AthleteProfile(Base):
    __tablename__ = "athlete_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ftp_watts: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    hr_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hr_threshold: Mapped[int | None] = mapped_column(Integer, nullable=True)
    experience_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    weekly_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    goals: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    preferred_training_days: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    max_ride_time_per_day_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    indoor_vs_outdoor_preference: Mapped[str | None] = mapped_column(String(50), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class PlannedWorkout(Base):
    __tablename__ = "planned_workouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    planned_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    duration_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_zone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="planned")
    moved_from_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    distance_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_power: Mapped[float | None] = mapped_column(Float, nullable=True)
    np_power: Mapped[float | None] = mapped_column(Float, nullable=True)
    tss: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_hr: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)


class DailyLoadMetric(Base):
    __tablename__ = "daily_load_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    metric_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False, index=True)
    tss_day: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    atl_7d: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    ctl_42d: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    tsb: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
