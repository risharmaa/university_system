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
    cursor.execute("SELECT e.course_number, c.title, e.semester, e.year, e.grade, e.credit_hours, c.credits FROM enrollment e JOIN courses c ON e.course_number = c.course_number AND e.department = c.department WHERE e.uid = %s", (uid,))
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
    total_ch   = sum(e['credits'] or e['credit_hours'] or 0 for e in completed)
    gpa = round(sum(GRADE_PTS.get(e['grade'],0)*(e['credits'] or e['credit_hours'] or 0) for e in completed)/max(total_ch,1), 2)

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
    thesis = request.form.get("thesis")
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
            "INSERT INTO form (form_id, uid, program_type, thesis) VALUES (%s, %s, %s, %s)",
            (form_id, uid, program, thesis if program == 'PhD' else None)
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
    advisor_id = request.args.get("advisor_id")
    degree = request.args.get("degree")
    year = request.args.get("year")
    sid = request.args.get("sid")
    sql = (
        "SELECT u.uid, u.fname, u.lname, "
        "s.program, s.graduation_status, s.advisor_id, "
        "adv.fname AS advisor_fname, adv.lname AS advisor_lname "
        "FROM users u "
        "JOIN students s ON u.uid = s.uid "
        "LEFT JOIN users adv ON s.advisor_id = adv.uid"
    )
    filters = []
    params = []
    if q:
        like = f"%{q}%"
        filters.append("(CAST(u.uid AS TEXT) LIKE %s OR u.fname LIKE %s OR u.lname LIKE %s "
            "OR (u.fname || ' ' || u.lname) LIKE %s"
        )
        params.extend([like, like, like, like])
    if advisor_id:
        filters.append("s.advisor_id = %s")
        params.append(advisor_id)
    if degree:
        filters.append("s.program = %s")
        params.append(degree)
    if year:
        filters.append("s.enrollment_year = %s")
        params.append(year)
    if sid:
        filters.append("u.uid = %s")
        params.append(sid)
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY u.lname, u.fname"
    cursor.execute(sql, tuple(params))
    rows = cursor.fetchall()
    uid = session["user"]["uid"]
    cursor.execute("SELECT * FROM users WHERE uid = %s", (uid,))
    current_user = cursor.fetchone()

    cursor.execute("SELECT u.uid, u.fname, u.lname FROM faculty f JOIN users u ON f.uid = u.uid WHERE f.advisor = 1")
    advisors = cursor.fetchall()
    mydb.commit()
    return render_template("secretary.html", students=rows, query=q, current_user=current_user, advisors=advisors, selected_advisor=advisor_id, selected_degree=degree)


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

@app.route("/faculty")
def faculty():
    # Only faculty users can access this page
    if "user" not in session or session["user"]["role"] != "faculty":
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    uid = session["user"]["uid"]
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT advisor, reviewer, cac FROM faculty WHERE uid = %s", (uid,))
    fac_role = cursor.fetchone()
    if not fac_role:
        flash("Access denied", "error")
        return redirect(url_for("login"))
    
    roles = []
    if fac_role["advisor"]:
        roles.append("advisor")
    if fac_role["reviewer"]:
        roles.append("reviewer")
    if fac_role["cac"]:
        roles.append("cac")

    # if not roles:
    #     flash("No faculty role assigned", "error")
    #     return redirect(url_for("login"))
    session["faculty_roles"] = roles
    return render_template("faculty_roles.html", roles=roles)

@app.route("/faculty/advisor")
def facultyadvisor():
    if "user" not in session or session["user"]["role"] != "faculty":
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    uid = session["user"]["uid"]
    if "faculty_roles" not in session or "advisor" not in session["faculty_roles"]:
        flash("Access denied", "error")
        return redirect(url_for("faculty"))
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT fname, lname FROM users WHERE uid = %s", (uid,))
    fac_user = cursor.fetchone()
    if fac_user:
        session["user"]["fname"] = fac_user["fname"]
        session["user"]["lname"] = fac_user["lname"]
        session.modified = True
    # Fetch all students assigned to this faculty advisor
    search = request.args.get('search')
    if search:
        cursor.execute(
            "SELECT s.uid, u.fname, u.lname, s.program, s.graduation_status "
            "FROM students s JOIN users u ON s.uid = u.uid "
            "WHERE s.advisor_id = %s AND s.uid = %s ORDER BY u.lname, u.fname",
            (uid, search)
        )
    else:
        cursor.execute(
            "SELECT s.uid, u.fname, u.lname, s.program, s.graduation_status "
            "FROM students s JOIN users u ON s.uid = u.uid "
            "WHERE s.advisor_id = %s ORDER BY u.lname, u.fname",
            (uid,)
        )
    advisees = cursor.fetchall()
    cursor.execute("SELECT * FROM users WHERE uid = %s", (uid,))
    current_user = cursor.fetchone()
    mydb.commit()
    return render_template("facultyadvisor.html", advisees=advisees, current_user = current_user)


