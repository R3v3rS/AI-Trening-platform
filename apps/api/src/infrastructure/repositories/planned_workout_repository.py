from datetime import date, datetime
from sqlalchemy.orm import Session
from infrastructure.db.models import PlannedWorkout


class PlannedWorkoutRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> PlannedWorkout:
        pw = PlannedWorkout(
            planned_date=date.fromisoformat(data["planned_date"]),
            type=data.get("type"),
            duration_sec=data.get("duration_sec"),
            target_zone=data.get("target_zone"),
            notes=data.get("notes"),
            structured_steps=data.get("structured_steps"),
            status="planned",
        )
        self.db.add(pw)
        self.db.commit()
        self.db.refresh(pw)
        return pw

    def get_by_id(self, workout_id: int) -> PlannedWorkout | None:
        return self.db.query(PlannedWorkout).filter_by(
            id=workout_id
        ).first()

    def get_range(
        self,
        from_date: date,
        to_date: date
    ) -> list[PlannedWorkout]:
        return (
            self.db.query(PlannedWorkout)
            .filter(PlannedWorkout.planned_date >= from_date)
            .filter(PlannedWorkout.planned_date <= to_date)
            .order_by(PlannedWorkout.planned_date.asc())
            .all()
        )

    def update_status(
        self,
        workout_id: int,
        status: str,
        moved_to_date: date | None = None,
    ) -> PlannedWorkout | None:
        pw = self.get_by_id(workout_id)
        if pw is None:
            return None

        if status == "moved" and moved_to_date is not None:
            pw.moved_from_date = pw.planned_date
            pw.planned_date = moved_to_date

        pw.status = status
        pw.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(pw)
        return pw


def planned_workout_to_dict(pw: PlannedWorkout) -> dict:
    return {
        "id": pw.id,
        "planned_date": pw.planned_date.isoformat(),
        "type": pw.type,
        "duration_sec": pw.duration_sec,
        "target_zone": pw.target_zone,
        "status": pw.status,
        "moved_from_date": (
            pw.moved_from_date.isoformat()
            if pw.moved_from_date else None
        ),
        "notes": pw.notes,
        "structured_steps": pw.structured_steps,
        "created_at": (
            pw.created_at.isoformat() if pw.created_at else None
        ),
        "updated_at": (
            pw.updated_at.isoformat() if pw.updated_at else None
        ),
    }
