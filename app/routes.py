import secrets
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import Markup
from datetime import datetime, timedelta
from collections import Counter
from collections import defaultdict
import hashlib
from .models import db, User, ExerciseEntry, DietEntry, SleepEntry, Message, ShareToken

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
            birthdate=request.form["birthdate"],
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

        # CSV upload
        if 'csv_file' in request.files and 'category' in request.form:
            file = request.files['csv_file']
            category = request.form['category']

            if not file or file.filename == '':
                flash("No file selected.", "danger")
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

        # Exercise Form
        elif "workout_type" in request.form:
            try:
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
                db.session.commit()
                flash("Exercise data saved successfully!", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Failed to save exercise data: {str(e)}", "danger")
            return redirect(url_for("main.upload"))

        # Diet Form
        elif "meal_type" in request.form:
            try:
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
                db.session.commit()
                flash("Diet data saved successfully!", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Failed to save diet data: {str(e)}", "danger")
            return redirect(url_for("main.upload"))

        # Sleep Form
        elif "sleep_start" in request.form:
            try:
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
                flash("Sleep data saved successfully!", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Failed to save sleep data: {str(e)}", "danger")
            return redirect(url_for("main.upload"))
        else:
            # Fallback for invalid or unhandled form submissions
            flash("Invalid form submission. Please check your input.", "danger")
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

    exercise_data = ExerciseEntry.query.filter_by(user_id=user_id).order_by(ExerciseEntry.date).all()
    diet_data = DietEntry.query.filter_by(user_id=user_id).order_by(DietEntry.date).all()
    sleep_data = SleepEntry.query.filter_by(user_id=user_id).order_by(SleepEntry.sleep_start).all()

    exercise_types = [e.workout_type for e in exercise_data]
    intensity_counter = Counter(exercise_types)
    exercise_intensity_labels = list(intensity_counter.keys())
    exercise_intensity_counts = list(intensity_counter.values())
    exercise_frequency = defaultdict(int)
    for e in exercise_data:
        week_str = e.date.strftime("%Y-Week%U")
        exercise_frequency[week_str] += 1
    exercise_frequency_labels = list(exercise_frequency.keys())
    exercise_frequency_values = list(exercise_frequency.values())

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

    sleep_duration_by_date = defaultdict(float)

    for s in sleep_data:
        date_str = s.sleep_start.strftime("%Y-%m-%d")
        duration_hours = (s.sleep_end - s.sleep_start).seconds / 3600
        sleep_duration_by_date[date_str] += duration_hours

    sleep_dates = sorted(sleep_duration_by_date.keys())
    sleep_duration = [sleep_duration_by_date[d] for d in sleep_dates]

    sleep_efficiency = [s.efficiency or 0 for s in sleep_data]

    sleep_wake_ups_by_date = defaultdict(int)
    for s in sleep_data:
        date_str = s.sleep_start.strftime("%Y-%m-%d")
        sleep_wake_ups_by_date[date_str] += s.wake_ups or 0

    sleep_wake_ups_dates = sorted(sleep_wake_ups_by_date.keys())
    sleep_wake_ups = [sleep_wake_ups_by_date[d] for d in sleep_wake_ups_dates]

    sleep_type = [s.sleep_type for s in sleep_data]
    sleep_stage_counter = Counter(sleep_type)
    sleep_stage_labels = list(sleep_stage_counter.keys())
    sleep_stage_counts = list(sleep_stage_counter.values())

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

# Delete Record of Exercise
@main.route("/records/exercise/delete/<int:entry_id>", methods=["POST"])
def delete_exercise(entry_id):
    if "user_id" not in session:
        flash("Please log in to delete records.", "warning")
        return redirect(url_for("main.login"))

    entry = ExerciseEntry.query.get_or_404(entry_id)
    if entry.user_id != session["user_id"]:
        flash("You can only delete your own records.", "danger")
        return redirect(url_for("main.exercise_records"))

    try:
        db.session.delete(entry)
        db.session.commit()
        flash("Exercise record deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to delete exercise record: {str(e)}", "danger")

    return redirect(url_for("main.exercise_records"))


# Delete Record of Diet
@main.route("/records/diet/delete/<int:entry_id>", methods=["POST"])
def delete_diet(entry_id):
    if "user_id" not in session:
        flash("Please log in to delete records.", "warning")
        return redirect(url_for("main.login"))

    entry = DietEntry.query.get_or_404(entry_id)
    if entry.user_id != session["user_id"]:
        flash("You can only delete your own records.", "danger")
        return redirect(url_for("main.diet_records"))

    try:
        db.session.delete(entry)
        db.session.commit()
        flash("Diet record deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to delete diet record: {str(e)}", "danger")

    return redirect(url_for("main.diet_records"))


# Delete Record of Sleep
@main.route("/records/sleep/delete/<int:entry_id>", methods=["POST"])
def delete_sleep(entry_id):
    if "user_id" not in session:
        flash("Please log in to delete records.", "warning")
        return redirect(url_for("main.login"))

    entry = SleepEntry.query.get_or_404(entry_id)
    if entry.user_id != session["user_id"]:
        flash("You can only delete your own records.", "danger")
        return redirect(url_for("main.sleep_records"))

    try:
        db.session.delete(entry)
        db.session.commit()
        flash("Sleep record deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to delete sleep record: {str(e)}", "danger")

    return redirect(url_for("main.sleep_records"))



@main.route("/share", methods=["GET", "POST"])
def share():
    if "user_id" not in session:
        flash("Please log in to share your progress.", "warning")
        return redirect(url_for("main.login"))

    user_id = session["user_id"]

    exercise_data = ExerciseEntry.query.filter_by(user_id=user_id).order_by(ExerciseEntry.date).all()
    diet_data = DietEntry.query.filter_by(user_id=user_id).order_by(DietEntry.date).all()
    sleep_data = SleepEntry.query.filter_by(user_id=user_id).order_by(SleepEntry.sleep_start).all()

    exercise_types = [e.workout_type for e in exercise_data]
    intensity_counter = Counter(exercise_types)
    exercise_intensity_labels = list(intensity_counter.keys())
    exercise_intensity_counts = list(intensity_counter.values())
    exercise_frequency = defaultdict(int)
    for e in exercise_data:
        week_str = e.date.strftime("%Y-Week%U")
        exercise_frequency[week_str] += 1
    exercise_frequency_labels = list(exercise_frequency.keys())
    exercise_frequency_values = list(exercise_frequency.values())

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

    sleep_duration_by_date = defaultdict(float)
    for s in sleep_data:
        date_str = s.sleep_start.strftime("%Y-%m-%d")
        duration_hours = (s.sleep_end - s.sleep_start).seconds / 3600
        sleep_duration_by_date[date_str] += duration_hours

    sleep_dates = sorted(sleep_duration_by_date.keys())
    sleep_duration = [sleep_duration_by_date[d] for d in sleep_dates]

    sleep_efficiency = [s.efficiency or 0 for s in sleep_data]

    sleep_wake_ups_by_date = defaultdict(int)
    for s in sleep_data:
        date_str = s.sleep_start.strftime("%Y-%m-%d")
        sleep_wake_ups_by_date[date_str] += s.wake_ups or 0

    sleep_wake_ups_dates = sorted(sleep_wake_ups_by_date.keys())
    sleep_wake_ups = [sleep_wake_ups_by_date[d] for d in sleep_wake_ups_dates]

    sleep_type = [s.sleep_type for s in sleep_data]
    sleep_stage_counter = Counter(sleep_type)
    sleep_stage_labels = list(sleep_stage_counter.keys())
    sleep_stage_counts = list(sleep_stage_counter.values())

    # summary message
    summary = (
        f"Sharing the recording!" )

    # Generate a secure share token and store in ShareToken
    share_token = secrets.token_hex(16)
    expires_at = datetime.utcnow() + timedelta(days=7)
    share_token_entry = ShareToken(token=share_token, user_id=user_id, expires_at=expires_at)
    db.session.add(share_token_entry)
    db.session.commit()

    if request.headers.get('X-Forwarded-Proto'):
        protocol = request.headers.get('X-Forwarded-Proto')
    else:
        protocol = 'https' if request.is_secure else 'http'

    host = request.headers.get('Host', request.host)
    base_url = f"{protocol}://{host}"
    share_url = f"{base_url}/health_info/{share_token}"

    if request.method == "POST":
        receiver_email = request.form.get("receiver_email")
        receiver = User.query.filter_by(email=receiver_email).first()
        if not receiver:
            flash("User with this email not found.", "danger")
            return redirect(url_for("main.share"))
        if receiver.id == user_id:
            flash("You cannot share with yourself.", "danger")
            return redirect(url_for("main.share"))

        message_content = f"{summary} View my health information: {share_url}"
        message = Message(
            sender_id=user_id,
            receiver_id=receiver.id,
            content=message_content,
            is_read=False,
            timestamp=datetime.utcnow()
        )
        db.session.add(message)
        db.session.commit()
        flash("Health information shared successfully!", "success")
        return redirect(url_for("main.share"))

    return render_template("share.html",
                           summary=summary,
                           share_url=share_url,
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
                           sleep_stage_counts=sleep_stage_counts)

# Health info route to display a user's health information using a token
@main.route("/health_info/<token>")
def health_info(token):
    print(f"Health info session data: {session.items()}")
    print(f"Cookies received: {request.cookies.get('session')}")
    if "user_id" not in session:
        flash("Please log in to view health information.", "warning")
        return redirect(url_for("main.login", next=request.url))

    share_token = ShareToken.query.filter_by(token=token).first()
    print(f"ShareToken found: {share_token}")
    if not share_token or share_token.expires_at < datetime.utcnow():
        flash("Invalid or expired share link.", "danger")
        return redirect(url_for("main.index"))

    user_id = share_token.user_id
    user = User.query.get_or_404(user_id)
    exercise_entries = ExerciseEntry.query.filter_by(user_id=user_id).order_by(ExerciseEntry.date.desc()).all()
    diet_entries = DietEntry.query.filter_by(user_id=user_id).order_by(DietEntry.date.desc()).all()
    sleep_entries = SleepEntry.query.filter_by(user_id=user_id).order_by(SleepEntry.sleep_start.desc()).all()

    return render_template("health_info.html",
                           user=user,
                           exercise_entries=exercise_entries,
                           diet_entries=diet_entries,
                           sleep_entries=sleep_entries)

@main.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("main.login"))
    user = User.query.get(session["user_id"])
    return render_template("profile.html", user=user)

@main.route("/profile/update", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Not logged in"})

    user = User.query.get(session["user_id"])
    user.first_name = request.form.get("first_name", user.first_name)
    user.last_name = request.form.get("last_name", user.last_name)
    user.birthdate = request.form.get("birthdate", user.birthdate)
    user.gender = request.form.get("gender", user.gender)
    user.country = request.form.get("country", user.country)

    db.session.commit()
    return jsonify({"status": "success", "message": "Profile updated"})

@main.route("/profile/password", methods=["POST"])
def change_password():
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Not logged in"})

    user = User.query.get(session["user_id"])
    old_password = request.form["old_password"]
    new_password = request.form["new_password"]

    if not check_password_hash(user.password, old_password):
        return jsonify({"status": "error", "message": "Old password is incorrect"})

    user.password = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({"status": "success", "message": "Password updated successfully"})

@main.route("/messages", methods=["GET", "POST"])
def messages():
    if "user_id" not in session:
        flash("Please log in to view your messages.", "warning")
        return redirect(url_for("main.login"))

    user_id = session["user_id"]

    # Handle POST requests (manual marking or mark all as read)
    if request.method == "POST":
        action = request.form.get("action")
        message_id = request.form.get("message_id")

        # Handle one-click mark all as read
        if action == "mark_all_read":
            unread_messages = Message.query.filter_by(receiver_id=user_id, is_read=False).all()
            if unread_messages:
                for message in unread_messages:
                    message.is_read = True
                db.session.commit()
                flash("All messages have been marked as read.", "success")
            else:
                flash("No unread messages to mark as read.", "info")
            return redirect(url_for("main.messages"))

        # Handle manual marking messages as read/unread
        if message_id:
            message = Message.query.get_or_404(message_id)

            # Ensure the user is the receiver of the message
            if message.receiver_id != user_id:
                flash("You do not have permission to modify this message.", "danger")
                return redirect(url_for("main.messages"))

            if action == "mark_read":
                message.is_read = True
                flash("Message marked as read.", "success")
            elif action == "mark_unread":
                message.is_read = False
                flash("Message marked as unread.", "success")

            db.session.commit()
            return redirect(url_for("main.messages"))

# Handle GET requests (display messages page)
    sent_messages = Message.query.filter_by(sender_id=user_id).order_by(Message.timestamp.desc()).all()
    received_messages = Message.query.filter_by(receiver_id=user_id).order_by(Message.timestamp.desc()).all()

    # Process messages to render links as clickable HTML
    for message in sent_messages + received_messages:
        # Check if the message content contains a URL
        if "http://" in message.content or "https://" in message.content:
            # Extract the URL
            parts = message.content.split("View my health information: ")
            if len(parts) > 1:
                url = parts[1]
                message.content = Markup(f'{parts[0]}View my health information: <a href="{url}" target="_blank">{url}</a>')

    return render_template("messages.html",
                           sent_messages=sent_messages,
                           received_messages=received_messages)