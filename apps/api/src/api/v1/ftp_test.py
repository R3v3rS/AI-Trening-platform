import os
import tempfile
from flask import Blueprint, request, jsonify
from core.database import SessionLocal
from infrastructure.fit.garmin_parser import GarminFitParser, FitParseError
from infrastructure.repositories.profile_repository import (
    ProfileRepository,
    profile_to_dict,
)
from domain.metrics.ftp_calculator import (
    calculate_ftp_from_ramp_test,
    calculate_ftp_from_20min_test,
)

ftp_test_bp = Blueprint("ftp_test", __name__, url_prefix="/api/v1")

VALID_PROTOCOLS = {"ramp", "20min"}


@ftp_test_bp.route("/ftp-test/from-fit", methods=["POST"])
def ftp_from_fit():
    """
    Parsuje plik FIT i sugeruje FTP na podstawie wybranego protokołu.
    Nie zapisuje automatycznie do profilu.
    """
    if "file" not in request.files:
        return jsonify({"error": "missing_file"}), 400

    file = request.files["file"]
    if not file.filename.lower().endswith(".fit"):
        return jsonify({
            "error": "invalid_file",
            "detail": "Plik musi mieć rozszerzenie .fit"
        }), 422

    protocol = request.args.get("protocol", "ramp")
    if protocol not in VALID_PROTOCOLS:
        return jsonify({
            "error": "invalid_protocol",
            "detail": f"Dozwolone protokoły: {sorted(VALID_PROTOCOLS)}"
        }), 422

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".fit", delete=False
        ) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        parser = GarminFitParser()
        try:
            result = parser.parse(tmp_path)
        except FitParseError as e:
            return jsonify({
                "error": "invalid_fit_file",
                "detail": str(e)
            }), 422
        finally:
            os.unlink(tmp_path)

        header = result["header"]
        samples = result["samples"]
        power_samples = [s.get("power") for s in samples]

        if protocol == "ramp":
            try:
                suggested_ftp = calculate_ftp_from_ramp_test(power_samples)
                cleaned = [p for p in power_samples if p is not None]
                samples_per_minute = 60
                avg_last_60s = (
                    sum(cleaned[-samples_per_minute:])
                    / len(cleaned[-samples_per_minute:])
                    if len(cleaned) >= samples_per_minute
                    else 0
                )
                return jsonify({
                    "suggested_ftp": suggested_ftp,
                    "protocol": "ramp",
                    "avg_power_last_60s": round(avg_last_60s, 1),
                    "note": (
                        "Zaktualizuj profil jeśli akceptujesz wynik. "
                        "Użyj POST /api/v1/ftp-test/accept"
                    ),
                }), 200
            except ValueError as e:
                return jsonify({
                    "error": "calculation_error",
                    "detail": str(e)
                }), 422

        else:  # 20min
            avg_power = header.get("avg_power")
            if not avg_power:
                return jsonify({
                    "error": "missing_data",
                    "detail": "Brak średniej mocy w pliku FIT."
                }), 422
            try:
                suggested_ftp = calculate_ftp_from_20min_test(avg_power)
                return jsonify({
                    "suggested_ftp": suggested_ftp,
                    "protocol": "20min",
                    "avg_power_20min": avg_power,
                    "note": (
                        "Zaktualizuj profil jeśli akceptujesz wynik. "
                        "Użyj POST /api/v1/ftp-test/accept"
                    ),
                }), 200
            except ValueError as e:
                return jsonify({
                    "error": "calculation_error",
                    "detail": str(e)
                }), 422

    except Exception as e:
        return jsonify({
            "error": "internal_error",
            "detail": str(e)
        }), 500


@ftp_test_bp.route("/ftp-test/manual", methods=["POST"])
def ftp_manual():
    """
    Oblicza sugerowane FTP na podstawie ręcznie podanej mocy.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "error": "invalid_body",
            "detail": "Wymagane ciało żądania w formacie JSON"
        }), 400

    protocol = data.get("protocol")
    if protocol not in VALID_PROTOCOLS:
        return jsonify({
            "error": "invalid_protocol",
            "detail": f"Dozwolone protokoły: {sorted(VALID_PROTOCOLS)}"
        }), 422

    avg_power = data.get("avg_power")
    if avg_power is None or not isinstance(avg_power, (int, float)):
        return jsonify({
            "error": "validation_error",
            "fields": {"avg_power": "Wymagana liczba > 0"}
        }), 422

    try:
        if protocol == "ramp":
            # Dla ręcznego ramp testu traktujemy avg_power
            # jako średnią ostatniej minuty
            suggested_ftp = round(avg_power * 0.75)
        else:
            suggested_ftp = calculate_ftp_from_20min_test(avg_power)

        return jsonify({
            "suggested_ftp": suggested_ftp,
            "protocol": protocol,
            "avg_power": avg_power,
        }), 200

    except ValueError as e:
        return jsonify({
            "error": "calculation_error",
            "detail": str(e)
        }), 422


@ftp_test_bp.route("/ftp-test/accept", methods=["POST"])
def ftp_accept():
    """
    Aktualizuje FTP w profilu sportowca po akceptacji wyniku testu.
    """
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({
            "error": "invalid_body",
            "detail": "Wymagane ciało żądania w formacie JSON"
        }), 400

    suggested_ftp = data.get("suggested_ftp")
    if suggested_ftp is None or not isinstance(suggested_ftp, int):
        return jsonify({
            "error": "validation_error",
            "fields": {"suggested_ftp": "Wymagana liczba całkowita > 0"}
        }), 422

    if suggested_ftp <= 0:
        return jsonify({
            "error": "validation_error",
            "fields": {"suggested_ftp": "Musi być większe niż 0"}
        }), 422

    db = SessionLocal()
    try:
        repo = ProfileRepository(db)
        profile = repo.upsert({"ftp_watts": suggested_ftp})
        return jsonify({
            "message": "FTP zaktualizowane pomyślnie.",
            "profile": profile_to_dict(profile),
        }), 200
    finally:
        db.close()
