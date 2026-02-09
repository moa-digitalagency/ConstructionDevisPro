import os
from flask import Flask
from flask_login import LoginManager
from models import db

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    
    app.secret_key = os.environ.get("SESSION_SECRET") or os.environ.get("FLASK_SECRET_KEY") or "dev-secret-key-change-in-production"
    
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
    app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "static", "uploads")
    
    db.init_app(app)
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'warning'
    
    from models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from routes import register_blueprints
    register_blueprints(app)
    
    from services.i18n_service import i18n
    i18n.init_app(app)

    from flask import session, redirect, request

    @app.route('/set_language/<lang>')
    def set_language(lang):
        if lang in i18n.supported_locales:
            session['lang'] = lang
        return redirect(request.referrer or '/')

    with app.app_context():
        db.create_all()
        from scripts.seed_data import seed_initial_data
        seed_initial_data()
    
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
