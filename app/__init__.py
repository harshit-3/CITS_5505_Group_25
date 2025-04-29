from flask import Flask
from .models import db


def create_app():
    app = Flask(__name__)
    app.secret_key = "super-secret-key"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tracker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        from .models import User  # 👈 force model import here!
        db.create_all()

    return app
