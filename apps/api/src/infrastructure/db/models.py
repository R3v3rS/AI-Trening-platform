from datetime import datetime, date
from sqlalchemy import Date, DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    tss: Mapped[float | None] = mapped_column(Float, nullable=True)


class DailyLoadMetric(Base):
    __tablename__ = "daily_load_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    metric_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False, index=True)
    tss_day: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    atl_7d: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    ctl_42d: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    tsb: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
