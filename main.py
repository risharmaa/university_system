# Active: 1773861604957@@regs26-sharma.ca1y0o4q8i1b.us-east-1.rds.amazonaws.com@3306@university
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
    host="regs26-sharma.ca1y0o4q8i1b.us-east-1.rds.amazonaws.com",
    user="admin",
    password="14998riya",
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
    cursor.execute("SELECT u.uid, u.fname, u.lname, u.email, s.program, u.address, s.graduation_status FROM users u JOIN students s ON u.uid = s.uid")
    students = cursor.fetchall()

    cursor.execute("SELECT u.uid, u.fname, u.lname, u.email, u.address FROM users u JOIN faculty f ON u.uid = f.uid")
    faculty = cursor.fetchall()

    cursor.execute("SELECT u.uid, u.fname, u.lname, u.email , u.address FROM users u JOIN secretary s on u.uid = s.uid")
    secretary = cursor.fetchall()

    cursor.execute("SELECT u.uid, u.fname, u.lname, a.degree, a.graduation_year, u.address FROM users u JOIN alumni a ON u.uid = a.uid")
    alumni = cursor.fetchall()

    cursor.execute("SELECT uid, fname, lname, email, address FROM users WHERE role='admin'")
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
        address = request.form.get("address")
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        cursor = mydb.cursor(dictionary=True)
        try:
            cursor.execute(
                "INSERT INTO users (uid, username, password, role, fname, lname, email, address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (uid, username, hashed_password, role, fname, lname, email, address),
            )
            mydb.commit()
            if role == "student":
                cursor.execute("INSERT INTO students (uid, program, graduation_status) VALUES (%s, %s, %s)", (uid, request.form.get("program"), "active"))
            elif role == "faculty":
                cursor.execute("INSERT INTO faculty (uid, cac, reviewer, advisor) VALUES (%s, %s, %s, %s)", (uid, False, False, False))
            elif role == "secretary":
                cursor.execute("INSERT INTO secretary (uid) VALUES (%s)", (uid,))
            elif role == "alumni":
                degree = request.form.get("degree")
                graduation_year = request.form.get("graduation_year")
                address = request.form.get("address")
                cursor.execute("INSERT INTO alumni (uid, degree, graduation_year) VALUES (%s, %s, %s, %s)", (uid, degree, graduation_year))
            mydb.commit()
            flash("New account created", "success")
        except mysql.connector.Error as e:
            flash("Error: UID or username already exists", "error")
        mydb.commit()
    return render_template("create_user.html")


