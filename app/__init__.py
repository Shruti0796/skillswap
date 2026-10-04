import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp
    from app.routes.matches import matches_bp
    from app.routes.connections import connections_bp
    from app.routes.sessions import sessions_bp
    from app.routes.reviews import reviews_bp
    from app.routes.notifications import notifications_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(matches_bp)
    app.register_blueprint(connections_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(notifications_bp)

    @app.context_processor
    def inject_unread_count():
        from flask_login import current_user
        from app.models import Notification
        if current_user.is_authenticated:
            count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        else:
            count = 0
        return {"unread_notifications": count}

    return app
