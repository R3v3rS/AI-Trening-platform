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
            "structured_steps": req.structured_steps,
        })
        return jsonify(planned_workout_to_dict(pw)), 201
    finally:
        db.close()

@calendar_bp.route("/planned-workouts/<int:workout_id>/export/zwo", methods=["GET"])
def export_zwo(workout_id: int):
    """
    Generuje plik ZWO z zaplanowanego treningu na podstawie structured_steps.
    Jeśli structured_steps nie istnieje, tworzy płaski blok dla zadanego typu treningu.
    """
    import json
    from infrastructure.repositories.profile_repository import ProfileRepository
    db = SessionLocal()
    try:
        repo = PlannedWorkoutRepository(db)
        pw = repo.get_by_id(workout_id)
        if not pw:
            return jsonify({"error": "not_found"}), 404
            
        profile_repo = ProfileRepository(db)
        profile = profile_repo.get_profile()
        ftp = profile.ftp_watts if profile and profile.ftp_watts else 200
        
        duration_sec = pw.duration_sec or 3600
        workout_tags = ""
        
        if pw.structured_steps:
            try:
                steps = json.loads(pw.structured_steps)
                for step in steps:
                    step_type = step.get("type")
                    if step_type == "warmup":
                        dur = step.get("duration", 300)
                        p_start = step.get("power_start", ftp * 0.4) / ftp
                        p_end = step.get("power_end", ftp * 0.7) / ftp
                        workout_tags += f'    <Warmup Duration="{dur}" PowerLow="{p_start:.2f}" PowerHigh="{p_end:.2f}"/>\n'
                    elif step_type == "cooldown":
                        dur = step.get("duration", 300)
                        p_start = step.get("power_start", ftp * 0.7) / ftp
                        p_end = step.get("power_end", ftp * 0.4) / ftp
                        workout_tags += f'    <Cooldown Duration="{dur}" PowerLow="{p_start:.2f}" PowerHigh="{p_end:.2f}"/>\n'
                    elif step_type == "interval":
                        repeat = step.get("repeat", 1)
                        on_dur = step.get("on_duration", 60)
                        off_dur = step.get("off_duration", 60)
                        on_pow = step.get("on_power", ftp) / ftp
                        off_pow = step.get("off_power", ftp * 0.5) / ftp
                        workout_tags += f'    <IntervalsT Repeat="{repeat}" OnDuration="{on_dur}" OffDuration="{off_dur}" OnPower="{on_pow:.2f}" OffPower="{off_pow:.2f}"/>\n'
                    else: # steady
                        dur = step.get("duration", 300)
                        p = step.get("power", ftp * 0.65) / ftp
                        workout_tags += f'    <SteadyState Duration="{dur}" Power="{p:.2f}"/>\n'
            except Exception as e:
                # W przypadku błędu parsowania JSON-a
                workout_tags = f'    <SteadyState Duration="{duration_sec}" Power="0.75"/>\n'
        else:
            # Proste przypisanie % FTP do zdefiniowanych typów treningu (stary sposób)
            power_zones = {
                "recovery": 0.50,
                "z2": 0.65,
                "tempo": 0.80,
                "long_ride": 0.65,
                "vo2max": 1.10,
                "ftp_test": 1.00
            }
            power_fraction = power_zones.get(pw.type, 0.70)
            workout_tags = f'    <SteadyState Duration="{duration_sec}" Power="{power_fraction}"/>\n'
        
        # Generowanie formatu XML/ZWO
        zwo_content = f"""<?xml version="1.0" encoding="UTF-8" ?>
<workout_file>
  <author>Treningowy Asystent Kolarza</author>
  <name>{(pw.type or 'Trening').upper()} na dzień {pw.planned_date}</name>
  <description>{pw.notes or "Wygenerowano automatycznie"}</description>
  <sportType>bike</sportType>
  <workout>
{workout_tags.rstrip()}
  </workout>
</workout_file>
"""
        from flask import Response
        response = Response(zwo_content, mimetype="application/xml")
        response.headers["Content-Disposition"] = f"attachment; filename=workout_{pw.planned_date}.zwo"
        return response
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
