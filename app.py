from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import db
import config

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    walks = db.query("SELECT walks.id, walks.user_id, minutes_walked, distance, steps, time_stamp, username FROM walks, users WHERE walks.user_id = users.id ORDER BY walks.id DESC")
    return render_template("index.html", walks=walks)

@app.route("/add_walk", methods=["POST"])
def add_walk():
    if "user_id" not in session:
        return redirect("/login")

    minutes_walked = request.form["minutes_walked"]
    distance = request.form["distance"]
    steps = request.form["steps"]

    db.execute("INSERT INTO walks (user_id, minutes_walked, distance, steps, time_stamp) VALUES (?, ?, ?, ?, datetime('now', 'localtime'))", [session["user_id"], minutes_walked, distance, steps])
    return redirect("/")

@app.route("/delete_walk/<int:walk_id>", methods=["POST"])
def delete_walk(walk_id):
    if "user_id" not in session:
        return redirect("/login")

    db.execute("DELETE FROM walks WHERE id = ? AND user_id = ?", [walk_id, session["user_id"]])
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        password_hash = generate_password_hash(password)
        try:
            db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", [username, password_hash])
            return redirect("/login")
        except sqlite3.IntegrityError:
            return "Error: Username in use"
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        rows = db.query("SELECT id, username, password_hash FROM users WHERE username = ?", [username])
        if rows and check_password_hash(rows[0]["password_hash"], password):
            session["user_id"] = rows[0]["id"]
            session["username"] = rows[0]["username"]
            return redirect("/")
        else:
            return "Error: Invalid username or password!"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")