@app.route("/faculty/advisee/<int:uid>")
def faculty_advisee(uid):
    # Only the assigned faculty advisor can view this advisee
    if "user" not in session or session["user"]["role"] != "faculty":
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    if "faculty_roles" not in session or "advisor" not in session["faculty_roles"]:
        flash("Access denied", "error")
        return redirect(url_for("faculty"))
    faculty_uid = session["user"]["uid"]
    cursor = mydb.cursor(dictionary=True)
    # Confirm the student belongs to this advisor (prevents accessing other advisors' students)
    cursor.execute(
        "SELECT s.uid, s.program, s.graduation_status, s.advisor_id, "
        "u.fname, u.lname, u.email "
        "FROM students s JOIN users u ON s.uid = u.uid "
        "WHERE s.uid = %s AND s.advisor_id = %s",
        (uid, faculty_uid)
    )
    student = cursor.fetchone()
    if not student:
        mydb.commit()
        flash("Advisee not found.", "error")
        return redirect(url_for("faculty"))
    # Fetch the student's enrollment history (transcript)
    cursor.execute(
        "SELECT e.course_number, e.department, c.title, e.semester, e.year, e.grade, e.credit_hours "
        "FROM enrollment e JOIN courses c ON e.course_number = c.course_number AND e.department = c.department "
        "WHERE e.uid = %s ORDER BY e.year, e.semester",
        (uid,)
    )
    enrollment = cursor.fetchall()
    # Fetch Form 1 if submitted, to show approval status and planned courses
    cursor.execute(
        "SELECT f.form_id, f.advisor_approval, f.thesis, f.program_type FROM form f WHERE f.uid = %s", (uid,)
    )
    form_row = cursor.fetchone()
    form_courses = []
    if form_row:
        cursor.execute(
            "SELECT fc.course_number, c.title, c.department "
            "FROM form_courses fc LEFT JOIN courses c ON fc.course_number = c.course_number AND fc.department = c.department "
            "WHERE fc.form_id = %s ORDER BY fc.course_number",
            (form_row["form_id"],)
        )
        form_courses = cursor.fetchall()
    mydb.commit()
    return render_template("faculty_advisee.html", student=student, enrollment=enrollment, form_row=form_row, form_courses=form_courses)



# Added: Route for faculty to approve a student's Form 1
@app.route("/faculty/advisee/<int:uid>/approve", methods=["POST"])
def faculty_approve_form1(uid):
    # Only faculty can approve Form 1
    if "user" not in session or session["user"]["role"] != "faculty":
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    if "faculty_roles" not in session or "advisor" not in session["faculty_roles"]:
        flash("Access denied", "error")
        return redirect(url_for("faculty"))

    faculty_uid = session["user"]["uid"]
    cursor = mydb.cursor(dictionary=True)

    # Make sure this student is actually assigned to this advisor
    cursor.execute(
        "SELECT uid FROM students WHERE uid = %s AND advisor_id = %s",
        (uid, faculty_uid)
    )
    student = cursor.fetchone()

    if not student:
        mydb.commit()
        flash("Student not found or not your advisee.", "error")
        return redirect(url_for("faculty"))

    # Set advisor_approval to 'approved' on the student's Form 1
    cursor.execute(
        "UPDATE form SET advisor_approval = 'approved' WHERE uid = %s",
        (uid,)
    )
    # Set registration_hold to false (allow students to register)
    cursor.execute("UPDATE students SET registration_hold = False WHERE uid = %s", (uid,))
    mydb.commit()

    flash("Form 1 approved successfully.", "success")
    return redirect(url_for("faculty_advisee", uid=uid))


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
        gre_verbal    = request.form.get("gre_verbal") or None
        gre_quant     = request.form.get("gre_quant") or None
        gre_year      = request.form.get("gre_year") or None
        work_exp      = request.form.get("work_experience", "").strip()
        interests     = request.form.get("areas_of_interest", "").strip()

        if not _is_valid_ssn(ssn):
            flash("SSN must be in XXX-XX-XXXX format.", "error")
            return render_template("applicant_register.html")

        uid = int(''.join([str(secrets.randbelow(10)) for _ in range(8)]))
        hashed = generate_password_hash("pass", method='pbkdf2:sha256')
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
            return render_template("applicant_registered.html", uid=uid)
        except mysql.connector.Error as e:
            mydb.rollback()
            flash(f"Registration error: {e}", "error")
    return render_template("applicant_register.html")


