from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timezone

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

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Shared fitness information
    is_read = db.Column(db.Boolean, default=False)  # Read/unread status
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # Timestamp of the message
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

    def __repr__(self):
        return f'<Message from {self.sender_id} to {self.receiver_id} at {self.timestamp}>'


class ShareToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(32), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    user = db.relationship('User', backref='share_tokens')