from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .models import db

migrate = Migrate()  # Initialize empty migrate object

def create_app():
    app = Flask(__name__)
    app.secret_key = "super-secret-key"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tracker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)  # Bind migrate after app is created

    from .routes import main
    app.register_blueprint(main)

    # Don't use db.create_all() — handled by migrations
    return app
