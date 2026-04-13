from datetime import date
from sqlalchemy.orm import Session
from infrastructure.db.models import DailyLoadMetric


class MetricsRepository:

    def __init__(self, db: Session):
        self.db = db

    def upsert_daily(
        self,
        metric_date: date,
        tss_day: float,
        atl: float,
        ctl: float,
        tsb: float,
    ) -> DailyLoadMetric:
        existing = self.db.query(DailyLoadMetric).filter_by(
            metric_date=metric_date
        ).first()

        if existing:
            existing.tss_day = tss_day
            existing.atl_7d = atl
            existing.ctl_42d = ctl
            existing.tsb = tsb
        else:
            existing = DailyLoadMetric(
                metric_date=metric_date,
                tss_day=tss_day,
                atl_7d=atl,
                ctl_42d=ctl,
                tsb=tsb,
            )
            self.db.add(existing)

        self.db.commit()
        self.db.refresh(existing)
        return existing

    def get_range(
        self,
        from_date: date,
        to_date: date
    ) -> list[DailyLoadMetric]:
        return (
            self.db.query(DailyLoadMetric)
            .filter(DailyLoadMetric.metric_date >= from_date)
            .filter(DailyLoadMetric.metric_date <= to_date)
            .order_by(DailyLoadMetric.metric_date.asc())
            .all()
        )
