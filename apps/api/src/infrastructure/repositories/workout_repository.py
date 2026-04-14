from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
from infrastructure.db.models import Workout


class WorkoutRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        from_date: date | None = None,
        to_date: date | None = None
    ) -> list[Workout]:
        query = self.db.query(Workout)
        if from_date:
            query = query.filter(func.date(Workout.started_at) >= from_date)
        if to_date:
            query = query.filter(func.date(Workout.started_at) <= to_date)
        return query.order_by(Workout.started_at.asc()).all()