@app.route("/applicant/dashboard", methods=["GET", "POST"])
def applicant_dashboard():
    if "user" not in session or session["user"]["role"] != "applicant":
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    uid = session["user"]["uid"]
    mydb.commit()
    cursor = mydb.cursor(dictionary=True)
    if request.method == "POST":
        fname = request.form.get("fname", "").strip()
        lname = request.form.get("lname", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()
        degree  = request.form.get("degree", "").strip()
        gre_verbal    = request.form.get("gre_verbal") or None
        gre_quant     = request.form.get("gre_quant") or None
        gre_year      = request.form.get("gre_year") or None
        work_experience      = request.form.get("work_experience", "").strip()
        areas_of_interest     = request.form.get("areas_of_interest", "").strip()
        try:
           cursor.execute("UPDATE users SET fname=%s, lname=%s, email=%s, address=%s WHERE uid=%s", (fname, lname, email, address, uid))
           cursor.execute("UPDATE applicant SET degree=%s, gre_verbal=%s, gre_quant=%s, gre_year=%s, work_experience=%s, areas_of_interest=%s WHERE uid=%s", (degree, gre_verbal, gre_quant, gre_year, work_experience, areas_of_interest, uid))
           mydb.commit()
           flash("Information updated successfully", "success")
        except mysql.connector.Error as e:
           mydb.rollback()
           flash("Error updating information", "error")
        return redirect(url_for("applicant_dashboard"))
    cursor.execute("SELECT a.*, u.fname, u.lname, u.email, u.address FROM applicant a JOIN users u ON a.uid=u.uid WHERE a.uid=%s", (uid,))
    applicant = cursor.fetchone()
    cursor.execute("SELECT * FROM recommendation_letter WHERE uid=%s ORDER BY id", (uid,))
    letters = cursor.fetchall()
    cursor.execute("SELECT * FROM prior_degree WHERE uid=%s ORDER BY year DESC", (uid,))
    degrees = cursor.fetchall()
    mydb.commit()
    return render_template("applicant_dashboard.html", applicant=applicant, letters=letters, degrees=degrees)


@app.route("/applicant/respond_offer", methods=["POST"])
def respond_offer():
    if "user" not in session or session["user"]["role"] != "applicant":
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    uid = session["user"]["uid"]
    response = request.form.get("response")
    if response not in ("accepted", "declined"):
        flash("Invalid response.", "error")
        return redirect(url_for("applicant_dashboard"))
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT status FROM applicant WHERE uid=%s", (uid,))
    row = cursor.fetchone()
    if not row or row["status"] not in ("admitted", "admitted_with_aid"):
        flash("No offer to respond to.", "error")
        return redirect(url_for("applicant_dashboard"))
    cursor.execute("UPDATE applicant SET status=%s WHERE uid=%s", (response, uid))
    mydb.commit()
    flash(f"You have {'accepted' if response == 'accepted' else 'declined'} the offer.", "success")
    return redirect(url_for("applicant_dashboard"))


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
    letter_id = cursor.lastrowid
    cursor.execute("SELECT u.fname, u.lname FROM users u WHERE u.uid=%s", (uid,))
    applicant = cursor.fetchone()
    submit_link = request.host_url.rstrip("/") + "/applicant/submit_letter/" + str(letter_id)
    return render_template("letter_requested.html",
        writer_name=writer_name, writer_email=writer_email,
        writer_title=writer_title, institution=institution,
        applicant=applicant, submit_link=submit_link)


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
    uid = request.args.get('uid')
    lname = request.args.get('lname')
    year = request.args.get('year')
    degree = request.args.get('degree')
    semester = request.args.get('semester')
    fac = None
    role = session["user"]["role"]
    reviewer_uid = session["user"]["uid"]
    if role == "faculty":
        cursor.execute("SELECT cac, reviewer FROM faculty WHERE uid=%s", (reviewer_uid,))
        fac = cursor.fetchone()
        if not fac or (not fac["cac"] and not fac["reviewer"]):
            flash("Only CAC members or reviewers can access applications.", "error")
            return redirect(url_for("faculty"))
        fac = fac["cac"]
        if uid:
            cursor.execute("SELECT a.uid, u.fname, u.lname, a.degree, a.status, a.transcript_received, "
            "(SELECT COUNT(*) FROM recommendation_letter WHERE uid=a.uid AND is_submitted=TRUE) AS letters_submitted "
            "FROM applicant a JOIN users u ON a.uid=u.uid WHERE a.uid = %s ORDER BY a.status, u.lname", (uid,))
        elif lname:
            cursor.execute("SELECT a.uid, u.fname, u.lname, a.degree, a.status, a.transcript_received, "
            "(SELECT COUNT(*) FROM recommendation_letter WHERE uid=a.uid AND is_submitted=TRUE) AS letters_submitted "
            "FROM applicant a JOIN users u ON a.uid=u.uid WHERE u.lname = %s ORDER BY a.status, u.lname", (lname,))
        else:
            cursor.execute(
                "SELECT a.uid, u.fname, u.lname, a.degree, a.status, a.transcript_received, "
                "(SELECT COUNT(*) FROM recommendation_letter WHERE uid=a.uid AND is_submitted=TRUE) AS letters_submitted "
                "FROM applicant a JOIN users u ON a.uid=u.uid ORDER BY a.status, u.lname"
            )
    elif role == "secretary":
        if uid:
            cursor.execute("SELECT a.uid, u.fname, u.lname, a.degree, a.status, a.transcript_received, "
            "(SELECT COUNT(*) FROM recommendation_letter WHERE uid=a.uid AND is_submitted=TRUE) AS letters_submitted "
            "FROM applicant a JOIN users u ON a.uid=u.uid WHERE a.uid = %s ORDER BY a.status, u.lname", (uid,))
        elif lname:
            cursor.execute("SELECT a.uid, u.fname, u.lname, a.degree, a.status, a.transcript_received, "
            "(SELECT COUNT(*) FROM recommendation_letter WHERE uid=a.uid AND is_submitted=TRUE) AS letters_submitted "
            "FROM applicant a JOIN users u ON a.uid=u.uid WHERE u.lname = %s ORDER BY a.status, u.lname", (lname,))
        elif year:
            cursor.execute("SELECT a.uid, u.fname, u.lname, a.degree, a.status, a.transcript_received, "
            "(SELECT COUNT(*) FROM recommendation_letter WHERE uid=a.uid AND is_submitted=TRUE) AS letters_submitted "
            "FROM applicant a JOIN users u ON a.uid=u.uid WHERE a.year_applied = %s ORDER BY a.status, u.lname", (year,))
        elif degree:
            cursor.execute("SELECT a.uid, u.fname, u.lname, a.degree, a.status, a.transcript_received, "
            "(SELECT COUNT(*) FROM recommendation_letter WHERE uid=a.uid AND is_submitted=TRUE) AS letters_submitted "
            "FROM applicant a JOIN users u ON a.uid=u.uid WHERE a.degree = %s ORDER BY a.status, u.lname", (degree,))
        elif semester:
            cursor.execute("SELECT a.uid, u.fname, u.lname, a.degree, a.status, a.transcript_received, "
            "(SELECT COUNT(*) FROM recommendation_letter WHERE uid=a.uid AND is_submitted=TRUE) AS letters_submitted "
            "FROM applicant a JOIN users u ON a.uid=u.uid WHERE a.semester_applied = %s ORDER BY a.status, u.lname", (semester,))
        else:
            cursor.execute(
                "SELECT a.uid, u.fname, u.lname, a.degree, a.status, a.transcript_received, "
                "(SELECT COUNT(*) FROM recommendation_letter WHERE uid=a.uid AND is_submitted=TRUE) AS letters_submitted "
                "FROM applicant a JOIN users u ON a.uid=u.uid ORDER BY a.status, u.lname"
            )
    else:
        if uid:
            cursor.execute("SELECT a.uid, u.fname, u.lname, a.degree, a.status, a.transcript_received, "
            "(SELECT COUNT(*) FROM recommendation_letter WHERE uid=a.uid AND is_submitted=TRUE) AS letters_submitted "
            "FROM applicant a JOIN users u ON a.uid=u.uid WHERE a.uid = %s ORDER BY a.status, u.lname", (uid,))
        elif lname:
            cursor.execute("SELECT a.uid, u.fname, u.lname, a.degree, a.status, a.transcript_received, "
            "(SELECT COUNT(*) FROM recommendation_letter WHERE uid=a.uid AND is_submitted=TRUE) AS letters_submitted "
            "FROM applicant a JOIN users u ON a.uid=u.uid WHERE u.lname = %s ORDER BY a.status, u.lname", (lname,))
        else:
            cursor.execute(
                "SELECT a.uid, u.fname, u.lname, a.degree, a.status, a.transcript_received, "
                "(SELECT COUNT(*) FROM recommendation_letter WHERE uid=a.uid AND is_submitted=TRUE) AS letters_submitted "
                "FROM applicant a JOIN users u ON a.uid=u.uid ORDER BY a.status, u.lname"
            )
    applicants = cursor.fetchall()
    mydb.commit()
    return render_template("applications.html", applicants=applicants, role=role, fac = fac)


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
    if not _is_staff():
        flash("Access denied.", "error")
        return redirect(url_for("login"))
    current_role = session["user"]["role"]
    current_uid  = session["user"]["uid"]
    mydb.commit()
    cursor = mydb.cursor(dictionary=True)
    # CAC faculty can make final decisions; regular reviewers cannot
    if current_role == "faculty":
        cursor.execute("SELECT cac FROM faculty WHERE uid=%s", (current_uid,))
        fac = cursor.fetchone()
        if not fac or not fac["cac"]:
            flash("Only CAC or Graduate Secretary can make final decisions.", "error")
            return redirect(url_for("applications"))
    # CAC and admin can see reviewer reviews; GS cannot
    can_see_reviews = current_role in ("admin", "faculty")
    cursor.execute("SELECT a.*, u.fname, u.lname FROM applicant a JOIN users u ON a.uid=u.uid WHERE a.uid=%s", (uid,))
    applicant = cursor.fetchone()
    cursor.execute("""
        SELECT r.*, u.fname AS reviewer_fname, u.lname AS reviewer_lname,
               adv.fname AS advisor_fname, adv.lname AS advisor_lname
        FROM app_review r
        JOIN users u ON r.reviewer_uid=u.uid
        LEFT JOIN users adv ON r.recommended_advisor=adv.uid
        WHERE r.uid=%s
    """, (uid,))
    reviews = cursor.fetchall()
    #get average review score
    cursor.execute("SELECT AVG(rating) as rating FROM app_review WHERE uid=%s", (uid,) )
    avg=cursor.fetchone()
    cursor.execute("SELECT uid, fname, lname FROM users WHERE role='faculty'")
    faculty_list = cursor.fetchall()
    if request.method == "POST":
        decision = request.form.get("decision")
        if decision in ("admitted", "admitted_with_aid", "rejected"):
            cursor.execute("UPDATE applicant SET status=%s WHERE uid=%s", (decision, uid))
            mydb.commit()
            if decision in ("admitted", "admitted_with_aid"):
                new_uid = int(''.join([str(secrets.randbelow(10)) for _ in range(8)]))
                hashed = generate_password_hash("pass", method='pbkdf2:sha256')
                cursor.execute(
                    "INSERT INTO users (uid,username,password,role,fname,lname,email,address) VALUES (%s,%s,%s,'student',%s,%s,%s,%s)",
                    (new_uid, str(new_uid), hashed, applicant['fname'], applicant['lname'], applicant.get('email',''), applicant.get('address',''))
                )
                cursor.execute("INSERT INTO students (uid,program) VALUES (%s,%s)", (new_uid, applicant['degree']))
                mydb.commit()
                flash(f"Decision: {decision}. Student account created — Username: {new_uid}, Password: pass", "success")
            else:
                flash(f"Decision recorded: {decision}.", "success")
            return redirect(url_for("applications"))
    mydb.commit()
    return render_template("final_decision.html", applicant=applicant, reviews=reviews, faculty_list=faculty_list, can_see_reviews=can_see_reviews, avg=avg['rating'] if avg else None)

#REGS routes
@app.route("/viewgrades")
def grades_list():
    cursor = mydb.cursor(dictionary=True)
    search = request.args.get('search')

    if session['user']['role'] == 'faculty':
        if search:
            cursor.execute("SELECT co.departmentname, co.coursenumber, c.title, co.sectionnum, co.semester, co.year FROM courses_offered AS co INNER JOIN courses AS c ON co.departmentname = c.department AND co.coursenumber = c.course_number INNER JOIN enrollment AS gr ON co.departmentname=gr.department AND co.coursenumber=gr.course_number WHERE instructorid = %s AND gr.uid=%s ORDER BY co.departmentname, co.coursenumber, co.year DESC", (session['user']['uid'], search,))
        else:
            cursor.execute("SELECT co.departmentname, co.coursenumber, c.title, co.sectionnum, co.semester, co.year FROM courses_offered AS co INNER JOIN courses AS c ON co.departmentname = c.department AND co.coursenumber = c.course_number WHERE instructorid = %s ORDER BY co.departmentname, co.coursenumber, co.year DESC", (session['user']['uid'],))
    else:
        if search:
            cursor.execute("SELECT co.departmentname, co.coursenumber, c.title, co.sectionnum, co.semester, co.year FROM courses_offered AS co INNER JOIN courses AS c ON co.departmentname = c.department AND co.coursenumber = c.course_number INNER JOIN enrollment AS gr ON co.departmentname=gr.department AND co.coursenumber=gr.course_number WHERE gr.uid=%s ORDER BY co.departmentname, co.coursenumber, co.year DESC", (search,))
        else:
            cursor.execute("SELECT co.departmentname, co.coursenumber, c.title, co.sectionnum, co.semester, co.year FROM courses_offered AS co INNER JOIN courses AS c ON co.departmentname = c.department AND co.coursenumber = c.course_number ORDER BY co.departmentname, co.coursenumber, co.year DESC")
    
    classes = cursor.fetchall()
    mydb.commit()
    return render_template('view_grades.html', title = "Grades", classes = classes)

@app.route('/<dpt>/<crn>/<sectionno>/<sem>/<year>', methods = ['GET', 'POST'])
def add_grades(dpt, crn, sectionno, sem, year):
    cursor = mydb.cursor(dictionary=True)
    if request.method == 'POST':
        new = request.form["newgrade"]
        cursor.execute("SELECT cg.uid, s.fname, s.lname, cg.grade, cg.prof_added FROM enrollment AS cg INNER JOIN users AS s ON cg.uid = s.uid WHERE cg.department = %s AND cg.course_number = %s AND cg.semester = %s AND cg.year = %s AND cg.sectionnum = %s", (dpt, crn, sem, year, sectionno))
        students = cursor.fetchall()
        if new != 'A' and new != 'A-' and new != 'B+' and new != 'B' and new != 'B-' and new != 'C+' and new != 'C' and new != 'F' and new != 'IP':
            return render_template('add_grades.html', title = "Class Grade", students = students, dpt = dpt, crn = crn, sectionno = sectionno, sem = sem, year = year, error = "Please enter a valid grade.")
        sid = int(request.form["id"])
        cursor.execute("SELECT prof_added FROM enrollment WHERE department = %s AND course_number = %s AND semester = %s AND year = %s AND sectionnum = %s AND uid = %s", (dpt, crn, sem, year, sectionno, sid))
        check = cursor.fetchone()
        if session['user']['role'] == 'faculty' and check['prof_added']==True:
            cursor.execute("SELECT cg.uid, s.fname, s.lname, cg.grade, cg.prof_added FROM enrollment AS cg INNER JOIN users AS s ON cg.uid = s.uid WHERE cg.department = %s AND cg.course_number = %s AND cg.semester = %s AND cg.year = %s AND cg.sectionnum = %s", (dpt, crn, sem, year, sectionno))
            students = cursor.fetchall()
            mydb.commit()
            return render_template('add_grades.html', title = "Class Grade", students = students, dpt = dpt, crn = crn, sectionno = sectionno, sem = sem, year = year, error = "You have already input a grade. If you would like to change this, please contact the system administrator or grad secretary.")
        else:
            if session['user']['role'] == 'faculty':
                cursor.execute("UPDATE enrollment SET grade = %s, prof_added = TRUE WHERE uid = %s AND department = %s AND course_number = %s AND semester = %s AND year = %s AND sectionnum = %s", (new, sid, dpt, crn, sem, year, sectionno))
            else:
                cursor.execute("UPDATE enrollment SET grade = %s, prof_added = FALSE WHERE uid = %s AND department = %s AND course_number = %s AND semester = %s AND year = %s AND sectionnum = %s", (new, sid, dpt, crn, sem, year, sectionno))
            mydb.commit()
    cursor.execute("SELECT cg.uid, s.fname, s.lname, cg.grade, cg.prof_added FROM enrollment AS cg INNER JOIN users AS s ON cg.uid = s.uid WHERE cg.department = %s AND cg.course_number = %s AND cg.semester = %s AND cg.year = %s AND cg.sectionnum = %s", (dpt, crn, sem, year, sectionno))
    students = cursor.fetchall()
    mydb.commit()
    return render_template('add_grades.html', title = "Class Grade", students = students, dpt = dpt, crn = crn, sectionno = sectionno, sem = sem, year = year, error = "")

@app.route('/schedule', methods = ['GET', 'POST'])
def schedule():
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT grade, enrollment.department, enrollment.course_number, enrollment.sectionnum, enrollment.semester, enrollment.year, courses.title, day, time FROM enrollment " \
    "right join courses on enrollment.department=courses.department AND enrollment.course_number = courses.course_number " \
    "right join courses_offered on enrollment.department=courses_offered.departmentname AND enrollment.course_number=courses_offered.coursenumber AND enrollment.sectionnum=courses_offered.sectionnum AND enrollment.semester=courses_offered.semester AND enrollment.year=courses_offered.year " \
    "WHERE enrollment.uid = %s and enrollment.prof_added = FALSE", (session['user']['uid'],))
    schedule = cursor.fetchall()
    mydb.commit()
    return render_template('schedule.html', schedule = schedule)

@app.route('/coursecatalog')
def courseCatalog():
  cursor = mydb.cursor(dictionary = True)
  
  dpt = request.args.get('dpt')
  courseno = request.args.get('courseno')
  title = request.args.get('title')

  if dpt and courseno and title:
    cursor.execute("SELECT * FROM courses WHERE department = %s AND course_number = %s AND title = %s", (dpt, courseno, title,))
  elif dpt and courseno:
    cursor.execute("SELECT * FROM courses WHERE department = %s AND course_number = %s", (dpt, courseno,))
  elif dpt and title:
    cursor.execute("SELECT * FROM courses WHERE department = %s AND title = %s", (dpt, title,))
  elif courseno and title:
    cursor.execute("SELECT * FROM courses WHERE course_number = %s AND title = %s", (courseno, title,))
  elif dpt:
    cursor.execute("SELECT * FROM courses WHERE department = %s", (dpt,))
  elif courseno:
    cursor.execute("SELECT * FROM courses WHERE course_number = %s", (courseno,))
  elif title:
    cursor.execute("SELECT * FROM courses WHERE title = %s", (title,))
  else:
    cursor.execute("SELECT * FROM courses")
    
  course = cursor.fetchall()

  mydb.commit()
  return render_template('course_catalog.html', title = "Course Catalog", course = course)

@app.route('/course/<dpt>/<courseno>', methods=['GET', 'POST'])
def showcourse(dpt, courseno):
  cursor = mydb.cursor(dictionary = True)

  cursor.execute("SELECT * FROM courses " \
  "INNER JOIN courses_offered ON courses.department=courses_offered.departmentname AND courses.course_number=courses_offered.coursenumber " \
  "INNER JOIN users ON courses_offered.instructorid=users.uid " \
  "WHERE department = %s AND course_number = %s", (dpt, courseno))
  course = cursor.fetchone()
  
  cursor.execute("SELECT prereqdpt, prereqnum, courses.title FROM prereqs " \
  "INNER JOIN courses ON prereqs.prereqdpt=courses.department AND prereqs.prereqnum=courses.course_number " \
  "WHERE dptname=%s AND coursenumber=%s", (dpt, courseno,))
  prerequisites = cursor.fetchall()
  if prerequisites == None:
      prerequisites = False

  studentid = session['user']['uid']
  cursor.execute("SELECT * FROM enrollment WHERE uid = %s AND department = %s AND course_number = %s", (studentid, dpt, courseno))
  enrolledIn = cursor.fetchone()

  conflict = False
  phd_err = False
  missing_prereqs = []
  schedule = None
  capacity = False
  holds = False
 
  if session['user']['role'] == 'student':
    if request.method == 'POST':
        if enrolledIn:
            cursor.execute("DELETE FROM enrollment WHERE (uid=%s AND department=%s AND course_number=%s)", (studentid, dpt, courseno,))
            mydb.commit()
        else:
            if course['capacity'] == 0:
                capacity = True
            cursor.execute("SELECT registration_hold FROM students WHERE uid = %s", (studentid,))
            hold = cursor.fetchone()
            if hold['registration_hold'] == True:
                holds = True

            cursor.execute("SELECT courses_offered.day, courses_offered.time FROM enrollment INNER JOIN courses_offered ON enrollment.department=courses_offered.departmentname AND enrollment.course_number=courses_offered.coursenumber WHERE enrollment.uid = %s AND enrollment.grade = 'IP'", (studentid,))
            enrolled = cursor.fetchall()

            conflicts = {
                '1500-1730': ['1530-1800', '1600-1830'],
                '1530-1800': ['1500-1730', '1600-1830', '1800-2030'],
                '1600-1830': ['1500-1730', '1530-1800', '1800-2030'],
                '1800-2030': ['1530-1800', '1600-1830'],
            }
            for enrolled_course in enrolled:
                if enrolled_course['day'] == course['day']:
                    if enrolled_course['time'] == course['time']:
                        conflict = True
                        break
                    if (enrolled_course['time'] in conflicts.get(course['time'])):
                        conflict = True
                        break
                   
            if not conflict:
                cursor.execute("SELECT prereqdpt, prereqnum FROM prereqs WHERE dptname=%s AND coursenumber=%s", (dpt, courseno,))
                prereqs = cursor.fetchall()

                for prereq in prereqs:
                    cursor.execute("SELECT * FROM enrollment WHERE (uid=%s AND department=%s AND course_number=%s AND grade != 'IP')", (studentid, prereq['prereqdpt'], prereq['prereqnum'],))
                    completed = cursor.fetchone()
                    if not completed:
                        missing_prereqs.append(prereq['prereqdpt'] + ' ' + str(prereq['prereqnum']))

            if not conflict and not missing_prereqs and not holds and not capacity:
                cursor.execute("SELECT program FROM students WHERE uid=%s", (studentid,))
                student = cursor.fetchone()


                if student['program'] == 'PhD' and not courseno.startswith('6'):
                    phd_err = True
                else:
                    cursor.execute("SELECT credits FROM courses WHERE course_number = %s AND department = %s", (courseno, dpt))
                    credit_hours = cursor.fetchone()
                    credit_hours = credit_hours['credits']
                    cursor.execute("INSERT INTO enrollment (uid, department, course_number, grade, semester, year, sectionnum, prof_added, credit_hours) VALUES (%s,%s,%s,%s,%s,%s,%s,%s, %s)", (studentid, dpt, courseno, 'IP', course['semester'], course['year'], course['sectionnum'], False, credit_hours))
                    #updating capacity w/enrollment
                    new_capacity = course['capacity'] - 1
                    cursor.execute("UPDATE courses_offered SET capacity = %s", (new_capacity,))
                    mydb.commit()
 
    cursor.execute("SELECT * FROM enrollment WHERE uid = %s AND department = %s AND course_number = %s", (studentid, dpt, courseno,))
    enrolledIn = cursor.fetchone()
    cursor.execute("SELECT grade, enrollment.department, enrollment.course_number, enrollment.sectionnum, enrollment.semester, enrollment.year, courses.title, day, time FROM enrollment " \
    "right join courses on enrollment.department=courses.department AND enrollment.course_number = courses.course_number " \
    "right join courses_offered on enrollment.department=courses_offered.departmentname AND enrollment.course_number=courses_offered.coursenumber AND enrollment.sectionnum=courses_offered.sectionnum AND enrollment.semester=courses_offered.semester AND enrollment.year=courses_offered.year " \
    "WHERE enrollment.uid = %s and enrollment.prof_added = FALSE", (session['user']['uid'],))
    schedule = cursor.fetchall()
    cursor.execute("SELECT * FROM courses " \
    "INNER JOIN courses_offered ON courses.department=courses_offered.departmentname AND courses.course_number=courses_offered.coursenumber " \
    "INNER JOIN users ON courses_offered.instructorid=users.uid " \
    "WHERE department = %s AND course_number = %s", (dpt, courseno))
    course = cursor.fetchone()
 
  mydb.commit()

  return render_template('course.html', title = "Course", course = course, enrolledIn = enrolledIn, conflict = conflict, missing_prereqs=missing_prereqs, prerequisites=prerequisites, phd_err=phd_err, schedule=schedule, capacity=capacity, holds=holds)

@app.route('/alumnilist')
def alumnilist():
    if session['user']['role'] != 'secretary':
        flash("Access denied.", "error")
        return redirect(url_for("login"))

    cursor = mydb.cursor(dictionary = True)
    program = request.args.get('program')
    grad_year = request.args.get('grad_year', type = int)
    grad_semester = request.args.get('grad_semester')
    if program:
        cursor.execute("SELECT users.uid, email, fname, lname, a.degree, a.graduation_year, a.graduation_semester from users INNER JOIN alumni AS a ON users.uid = a.uid WHERE a.degree = %s", (program,))
    elif grad_year:
        cursor.execute("SELECT users.uid, email, fname, lname, a.degree, a.graduation_year, a.graduation_semester from users INNER JOIN alumni AS a ON users.uid = a.uid WHERE a.graduation_year = %s", (grad_year,))
    elif grad_semester:
        cursor.execute("SELECT users.uid, email, fname, lname, a.degree, a.graduation_year, a.graduation_semester from users INNER JOIN alumni AS a ON users.uid = a.uid WHERE a.graduation_semester = %s", (grad_semester,))
    else:
        cursor.execute("SELECT users.uid, email, fname, lname, a.degree, a.graduation_year, a.graduation_semester from users INNER JOIN alumni AS a ON users.uid = a.uid")
    alum = cursor.fetchall()
    
    return render_template('alumnilist.html', title = "Alumni List", alum = alum)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
