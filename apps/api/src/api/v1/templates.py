from flask import Blueprint, request, jsonify
from core.database import SessionLocal
from infrastructure.db.models import WorkoutTemplate

templates_bp = Blueprint("templates", __name__, url_prefix="/api/v1/templates")

@templates_bp.route("", methods=["GET"])
def get_templates():
    db = SessionLocal()
    try:
        templates = db.query(WorkoutTemplate).order_by(WorkoutTemplate.created_at.desc()).all()
        return jsonify([{
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "type": t.type,
            "structured_steps": t.structured_steps
        } for t in templates])
    finally:
        db.close()

@templates_bp.route("", methods=["POST"])
def create_template():
    data = request.json
    db = SessionLocal()
    try:
        t = WorkoutTemplate(
            name=data.get("name", "Nowy Szablon"),
            description=data.get("description"),
            type=data.get("type", "z2"),
            structured_steps=data.get("structured_steps")
        )
        db.add(t)
        db.commit()
        db.refresh(t)
        return jsonify({
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "type": t.type,
            "structured_steps": t.structured_steps
        }), 201
    finally:
        db.close()

@templates_bp.route("/<int:t_id>", methods=["DELETE"])
def delete_template(t_id):
    db = SessionLocal()
    try:
        t = db.query(WorkoutTemplate).get(t_id)
        if t:
            db.delete(t)
            db.commit()
        return jsonify({"success": True})
    finally:
        db.close()