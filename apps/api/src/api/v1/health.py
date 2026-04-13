from flask import Blueprint, jsonify
from core.database import check_db_connection

health_bp = Blueprint("health", __name__, url_prefix="/api/v1")


@health_bp.route("/health")
def health():
    db_ok = check_db_connection()
    return jsonify({
        "status": "ok" if db_ok else "degraded",
        "db": "connected" if db_ok else "error"
    }), 200 if db_ok else 503
