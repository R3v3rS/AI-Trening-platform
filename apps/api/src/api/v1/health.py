from flask import Blueprint, jsonify
from core.database import check_db_connection

health_bp = Blueprint("health", __name__, url_prefix="/api/v1")

@health_bp.route("/health")
def health():
    db_status = "connected" if check_db_connection() else "error"
    return jsonify({"status": "ok", "db": db_status})
