import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///tracker.db"
    DEBUG = True

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
