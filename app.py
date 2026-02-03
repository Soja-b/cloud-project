from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "jobconnect_secret_key"

# ================= DATABASE =================
def get_db():
    return sqlite3.connect("database.db")

def create_tables():
    con = get_db()
    cur = con.cursor()

    # USERS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # JOBS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS jobs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        location TEXT NOT NULL,
        status TEXT DEFAULT 'Open'
    )
    """)

    # APPLICATIONS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS applications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        applicant_email TEXT,
        status TEXT DEFAULT 'Applied'
    )
    """)

    # REVIEWS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reviews(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rating INTEGER,
        comment TEXT
    )
    """)

    con.commit()
    con.close()

create_tables()

# ================= ROUTES =================

# ---------- HOME ----------
@app.route("/")
def index():
    return render_template("index.html")


# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        if not name or not email or not password or not role:
            return "All fields are required"

        try:
            con = get_db()
            cur = con.cursor()
            cur.execute(
                "INSERT INTO users(name, email, password, role) VALUES (?,?,?,?)",
                (name, email, password, role)
            )
            con.commit()
            con.close()
        except sqlite3.IntegrityError:
            return "Email already registered"

        return redirect(url_for("login"))

    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        con = get_db()
        cur = con.cursor()
        cur.execute(
            "SELECT name, email, role FROM users WHERE email=? AND password=?",
            (email, password)
        )
        user = cur.fetchone()
        con.close()

        if user:
            session["name"] = user[0]
            session["email"] = user[1]
            session["role"] = user[2]

            # ✅ ROLE BASED REDIRECT (THIS IS THE KEY)
            if user[2] == "provider":
                return redirect(url_for("post_job"))
            else:
                return redirect(url_for("jobs"))

        else:
            return "Invalid login"

    return render_template("login.html")


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- VIEW JOBS (LOGIN REQUIRED) ----------
@app.route("/jobs")
def jobs():
    if "email" not in session:
        return redirect(url_for("login"))

    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM jobs")
    jobs = cur.fetchall()
    con.close()

    return render_template("jobs.html", jobs=jobs)


# ---------- POST JOB (ONLY PROVIDER) ----------
@app.route("/post", methods=["GET", "POST"])
def post_job():
    if "email" not in session or session["role"] != "provider":
        return redirect(url_for("jobs"))

    if request.method == "POST":
        title = request.form.get("title")
        desc = request.form.get("description")

        con = get_db()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO jobs(title, description) VALUES (?,?)",
            (title, desc)
        )
        con.commit()
        con.close()

        return redirect(url_for("jobs"))

    return render_template("post_job.html")


# ---------- APPLY JOB (STUDENT / FREELANCER) ----------
@app.route("/apply/<int:job_id>", methods=["GET", "POST"])
def apply(job_id):
    # Only logged-in job seekers can apply
    if "email" not in session or session["role"] != "seeker":
        return redirect(url_for("login"))

    if request.method == "POST":
        con = get_db()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO applications (job_id, applicant_email) VALUES (?, ?)",
            (job_id, session["email"])
        )
        con.commit()
        con.close()

        return redirect(url_for("payment"))

    return render_template("apply.html", job_id=job_id)

# ---------- PAYMENT ----------
@app.route("/payment", methods=["GET", "POST"])
def payment():
    if "email" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        return redirect(url_for("review"))

    return render_template("payment.html")


# ---------- REVIEW ----------
@app.route("/review", methods=["GET", "POST"])
def review():
    if "email" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        rating = request.form.get("rating")
        comment = request.form.get("comment")

        con = get_db()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO reviews(rating, comment) VALUES (?,?)",
            (rating, comment)
        )
        con.commit()
        con.close()

        return redirect(url_for("jobs"))

    return render_template("review.html")


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
