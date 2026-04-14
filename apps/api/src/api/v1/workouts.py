from datetime import date
from flask import Blueprint, request, jsonify
from core.database import SessionLocal
from infrastructure.repositories.metrics_repository import MetricsRepository
from infrastructure.repositories.workout_repository import WorkoutRepository

workouts_bp = Blueprint("workouts", __name__, url_prefix="/api/v1")

@workouts_bp.route("/workouts", methods=["GET"])
def get_workouts():
    from_str = request.args.get("from")
    to_str = request.args.get("to")
    
    from_date = date.fromisoformat(from_str) if from_str else None
    to_date = date.fromisoformat(to_str) if to_str else None
    
    db = SessionLocal()
    try:
        repo = WorkoutRepository(db)
        workouts = repo.get_all(from_date, to_date)
        return jsonify([{
            "id": w.id,
            "source": w.source,
            "started_at": w.started_at.isoformat(),
            "duration_sec": w.duration_sec,
            "distance_m": w.distance_m,
            "avg_power": w.avg_power,
            "np_power": w.np_power,
            "if_value": w.if_value,
            "tss": w.tss,
            "avg_hr": w.avg_hr,
            "max_hr": w.max_hr,
            "avg_cadence": w.avg_cadence,
            "type": "completed"
        } for w in workouts]), 200
    finally:
        db.close()


@workouts_bp.route("/metrics/load", methods=["GET"])
def get_load_metrics():
    from_str = request.args.get("from")
    to_str = request.args.get("to")

    if not from_str or not to_str:
        return jsonify({
            "error": "missing_params",
            "detail": "Wymagane parametry: from, to (YYYY-MM-DD)"
        }), 400

    try:
        from_date = date.fromisoformat(from_str)
        to_date = date.fromisoformat(to_str)
    except ValueError:
        return jsonify({
            "error": "invalid_date_format",
            "detail": "Format daty: YYYY-MM-DD"
        }), 422

    if from_date > to_date:
        return jsonify({
            "error": "invalid_range",
            "detail": "from musi być wcześniej niż to"
        }), 422

    db = SessionLocal()
    try:
        repo = MetricsRepository(db)
        metrics = repo.get_range(from_date, to_date)

        return jsonify([
            {
                "date": m.metric_date.isoformat(),
                "tss": m.tss_day,
                "atl": m.atl_7d,
                "ctl": m.ctl_42d,
                "tsb": m.tsb,
            }
            for m in metrics
        ]), 200
    finally:
        db.close()
