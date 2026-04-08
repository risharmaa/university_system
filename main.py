import mysql
import mysql.connector 

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
import os
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.secret_key ="secret_key"
mydb = mysql.connector.connect(
    host="ads26-gill.c5w0gocewai2.us-east-1.rds.amazonaws.com",
    user="admin",
    password="kirangill2006!",
    database="university"
)

app.debug = True

def get_db():
    if not mydb.is_connected():
        mydb.reconnect(attempts=3, delay=2)
    return mydb


@app.route('/')
def index():
  return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        mydb.commit()
        cursor = mydb.cursor(dictionary=True)
        cursor.execute( "SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and (
            user["password"] == password
            or check_password_hash(user["password"], password)
        ):
            session["user"] = {
                "uid": user["uid"],
                "username": user["username"],
                "role": user['role'],
                "fname": user["fname"],
                "lname": user["lname"],
            }
            flash("Logged in successfully.", "success")
            if user["role"] == 'admin':
                return redirect(url_for("admin"))
            elif user["role"] == "student":
                return redirect(url_for("student"))
            elif user["role"] == "secretary":
                return redirect(url_for("secretary"))
            elif user["role"] == "alumni":
                return redirect(url_for("alumni"))
            elif user["role"] == "faculty":
                return redirect(url_for("faculty"))
            elif user["role"] == "applicant":
                return redirect(url_for("applicant_dashboard"))
            else:
                flash("Invalid user or password", "error")
                return redirect(url_for("login"))
        else:
            flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "user" not in session or session["user"]["role"] != "admin":
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    mydb.commit()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT u.uid, u.fname, u.lname, u.email, s.program, s.address, s.graduation_status FROM users u JOIN students s ON u.uid = s.uid")
    students = cursor.fetchall()

    cursor.execute("SELECT u.uid, u.fname, u.lname, u.email FROM users u JOIN faculty f ON u.uid = f.uid")
    faculty = cursor.fetchall()

    cursor.execute("SELECT u.uid, u.fname, u.lname, u.email FROM users u JOIN secretary s on u.uid = s.uid")
    secretary = cursor.fetchall()

    cursor.execute("SELECT u.uid, u.fname, u.lname, a.degree, a.graduation_year, a.address FROM users u JOIN alumni a ON u.uid = a.uid")
    alumni = cursor.fetchall()

    cursor.execute("SELECT uid, fname, lname, email FROM users WHERE role='admin'")
    admins = cursor.fetchall()
    mydb.commit()
    return render_template("admin.html", students=students, faculty=faculty, alumni=alumni, admins=admins, secretary=secretary)

@app.route("/admin/create_user", methods=["GET", "POST"])
def create_user():
    if "user" not in session or session["user"]["role"] != "admin":
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    if request.method == "POST":
        uid = request.form.get("uid")
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        cursor = mydb.cursor(dictionary=True)
        try:
            cursor.execute(
                "INSERT INTO users (uid, username, password, role, fname, lname, email) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (uid, username, hashed_password, role, fname, lname, email),
            )
            mydb.commit()
            if role == "student":
                cursor.execute("INSERT INTO students (uid, program, graduation_status) VALUES (%s, %s, %s)", (uid, request.form.get("program"), "active"))
            elif role == "faculty":
                cursor.execute("INSERT INTO faculty (uid) VALUES (%s)", (uid,))
            elif role == "secretary":
                cursor.execute("INSERT INTO secretary (uid) VALUES (%s)", (uid,))
            elif role == "alumni":
                degree = request.form.get("degree")
                graduation_year = request.form.get("graduation_year")
                address = request.form.get("address")
                cursor.execute("INSERT INTO alumni (uid, degree, graduation_year, address) VALUES (%s, %s, %s, %s)", (uid, degree, graduation_year, address))
            mydb.commit()
            flash("New account created", "success")
        except mysql.connector.Error as e:
            flash("Error: UID or username already exists", "error")
        mydb.commit()
    return render_template("create_user.html")

