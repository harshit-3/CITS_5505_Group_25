from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    birthdate = db.Column(db.String(20))  
    gender = db.Column(db.String(20))
    country = db.Column(db.String(100))

    # Relationships
    exercise_entries = db.relationship("ExerciseEntry", backref="user", cascade="all, delete-orphan")
    diet_entries = db.relationship("DietEntry", backref="user", cascade="all, delete-orphan")
    sleep_entries = db.relationship("SleepEntry", backref="user", cascade="all, delete-orphan")

class ExerciseEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    workout_type = db.Column(db.String(100))
    intensity = db.Column(db.String(50))
    duration = db.Column(db.Integer)
    distance = db.Column(db.Float)
    calories = db.Column(db.Integer)
    heart_rate = db.Column(db.Integer)
    date = db.Column(db.Date)  
    notes = db.Column(db.Text)

class DietEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    meal_type = db.Column(db.String(50))
    food_name = db.Column(db.String(100))
    calories = db.Column(db.Integer)
    meal_time = db.Column(db.String(10))  
    protein = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fats = db.Column(db.Float)
    water = db.Column(db.Integer)
    date = db.Column(db.Date)  
    notes = db.Column(db.Text)

class SleepEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sleep_start = db.Column(db.DateTime)  
    sleep_end = db.Column(db.DateTime)    
    sleep_quality = db.Column(db.String(50))
    wake_ups = db.Column(db.Integer)
    efficiency = db.Column(db.Float)
    sleep_type = db.Column(db.String(20))
    notes = db.Column(db.Text)
