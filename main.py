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
            elif user["applicant"] == "applicant":
                return redirect(url_for("applicant"))
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