@app.route("/admin/update/<int:uid>", methods=["GET", "POST"])
def admin_update(uid):
    if "user" not in session or session["user"]["role"] != "admin":
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE uid=%s", (uid,))
    user = cursor.fetchone()
    if not user:
        mydb.commit()
        flash("User not found", "error")
        return redirect(url_for("admin"))
    role = user["role"]
    student_info = None
    alumni_info = None
    if role == "student":
        cursor.execute("SELECT * FROM students WHERE uid=%s", (uid,))
        student_info = cursor.fetchone()
    elif role == "alumni":
        cursor.execute("SELECT * FROM alumni WHERE uid=%s", (uid,))
        alumni_info = cursor.fetchone()
    if request.method == "POST":
        fname = request.form.get("fname") or user["fname"]
        lname = request.form.get("lname") or user["lname"]
        email = request.form.get("email") or user["email"]
        password = request.form.get("password")
        if password:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            cursor.execute("UPDATE users SET fname=%s, lname=%s, email=%s, password=%s WHERE uid=%s", (fname, lname, email, hashed_password, uid))
        else:
            cursor.execute("UPDATE users SET fname=%s, lname=%s, email=%s WHERE uid=%s", (fname, lname, email, uid))

        if role == "student" and student_info:
            address = request.form.get("address") or student_info["address"]
            program = request.form.get("program") or student_info["program"]
            cursor.execute("UPDATE students SET address=%s, program=%s WHERE uid=%s", (address, program, uid))
        elif role == "alumni" and alumni_info:
            address = request.form.get("address") or alumni_info["address"]
            degree = request.form.get("degree") or alumni_info["degree"]
            graduation_year = request.form.get("graduation_year") or alumni_info["graduation_year"]
            cursor.execute("UPDATE alumni SET address=%s, degree=%s, graduation_year=%s WHERE uid=%s", (address, degree, graduation_year, uid))
        
        mydb.commit()
        flash("User updated", "success")
    cursor.execute("SELECT * FROM users WHERE uid=%s", (uid,))
    user = cursor.fetchone()
    role = user["role"]
    if role == "student":
        cursor.execute("SELECT * FROM students WHERE uid=%s", (uid,))
        student_info = cursor.fetchone()
    elif role == "alumni":
        cursor.execute("SELECT * FROM alumni WHERE uid=%s", (uid,))
        alumni_info = cursor.fetchone()
    mydb.commit()
    return render_template("admin_update.html", user=user, student_info=student_info, alumni_info=alumni_info)

@app.route("/admin/reset")
def resetdb():
    if "user" not in session or session["user"]["role"] != "admin":
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    with open("schema.sql", "r") as f:
        sql = f.read()
    for command in sql.split(";"):
        command = command.strip()
        if command:
            cursor.execute(command)
    conn.commit()
    cursor.close()
    flash("Database reset!", "success")
    return redirect(url_for("admin"))

@app.route("/alumni", methods=["GET"])
def alumni():
    if "user" not in session or session["user"]["role"] != 'alumni':
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    alumni_uid = session["user"]["uid"]
    mydb.commit()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT u.uid, u.username, u.email, u.fname, u.lname, a.address, a.degree, a.graduation_year FROM users u JOIN alumni a ON u.uid = a.uid WHERE u.uid = %s", (alumni_uid,))
    alumni_info = cursor.fetchone()
    if alumni_info:
        session["user"]["fname"] = alumni_info["fname"]
        session["user"]["lname"] = alumni_info["lname"]
        session.modified = True
    cursor.execute(
        "SELECT e.course_number, c.department, c.title, e.semester, e.year, e.grade, e.credit_hours "
        "FROM enrollment e JOIN courses c ON e.course_number = c.course_number AND e.department = c.department "
        "WHERE e.uid = %s ORDER BY e.year, e.semester", (alumni_uid,)
    )
    enrollment = cursor.fetchall()
    mydb.commit()
    return render_template("alumni.html", alumni=alumni_info, enrollment=enrollment)