@app.route("/student")
def student():
    if "user" not in session or session["user"]["role"] != "student":
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    uid = session["user"]["uid"]
    mydb.commit()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT s.uid, u.address, s.program, u.fname, u.lname, u.email FROM students s JOIN users u ON s.uid = u.uid WHERE s.uid = %s", (uid,))
    info = cursor.fetchone()
    if info:
        session["user"]["fname"] = info["fname"]
        session["user"]["lname"] = info["lname"]
        session.modified = True
    cursor.execute("SELECT e.course_number, c.title, e.semester, e.year, e.grade, e.credit_hours FROM enrollment e JOIN courses c ON e.course_number = c.course_number AND e.department = c.department WHERE e.uid = %s", (uid,))
    enrollment = cursor.fetchall()
    
    cursor.execute("SELECT c.title, c.department, e.grade FROM enrollment e JOIN courses c ON e.course_number = c.course_number AND e.department = c.department WHERE e.uid = %s", (uid,))
    courses = cursor.fetchall()
    phd_suggestions = []
    if info['program'] == 'MS':
        cyber = ['Security 1', 'Cryptography', 'Network Security']
        if any (c['title'] in cyber and c['grade'] in ['A', 'B'] for c in courses):
            phd_suggestions.append('Cybersecurity')
        machine = ['Machine Learning']
        if any (c['title'] in machine and c['grade'] in ['A', 'B'] for c in courses):
            phd_suggestions.append('Machine Learning')
        cloud = ['Cloud Computing']
        if any (c['title'] in cloud and c['grade'] in ['A', 'B'] for c in courses):
            phd_suggestions.append('Cloud Computing')
        ai = ['AI']
        if any (c['title'] in ai and c['grade'] in ['A', 'B'] for c in courses):
            phd_suggestions.append("AI")
    # --- Added: compute GPA, credits, and checklist for dashboard stats ---
    GRADE_PTS = {"A":4.0,"A-":3.7,"B+":3.3,"B":3.0,"B-":2.7,"C+":2.3,"C":2.0,"F":0.0}
    completed = [e for e in enrollment if e['grade'] not in ('IP', None, '')]
    total_ch   = sum(e['credit_hours'] for e in completed)
    gpa = round(sum(GRADE_PTS.get(e['grade'],0)*e['credit_hours'] for e in completed)/max(total_ch,1), 2)

    # GPA ring color and fill percentage (capped at 100)
    gpa_color = "#28a745" if gpa >= 3.5 else ("#ffc107" if gpa >= 3.0 else "#dc3545")
    gpa_pct   = min(int(gpa / 4.0 * 100), 100)

    # Program thresholds
    is_ms      = info['program'] == 'MS'
    min_gpa    = 3.0 if is_ms else 3.5
    credits_req = 30  if is_ms else 36
    max_below_b = 2   if is_ms else 1
    credits_pct = min(int(total_ch / credits_req * 100), 100)

    # Graduation readiness checklist items
    below_b_grades = {"B-","C+","C","F"}
    below_b_count  = sum(1 for e in completed if e['grade'] in below_b_grades)
    taken_nums     = {e['course_number'] for e in completed}
    core_done      = {6212,6221,6461}.issubset(taken_nums)
    checklist = [
        {"label": f"GPA ≥ {min_gpa}  (yours: {gpa})",          "pass": gpa >= min_gpa},
        {"label": f"Credits ≥ {credits_req}  (yours: {total_ch})", "pass": total_ch >= credits_req},
        {"label": f"Below-B grades ≤ {max_below_b}  (yours: {below_b_count})", "pass": below_b_count <= max_below_b},
    ]
    if is_ms:
        checklist.insert(2, {"label": "Core courses (6212, 6221, 6461)", "pass": core_done})
    # --- End: stats block ---

    uid = session["user"]["uid"]
    cursor.execute("SELECT * FROM users WHERE uid = %s", (uid,))
    current_user = cursor.fetchone()
    return render_template("student.html", student=info, enrollment=enrollment,
                           phd_suggestions=phd_suggestions, gpa=gpa,
                           gpa_color=gpa_color, gpa_pct=gpa_pct,
                           total_credits=total_ch, credits_req=credits_req,
                           credits_pct=credits_pct, checklist=checklist, current_user=current_user)

@app.route("/student/info", methods=["POST"])
def student_info():
    if "user" not in session or session["user"]["role"] != "student":
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    uid = session["user"]["uid"]
    address = request.form.get("address")
    email = request.form.get("email")
    password = request.form.get("password")
    cursor = mydb.cursor(dictionary=True)
    if address:
        cursor.execute("UPDATE users SET address=%s WHERE uid=%s", (address, uid))
    if email:
        cursor.execute("UPDATE users SET email=%s WHERE uid=%s", (email, uid))
    if password:
        cursor.execute("UPDATE users SET password=%s WHERE uid=%s", (password, uid))
    mydb.commit()
    flash("Information updated")
    return redirect(url_for('student'))

