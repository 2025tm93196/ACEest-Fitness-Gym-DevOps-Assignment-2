import os
import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, jsonify, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-this-key")

DATABASE = os.environ.get("DATABASE", "fitness.db")

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                age INTEGER NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                activity TEXT NOT NULL,
                duration INTEGER NOT NULL,
                FOREIGN KEY(member_id) REFERENCES members(id)
            )
        """)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>ACEest Fitness & Gym</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f4f6f8; }
        h1 { color: #173b65; }
        .card { background: white; padding: 20px; margin: 15px 0;
                border-radius: 8px; }
        input, select, button { padding: 10px; margin: 5px; }
        button { background: #173b65; color: white; border: 0; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; }
        td, th { padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }
    </style>
</head>
<body>
    <h1>ACEest Fitness & Gym</h1>
    <h2>Fitness Management Dashboard</h2>

    <div class="card">
        <h3>Register Member</h3>
        <form method="POST" action="/members">
            <input name="name" placeholder="Member Name" required>
            <input name="email" type="email" placeholder="Email" required>
            <input name="age" type="number" min="1" max="120"
                   placeholder="Age" required>
            <button type="submit">Register</button>
        </form>
    </div>

    <div class="card">
        <h3>Members ({{ members|length }})</h3>
        <table>
            <tr><th>Name</th><th>Email</th><th>Age</th></tr>
            {% for m in members %}
            <tr>
                <td>{{ m.name }}</td>
                <td>{{ m.email }}</td>
                <td>{{ m.age }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <div class="card">
        <h3>Record Workout</h3>
        <form method="POST" action="/workouts">
            <select name="member_id" required>
                <option value="">Select Member</option>
                {% for m in members %}
                <option value="{{ m.id }}">{{ m.name }}</option>
                {% endfor %}
            </select>
            <input name="activity" placeholder="Activity" required>
            <input name="duration" type="number" min="1"
                   placeholder="Duration (minutes)" required>
            <button type="submit">Save Workout</button>
        </form>
    </div>

    <div class="card">
        <h3>Workout History</h3>
        <table>
            <tr><th>Member</th><th>Activity</th><th>Duration (minutes)</th></tr>
            {% for w in workouts %}
            <tr>
                <td>{{ w.name }}</td>
                <td>{{ w.activity }}</td>
                <td>{{ w.duration }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    with get_db() as conn:
        members = conn.execute("SELECT * FROM members ORDER BY id DESC").fetchall()
        workouts = conn.execute("""
            SELECT members.name, workouts.activity, workouts.duration
            FROM workouts JOIN members ON members.id = workouts.member_id
            ORDER BY workouts.id DESC
        """).fetchall()
    return render_template_string(HTML, members=members, workouts=workouts)

@app.route("/members", methods=["POST"])
def add_member():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    age = request.form.get("age", type=int)

    if not name or not email or age is None or not 1 <= age <= 120:
        return "Invalid member details", 400

    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO members (name, email, age) VALUES (?, ?, ?)",
                (name, email, age)
            )
    except sqlite3.IntegrityError:
        return "A member with this email already exists", 409

    return redirect(url_for("home"))

@app.route("/workouts", methods=["POST"])
def add_workout():
    member_id = request.form.get("member_id", type=int)
    activity = request.form.get("activity", "").strip()
    duration = request.form.get("duration", type=int)

    if not member_id or not activity or duration is None or duration <= 0:
        return "Invalid workout details", 400

    with get_db() as conn:
        member = conn.execute(
            "SELECT id FROM members WHERE id = ?", (member_id,)
        ).fetchone()
        if member is None:
            return "Member not found", 404

        conn.execute(
            "INSERT INTO workouts (member_id, activity, duration) VALUES (?, ?, ?)",
            (member_id, activity, duration)
        )

    return redirect(url_for("home"))

@app.route("/health")
def health():
    return jsonify({
        "application": "ACEest Fitness & Gym",
        "status": "UP"
    })

with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