@app.route("/alumni/update", methods = ["GET", "POST"])
def alumni_update():
    if "user" not in session or session["user"]["role"] != 'alumni':
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    uid = session["user"]["uid"]
    password = request.form.get("password")
    email = request.form.get("email")
    address = request.form.get("address")
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("UPDATE users SET email = %s, password = %s WHERE uid = %s", (email, password, uid))
    cursor.execute("UPDATE alumni SET address = %s WHERE uid = %s", (address, uid))
    flash("Updated Sucessfully!", "success")
    mydb.commit()
    return redirect(url_for("alumni")) 

@app.route('/logout', methods=['GET'])
def logout():
  session.clear()
  return redirect("/")

# ── APPS: Applicant routes ──────────────────────────────────────────────────

import re, secrets

def _is_valid_ssn(ssn):
    return bool(re.match(r'^\d{3}-\d{2}-\d{4}$', ssn or ''))

@app.route("/applicant/register", methods=["GET", "POST"])
def applicant_register():
    if request.method == "POST":
        fname = request.form.get("fname", "").strip()
        lname = request.form.get("lname", "").strip()
        email = request.form.get("email", "").strip()
        ssn   = request.form.get("ssn", "").strip()
        address = request.form.get("address", "").strip()
        degree  = request.form.get("degree", "").strip()
        password = request.form.get("password", "")
        gre_verbal = request.form.get("gre_verbal") or None
        gre_quant  = request.form.get("gre_quant") or None
        gre_year   = request.form.get("gre_year") or None
        work_exp   = request.form.get("work_experience", "").strip()
        interests  = request.form.get("areas_of_interest", "").strip()

        if not _is_valid_ssn(ssn):
            flash("SSN must be in XXX-XX-XXXX format.", "error")
            return render_template("applicant_register.html")

        uid = int(''.join([str(secrets.randbelow(10)) for _ in range(8)]))
        hashed = generate_password_hash(password, method='pbkdf2:sha256')
        username = str(uid)
        cursor = mydb.cursor(dictionary=True)
        try:
            cursor.execute(
                "INSERT INTO users (uid,username,password,role,fname,lname,email,address) VALUES (%s,%s,%s,'applicant',%s,%s,%s,%s)",
                (uid, username, hashed, fname, lname, email, address)
            )
            cursor.execute(
                "INSERT INTO applicant (uid,ssn,degree,gre_verbal,gre_quant,gre_year,work_experience,areas_of_interest) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (uid, ssn, degree, gre_verbal, gre_quant, gre_year, work_exp, interests)
            )
            mydb.commit()

            # Save prior degrees
            deg_types = request.form.getlist("deg_type[]")
            deg_years = request.form.getlist("deg_year[]")
            deg_gpas  = request.form.getlist("deg_gpa[]")
            deg_univs = request.form.getlist("deg_univ[]")
            for dt, dy, dg, du in zip(deg_types, deg_years, deg_gpas, deg_univs):
                if dt and du:
                    cursor.execute(
                        "INSERT INTO prior_degree (uid,degree_type,year,gpa,university) VALUES (%s,%s,%s,%s,%s)",
                        (uid, dt, dy or None, dg or None, du)
                    )
            mydb.commit()
            flash(f"Registration successful! Your UID is {uid}. Please log in.", "success")
            return redirect(url_for("login"))
        except mysql.connector.Error as e:
            mydb.rollback()
            flash(f"Registration error: {e}", "error")
    return render_template("applicant_register.html")


@app.route("/applicant/dashboard")
def applicant_dashboard():
    if "user" not in session or session["user"]["role"] != "applicant":
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    uid = session["user"]["uid"]
    mydb.commit()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT a.*, u.fname, u.lname, u.email, u.address FROM applicant a JOIN users u ON a.uid=u.uid WHERE a.uid=%s", (uid,))
    applicant = cursor.fetchone()
    cursor.execute("SELECT * FROM recommendation_letter WHERE uid=%s ORDER BY id", (uid,))
    letters = cursor.fetchall()
    cursor.execute("SELECT * FROM prior_degree WHERE uid=%s ORDER BY year DESC", (uid,))
    degrees = cursor.fetchall()
    mydb.commit()
    return render_template("applicant_dashboard.html", applicant=applicant, letters=letters, degrees=degrees)


