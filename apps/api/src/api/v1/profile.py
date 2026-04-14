from flask import Blueprint, request, jsonify
from core.database import SessionLocal
from infrastructure.repositories.profile_repository import (
    ProfileRepository,
    profile_to_dict,
)
from schemas.profile import ProfileUpdateRequest

profile_bp = Blueprint("profile", __name__, url_prefix="/api/v1")


@profile_bp.route("/profile", methods=["GET"])
def get_profile():
    db = SessionLocal()
    try:
        repo = ProfileRepository(db)
        profile = repo.get()
        if profile is None:
            return jsonify({"error": "profile_not_found"}), 404
        return jsonify(profile_to_dict(profile)), 200
    finally:
        db.close()


@profile_bp.route("/profile", methods=["PUT"])
def update_profile():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({
            "error": "invalid_body",
            "detail": "Wymagane ciało żądania w formacie JSON"
        }), 400

    req = ProfileUpdateRequest.from_dict(data)
    errors = req.validate()
    if errors:
        return jsonify({
            "error": "validation_error",
            "fields": errors
        }), 422

    update_data = {
        k: v for k, v in {
            "ftp_watts": req.ftp_watts,
            "weight_kg": req.weight_kg,
            "hr_max": req.hr_max,
            "hr_threshold": req.hr_threshold,
            "experience_level": req.experience_level,
            "weekly_hours": req.weekly_hours,
            "goals": req.goals,
            "preferred_training_days": req.preferred_training_days,
            "max_ride_time_per_day_min": req.max_ride_time_per_day_min,
            "indoor_vs_outdoor_preference": req.indoor_vs_outdoor_preference,
        }.items()
        if v is not None
    }

    if not update_data:
        return jsonify({
            "error": "empty_update",
            "detail": "Nie podano żadnych pól do aktualizacji"
        }), 400

    db = SessionLocal()
    try:
        repo = ProfileRepository(db)
        profile = repo.upsert(update_data)
        return jsonify(profile_to_dict(profile)), 200
    finally:
        db.close()