@app.route("/form1", methods=["GET", "POST"])
def form1():
    if "user" not in session or session["user"]["role"] != "student":
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    user = session["user"]
    uid = user["uid"]
    cursor = mydb.cursor(dictionary=True)
    cursor.execute(
        "SELECT course_number, department, title, credits FROM courses ORDER BY department, course_number")
    courses = cursor.fetchall()

    cursor.execute("SELECT * FROM students WHERE uid = %s", (uid,))
    student = cursor.fetchone()
    if request.method == "GET":
        cursor.execute("SELECT * FROM form WHERE uid = %s", (uid,))
        existing_form = cursor.fetchone()
        existing_courses = []
        if existing_form:
            cursor.execute(
                "SELECT course_number, department FROM form_courses WHERE form_id = %s",
                (existing_form["form_id"],)
            )
            rows = cursor.fetchall()
            existing_courses = [r["course_number"] for r in rows]
        mydb.commit()
        return render_template("form1.html", user=user, courses=courses, student=student,
                               existing_form=existing_form, existing_courses=existing_courses)

    # POST - parse selected courses (skip blanks, remove duplicates)
    selected = []
    for i in range(12):
        val = request.form.get(f"course_{i}", "").strip()
        if val:
            try:
                num = int(val)
                if num not in selected:
                    selected.append(num)
            except ValueError:
                pass

    if not selected:
        flash("Please select at least one course.", "error")
        return redirect(url_for("form1"))

    # Validate selected courses exist in the catalog
    valid_nums = {c["course_number"] for c in courses}
    bad = [n for n in selected if n not in valid_nums]
    if bad:
        flash(f"Unrecognized course number(s): {bad}", "error")
        return redirect(url_for("form1"))

    # Load program requirements from DB
    program = student["program"] or "MS"
    cursor.execute("SELECT * FROM programs WHERE program_name = %s", (program,))
    prog = cursor.fetchone()
    errors = []

    if program == "MS" and prog:
        # Check all 3 core courses are included
        core_nums = [int(c.strip().split()[-1]) for c in (prog["core_courses"] or "").split(",") if c.strip()]
        missing = [n for n in core_nums if n not in selected]
        if missing:
            errors.append(f"Missing required core course(s): {missing}")
        # Check at most max_outside_courses non-CSCI courses
        outside = sum(1 for n in selected
                      for c in courses if c["course_number"] == n and c["department"] != "CSCI")
        max_out = prog["max_outside_courses"] or 2
        if outside > max_out:
            errors.append(f"Too many non-CSCI courses ({outside}); maximum allowed is {max_out}.")

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("form1"))

    # Save to DB: one form per student (form_id = uid)
    form_id = uid
    try:
        cursor.execute("DELETE FROM form_courses WHERE form_id = %s", (form_id,))
        cursor.execute("DELETE FROM form WHERE uid = %s", (uid,))
        cursor.execute(
            "INSERT INTO form (form_id, uid, program_type) VALUES (%s, %s, %s)",
            (form_id, uid, program)
        )
        for num in selected:
            cursor.execute(
                "INSERT INTO form_courses (form_id, course_number, department) VALUES (%s, %s, %s)",
                (form_id, num, "CSCI")
            )
        mydb.commit()
        flash("Form 1 submitted successfully!", "success")
    except mysql.connector.Error as e:
        mydb.rollback()
        flash(f"Error saving Form 1: {e}", "error")
    mydb.commit()
    return redirect(url_for("student"))


# Grade point values used for GPA calculation
GRADE_POINTS = {"A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0,
                "B-": 2.7, "C+": 2.3, "C": 2.0, "F": 0.0}

# Grades considered "below B" per program requirements
BELOW_B = {"B-", "C+", "C", "F"}

