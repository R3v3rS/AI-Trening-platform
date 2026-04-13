from datetime import date
from flask import Blueprint, request, jsonify
from core.database import SessionLocal
from infrastructure.repositories.metrics_repository import MetricsRepository

workouts_bp = Blueprint("workouts", __name__, url_prefix="/api/v1")


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