@app.route("/applicant/request_recommendation", methods=["POST"])
def request_recommendation():
    if "user" not in session or session["user"]["role"] != "applicant":
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    uid = session["user"]["uid"]
    writer_name  = request.form.get("writer_name", "").strip()
    writer_email = request.form.get("writer_email", "").strip()
    writer_title = request.form.get("writer_title", "").strip()
    institution  = request.form.get("institution_name", "").strip()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO recommendation_letter (uid,writer_name,writer_email,writer_title,institution_name) VALUES (%s,%s,%s,%s,%s)",
        (uid, writer_name, writer_email, writer_title, institution)
    )
    mydb.commit()
    flash("Recommendation letter request sent.", "success")
    return redirect(url_for("applicant_dashboard"))


@app.route("/applicant/submit_letter/<int:letter_id>", methods=["GET", "POST"])
def submit_letter(letter_id):
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM recommendation_letter WHERE id=%s", (letter_id,))
    letter = cursor.fetchone()
    if not letter:
        return "Letter not found", 404
    if letter["is_submitted"]:
        return render_template("letter_submitted.html", already=True)
    if request.method == "POST":
        content = request.form.get("letter_content", "").strip()
        cursor.execute(
            "UPDATE recommendation_letter SET letter_content=%s, is_submitted=TRUE, submission_date=NOW() WHERE id=%s",
            (content, letter_id)
        )
        mydb.commit()
        _check_completeness(letter["uid"], cursor)
        mydb.commit()
        return render_template("letter_submitted.html", already=False)
    return render_template("submit_letter.html", letter=letter)


def _check_completeness(uid, cursor):
    cursor.execute("SELECT transcript_received FROM applicant WHERE uid=%s", (uid,))
    row = cursor.fetchone()
    if not row:
        return
    cursor.execute("SELECT COUNT(*) AS cnt FROM recommendation_letter WHERE uid=%s AND is_submitted=TRUE", (uid,))
    submitted = cursor.fetchone()["cnt"]
    if row["transcript_received"] and submitted >= 1:
        cursor.execute("UPDATE applicant SET status='under review' WHERE uid=%s AND status='incomplete'", (uid,))


def _is_staff():
    return "user" in session and session["user"]["role"] in ("admin", "secretary", "faculty")


@app.route("/applications")
def applications():
    if not _is_staff():
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    mydb.commit()
    cursor = mydb.cursor(dictionary=True)
    role = session["user"]["role"]
    reviewer_uid = session["user"]["uid"]
    if role == "faculty":
        cursor.execute(
            "SELECT a.uid, u.fname, u.lname, a.degree, a.status FROM applicant a JOIN users u ON a.uid=u.uid "
            "WHERE a.status='under review' AND a.uid NOT IN (SELECT uid FROM app_review WHERE reviewer_uid=%s) "
            "ORDER BY u.lname, u.fname", (reviewer_uid,)
        )
    else:
        cursor.execute(
            "SELECT a.uid, u.fname, u.lname, a.degree, a.status FROM applicant a JOIN users u ON a.uid=u.uid ORDER BY a.status, u.lname"
        )
    applicants = cursor.fetchall()
    mydb.commit()
    return render_template("applications.html", applicants=applicants, role=role)


@app.route("/applications/transcript/<int:uid>", methods=["POST"])
def update_transcript(uid):
    if not _is_staff() or session["user"]["role"] not in ("admin", "secretary"):
        flash("Access denied.", "error")
        return redirect(url_for("applications"))
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT transcript_received FROM applicant WHERE uid=%s", (uid,))
    row = cursor.fetchone()
    if row:
        new_val = not row["transcript_received"]
        cursor.execute("UPDATE applicant SET transcript_received=%s WHERE uid=%s", (new_val, uid))
        mydb.commit()
        _check_completeness(uid, cursor)
        mydb.commit()
    return redirect(url_for("applications"))


