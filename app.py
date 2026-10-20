import hashlib
import os
import random
import sqlite3
from functools import wraps
from flask import (
    Flask,
    flash,
     g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "skillswap-dev-secret-key-change-in-prod")
DB = os.environ.get("DATABASE_PATH", "skillswap.db")

CATEGORIES = [
    "Programming",
    "Design",
    "Languages",
    "Music",
    "Math",
    "Science",
    "Writing",
    "Business",
    "Arts & Crafts",
    "Fitness",
    "Cooking",
    "Other",
]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


def init_db():
    db = sqlite3.connect(DB)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            bio TEXT DEFAULT '',
            avatar_color TEXT DEFAULT '#6366f1',
            university TEXT DEFAULT '',
            joined_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            skill_type TEXT NOT NULL,
            level TEXT DEFAULT 'Beginner',
            wants_in_return TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user INTEGER NOT NULL,
            to_user INTEGER NOT NULL,
            skill_id INTEGER NOT NULL,
            message TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(from_user) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(to_user) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(skill_id) REFERENCES skills(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reviewer_id INTEGER NOT NULL,
            reviewee_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(reviewer_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(reviewee_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user INTEGER NOT NULL,
            to_user INTEGER NOT NULL,
            body TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(from_user) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(to_user) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )
    db.commit()
    db.close()


# Initialize tables on import so WSGI servers (Gunicorn) always have a ready DB
init_db()


@app.route("/")
def index():
    db = get_db()
    total_users = db.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
    total_skills = db.execute("SELECT COUNT(*) as c FROM skills").fetchone()["c"]
    total_matches = db.execute(
        "SELECT COUNT(*) as c FROM requests WHERE status='accepted'"
    ).fetchone()["c"]
    recent = db.execute(
        """SELECT s.*, u.name, u.avatar_color FROM skills s
           JOIN users u ON s.user_id=u.id ORDER BY s.created_at DESC LIMIT 6"""
    ).fetchall()
    return render_template(
        "index.html",
        total_users=total_users,
        total_skills=total_skills,
        total_matches=total_matches,
        recent=recent,
        categories=CATEGORIES,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        pw = request.form.get("password", "")
        university = request.form.get("university", "").strip()
        if not name or not email or not pw:
            flash("All fields required.", "danger")
            return redirect(url_for("register"))
        if len(pw) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("register"))
        colors = [
            "#6366f1",
            "#8b5cf6",
            "#ec4899",
            "#f59e0b",
            "#10b981",
            "#3b82f6",
            "#ef4444",
        ]
        color = random.choice(colors)
        db = get_db()
        try:
            db.execute(
                "INSERT INTO users(name,email,password,university,avatar_color) VALUES(?,?,?,?,?)",
                (name, email, hash_pw(pw), university, color),
            )
            db.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already registered.", "danger")
    return render_template("auth.html", mode="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        pw = request.form.get("password", "")
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, hash_pw(pw)),
        ).fetchone()
        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["avatar_color"] = user["avatar_color"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("auth.html", mode="login")


@app.route("/logout")
def logout():
    session.clear()
    flash("You've been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    uid = session["user_id"]
    my_skills = db.execute(
        "SELECT * FROM skills WHERE user_id=? ORDER BY created_at DESC", (uid,)
    ).fetchall()
    incoming = db.execute(
        """SELECT r.*, u.name as from_name, u.avatar_color, s.title as skill_title
           FROM requests r JOIN users u ON r.from_user=u.id JOIN skills s ON r.skill_id=s.id
           WHERE r.to_user=? ORDER BY r.created_at DESC""",
        (uid,),
    ).fetchall()
    outgoing = db.execute(
        """SELECT r.*, u.name as to_name, u.avatar_color as to_color, s.title as skill_title
           FROM requests r JOIN users u ON r.to_user=u.id JOIN skills s ON r.skill_id=s.id
           WHERE r.from_user=? ORDER BY r.created_at DESC""",
        (uid,),
    ).fetchall()
    unread = db.execute(
        "SELECT COUNT(*) as c FROM messages WHERE to_user=? AND is_read=0", (uid,)
    ).fetchone()["c"]
    partners = db.execute(
        """SELECT DISTINCT u.id, u.name, u.avatar_color FROM requests r
           JOIN users u ON (CASE WHEN r.from_user=? THEN r.to_user ELSE r.from_user END)=u.id
           WHERE (r.from_user=? OR r.to_user=?) AND r.status='accepted'""",
        (uid, uid, uid),
    ).fetchall()
    pending_in = sum(1 for r in incoming if r["status"] == "pending")
    return render_template(
        "dashboard.html",
        my_skills=my_skills,
        incoming=incoming,
        outgoing=outgoing,
        unread=unread,
        partners=partners,
        pending_in=pending_in,
        categories=CATEGORIES,
    )


@app.route("/skills")
def skills():
    db = get_db()
    cat = request.args.get("cat", "")
    q = request.args.get("q", "")
    stype = request.args.get("type", "")
    level = request.args.get("level", "")
    sql = """SELECT s.*, u.name, u.avatar_color, u.university FROM skills s
             JOIN users u ON s.user_id=u.id WHERE 1=1"""
    params = []
    if cat:
        sql += " AND s.category=?"
        params.append(cat)
    if q:
        sql += " AND (s.title LIKE ? OR s.description LIKE ?)"
        params += [f"%{q}%", f"%{q}%"]
    if stype:
        sql += " AND s.skill_type=?"
        params.append(stype)
    if level:
        sql += " AND s.level=?"
        params.append(level)
    if "user_id" in session:
        sql += " AND s.user_id != ?"
        params.append(session["user_id"])
    sql += " ORDER BY s.created_at DESC"
    all_skills = db.execute(sql, params).fetchall()
    return render_template(
        "skills.html",
        skills=all_skills,
        categories=CATEGORIES,
        cat=cat,
        q=q,
        stype=stype,
        level=level,
    )


@app.route("/skills/add", methods=["GET", "POST"])
@login_required
def add_skill():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        desc = request.form.get("description", "").strip()
        cat = request.form.get("category", "")
        stype = request.form.get("skill_type", "")
        level = request.form.get("level", "Intermediate")
        wants = request.form.get("wants_in_return", "").strip()
        if not title or not desc or not cat or not stype:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("add_skill"))
        db = get_db()
        db.execute(
            "INSERT INTO skills(user_id,title,description,category,skill_type,level,wants_in_return) VALUES(?,?,?,?,?,?,?)",
            (session["user_id"], title, desc, cat, stype, level, wants),
        )
        db.commit()
        flash("Skill posted successfully!", "success")
        return redirect(url_for("dashboard"))
    return render_template("add_skill.html", categories=CATEGORIES)


@app.route("/skills/delete/<int:sid>", methods=["GET", "POST"])
@login_required
def delete_skill(sid):
    db = get_db()
    skill = db.execute(
        "SELECT id FROM skills WHERE id=? AND user_id=?", (sid, session["user_id"])
    ).fetchone()
    if skill:
        db.execute("DELETE FROM requests WHERE skill_id=?", (sid,))
        db.execute("DELETE FROM skills WHERE id=?", (sid,))
        db.commit()
        flash("Skill removed.", "info")
    return redirect(url_for("dashboard"))


@app.route("/request/<int:skill_id>", methods=["POST"])
@login_required
def send_request(skill_id):
    db = get_db()
    skill = db.execute("SELECT * FROM skills WHERE id=?", (skill_id,)).fetchone()
    if not skill or skill["user_id"] == session["user_id"]:
        flash("Invalid request.", "danger")
        return redirect(url_for("skills"))
    existing = db.execute(
        "SELECT id FROM requests WHERE from_user=? AND skill_id=?",
        (session["user_id"], skill_id),
    ).fetchone()
    if existing:
        flash("You already sent a request for this skill.", "warning")
        return redirect(url_for("skills"))
    msg = request.form.get("message", "").strip()
    db.execute(
        "INSERT INTO requests(from_user,to_user,skill_id,message) VALUES(?,?,?,?)",
        (session["user_id"], skill["user_id"], skill_id, msg),
    )
    db.commit()
    flash("Request sent!", "success")
    return redirect(url_for("skills"))


@app.route("/request/respond/<int:rid>/<action>", methods=["GET", "POST"])
@login_required
def respond_request(rid, action):
    if action not in ("accepted", "rejected"):
        return redirect(url_for("dashboard"))
    db = get_db()
    db.execute(
        "UPDATE requests SET status=? WHERE id=? AND to_user=?",
        (action, rid, session["user_id"]),
    )
    db.commit()
    flash(f"Request {action}.", "success" if action == "accepted" else "info")
    return redirect(url_for("dashboard"))


@app.route("/profile/<int:uid>")
def profile(uid):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("index"))
    user_skills = db.execute(
        "SELECT * FROM skills WHERE user_id=? ORDER BY created_at DESC", (uid,)
    ).fetchall()
    reviews = db.execute(
        """SELECT r.*, u.name as reviewer_name, u.avatar_color FROM reviews r
           JOIN users u ON r.reviewer_id=u.id WHERE r.reviewee_id=? ORDER BY r.created_at DESC""",
        (uid,),
    ).fetchall()
    avg_rating = db.execute(
        "SELECT AVG(rating) as avg FROM reviews WHERE reviewee_id=?", (uid,)
    ).fetchone()["avg"]
    can_review = False
    if "user_id" in session and session["user_id"] != uid:
        accepted = db.execute(
            """SELECT id FROM requests WHERE status='accepted' AND
               ((from_user=? AND to_user=?) OR (from_user=? AND to_user=?))""",
            (session["user_id"], uid, uid, session["user_id"]),
        ).fetchone()
        already = db.execute(
            "SELECT id FROM reviews WHERE reviewer_id=? AND reviewee_id=?",
            (session["user_id"], uid),
        ).fetchone()
        can_review = bool(accepted and not already)
    return render_template(
        "profile.html",
        user=user,
        skills=user_skills,
        reviews=reviews,
        avg_rating=avg_rating,
        can_review=can_review,
    )


@app.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    db = get_db()
    uid = session["user_id"]
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        bio = request.form.get("bio", "").strip()
        university = request.form.get("university", "").strip()
        if not name:
            flash("Name cannot be empty.", "danger")
            return redirect(url_for("edit_profile"))
        db.execute(
            "UPDATE users SET name=?,bio=?,university=? WHERE id=?",
            (name, bio, university, uid),
        )
        db.commit()
        session["user_name"] = name
        flash("Profile updated!", "success")
        return redirect(url_for("profile", uid=uid))
    user = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    return render_template("edit_profile.html", user=user)


@app.route("/review/<int:uid>", methods=["POST"])
@login_required
def add_review(uid):
    reviewer_id = session["user_id"]
    if reviewer_id == uid:
        flash("You cannot review yourself.", "danger")
        return redirect(url_for("profile", uid=uid))

    db = get_db()
    accepted = db.execute(
        """SELECT id FROM requests WHERE status='accepted' AND
           ((from_user=? AND to_user=?) OR (from_user=? AND to_user=?))""",
        (reviewer_id, uid, uid, reviewer_id),
    ).fetchone()
    already = db.execute(
        "SELECT id FROM reviews WHERE reviewer_id=? AND reviewee_id=?",
        (reviewer_id, uid),
    ).fetchone()
    if not accepted or already:
        flash("You are not eligible to review this user.", "warning")
        return redirect(url_for("profile", uid=uid))

    try:
        rating = max(1, min(5, int(request.form.get("rating", 5))))
    except ValueError:
        rating = 5
    comment = request.form.get("comment", "").strip()
    db.execute(
        "INSERT INTO reviews(reviewer_id,reviewee_id,rating,comment) VALUES(?,?,?,?)",
        (reviewer_id, uid, rating, comment),
    )
    db.commit()
    flash("Review submitted!", "success")
    return redirect(url_for("profile", uid=uid))


@app.route("/messages")
@login_required
def messages():
    db = get_db()
    uid = session["user_id"]
    contacts = db.execute(
        """SELECT DISTINCT u.id, u.name, u.avatar_color,
           (SELECT COUNT(*) FROM messages WHERE from_user=u.id AND to_user=? AND is_read=0) as unread
           FROM messages m JOIN users u ON (CASE WHEN m.from_user=? THEN m.to_user ELSE m.from_user END)=u.id
           WHERE m.from_user=? OR m.to_user=?""",
        (uid, uid, uid, uid),
    ).fetchall()
    selected_uid = request.args.get("with", type=int)
    chat = []
    selected_user = None
    if selected_uid:
        selected_user = db.execute(
            "SELECT * FROM users WHERE id=?", (selected_uid,)
        ).fetchone()
        chat = db.execute(
            """SELECT m.*, u.name, u.avatar_color FROM messages m
               JOIN users u ON m.from_user=u.id
               WHERE (m.from_user=? AND m.to_user=?) OR (m.from_user=? AND m.to_user=?)
               ORDER BY m.created_at ASC""",
            (uid, selected_uid, selected_uid, uid),
        ).fetchall()
        db.execute(
            "UPDATE messages SET is_read=1 WHERE from_user=? AND to_user=?",
            (selected_uid, uid),
        )
        db.commit()
    return render_template(
        "messages.html",
        contacts=contacts,
        chat=chat,
        selected_user=selected_user,
        selected_uid=selected_uid,
    )


@app.route("/messages/send", methods=["POST"])
@login_required
def send_message():
    to_uid = int(request.form["to_user"])
    body = request.form.get("body", "").strip()
    if body and to_uid != session["user_id"]:
        db = get_db()
        db.execute(
            "INSERT INTO messages(from_user,to_user,body) VALUES(?,?,?)",
            (session["user_id"], to_uid, body),
        )
        db.commit()
    return redirect(url_for("messages", **{"with": to_uid}))


@app.route("/api/stats")
def api_stats():
    db = get_db()
    cats = db.execute(
        "SELECT category, COUNT(*) as cnt FROM skills GROUP BY category"
    ).fetchall()
    return jsonify(
        {"labels": [r["category"] for r in cats], "data": [r["cnt"] for r in cats]}
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)