def run_audit(uid, program, cursor):
    """Check all graduation requirements for a student. Returns a dict of results."""

    # Load program requirements from DB (so rules can change without code changes)
    cursor.execute("SELECT * FROM programs WHERE program_name = %s", (program,))
    prog = cursor.fetchone()
    if not prog:
        return {"error": "Program not found in database."}

    # Fetch completed enrollment rows (exclude IP — in progress courses don't count)
    cursor.execute(
        "SELECT e.course_number, c.department, e.grade, e.credit_hours "
        "FROM enrollment e JOIN courses c ON e.course_number = c.course_number AND e.department = c.department "
        "WHERE e.uid = %s AND e.grade != 'IP'", (uid,)
    )
    rows = cursor.fetchall()

    # Calculate GPA and totals from completed courses
    total_credits, gpa_points, below_b_count, outside_cs = 0, 0.0, 0, 0
    for r in rows:
        pts = GRADE_POINTS.get(r["grade"], 0.0)
        total_credits += r["credit_hours"]
        gpa_points += pts * r["credit_hours"]
        if r["grade"] in BELOW_B:
            below_b_count += 1
        if r["department"] != "CSCI":
            outside_cs += 1
    gpa = round(gpa_points / total_credits, 2) if total_credits > 0 else 0.0

    # Check each requirement and store pass/fail + detail message
    results = {}
    results["gpa"] = {"pass": gpa >= prog["min_gpa"],
                      "detail": f"GPA: {gpa:.2f} (need ≥ {prog['min_gpa']})"}
    results["credits"] = {"pass": total_credits >= prog["credits_required"],
                          "detail": f"Credits: {total_credits} (need ≥ {prog['credits_required']})"}
    results["below_b"] = {"pass": below_b_count <= prog["max_grades_below_B"],
                          "detail": f"Grades below B: {below_b_count} (max {prog['max_grades_below_B']})"}
    results["suspended"] = {"pass": below_b_count < 3,
                            "detail": "Academic suspension: 3+ grades below B" if below_b_count >= 3 else "Not suspended"}

    # MS-specific checks
    if program == "MS":
        # Parse core course numbers as integers (e.g. 'CSCI 6212' -> 6212)
        # so they match the integer course_number values stored in enrollment
        core = [int(c.strip().split()[-1]) for c in (prog["core_courses"] or "").split(",") if c.strip()]
        taken = {r["course_number"] for r in rows if r["grade"] != "F"}
        missing_core = [c for c in core if c not in taken]
        results["core"] = {"pass": len(missing_core) == 0,
                           "detail": f"Core courses missing: {missing_core}" if missing_core else "All core courses completed"}
        results["outside"] = {"pass": outside_cs <= prog["max_outside_courses"],
                              "detail": f"Outside CS courses: {outside_cs} (max {prog['max_outside_courses']})"}

    # PhD-specific checks
    if program == "PhD":
        cs_credits = sum(r["credit_hours"] for r in rows if r["department"] == "CSCI")
        results["cs_credits"] = {"pass": cs_credits >= prog["credits_required_cs"],
                                 "detail": f"CS credits: {cs_credits} (need ≥ {prog['credits_required_cs']})"}

    # Check Form 1 submitted and advisor approved
    cursor.execute("SELECT form_id, advisor_approval FROM form WHERE uid = %s", (uid,))
    form = cursor.fetchone()
    form_ok = form is not None
    approved_ok = form and form["advisor_approval"] == "approved"
    results["form1_submitted"] = {"pass": form_ok, "detail": "Form 1 submitted" if form_ok else "Form 1 not submitted"}
    results["form1_approved"] = {"pass": bool(approved_ok), "detail": "Advisor approved Form 1" if approved_ok else "Advisor has not approved Form 1"}

    # Overall: student is cleared only if every check passes
    results["cleared"] = all(v["pass"] for k, v in results.items() if k != "suspended")
    results["gpa_value"] = gpa
    return results



# Added: Graduation application route
@app.route("/graduation", methods=["GET", "POST"])
def graduation():
    # Only students can apply for graduation
    if "user" not in session or session["user"]["role"] != "student":
        flash("Access denied.", "error")
        return redirect(url_for("login"))

    uid = session["user"]["uid"]
    cursor = mydb.cursor(dictionary=True)
    # Get student's program (MS or PhD)
    cursor.execute(
        "SELECT s.program, s.graduation_status, u.fname, u.lname "
        "FROM students s JOIN users u ON s.uid = u.uid WHERE s.uid = %s", (uid,)
    )
    student = cursor.fetchone()

    if not student:
        mydb.commit()
        flash("Student record not found.", "error")
        return redirect(url_for("student"))

    audit = None
    if request.method == "POST":
        # Run the audit against all graduation requirements
        audit = run_audit(uid, student["program"], cursor)

        # Check suspension first - 3+ grades below B = academic suspension (spec requirement)
        if audit.get("suspended") and not audit["suspended"]["pass"]:
            cursor.execute(
                "UPDATE students SET graduation_status = 'suspended' WHERE uid = %s", (uid,)
            )
            mydb.commit()
            flash("You have been placed under academic suspension (3+ grades below B).", "error")
        elif audit.get("cleared"):
            # Update graduation status to cleared_for_graduation
            cursor.execute(
                "UPDATE students SET graduation_status = 'cleared_for_graduation' WHERE uid = %s", (uid,)
            )
            mydb.commit()
            flash("Congratulations! You have been cleared for graduation.", "success")
        else:
            flash("You do not yet meet all graduation requirements. See details below.", "error")

    mydb.commit()
    return render_template("graduation.html", student=student, audit=audit)

