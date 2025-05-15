from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .models import db

migrate = Migrate()  # Initialize empty migrate object

def create_app(config_class=None):
    app = Flask(__name__)
    if config_class:
        app.config.from_object(config_class)
    else:
        app.config['SECRET_KEY'] = "super-secret-key"
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tracker.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)  # Bind migrate after app is created

    print("current database config is：", app.config['SQLALCHEMY_DATABASE_URI'])

    # Import models after db initialization to avoid circular imports
    from . import models

    # Context processor to inject Message model into all templates
    @app.context_processor
    def inject_message_model():
        return dict(Message=models.Message)

    from .routes import main
    app.register_blueprint(main)

    # Don't use db.create_all() — handled by migrations
    return app
