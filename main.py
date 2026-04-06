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


@app.route('/logout', methods=['GET'])
def logout():
  session.clear()
  return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
