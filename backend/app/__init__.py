from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    from config import Config
    app.config.from_object(Config)

    os.makedirs(os.path.dirname(app.config['DATABASE_PATH']), exist_ok=True)

    CORS(app, supports_credentials=True)

    db.init_app(app)

    from app.routes.asset import asset_bp
    from app.routes.log import log_bp
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    app.register_blueprint(asset_bp, url_prefix='/api')
    app.register_blueprint(log_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')

    with app.app_context():
        from app.models import asset, mac_address, usage_record, operation_log, user
        db.create_all()
        
        from app.models.user import User
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()

    return app
