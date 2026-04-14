import os
import tempfile

from flask import Blueprint, jsonify, request

from core.database import SessionLocal
from domain.metrics import MetricsError, calculate_metrics
from infrastructure.fit import FitParseError, GarminFitParser
from infrastructure.db.models import Workout

import_fit_bp = Blueprint("import_fit", __name__, url_prefix="/api/v1")


@import_fit_bp.route("/workouts/import-fit", methods=["POST"])
def import_fit():
    if "file" not in request.files:
        return jsonify({"error": "missing_file"}), 400

    fit_file = request.files["file"]
    if fit_file.filename == "":
        return jsonify({"error": "empty_filename"}), 400

    ftp_raw = request.form.get("ftp")
    ftp = float(ftp_raw) if ftp_raw else None

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".fit") as tmp:
            fit_file.save(tmp.name)
            temp_path = tmp.name

        parser = GarminFitParser()
        parsed = parser.parse(temp_path)

        header = parsed.get("header", {})
        samples = parsed.get("samples", [])
        power_samples = [sample.get("power") for sample in samples]

        duration_sec = header.get("duration_sec")
        if duration_sec is None and samples:
            valid_offsets = [s.get("sec_from_start") for s in samples if s.get("sec_from_start") is not None]
            duration_sec = max(valid_offsets) if valid_offsets else None

        metrics = calculate_metrics(power_samples, duration_sec, ftp)
        db = SessionLocal()
        workout = None
        try:
            if header.get("started_at"):
                workout = Workout(
                    started_at=header.get("started_at"),
                    tss=metrics.get("tss"),
                )
                db.add(workout)
                db.commit()
                db.refresh(workout)

            # Przelicz metryki długoterminowe po imporcie
            try:
                from domain.metrics.load_calculator import recalculate_load_metrics
                if workout is not None:
                    recalculate_load_metrics(workout.started_at.date(), db)
            except Exception as e:
                # Nie blokuj importu jeśli przeliczenie metryk zawiedzie
                print(f"[WARN] Błąd przeliczania CTL/ATL/TSB: {e}")
        finally:
            db.close()

        return jsonify(
            {
                "file_hash": parsed.get("file_hash"),
                "header": {
                    **header,
                    "started_at": header.get("started_at").isoformat() if header.get("started_at") else None,
                },
                "samples_count": len(samples),
                "metrics": metrics,
            }
        ), 200
    except FitParseError as exc:
        return jsonify({"error": "fit_parse_error", "detail": str(exc)}), 422
    except (MetricsError, ValueError) as exc:
        return jsonify({"error": "metrics_error", "detail": str(exc)}), 400
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