def _is_secretary_session():
    if "user" not in session:
        return False
    role = session["user"].get("role", "").lower()
    if role == "admin":
        return True
    if role != "secretary":
        return False
    cursor = mydb.cursor(dictionary=True)
    row = cursor.execute(
        "SELECT 1 FROM secretary WHERE uid = %s", (session["user"]["uid"],)
    )
    row = cursor.fetchone()
    return row is not None

@app.route("/secretary")
def secretary():
    if not _is_secretary_session():
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    uid = session["user"]["uid"]
    mydb.commit()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT fname, lname FROM users WHERE uid = %s", (uid,))
    sec_user = cursor.fetchone()
    if sec_user:
        session["user"]["fname"] = sec_user["fname"]
        session["user"]["lname"] = sec_user["lname"]
        session.modified = True
    q = request.args.get("q", "").strip()
    sql = (
        "SELECT u.uid, u.fname, u.lname, s.program, s.graduation_status, s.advisor_id, "
        "af.fname AS advisor_fname, af.lname AS advisor_lname "
        "FROM users u JOIN students s ON u.uid = s.uid "
    )
    if q:
        like = f"%{q}%"
        sql += (
            " WHERE CAST(u.uid AS TEXT) LIKE %s OR u.fname LIKE %s OR u.lname LIKE %s "
            "OR (u.fname || ' ' || u.lname) LIKE %s"
        )
        sql += " ORDER BY u.lname, u.fname"
        cursor.execute(sql, (like, like, like, like))
        rows = cursor.fetchall()
    else:
        sql += " ORDER BY u.lname, u.fname"
        cursor.execute(sql)
        rows = cursor.fetchall()
    uid = session["user"]["uid"]
    cursor.execute("SELECT * FROM users WHERE uid = %s", (uid,))
    current_user = cursor.fetchone()
    mydb.commit()
    return render_template("secretary.html", students=rows, query=q, current_user=current_user)


@app.route("/secretary/student/<int:uid>")
def secretary_student(uid):
    if not _is_secretary_session():
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    mydb.commit()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute(
        "SELECT s.*, u.username, u.fname, u.lname, u.email "
        "FROM students s JOIN users u ON s.uid = u.uid WHERE s.uid = %s",
        (uid,),
    )
    student = cursor.fetchone()
    if not student:
        mydb.commit()
        flash("Student not found.", "error")
        return redirect(url_for("secretary"))
    cursor.execute(
        "SELECT e.course_number, e.department, c.title, e.semester, e.year, e.grade, e.credit_hours "
        "FROM enrollment e JOIN courses c ON e.course_number = c.course_number AND e.department = c.department "
        "WHERE e.uid = %s ORDER BY e.year, e.semester",
        (uid,),
    )
    enrollment = cursor.fetchall()
    cursor.execute(
        "SELECT u.uid, u.fname, u.lname FROM users u "
        "JOIN faculty f ON u.uid = f.uid ORDER BY u.lname, u.fname"
    )
    faculty = cursor.fetchall()
    mydb.commit()
    return render_template(
        "secretary_student.html",
        student=student,
        enrollment=enrollment,
        faculty=faculty,
        default_grad_year=datetime.now().year,
    )


