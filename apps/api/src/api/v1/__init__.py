from .health import health_bp
from .profile import profile_bp
from .workouts import workouts_bp
from .calendar import calendar_bp
from .import_fit import import_fit_bp
from .ftp_test import ftp_test_bp

def register_blueprints(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(workouts_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(import_fit_bp)
    app.register_blueprint(ftp_test_bp)
