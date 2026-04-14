from flask import Flask, jsonify
from flask_cors import CORS
from core.config import Config
from core.database import init_db
from api.v1 import register_blueprints


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins=["http://localhost:5173"])

    init_db()
    register_blueprints(app)
    from api.v1.templates import templates_bp
    app.register_blueprint(templates_bp)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "not_found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "internal_server_error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
