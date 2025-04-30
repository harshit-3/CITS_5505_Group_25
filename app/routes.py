from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, ExerciseEntry, DietEntry, SleepEntry
from markupsafe import Markup

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html",logged_in= ("user_id" in session))


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
            error = "No account found with this email. Try signing up instead."
            return render_template("login.html", error=error)

        if not check_password_hash(user.password, password):
            error = "Incorrect password. Please try again."
            return render_template("login.html", error=error, email=email)

        # Success
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

        # 🔍 Unified CSV file handling based on tab category
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
                        date=row.get("date"),
                        notes=row.get("notes", "")
                    )
                    db.session.add(entry)
                db.session.commit()
                flash("Exercise data uploaded from CSV!", "success")

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
                        date=row.get("date"),
                        notes=row.get("notes", "")
                    )
                    db.session.add(entry)
                db.session.commit()
                flash("Diet data uploaded from CSV!", "success")

            elif category == "sleep":
                for _, row in df.iterrows():
                    entry = SleepEntry(
                        user_id=user_id,
                        sleep_start=row.get("sleep_start"),
                        sleep_end=row.get("sleep_end"),
                        sleep_quality=row.get("sleep_quality"),
                        wake_ups=row.get("wake_ups"),
                        efficiency=row.get("efficiency"),
                        sleep_type=row.get("sleep_type"),
                        notes=row.get("notes", "")
                    )
                    db.session.add(entry)
                db.session.commit()
                flash("Sleep data uploaded from CSV!", "success")

            else:
                flash("Invalid upload category.", "danger")

            return redirect(url_for("main.upload"))

        # 🧾 Manual Form Input: Exercise
        elif "workout_type" in request.form:
            entry = ExerciseEntry(
                user_id=user_id,
                workout_type=request.form["workout_type"],
                intensity=request.form.get("intensity"),
                duration=request.form.get("duration"),
                distance=request.form.get("distance"),
                calories=request.form.get("calories"),
                heart_rate=request.form.get("heart_rate"),
                date=request.form["date"],
                notes=request.form.get("notes", "") or "None"
            )
            db.session.add(entry)
            db.session.commit()
            flash("Exercise entry saved!", "success")

        # 🧾 Manual Form Input: Diet
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
                date=request.form["diet_date"],
                notes=request.form.get("diet_notes", "") or "None"
            )
            db.session.add(entry)
            db.session.commit()
            flash("Diet entry saved!", "success")

        # 🧾 Manual Form Input: Sleep
        elif "sleep_start" in request.form:
            entry = SleepEntry(
                user_id=user_id,
                sleep_start=request.form["sleep_start"],
                sleep_end=request.form["sleep_end"],
                sleep_quality=request.form["sleep_quality"],
                wake_ups=request.form.get("wake_ups"),
                efficiency=request.form.get("efficiency"),
                sleep_type=request.form.get("sleep_type"),
                notes=request.form.get("sleep_notes", "") or "None"
            )
            db.session.add(entry)
            db.session.commit()
            flash("Sleep entry saved!", "success")

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

    user_id = session["user_id"]
    records = ExerciseEntry.query.filter_by(user_id=user_id).order_by(ExerciseEntry.date.desc()).all()
    return render_template("exercise_records.html", records=records)

@main.route("/records/diet")
def diet_records():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    user_id = session["user_id"]
    records = DietEntry.query.filter_by(user_id=user_id).order_by(DietEntry.date.desc()).all()
    return render_template("diet_records.html", records=records)

@main.route("/records/sleep")
def sleep_records():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    user_id = session["user_id"]
    records = SleepEntry.query.filter_by(user_id=user_id).order_by(SleepEntry.sleep_start.desc()).all()
    return render_template("sleep_records.html", records=records)


@main.route("/analysis")
def analysis():
    if "user_id" not in session:
        flash("Please log in to view analysis.", "warning")
        return redirect(url_for("main.login"))
    return render_template("analysis.html")

@main.route("/share")
def share():
    if "user_id" not in session:
        flash("Please log in to share your progress.", "warning")
        return redirect(url_for("main.login"))
    return render_template("share.html")
