from flask import Flask, render_template, request, redirect, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import db
import config

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    query = request.args.get("query", "").strip()
    if query:
        walks = db.query(
            "SELECT walks.id, walks.user_id, minutes_walked, distance, steps, time_stamp, username "
            "FROM walks, users "
            "WHERE walks.user_id = users.id AND users.username LIKE ? "
            "ORDER BY walks.id DESC",
            [f"%{query}%"]
        )
    else:
        walks = db.query(
            "SELECT walks.id, walks.user_id, minutes_walked, distance, steps, time_stamp, username "
            "FROM walks, users "
            "WHERE walks.user_id = users.id "
            "ORDER BY walks.id DESC"
        )
    return render_template("index.html", walks=walks, query=query)

@app.route("/add_walk", methods=["POST"])
def add_walk():
    if "user_id" not in session:
        return redirect("/login")

    try:
        minutes_walked = int(request.form["minutes_walked"])
        distance = float(request.form["distance"])
        steps = int(request.form["steps"])
    except (ValueError, KeyError):
        return "Error: Invalid numbers given!", 400
    if minutes_walked <= 0 or distance < 0 or steps < 0:
        return "Error: Duration must be > 0 and distance/steps cannot be negative!", 400
    db.execute(
        "INSERT INTO walks (user_id, minutes_walked, distance, steps, time_stamp) "
        "VALUES (?, ?, ?, ?, datetime('now', 'localtime'))", 
        [session["user_id"], minutes_walked, distance, steps]
    )
    return redirect("/")

@app.route("/edit_walk/<int:walk_id>", methods=["GET", "POST"])
def edit_walk(walk_id):
    if "user_id" not in session:
        return redirect("/login")

    rows = db.query("SELECT id, user_id, minutes_walked, distance, steps FROM walks WHERE id = ?", [walk_id])
    if not rows:
        abort(404)
    walk = rows[0]

    if walk["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "POST":
        minutes_walked = request.form["minutes_walked"]
        distance = request.form["distance"]
        steps = request.form["steps"]

        db.execute(
            "UPDATE walks SET minutes_walked = ?, distance = ?, steps = ? WHERE id = ? AND user_id = ?",
            [minutes_walked, distance, steps, walk_id, session["user_id"]]
        )
        return redirect("/")

    return render_template("edit_walk.html", walk=walk)

@app.route("/delete_walk/<int:walk_id>", methods=["POST"])
def delete_walk(walk_id):
    if "user_id" not in session:
        return redirect("/login")
    
    rows = db.query("SELECT user_id FROM walks WHERE id = ?", [walk_id])
    if not rows:
        abort(404)
    if rows[0]["user_id"] != session["user_id"]:
        abort(403)

    db.execute("DELETE FROM walks WHERE id = ? AND user_id = ?", [walk_id, session["user_id"]])
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if len(username) < 2 or len(username) > 64:
            return "Error: Username must be 2-64 characters long!", 400
        if len(password) < 6:
            return "Error: Password must be at least 6 characters long!", 400
        password_hash = generate_password_hash(password)
        try:
            db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", [username, password_hash])
            return redirect("/login")
        except sqlite3.IntegrityError:
            return "Error: Username in use", 400
            
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