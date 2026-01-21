from routes.auth import auth_bp
from routes.main import main_bp
from routes.projects import projects_bp
from routes.quotes import quotes_bp
from routes.bpu import bpu_bp
from routes.admin import admin_bp
from routes.onboarding import onboarding_bp
from routes.api import api_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(quotes_bp, url_prefix='/quotes')
    app.register_blueprint(bpu_bp, url_prefix='/bpu')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(onboarding_bp, url_prefix='/onboarding')
    app.register_blueprint(api_bp, url_prefix='/api')
