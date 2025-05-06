from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, ExerciseEntry, DietEntry, SleepEntry
from markupsafe import Markup
from datetime import datetime
import io
import base64
import matplotlib.pyplot as plt
from flask import send_file
from collections import Counter
from collections import defaultdict


main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html", logged_in=("user_id" in session))

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return redirect(url_for("main.register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            error = "An account with this email already exists. Try logging in or use 'Forgot Password'."
            return render_template("register.html", error=error)

        new_user = User(
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
            email=email,
            password=generate_password_hash(password),
            birthdate=request.form["birthdate"],  # Could parse to date if model is updated
            gender=request.form["gender"],
            country=request.form["country"]
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if not user:
            return render_template("login.html", error="No account found with this email.")
        if not check_password_hash(user.password, password):
            return render_template("login.html", error="Incorrect password.", email=email)

        session["user_id"] = user.id
        flash("Login successful!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("login.html")


@main.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to access your dashboard.", "warning")
        return redirect(url_for("main.login"))
    return render_template("dashboard.html")

@main.route("/upload", methods=["GET", "POST"])
def upload():
    if "user_id" not in session:
        flash("Please log in to upload data.", "warning")
        return redirect(url_for("main.login"))

    if request.method == "POST":
        user_id = session["user_id"]

        if 'csv_file' in request.files and 'category' in request.form:
            file = request.files['csv_file']
            category = request.form['category']

            if not file or file.filename == '':
                flash("No file selected.", "warning")
                return redirect(url_for("main.upload"))

            import pandas as pd
            try:
                df = pd.read_csv(file)
            except Exception:
                flash("Invalid CSV format.", "danger")
                return redirect(url_for("main.upload"))

            try:
                if category == "exercise":
                    for _, row in df.iterrows():
                        entry = ExerciseEntry(
                            user_id=user_id,
                            workout_type=row.get("workout_type"),
                            intensity=row.get("intensity"),
                            duration=row.get("duration"),
                            distance=row.get("distance"),
                            calories=row.get("calories"),
                            heart_rate=row.get("heart_rate"),
                            date=datetime.strptime(row.get("date"), "%Y-%m-%d").date(),
                            notes=row.get("notes", "")
                        )
                        db.session.add(entry)

                elif category == "diet":
                    for _, row in df.iterrows():
                        entry = DietEntry(
                            user_id=user_id,
                            meal_type=row.get("meal_type"),
                            food_name=row.get("food_name"),
                            calories=row.get("calories"),
                            meal_time=row.get("meal_time"),
                            protein=row.get("protein"),
                            carbs=row.get("carbs"),
                            fats=row.get("fats"),
                            water=row.get("water"),
                            date=datetime.strptime(row.get("date"), "%Y-%m-%d").date(),
                            notes=row.get("notes", "")
                        )
                        db.session.add(entry)

                elif category == "sleep":
                    for _, row in df.iterrows():
                        entry = SleepEntry(
                            user_id=user_id,
                            sleep_start=datetime.strptime(row.get("sleep_start"), "%Y-%m-%dT%H:%M"),
                            sleep_end=datetime.strptime(row.get("sleep_end"), "%Y-%m-%dT%H:%M"),
                            sleep_quality=row.get("sleep_quality"),
                            wake_ups=row.get("wake_ups"),
                            efficiency=row.get("efficiency"),
                            sleep_type=row.get("sleep_type"),
                            notes=row.get("notes", "")
                        )
                        db.session.add(entry)
                else:
                    flash("Invalid upload category.", "danger")
                    return redirect(url_for("main.upload"))

                db.session.commit()
                flash(f"{category.capitalize()} data uploaded from CSV!", "success")
            except Exception as e:
                flash(f"Error processing CSV data: {str(e)}", "danger")

            return redirect(url_for("main.upload"))

        # Manual: Exercise
        elif "workout_type" in request.form:
            entry = ExerciseEntry(
                user_id=user_id,
                workout_type=request.form["workout_type"],
                intensity=request.form.get("intensity"),
                duration=request.form.get("duration"),
                distance=request.form.get("distance"),
                calories=request.form.get("calories"),
                heart_rate=request.form.get("heart_rate"),
                date=datetime.strptime(request.form["date"], "%Y-%m-%d").date(),
                notes=request.form.get("notes", "") or "None"
            )
            db.session.add(entry)

        # Manual: Diet
        elif "meal_type" in request.form:
            entry = DietEntry(
                user_id=user_id,
                meal_type=request.form["meal_type"],
                food_name=request.form["food_name"],
                calories=request.form["diet_calories"],
                meal_time=request.form.get("meal_time"),
                protein=request.form.get("protein"),
                carbs=request.form.get("carbs"),
                fats=request.form.get("fats"),
                water=request.form.get("water"),
                date=datetime.strptime(request.form["diet_date"], "%Y-%m-%d").date(),
                notes=request.form.get("diet_notes", "") or "None"
            )
            db.session.add(entry)

        # Manual: Sleep
        elif "sleep_start" in request.form:
            entry = SleepEntry(
                user_id=user_id,
                sleep_start=datetime.strptime(request.form["sleep_start"], "%Y-%m-%dT%H:%M"),
                sleep_end=datetime.strptime(request.form["sleep_end"], "%Y-%m-%dT%H:%M"),
                sleep_quality=request.form["sleep_quality"],
                wake_ups=request.form.get("wake_ups"),
                efficiency=request.form.get("efficiency"),
                sleep_type=request.form.get("sleep_type"),
                notes=request.form.get("sleep_notes", "") or "None"
            )
            db.session.add(entry)

        db.session.commit()
        flash("Data saved successfully!", "success")
        return redirect(url_for("main.upload"))

    return render_template("upload.html")

@main.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))

@main.route("/records/exercise")
def exercise_records():
    if "user_id" not in session:
        return redirect(url_for("main.login"))
    records = ExerciseEntry.query.filter_by(user_id=session["user_id"]).order_by(ExerciseEntry.date.desc()).all()
    return render_template("exercise_records.html", records=records)

@main.route("/records/diet")
def diet_records():
    if "user_id" not in session:
        return redirect(url_for("main.login"))
    records = DietEntry.query.filter_by(user_id=session["user_id"]).order_by(DietEntry.date.desc()).all()
    return render_template("diet_records.html", records=records)

@main.route("/records/sleep")
def sleep_records():
    if "user_id" not in session:
        return redirect(url_for("main.login"))
    records = SleepEntry.query.filter_by(user_id=session["user_id"]).order_by(SleepEntry.sleep_start.desc()).all()
    return render_template("sleep_records.html", records=records)


@main.route("/analysis")
def analysis():
    if "user_id" not in session:
        flash("Please log in to view analysis.", "warning")
        return redirect(url_for("main.login"))

    user_id = session["user_id"]

    #  get all the data required
    exercise_data = ExerciseEntry.query.filter_by(user_id=user_id).order_by(ExerciseEntry.date).all()
    # print("exercise_data=========================")
    # print(exercise_data)
    # print("exercise_data=========================")
    diet_data = DietEntry.query.filter_by(user_id=user_id).order_by(DietEntry.date).all()
    # print("diet_data+++++++++++++++++++++++++++")
    # print(diet_data)
    # print("diet_data+++++++++++++++++++++++++++")
    sleep_data = SleepEntry.query.filter_by(user_id=user_id).order_by(SleepEntry.sleep_start).all()
    # print("sleep_data----------------------------")
    # print(sleep_data)
    # print("sleep_data----------------------------")

    #  Extract fields (required for each image)
    exercise_types = [e.workout_type for e in exercise_data]
    intensity_counter = Counter(exercise_types)
    exercise_intensity_labels = list(intensity_counter.keys())
    exercise_intensity_counts = list(intensity_counter.values())
    # Exercise frequency by week
    exercise_frequency = defaultdict(int)
    for e in exercise_data:
        week_str = e.date.strftime("%Y-Week%U")
        exercise_frequency[week_str] += 1
    exercise_frequency_labels = list(exercise_frequency.keys())
    exercise_frequency_values = list(exercise_frequency.values())

    # Aggregate exercise data by date
    exercise_duration_by_date = defaultdict(int)
    exercise_calories_by_date = defaultdict(int)
    exercise_heart_rate_by_date = defaultdict(list)

    for e in exercise_data:
        date_str = e.date.strftime("%Y-%m-%d")
        exercise_duration_by_date[date_str] += e.duration or 0
        exercise_calories_by_date[date_str] += e.calories or 0
        if e.heart_rate:
            exercise_heart_rate_by_date[date_str].append(e.heart_rate)

    exercise_dates = sorted(exercise_duration_by_date.keys())
    exercise_durations = [exercise_duration_by_date[d] for d in exercise_dates]
    exercise_calories = [exercise_calories_by_date[d] for d in exercise_dates]
    exercise_heart_rate = [
        round(sum(exercise_heart_rate_by_date[d]) / len(exercise_heart_rate_by_date[d]), 1)
        if exercise_heart_rate_by_date[d] else 0
        for d in exercise_dates
    ]

    # Aggregate diet data by date
    diet_calories_by_date = defaultdict(int)
    diet_water_by_date = defaultdict(int)

    for d in diet_data:
        date_str = d.date.strftime("%Y-%m-%d")
        diet_calories_by_date[date_str] += d.calories or 0
        diet_water_by_date[date_str] += d.water or 0

    diet_dates = sorted(diet_calories_by_date.keys())
    diet_calories = [diet_calories_by_date[d] for d in diet_dates]
    diet_water = [diet_water_by_date[d] for d in diet_dates]

    diet_protein = [d.protein or 0 for d in diet_data]
    diet_carbs = [d.carbs or 0 for d in diet_data]
    diet_fats = [d.fats or 0 for d in diet_data]
    diet_meal_type = [d.meal_type for d in diet_data]
    meal_frequency = defaultdict(int)
    for d in diet_data:
        week_str = d.date.strftime("%Y-Week%U")
        meal_frequency[week_str] += 1
    meal_labels = list(meal_frequency.keys())
    meal_values = list(meal_frequency.values())

    # Aggregate sleep duration by date
    sleep_duration_by_date = defaultdict(float)

    for s in sleep_data:
        date_str = s.sleep_start.strftime("%Y-%m-%d")
        duration_hours = (s.sleep_end - s.sleep_start).seconds / 3600
        sleep_duration_by_date[date_str] += duration_hours

    sleep_dates = sorted(sleep_duration_by_date.keys())
    sleep_duration = [sleep_duration_by_date[d] for d in sleep_dates]

    sleep_efficiency = [s.efficiency or 0 for s in sleep_data]

    # Group and sum wake-up counts per date
    sleep_wake_ups_by_date = defaultdict(int)
    for s in sleep_data:
        date_str = s.sleep_start.strftime("%Y-%m-%d")
        sleep_wake_ups_by_date[date_str] += s.wake_ups or 0

    sleep_wake_ups_dates = sorted(sleep_wake_ups_by_date.keys())
    sleep_wake_ups = [sleep_wake_ups_by_date[d] for d in sleep_wake_ups_dates]

    sleep_type = [s.sleep_type for s in sleep_data]
    # Compute count of each sleep type
    sleep_stage_counter = Counter(sleep_type)
    sleep_stage_labels = list(sleep_stage_counter.keys())
    sleep_stage_counts = list(sleep_stage_counter.values())



    #  Pass to the template
    return render_template("analysis.html",
        exercise_dates=exercise_dates,
        exercise_durations=exercise_durations,
        exercise_calories=exercise_calories,
        exercise_heart_rate=exercise_heart_rate,
        exercise_types=exercise_types,
        exercise_intensity_labels=exercise_intensity_labels,
        exercise_intensity_counts=exercise_intensity_counts,
        exercise_frequency_labels=exercise_frequency_labels,
        exercise_frequency_values=exercise_frequency_values,


        diet_dates=diet_dates,
        diet_calories=diet_calories,
        diet_water=diet_water,
        diet_protein=diet_protein,
        diet_carbs=diet_carbs,
        diet_fats=diet_fats,
        diet_meal_type=diet_meal_type,
        meal_labels=meal_labels,
        meal_values=meal_values,

        sleep_dates=sleep_dates,
        sleep_efficiency=sleep_efficiency,
        sleep_wake_ups=sleep_wake_ups,
        sleep_wake_ups_dates=sleep_wake_ups_dates,
        sleep_type=sleep_type,
        sleep_duration=sleep_duration,
        sleep_stage_labels=sleep_stage_labels,
        sleep_stage_counts=sleep_stage_counts,
    )


@main.route("/share")
def share():
    if "user_id" not in session:
        flash("Please log in to share your progress.", "warning")
        return redirect(url_for("main.login"))
    return render_template("share.html")