@app.route("/secretary/assign_advisor", methods=["POST"])
def secretary_assign_advisor():
    if not _is_secretary_session():
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    student_uid = request.form.get("student_uid", type=int)
    advisor_uid = request.form.get("advisor_id", type=int)
    if not student_uid or not advisor_uid:
        flash("Missing student or advisor.", "error")
        return redirect(url_for("secretary"))
    cursor = mydb.cursor(dictionary=True)
    cursor.execute(
        "SELECT 1 FROM faculty WHERE uid = %s", (advisor_uid,)
    )
    fac = cursor.fetchone()
    if not fac:
        mydb.commit()
        flash("Invalid advisor.", "error")
        return redirect(url_for("secretary_student", uid=student_uid))
    cursor.execute(
        "UPDATE students SET advisor_id = %s WHERE uid = %s",
        (advisor_uid, student_uid),
    )
    mydb.commit()
    flash("Advisor updated.", "success")
    return redirect(url_for("secretary_student", uid=student_uid))


@app.route("/secretary/graduate", methods=["POST"])
def secretary_graduate():
    if not _is_secretary_session():
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    student_uid = request.form.get("student_uid", type=int)
    degree = (request.form.get("degree") or "").strip() or "MS"
    graduation_year = request.form.get("graduation_year", type=int)
    if not student_uid or not graduation_year:
        flash("Missing data.", "error")
        return redirect(url_for("secretary"))
    cursor = mydb.cursor(dictionary=True)
    cursor.execute(
        "SELECT s.*, u.fname, u.lname FROM students s JOIN users u ON s.uid = u.uid "
        "WHERE s.uid = %s",
        (student_uid,),
    )
    st = cursor.fetchone()
    if not st:
        mydb.commit()
        flash("Student not found.", "error")
        return redirect(url_for("secretary"))
    if (st["graduation_status"] or "") != "cleared_for_graduation":
        mydb.commit()
        flash("Student is not cleared for graduation.", "error")
        return redirect(url_for("secretary_student", uid=student_uid))
    cursor.execute("SELECT 1 FROM alumni WHERE uid = %s", (student_uid,))
    dup = cursor.fetchone()
    if dup:
        mydb.commit()
        flash("Already recorded as alumni.", "error")
        return redirect(url_for("secretary_student", uid=student_uid))
    try:
        cursor.execute(
            "DELETE FROM form_courses WHERE form_id IN "
            "(SELECT form_id FROM form WHERE uid = %s)",
            (student_uid,),
        )
        cursor.execute("DELETE FROM form WHERE uid = %s", (student_uid,))
        # Do NOT delete enrollment - spec says keep enrollment history intact
        # so alumni can view their transcript and re-enroll in future
        cursor.execute(
            "INSERT INTO alumni (uid, degree, graduation_year) VALUES (%s, %s, %s)",
            (student_uid, degree, graduation_year),
        )
        cursor.execute("UPDATE users SET role = 'alumni' WHERE uid = %s", (student_uid,))
        cursor.execute("DELETE FROM students WHERE uid = %s", (student_uid,))
        mydb.commit()
    except mysql.connector.Error as e:
        mydb.rollback()
        cursor.close()
        flash(f"Could not record graduation: {e}", "error")
        return redirect(url_for("secretary_student", uid=student_uid))
    mydb.commit()
    flash("Graduation recorded; user is now alumni.", "success")
    return redirect(url_for("secretary"))



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
            address = request.form.get("address") or user["address"]
            program = request.form.get("program") or student_info["program"]
            cursor.execute("UPDATE users SET address=%s WHERE uid=%s", (address, uid))
            cursor.execute("UPDATE students SET program=%s WHERE uid=%s", (program, uid))
        elif role == "alumni" and alumni_info:
            address = request.form.get("address") or user["address"]
            degree = request.form.get("degree") or alumni_info["degree"]
            graduation_year = request.form.get("graduation_year") or alumni_info["graduation_year"]
            cursor.execute("UPDATE users SET address=%s WHERE uid=%", (address, uid))
            cursor.execute("UPDATE alumni SET degree=%s, graduation_year=%s WHERE uid=%s", (degree, graduation_year, uid))
        
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

@app.route("/reset")
def resetdb():
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
    cursor.execute("SELECT u.uid, u.username, u.email, u.fname, u.lname, u.address, a.degree, a.graduation_year FROM users u JOIN alumni a ON u.uid = a.uid WHERE u.uid = %s", (alumni_uid,))
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