@app.route("/applications/review/<int:uid>", methods=["GET", "POST"])
def review_applicant(uid):
    if not _is_staff() or session["user"]["role"] not in ("admin", "secretary", "faculty"):
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    reviewer_uid = session["user"]["uid"]
    mydb.commit()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT a.*, u.fname, u.lname, u.email FROM applicant a JOIN users u ON a.uid=u.uid WHERE a.uid=%s", (uid,))
    applicant = cursor.fetchone()
    if not applicant:
        flash("Applicant not found.", "error")
        return redirect(url_for("applications"))
    cursor.execute("SELECT * FROM prior_degree WHERE uid=%s", (uid,))
    degrees = cursor.fetchall()
    cursor.execute("SELECT * FROM recommendation_letter WHERE uid=%s", (uid,))
    letters = cursor.fetchall()
    cursor.execute("SELECT * FROM app_review WHERE uid=%s AND reviewer_uid=%s", (uid, reviewer_uid))
    existing_review = cursor.fetchone()
    cursor.execute("SELECT u.uid, u.fname, u.lname FROM users u JOIN faculty f ON u.uid=f.uid ORDER BY u.lname")
    faculty_list = cursor.fetchall()
    if request.method == "POST":
        rating = request.form.get("rating")
        deficiency = request.form.get("deficiency_courses", "").strip()
        reasons = ",".join(request.form.getlist("reject_reasons"))
        comment = request.form.get("comment", "").strip()
        advisor = request.form.get("recommended_advisor") or None
        if existing_review:
            cursor.execute(
                "UPDATE app_review SET rating=%s,deficiency_courses=%s,reject_reasons=%s,comment=%s,recommended_advisor=%s WHERE id=%s",
                (rating, deficiency, reasons, comment, advisor, existing_review["id"])
            )
        else:
            cursor.execute(
                "INSERT INTO app_review (uid,reviewer_uid,rating,deficiency_courses,reject_reasons,comment,recommended_advisor) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (uid, reviewer_uid, rating, deficiency, reasons, comment, advisor)
            )
        # Also handle per-letter ratings
        for letter in letters:
            lr = request.form.get(f"letter_rating_{letter['id']}")
            lg = request.form.get(f"letter_generic_{letter['id']}")
            lc = request.form.get(f"letter_credible_{letter['id']}")
            if lr:
                cursor.execute(
                    "UPDATE recommendation_letter SET rating=%s, is_generic=%s, is_credible=%s WHERE id=%s",
                    (lr, lg, lc, letter["id"])
                )
        mydb.commit()
        flash("Review submitted.", "success")
        return redirect(url_for("applications"))
    mydb.commit()
    return render_template("review_applicant.html", applicant=applicant, degrees=degrees,
                           letters=letters, existing_review=existing_review, faculty_list=faculty_list)


@app.route("/applications/decision/<int:uid>", methods=["GET", "POST"])
def final_decision(uid):
    if not _is_staff() or session["user"]["role"] not in ("admin", "secretary"):
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    mydb.commit()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT a.*, u.fname, u.lname FROM applicant a JOIN users u ON a.uid=u.uid WHERE a.uid=%s", (uid,))
    applicant = cursor.fetchone()
    cursor.execute("SELECT r.*, u.fname, u.lname FROM app_review r JOIN users u ON r.reviewer_uid=u.uid WHERE r.uid=%s", (uid,))
    reviews = cursor.fetchall()
    if request.method == "POST":
        decision = request.form.get("decision")
        if decision in ("admitted", "admitted_with_aid", "rejected"):
            cursor.execute("UPDATE applicant SET status=%s WHERE uid=%s", (decision, uid))
            mydb.commit()
            flash(f"Decision recorded: {decision}.", "success")
            return redirect(url_for("applications"))
    mydb.commit()
    return render_template("final_decision.html", applicant=applicant, reviews=reviews)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
