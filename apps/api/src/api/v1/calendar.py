from datetime import date
from flask import Blueprint, request, jsonify
from core.database import SessionLocal
from infrastructure.repositories.planned_workout_repository import (
    PlannedWorkoutRepository,
    planned_workout_to_dict,
)
from infrastructure.repositories.workout_repository import WorkoutRepository
from schemas.calendar import (
    PlannedWorkoutCreateRequest,
    StatusUpdateRequest,
)

calendar_bp = Blueprint("calendar", __name__, url_prefix="/api/v1")


def _parse_date_param(name: str) -> tuple[date | None, dict | None]:
    val = request.args.get(name)
    if not val:
        return None, {"error": "missing_params",
                      "detail": f"Wymagany parametr: {name}"}
    try:
        return date.fromisoformat(val), None
    except ValueError:
        return None, {"error": "invalid_date_format",
                      "detail": f"{name} musi być w formacie YYYY-MM-DD"}


def _workout_to_dict(w) -> dict:
    return {
        "id": w.id,
        "type": "completed",
        "started_at": w.started_at.isoformat(),
        "duration_sec": w.duration_sec,
        "distance_m": w.distance_m,
        "avg_power": w.avg_power,
        "np_power": w.np_power,
        "tss": w.tss,
        "avg_hr": w.avg_hr,
        "source": w.source,
    }


@calendar_bp.route("/calendar", methods=["GET"])
def get_calendar():
    from_date, err = _parse_date_param("from")
    if err:
        return jsonify(err), 400

    to_date, err = _parse_date_param("to")
    if err:
        return jsonify(err), 400

    if from_date > to_date:
        return jsonify({
            "error": "invalid_range",
            "detail": "from musi być wcześniej niż to"
        }), 422

    db = SessionLocal()
    try:
        planned_repo = PlannedWorkoutRepository(db)
        workout_repo = WorkoutRepository(db)

        planned = planned_repo.get_range(from_date, to_date)
        completed = workout_repo.get_all(from_date, to_date)

        return jsonify({
            "planned": [planned_workout_to_dict(p) for p in planned],
            "completed": [_workout_to_dict(w) for w in completed],
        }), 200
    finally:
        db.close()


@calendar_bp.route("/planned-workouts", methods=["POST"])
def create_planned_workout():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "error": "invalid_body",
            "detail": "Wymagane ciało żądania w formacie JSON"
        }), 400

    req = PlannedWorkoutCreateRequest.from_dict(data)
    errors = req.validate()
    if errors:
        return jsonify({
            "error": "validation_error",
            "fields": errors
        }), 422

    db = SessionLocal()
    try:
        repo = PlannedWorkoutRepository(db)
        pw = repo.create({
            "planned_date": req.planned_date,
            "type": req.type,
            "duration_sec": req.duration_sec,
            "target_zone": req.target_zone,
            "notes": req.notes,
        })
        return jsonify(planned_workout_to_dict(pw)), 201
    finally:
        db.close()


@calendar_bp.route(
    "/planned-workouts/<int:workout_id>/status",
    methods=["PATCH"]
)
def update_planned_workout_status(workout_id: int):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "error": "invalid_body",
            "detail": "Wymagane ciało żądania w formacie JSON"
        }), 400

    req = StatusUpdateRequest.from_dict(data)
    errors = req.validate()
    if errors:
        return jsonify({
            "error": "validation_error",
            "fields": errors
        }), 422

    moved_to = (
        date.fromisoformat(req.moved_to_date)
        if req.moved_to_date else None
    )

    db = SessionLocal()
    try:
        repo = PlannedWorkoutRepository(db)
        pw = repo.update_status(workout_id, req.status, moved_to)
        if pw is None:
            return jsonify({"error": "not_found"}), 404
        return jsonify(planned_workout_to_dict(pw)), 200
    finally:
        db.close()
