from flask import Flask, request, redirect, url_for, session, render_template_string
import sqlite3
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = "QUIZNOVA_SECRET_2026"
DB = "quiznova.db"


# =========================================================
# DATABASE
# =========================================================

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    con = db()

    con.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll TEXT UNIQUE NOT NULL,
            email TEXT DEFAULT '',
            present INTEGER DEFAULT 0
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS exams(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT NOT NULL,
            duration INTEGER DEFAULT 15,
            passing INTEGER DEFAULT 40,
            status TEXT DEFAULT 'Active'
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS questions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER,
            question TEXT NOT NULL,
            qtype TEXT DEFAULT 'mcq',
            option_a TEXT DEFAULT '',
            option_b TEXT DEFAULT '',
            option_c TEXT DEFAULT '',
            option_d TEXT DEFAULT '',
            answer TEXT DEFAULT '',
            marks INTEGER DEFAULT 1
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS attempts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            exam_id INTEGER,
            score INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0,
            percentage REAL DEFAULT 0,
            status TEXT DEFAULT 'FAIL',
            submitted_at TEXT
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS answers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attempt_id INTEGER,
            question_id INTEGER,
            answer TEXT
        )
    """)

    # Demo exam only on first run
    if con.execute("SELECT COUNT(*) FROM exams").fetchone()[0] == 0:

        cur = con.execute("""
            INSERT INTO exams(title,subject,duration,passing)
            VALUES(?,?,?,?)
        """, (
            "Computer Science Smart Assessment",
            "Computer Science",
            15,
            40
        ))

        exam_id = cur.lastrowid

        demo_questions = [
            (exam_id, "Which language is used to structure web pages?",
             "mcq", "HTML", "CSS", "Python", "SQL", "HTML", 1),

            (exam_id, "Which language is mainly used for styling web pages?",
             "mcq", "HTML", "CSS", "JavaScript", "SQL", "CSS", 1),

            (exam_id, "Which language adds interactivity to webpages?",
             "mcq", "HTML", "CSS", "JavaScript", "SQL", "JavaScript", 1),

            (exam_id, "What does CPU stand for?",
             "mcq", "Central Processing Unit", "Computer Processing Unit",
             "Central Program Unit", "Control Processing Unit",
             "Central Processing Unit", 1),

            (exam_id, "Which one is an operating system?",
             "mcq", "Windows", "HTML", "CSS", "SQL", "Windows", 1),

            (exam_id, "Which language is commonly used to manage databases?",
             "mcq", "CSS", "SQL", "HTML", "Photoshop", "SQL", 1),

            (exam_id, "What is the full form of RAM?",
             "mcq", "Random Access Memory", "Read Access Memory",
             "Rapid Access Machine", "Random Application Module",
             "Random Access Memory", 1),

            (exam_id, "Which device connects computers to a network?",
             "mcq", "Router", "Keyboard", "Monitor", "Printer", "Router", 1),

            (exam_id, "What is an online examination system?",
             "subjective", "", "", "", "", "", 2),

            (exam_id, "Write two advantages of online examinations.",
             "subjective", "", "", "", "", "", 2)
        ]

        con.executemany("""
            INSERT INTO questions(
                exam_id,question,qtype,
                option_a,option_b,option_c,option_d,
                answer,marks
            )
            VALUES(?,?,?,?,?,?,?,?,?)
        """, demo_questions)

    con.commit()
    con.close()


init_db()


# =========================================================
# MODERN 3D STYLE
# =========================================================

STYLE = """
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

*{
    box-sizing:border-box;
    margin:0;
    padding:0;
}

html{
    scroll-behavior:smooth;
}

body{
    font-family:Inter,Arial,sans-serif;
    background:
        radial-gradient(circle at 15% 15%,#352c8950,transparent 28%),
        radial-gradient(circle at 85% 70%,#00b8ff20,transparent 30%),
        #050712;
    color:#f7f8ff;
    min-height:100vh;
    overflow-x:hidden;
}

body:before{
    content:"";
    position:fixed;
    inset:0;
    pointer-events:none;
    background-image:
        linear-gradient(#ffffff04 1px,transparent 1px),
        linear-gradient(90deg,#ffffff04 1px,transparent 1px);
    background-size:45px 45px;
    mask-image:linear-gradient(to bottom,black,transparent);
}

a{
    text-decoration:none;
    color:inherit;
}

button,input,textarea,select{
    font-family:inherit;
}

.layout{
    min-height:100vh;
}

.sidebar{
    position:fixed;
    left:0;
    top:0;
    bottom:0;
    width:255px;
    padding:25px 16px;
    z-index:20;
    background:rgba(8,12,27,.86);
    backdrop-filter:blur(20px);
    border-right:1px solid #ffffff12;
}

.logo{
    font-size:27px;
    font-weight:900;
    padding:5px 14px 35px;
    letter-spacing:-1px;
}

.logo span{
    color:#8c72ff;
}

.menu-title{
    font-size:10px;
    color:#69728e;
    letter-spacing:1.5px;
    font-weight:800;
    padding:12px 14px;
}

.menu a{
    display:block;
    padding:13px 15px;
    margin:5px 0;
    color:#9ba5c0;
    border-radius:13px;
    transition:.25s;
}

.menu a:hover{
    color:#fff;
    background:linear-gradient(135deg,#7060ff20,#00c8ff10);
    transform:translateX(5px);
    box-shadow:0 8px 25px #0005;
}

.main{
    margin-left:255px;
    padding:30px;
    width:calc(100% - 255px);
}

.topbar{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:25px;
    gap:15px;
}

.topbar h1{
    font-size:28px;
}

.user-pill{
    padding:10px 15px;
    border-radius:13px;
    border:1px solid #ffffff14;
    background:#11172a;
    color:#bac2da;
}

.hero{
    position:relative;
    overflow:hidden;
    min-height:330px;
    padding:45px;
    border-radius:30px;
    border:1px solid #ffffff18;
    background:
        radial-gradient(circle at 80% 30%,#806dff55,transparent 28%),
        radial-gradient(circle at 100% 100%,#00c8ff35,transparent 30%),
        linear-gradient(135deg,#141a3c,#211b4e,#0e1830);
    box-shadow:
        0 35px 90px #0009,
        inset 0 1px 1px #ffffff20;
    transform-style:preserve-3d;
}

.hero:hover{
    transform:perspective(1000px) rotateX(1deg) rotateY(-1deg);
}

.hero h2{
    position:relative;
    z-index:2;
    font-size:42px;
    line-height:1.12;
    max-width:760px;
    margin:15px 0;
}

.hero p{
    position:relative;
    z-index:2;
    color:#b7c0d9;
    line-height:1.8;
    max-width:720px;
}

.badge{
    display:inline-block;
    padding:7px 12px;
    border-radius:20px;
    background:#806eff1c;
    border:1px solid #907fff35;
    color:#a99cff;
    font-size:10px;
    font-weight:800;
    letter-spacing:1px;
}

.orb{
    position:absolute;
    width:190px;
    height:190px;
    right:100px;
    top:60px;
    border-radius:50%;
    background:
        radial-gradient(circle at 30% 25%,#fff8,transparent 5%),
        linear-gradient(135deg,#806aff,#00caff);
    opacity:.25;
    filter:blur(.2px);
    box-shadow:
        0 0 80px #806aff,
        inset -30px -30px 60px #0008;
    animation:float 5s ease-in-out infinite;
}

.orb2{
    position:absolute;
    width:80px;
    height:80px;
    right:70px;
    bottom:35px;
    border-radius:25px;
    background:#00caff;
    opacity:.25;
    transform:rotate(35deg);
    animation:spin 9s linear infinite;
}

@keyframes float{
    0%,100%{transform:translateY(0) rotate(0)}
    50%{transform:translateY(-20px) rotate(8deg)}
}

@keyframes spin{
    to{transform:rotate(395deg)}
}

.cards{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:17px;
    margin:22px 0;
}

.card{
    background:linear-gradient(145deg,#11182b,#0c1222);
    border:1px solid #ffffff12;
    border-radius:21px;
    padding:23px;
    box-shadow:
        0 20px 45px #0006,
        inset 0 1px 0 #ffffff08;
}

.card:hover{
    border-color:#8977ff35;
    transform:translateY(-3px);
    transition:.25s;
}

.stat-title{
    color:#707b99;
    font-size:11px;
    font-weight:700;
}

.stat{
    font-size:29px;
    font-weight:900;
    margin-top:9px;
}

.purple{color:#a08dff}
.green{color:#54e4a1}
.blue{color:#5ec4ff}
.orange{color:#ffc06e}
.red{color:#ff718e}

.grid{
    display:grid;
    grid-template-columns:2fr 1fr;
    gap:18px;
}

.exam-card{
    background:linear-gradient(145deg,#11182b,#0c1222);
    border:1px solid #ffffff12;
    border-radius:21px;
    padding:25px;
    margin-bottom:17px;
    box-shadow:0 18px 45px #0005;
}

.exam-card h2,
.exam-card h3{
    margin:10px 0;
}

.muted{
    color:#818ba7;
    font-size:13px;
    line-height:1.8;
}

.btn{
    display:inline-block;
    border:0;
    padding:13px 19px;
    border-radius:12px;
    margin-top:16px;
    font-weight:800;
    cursor:pointer;
    transition:.25s;
}

.btn:hover{
    transform:translateY(-3px) scale(1.01);
}

.primary{
    color:white;
    background:linear-gradient(135deg,#6958ff,#a35cff);
    box-shadow:0 12px 35px #765cff45;
}

.secondary{
    background:#171f35;
    color:#cbd2e6;
    border:1px solid #ffffff0e;
}

.danger{
    background:#351827;
    color:#ff9db6;
}

.form-box{
    max-width:520px;
    margin:70px auto;
}

.form-box h1{
    margin:12px 0;
}

input,
textarea,
select{
    width:100%;
    padding:14px;
    margin:7px 0 15px;
    border:1px solid #293451;
    border-radius:12px;
    background:#080e1d;
    color:white;
    outline:none;
}

input:focus,
textarea:focus,
select:focus{
    border-color:#806eff;
    box-shadow:0 0 0 3px #806eff12;
}

textarea{
    min-height:120px;
    resize:vertical;
}

.exam-header{
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:20px;
    padding:21px;
    margin-bottom:18px;
    border-radius:18px;
    background:#10172a;
    border:1px solid #ffffff12;
}

.timer{
    min-width:105px;
    text-align:center;
    padding:13px 17px;
    border-radius:13px;
    background:#341d35;
    color:#ffb1cf;
    font-weight:900;
    font-size:19px;
    box-shadow:0 10px 30px #0005;
}

.question{
    margin-bottom:17px;
}

.question-number{
    color:#8e7cff;
    font-size:11px;
    font-weight:900;
    letter-spacing:.7px;
    margin-bottom:10px;
}

.question h3{
    line-height:1.6;
    margin-bottom:14px;
}

.option{
    display:block;
    padding:14px;
    margin:8px 0;
    border:1px solid #293451;
    background:#090f1e;
    border-radius:12px;
    cursor:pointer;
    transition:.2s;
}

.option:hover{
    background:#151d35;
    border-color:#7768ff;
    transform:translateX(3px);
}

.option input{
    width:auto;
    margin:0 8px 0 0;
}

.palette{
    display:flex;
    gap:7px;
    flex-wrap:wrap;
}

.palette span{
    width:33px;
    height:33px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#202943;
    border-radius:8px;
    font-size:11px;
}

.progress{
    height:8px;
    background:#202943;
    border-radius:20px;
    overflow:hidden;
    margin-top:13px;
}

.progress div{
    height:100%;
    background:linear-gradient(90deg,#6658ff,#b45cff);
}

.three{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:14px;
}

.result{
    max-width:800px;
    margin:50px auto;
    text-align:center;
}

.score{
    font-size:75px;
    font-weight:900;
    color:#9584ff;
    margin:22px;
    text-shadow:0 0 35px #7865ff55;
}

table{
    width:100%;
    border-collapse:collapse;
}

th,td{
    padding:14px;
    text-align:left;
    border-bottom:1px solid #ffffff10;
    font-size:13px;
}

th{
    color:#9889ff;
}

.certificate{
    max-width:920px;
    margin:40px auto;
    padding:65px;
    text-align:center;
    color:#171c35;
    background:
        radial-gradient(circle at 50% 0%,#c9c0ff,#fff 30%),
        white;
    border:12px solid #7563e9;
    box-shadow:0 30px 90px #0009;
}

.certificate h1{
    color:#4939b9;
    font-size:40px;
    margin:18px;
}

.student-name{
    font-size:36px;
    font-weight:900;
    margin:25px;
}

.feature-grid{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:17px;
    margin-top:20px;
}

.feature{
    min-height:150px;
}

@media(max-width:950px){

    .sidebar{
        width:72px;
        padding:20px 8px;
    }

    .logo{
        font-size:0;
        text-align:center;
    }

    .logo:first-letter{
        font-size:27px;
    }

    .menu a{
        font-size:0;
        text-align:center;
        padding:13px 5px;
    }

    .main{
        margin-left:72px;
        width:calc(100% - 72px);
        padding:18px;
    }

    .cards{
        grid-template-columns:1fr 1fr;
    }

    .grid{
        grid-template-columns:1fr;
    }

    .feature-grid{
        grid-template-columns:1fr 1fr;
    }

    .orb{
        display:none;
    }
}

@media(max-width:600px){

    .cards,
    .three,
    .feature-grid{
        grid-template-columns:1fr;
    }

    .hero{
        padding:27px;
        min-height:300px;
    }

    .hero h2{
        font-size:28px;
    }

    .topbar{
        align-items:flex-start;
        flex-direction:column;
    }

    .exam-header{
        align-items:flex-start;
        flex-direction:column;
    }

    .certificate{
        padding:35px 14px;
        border-width:7px;
    }

    .certificate h1{
        font-size:27px;
    }

    .student-name{
        font-size:26px;
    }
}

@media print{

    body{
        background:white;
    }

    .certificate{
        box-shadow:none;
        margin:0;
    }

    .btn{
        display:none;
    }
}

</style>
"""


# =========================================================
# SIDEBARS
# =========================================================

def student_sidebar():
    return """
    <aside class="sidebar">
        <div class="logo">QUIZ<span>NOVA</span></div>

        <div class="menu-title">STUDENT</div>

        <div class="menu">
            <a href="/dashboard">🏠 Dashboard</a>
            <a href="/exams">📝 Examinations</a>
            <a href="/attendance">📅 Attendance</a>
            <a href="/results">📊 Results</a>
            <a href="/leaderboard">🏆 Leaderboard</a>
            <a href="/profile">👤 Profile</a>
            <a href="/logout">🚪 Logout</a>
        </div>
    </aside>
    """


def admin_sidebar():
    return """
    <aside class="sidebar">
        <div class="logo">QUIZ<span>NOVA</span></div>

        <div class="menu-title">ADMIN</div>

        <div class="menu">
            <a href="/admin">📊 Dashboard</a>
            <a href="/admin/students">👥 Students</a>
            <a href="/admin/exams">📝 Exams</a>
            <a href="/admin/questions">❓ Question Bank</a>
            <a href="/admin/results">📈 Results</a>
            <a href="/admin/attendance">📅 Attendance</a>
            <a href="/logout">🚪 Logout</a>
        </div>
    </aside>
    """


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template_string(STYLE + """
    <main class="main" style="margin-left:0;width:100%;max-width:1300px;margin:auto">

        <div class="topbar">
            <h1>🚀 QuizNova</h1>

            <div class="user-pill">
                Smart Online Examination System
            </div>
        </div>

        <section class="hero">

            <div class="orb"></div>
            <div class="orb2"></div>

            <span class="badge">NEXT GENERATION EXAMINATION PLATFORM</span>

            <h2>
                Smarter Exams.<br>
                Better Performance.
            </h2>

            <p>
                QuizNova is a complete online examination platform
                designed for students, teachers and administrators.
                Create exams, manage questions, conduct tests,
                generate results and issue digital certificates.
            </p>

            <a href="/login" class="btn primary">
                Enter Student Portal →
            </a>

            <a href="/admin/login" class="btn secondary">
                Admin Portal
            </a>

        </section>

        <div class="cards">

            <div class="card">
                <div class="stat-title">EXAMINATION</div>
                <div class="stat purple">ONLINE</div>
            </div>

            <div class="card">
                <div class="stat-title">RESULTS</div>
                <div class="stat green">AUTO</div>
            </div>

            <div class="card">
                <div class="stat-title">QUESTIONS</div>
                <div class="stat blue">SMART</div>
            </div>

            <div class="card">
                <div class="stat-title">CERTIFICATE</div>
                <div class="stat orange">DIGITAL</div>
            </div>

        </div>

        <div class="feature-grid">

            <div class="card feature">
                <h2>🧠 Smart Assessment</h2>
                <p class="muted">
                    MCQ and subjective questions with automatic
                    MCQ evaluation.
                </p>
            </div>

            <div class="card feature">
                <h2>⏱️ Live Timer</h2>
                <p class="muted">
                    Timed examination with automatic submission.
                </p>
            </div>

            <div class="card feature">
                <h2>📊 Analytics</h2>
                <p class="muted">
                    Results, percentage, performance and history.
                </p>
            </div>

            <div class="card feature">
                <h2>👨‍💼 Admin Control</h2>
                <p class="muted">
                    Create exams and add questions without changing code.
                </p>
            </div>

            <div class="card feature">
                <h2>🏆 Leaderboard</h2>
                <p class="muted">
                    Display best student performance.
                </p>
            </div>

            <div class="card feature">
                <h2>🎓 Certificate</h2>
                <p class="muted">
                    Generate and print digital achievement certificates.
                </p>
            </div>

        </div>

    </main>
    """)


# =========================================================
# STUDENT LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        roll = request.form.get("roll", "").strip()
        email = request.form.get("email", "").strip()

        if not name or not roll:
            return "Name and Roll Number are required."

        con = db()

        student = con.execute(
            "SELECT * FROM students WHERE roll=?",
            (roll,)
        ).fetchone()

        if student:
            con.execute("""
                UPDATE students
                SET name=?, email=?, present=1
                WHERE roll=?
            """, (name, email, roll))
        else:
            con.execute("""
                INSERT INTO students(name,roll,email,present)
                VALUES(?,?,?,1)
            """, (name, roll, email))

        con.commit()

        student = con.execute(
            "SELECT * FROM students WHERE roll=?",
            (roll,)
        ).fetchone()

        con.close()

        session["student_id"] = student["id"]

        return redirect("/dashboard")

    return render_template_string(STYLE + """
    <div class="form-box card">

        <span class="badge">STUDENT PORTAL</span>

        <h1>Welcome to QuizNova 👋</h1>

        <p class="muted">
            Enter your details to access your examination dashboard.
        </p>

        <form method="POST">

            <label>Full Name</label>
            <input name="name" placeholder="Enter your name" required>

            <label>Roll Number</label>
            <input name="roll" placeholder="Enter roll number" required>

            <label>Email</label>
            <input type="email" name="email" placeholder="Enter email">

            <button class="btn primary" style="width:100%">
                Enter Student Portal →
            </button>

        </form>

        <a href="/" class="btn secondary">Back Home</a>

    </div>
    """)


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "student_id" not in session:
        return redirect("/login")

    con = db()

    student = con.execute(
        "SELECT * FROM students WHERE id=?",
        (session["student_id"],)
    ).fetchone()

    exams = con.execute(
        "SELECT * FROM exams WHERE status='Active'"
    ).fetchall()

    attempts = con.execute("""
        SELECT attempts.*, exams.title
        FROM attempts
        JOIN exams ON exams.id=attempts.exam_id
        WHERE student_id=?
        ORDER BY attempts.id DESC
    """, (student["id"],)).fetchall()

    con.close()

    average = 0

    if attempts:
        average = round(
            sum(a["percentage"] for a in attempts) / len(attempts),
            1
        )

    return render_template_string(STYLE + """
    <div class="layout">

        {{ sidebar|safe }}

        <main class="main">

            <div class="topbar">

                <h1>Hello, {{ student["name"] }} 👋</h1>

                <div class="user-pill">
                    Roll: {{ student["roll"] }}
                </div>

            </div>

            <section class="hero">

                <div class="orb"></div>

                <span class="badge">STUDENT DASHBOARD</span>

                <h2>Your examination journey starts here.</h2>

                <p>
                    Attempt examinations, track performance,
                    view results and earn digital certificates.
                </p>

                <a href="/exams" class="btn primary">
                    Explore Examinations →
                </a>

            </section>

            <div class="cards">

                <div class="card">
                    <div class="stat-title">ATTENDANCE</div>
                    <div class="stat green">
                        {{ "PRESENT" if student["present"] else "ABSENT" }}
                    </div>
                </div>

                <div class="card">
                    <div class="stat-title">ATTEMPTS</div>
                    <div class="stat purple">
                        {{ attempts|length }}
                    </div>
                </div>

                <div class="card">
                    <div class="stat-title">AVERAGE</div>
                    <div class="stat blue">
                        {{ average }}%
                    </div>
                </div>

                <div class="card">
                    <div class="stat-title">ACCOUNT</div>
                    <div class="stat green">ACTIVE</div>
                </div>

            </div>

            <div class="grid">

                <div class="exam-card">

                    <span class="badge">AVAILABLE EXAM</span>

                    {% if exams %}

                        <h2>{{ exams[0]["title"] }}</h2>

                        <p class="muted">
                            Subject: {{ exams[0]["subject"] }}<br>
                            Duration: {{ exams[0]["duration"] }} minutes<br>
                            Passing: {{ exams[0]["passing"] }}%
                        </p>

                        <a class="btn primary"
                           href="/instructions/{{ exams[0]['id'] }}">
                            Start Examination →
                        </a>

                    {% else %}

                        <h3>No active examinations.</h3>

                    {% endif %}

                </div>

                <div class="exam-card">

                    <span class="badge">PERFORMANCE</span>

                    <h2>{{ average }}%</h2>

                    <p class="muted">
                        Overall examination performance
                    </p>

                    <div class="progress">
                        <div style="width:{{ average }}%"></div>
                    </div>

                </div>

            </div>

        </main>

    </div>
    """,
    sidebar=student_sidebar(),
    student=student,
    exams=exams,
    attempts=attempts,
    average=average)


# =========================================================
# EXAMS
# =========================================================

@app.route("/exams")
def exams():

    if "student_id" not in session:
        return redirect("/login")

    con = db()

    exams = con.execute(
        "SELECT * FROM exams WHERE status='Active'"
    ).fetchall()

    con.close()

    return render_template_string(STYLE + """
    <div class="layout">

        {{ sidebar|safe }}

        <main class="main">

            <div class="topbar">
                <h1>📝 Available Examinations</h1>
            </div>

            {% for exam in exams %}

            <div class="exam-card">

                <span class="badge">{{ exam["subject"] }}</span>

                <h2>{{ exam["title"] }}</h2>

                <p class="muted">
                    ⏱ {{ exam["duration"] }} Minutes
                    &nbsp; • &nbsp;
                    🎯 Passing {{ exam["passing"] }}%
                    &nbsp; • &nbsp;
                    📝 MCQ + Subjective
                </p>

                <a class="btn primary"
                   href="/instructions/{{ exam['id'] }}">
                    View Examination →
                </a>

            </div>

            {% else %}

            <div class="card">
                No examinations available.
            </div>

            {% endfor %}

        </main>

    </div>
    """,
    sidebar=student_sidebar(),
    exams=exams)


# =========================================================
# INSTRUCTIONS
# =========================================================

@app.route("/instructions/<int:exam_id>")
def instructions(exam_id):

    if "student_id" not in session:
        return redirect("/login")

    con = db()

    exam = con.execute(
        "SELECT * FROM exams WHERE id=?",
        (exam_id,)
    ).fetchone()

    con.close()

    if not exam:
        return "Exam not found."

    return render_template_string(STYLE + """
    <div class="form-box card">

        <span class="badge">EXAM INSTRUCTIONS</span>

        <h1>{{ exam["title"] }}</h1>

        <p class="muted">
            Please read the instructions before starting.
        </p>

        <div class="card">

            <p class="muted">
                ✓ Duration: {{ exam["duration"] }} minutes<br><br>
                ✓ MCQ answers are automatically evaluated<br><br>
                ✓ Subjective answers are stored for review<br><br>
                ✓ Exam automatically submits when timer ends<br><br>
                ✓ Do not close the examination page
            </p>

        </div>

        <a class="btn primary"
           href="/take-exam/{{ exam['id'] }}">
            I Understand — Start Exam →
        </a>

        <a class="btn secondary" href="/exams">
            Back
        </a>

    </div>
    """, exam=exam)


# =========================================================
# TAKE EXAM
# =========================================================

@app.route("/take-exam/<int:exam_id>")
def take_exam(exam_id):

    if "student_id" not in session:
        return redirect("/login")

    con = db()

    exam = con.execute(
        "SELECT * FROM exams WHERE id=?",
        (exam_id,)
    ).fetchone()

    questions = con.execute("""
        SELECT * FROM questions
        WHERE exam_id=?
    """, (exam_id,)).fetchall()

    con.close()

    if not exam:
        return "Exam not found."

    questions = list(questions)
    random.shuffle(questions)

    return render_template_string(STYLE + """
    <main class="main"
          style="margin-left:0;width:100%;max-width:1050px;margin:auto">

        <div class="exam-header">

            <div>
                <span class="badge">LIVE EXAMINATION</span>
                <h2>{{ exam["title"] }}</h2>
            </div>

            <div class="timer" id="timer">
                {{ exam["duration"] }}:00
            </div>

        </div>

        <form id="examForm"
              method="POST"
              action="/submit/{{ exam['id'] }}">

            {% for q in questions %}

            <div class="card question">

                <div class="question-number">
                    QUESTION {{ loop.index }} • {{ q["marks"] }} MARK
                </div>

                <h3>{{ q["question"] }}</h3>

                {% if q["qtype"] == "mcq" %}

                    <label class="option">
                        <input type="radio"
                               name="q{{ q['id'] }}"
                               value="{{ q['option_a'] }}">
                        {{ q["option_a"] }}
                    </label>

                    <label class="option">
                        <input type="radio"
                               name="q{{ q['id'] }}"
                               value="{{ q['option_b'] }}">
                        {{ q["option_b"] }}
                    </label>

                    <label class="option">
                        <input type="radio"
                               name="q{{ q['id'] }}"
                               value="{{ q['option_c'] }}">
                        {{ q["option_c"] }}
                    </label>

                    <label class="option">
                        <input type="radio"
                               name="q{{ q['id'] }}"
                               value="{{ q['option_d'] }}">
                        {{ q["option_d"] }}
                    </label>

                {% else %}

                    <textarea
                        name="q{{ q['id'] }}"
                        placeholder="Write your answer here..."></textarea>

                {% endif %}

            </div>

            {% endfor %}

            <div class="card">

                <div class="question-number">
                    QUESTION PALETTE
                </div>

                <div class="palette">

                    {% for q in questions %}
                        <span>{{ loop.index }}</span>
                    {% endfor %}

                </div>

            </div>

            <button class="btn primary"
                    type="submit"
                    onclick="return confirm('Submit your examination?')">
                Submit Examination ✓
            </button>

        </form>

    </main>

    <script>

    let seconds = {{ exam["duration"] }} * 60;
    const timer = document.getElementById("timer");
    const form = document.getElementById("examForm");

    function updateTimer(){

        let minutes = Math.floor(seconds / 60);
        let secs = seconds % 60;

        if(secs < 10){
            secs = "0" + secs;
        }

        timer.innerHTML = minutes + ":" + secs;

        if(seconds <= 0){
            alert("Time is over. Your examination will be submitted.");
            form.submit();
            return;
        }

        seconds--;
    }

    updateTimer();
    setInterval(updateTimer,1000);

    </script>
    """,
    exam=exam,
    questions=questions)


# =========================================================
# SUBMIT EXAM
# =========================================================

@app.route("/submit/<int:exam_id>", methods=["POST"])
def submit_exam(exam_id):

    if "student_id" not in session:
        return redirect("/login")

    con = db()

    exam = con.execute(
        "SELECT * FROM exams WHERE id=?",
        (exam_id,)
    ).fetchone()

    questions = con.execute(
        "SELECT * FROM questions WHERE exam_id=?",
        (exam_id,)
    ).fetchall()

    score = 0
    total = 0
    submitted_answers = []

    for q in questions:

        answer = request.form.get("q" + str(q["id"]), "")

        submitted_answers.append((q["id"], answer))

        if q["qtype"] == "mcq":

            total += q["marks"]

            if answer == q["answer"]:
                score += q["marks"]

    percentage = 0

    if total:
        percentage = round((score / total) * 100, 2)

    status = "PASS" if percentage >= exam["passing"] else "FAIL"

    cur = con.execute("""
        INSERT INTO attempts(
            student_id,exam_id,score,total,
            percentage,status,submitted_at
        )
        VALUES(?,?,?,?,?,?,?)
    """, (
        session["student_id"],
        exam_id,
        score,
        total,
        percentage,
        status,
        datetime.now().strftime("%d-%m-%Y %I:%M %p")
    ))

    attempt_id = cur.lastrowid

    for qid, answer in submitted_answers:

        con.execute("""
            INSERT INTO answers(
                attempt_id,question_id,answer
            )
            VALUES(?,?,?)
        """, (attempt_id, qid, answer))

    con.commit()
    con.close()

    return redirect(url_for("result", attempt_id=attempt_id))


# =========================================================
# RESULT
# =========================================================

@app.route("/result/<int:attempt_id>")
def result(attempt_id):

    if "student_id" not in session:
        return redirect("/login")

    con = db()

    attempt = con.execute("""
        SELECT attempts.*, exams.title, exams.subject
        FROM attempts
        JOIN exams ON exams.id=attempts.exam_id
        WHERE attempts.id=?
        AND attempts.student_id=?
    """, (
        attempt_id,
        session["student_id"]
    )).fetchone()

    con.close()

    if not attempt:
        return "Result not found."

    return render_template_string(STYLE + """
    <div class="layout">

        {{ sidebar|safe }}

        <main class="main">

            <div class="result card">

                <span class="badge">EXAM COMPLETED</span>

                <h1>Your Result</h1>

                <p class="muted">
                    {{ attempt["title"] }}
                </p>

                <div class="score">
                    {{ attempt["percentage"] }}%
                </div>

                <div class="three">

                    <div class="card">
                        <div class="stat-title">SCORE</div>
                        <div class="stat purple">
                            {{ attempt["score"] }}/{{ attempt["total"] }}
                        </div>
                    </div>

                    <div class="card">
                        <div class="stat-title">PERCENTAGE</div>
                        <div class="stat blue">
                            {{ attempt["percentage"] }}%
                        </div>
                    </div>

                    <div class="card">
                        <div class="stat-title">STATUS</div>
                        <div class="stat green">
                            {{ attempt["status"] }}
                        </div>
                    </div>

                </div>

                <a class="btn primary"
                   href="/certificate/{{ attempt['id'] }}">
                    🏆 View Certificate
                </a>

                <a class="btn secondary"
                   href="/results">
                    Result History
                </a>

            </div>

        </main>

    </div>
    """,
    sidebar=student_sidebar(),
    attempt=attempt)


# =========================================================
# RESULTS HISTORY
# =========================================================

@app.route("/results")
def results():

    if "student_id" not in session:
        return redirect("/login")

    con = db()

    rows = con.execute("""
        SELECT attempts.*, exams.title
        FROM attempts
        JOIN exams ON exams.id=attempts.exam_id
        WHERE attempts.student_id=?
        ORDER BY attempts.id DESC
    """, (session["student_id"],)).fetchall()

    con.close()

    return render_template_string(STYLE + """
    <div class="layout">

        {{ sidebar|safe }}

        <main class="main">

            <div class="topbar">
                <h1>📊 Result History</h1>
            </div>

            <div class="card">

                <table>

                    <tr>
                        <th>EXAM</th>
                        <th>SCORE</th>
                        <th>PERCENTAGE</th>
                        <th>STATUS</th>
                        <th>DATE</th>
                    </tr>

                    {% for r in rows %}

                    <tr>
                        <td>{{ r["title"] }}</td>
                        <td>{{ r["score"] }}/{{ r["total"] }}</td>
                        <td>{{ r["percentage"] }}%</td>
                        <td>{{ r["status"] }}</td>
                        <td>{{ r["submitted_at"] }}</td>
                    </tr>

                    {% else %}

                    <tr>
                        <td colspan="5">No results available.</td>
                    </tr>

                    {% endfor %}

                </table>

            </div>

        </main>

    </div>
    """,
    sidebar=student_sidebar(),
    rows=rows)


# =========================================================
# ATTENDANCE
# =========================================================

@app.route("/attendance")
def attendance():

    if "student_id" not in session:
        return redirect("/login")

    con = db()

    student = con.execute(
        "SELECT * FROM students WHERE id=?",
        (session["student_id"],)
    ).fetchone()

    con.close()

    return render_template_string(STYLE + """
    <div class="layout">

        {{ sidebar|safe }}

        <main class="main">

            <div class="topbar">
                <h1>📅 Attendance</h1>
            </div>

            <div class="card">

                <span class="badge">EXAM ATTENDANCE</span>

                <h2 style="margin:15px 0">
                    {{ "PRESENT" if student["present"] else "ABSENT" }}
                </h2>

                <p class="muted">
                    Attendance is recorded when the student enters
                    the examination portal.
                </p>

            </div>

        </main>

    </div>
    """,
    sidebar=student_sidebar(),
    student=student)


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
def profile():

    if "student_id" not in session:
        return redirect("/login")

    con = db()

    student = con.execute(
        "SELECT * FROM students WHERE id=?",
        (session["student_id"],)
    ).fetchone()

    con.close()

    return render_template_string(STYLE + """
    <div class="layout">

        {{ sidebar|safe }}

        <main class="main">

            <div class="topbar">
                <h1>👤 My Profile</h1>
            </div>

            <div class="card">

                <h2>{{ student["name"] }}</h2>

                <p class="muted">
                    Student ID: {{ student["id"] }}<br>
                    Roll Number: {{ student["roll"] }}<br>
                    Email: {{ student["email"] or "Not added" }}<br>
                    Attendance:
                    {{ "Present" if student["present"] else "Absent" }}
                </p>

            </div>

        </main>

    </div>
    """,
    sidebar=student_sidebar(),
    student=student)


# =========================================================
# LEADERBOARD
# =========================================================

@app.route("/leaderboard")
def leaderboard():

    con = db()

    rows = con.execute("""
        SELECT
            students.name,
            students.roll,
            MAX(attempts.percentage) AS best_score
        FROM attempts
        JOIN students ON students.id=attempts.student_id
        GROUP BY students.id
        ORDER BY best_score DESC
        LIMIT 20
    """).fetchall()

    con.close()

    return render_template_string(STYLE + """
    <div class="layout">

        {{ sidebar|safe }}

        <main class="main">

            <div class="topbar">
                <h1>🏆 Leaderboard</h1>
            </div>

            <div class="card">

                <table>

                    <tr>
                        <th>RANK</th>
                        <th>STUDENT</th>
                        <th>ROLL</th>
                        <th>BEST SCORE</th>
                    </tr>

                    {% for row in rows %}

                    <tr>
                        <td>#{{ loop.index }}</td>
                        <td>{{ row["name"] }}</td>
                        <td>{{ row["roll"] }}</td>
                        <td>{{ row["best_score"] }}%</td>
                    </tr>

                    {% else %}

                    <tr>
                        <td colspan="4">
                            Leaderboard will appear after examinations.
                        </td>
                    </tr>

                    {% endfor %}

                </table>

            </div>

        </main>

    </div>
    """,
    sidebar=student_sidebar(),
    rows=rows)


# =========================================================
# CERTIFICATE
# =========================================================

@app.route("/certificate/<int:attempt_id>")
def certificate(attempt_id):

    if "student_id" not in session:
        return redirect("/login")

    con = db()

    attempt = con.execute("""
        SELECT *
        FROM attempts
        WHERE id=?
        AND student_id=?
    """, (
        attempt_id,
        session["student_id"]
    )).fetchone()

    if not attempt:
        con.close()
        return "Certificate record not found."

    student = con.execute(
        "SELECT * FROM students WHERE id=?",
        (attempt["student_id"],)
    ).fetchone()

    exam = con.execute(
        "SELECT * FROM exams WHERE id=?",
        (attempt["exam_id"],)
    ).fetchone()

    con.close()

    return render_template_string(STYLE + """
    <div class="certificate">

        <div style="font-size:60px">🏆</div>

        <p><strong>QUIZNOVA</strong></p>

        <h1>Certificate of Achievement</h1>

        <p>This certificate is proudly presented to</p>

        <div class="student-name">
            {{ student["name"] }}
        </div>

        <p>
            Roll Number:
            <strong>{{ student["roll"] }}</strong>
        </p>

        <br>

        <p>for successfully completing</p>

        <h2>{{ exam["title"] }}</h2>

        <br>

        <p>
            Score:
            <strong>
                {{ attempt["score"] }}/{{ attempt["total"] }}
            </strong>
        </p>

        <p>
            Percentage:
            <strong>{{ attempt["percentage"] }}%</strong>
        </p>

        <p>
            Result:
            <strong>{{ attempt["status"] }}</strong>
        </p>

        <br>

        <p>Date: {{ attempt["submitted_at"] }}</p>

        <button class="btn primary" onclick="window.print()">
            🖨 Print Certificate
        </button>

        <a href="/dashboard" class="btn secondary">
            Dashboard
        </a>

    </div>
    """,
    attempt=attempt,
    student=student,
    exam=exam)


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":

            session["admin"] = True
            return redirect("/admin")

        return render_template_string(STYLE + """
        <div class="form-box card">

            <h1>Login Failed</h1>

            <p class="muted">
                Incorrect username or password.
            </p>

            <a href="/admin/login" class="btn primary">
                Try Again
            </a>

        </div>
        """)

    return render_template_string(STYLE + """
    <div class="form-box card">

        <span class="badge">ADMIN PORTAL</span>

        <h1>QuizNova Administration</h1>

        <p class="muted">
            Create examinations, manage students,
            add questions and view results.
        </p>

        <form method="POST">

            <label>Username</label>
            <input name="username" placeholder="admin" required>

            <label>Password</label>
            <input type="password"
                   name="password"
                   placeholder="admin123"
                   required>

            <button class="btn primary" style="width:100%">
                Login to Admin Panel →
            </button>

        </form>

        <p class="muted" style="margin-top:15px">
            Demo Login: admin / admin123
        </p>

    </div>
    """)


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin():

    if not session.get("admin"):
        return redirect("/admin/login")

    con = db()

    students = con.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    exams = con.execute(
        "SELECT COUNT(*) FROM exams"
    ).fetchone()[0]

    questions = con.execute(
        "SELECT COUNT(*) FROM questions"
    ).fetchone()[0]

    attempts = con.execute(
        "SELECT COUNT(*) FROM attempts"
    ).fetchone()[0]

    con.close()

    return render_template_string(STYLE + """
    <div class="layout">

        {{ sidebar|safe }}

        <main class="main">

            <div class="topbar">

                <h1>Admin Dashboard</h1>

                <div class="user-pill">
                    Administrator
                </div>

            </div>

            <section class="hero">

                <div class="orb"></div>

                <span class="badge">ADMIN CONTROL CENTER</span>

                <h2>Manage the complete examination ecosystem.</h2>

                <p>
                    Create papers, build your question bank,
                    manage students and monitor results.
                </p>

            </section>

            <div class="cards">

                <div class="card">
                    <div class="stat-title">STUDENTS</div>
                    <div class="stat purple">{{ students }}</div>
                </div>

                <div class="card">
                    <div class="stat-title">EXAMS</div>
                    <div class="stat blue">{{ exams }}</div>
                </div>

                <div class="card">
                    <div class="stat-title">QUESTIONS</div>
                    <div class="stat orange">{{ questions }}</div>
                </div>

                <div class="card">
                    <div class="stat-title">ATTEMPTS</div>
                    <div class="stat green">{{ attempts }}</div>
                </div>

            </div>

            <div class="grid">

                <div class="exam-card">

                    <h2>⚡ Quick Management</h2>

                    <a class="btn primary" href="/admin/exams">
                        Create / Manage Exams
                    </a>

                    <a class="btn secondary"
                       href="/admin/questions">
                        Question Bank
                    </a>

                </div>

                <div class="exam-card">

                    <h2>📊 Reports</h2>

                    <a class="btn primary" href="/admin/results">
                        View Results
                    </a>

                    <a class="btn secondary"
                       href="/admin/attendance">
                        Attendance
                    </a>

                </div>

            </div>

        </main>

    </div>
    """,
    sidebar=admin_sidebar(),
    students=students,
    exams=exams,
    questions=questions,
    attempts=attempts)


# =========================================================
# ADMIN STUDENTS
# =========================================================

@app.route("/admin/students")
def admin_students():

    if not session.get("admin"):
        return redirect("/admin/login")

    con = db()

    students = con.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    con.close()

    return render_template_string(STYLE + """
    <div class="layout">

        {{ sidebar|safe }}

        <main class="main">

            <div class="topbar">
                <h1>👥 Student Management</h1>
            </div>

            <div class="card">

                <table>

                    <tr>
                        <th>ID</th>
                        <th>NAME</th>
                        <th>ROLL</th>
                        <th>EMAIL</th>
                        <th>ATTENDANCE</th>
                    </tr>

                    {% for s in students %}

                    <tr>
                        <td>{{ s["id"] }}</td>
                        <td>{{ s["name"] }}</td>
                        <td>{{ s["roll"] }}</td>
                        <td>{{ s["email"] }}</td>
                        <td>
                            {{ "PRESENT" if s["present"] else "ABSENT" }}
                        </td>
                    </tr>

                    {% endfor %}

                </table>

            </div>

        </main>

    </div>
    """,
    sidebar=admin_sidebar(),
    students=students)


# =========================================================
# ADMIN EXAMS
# =========================================================

@app.route("/admin/exams", methods=["GET", "POST"])
def admin_exams():

    if not session.get("admin"):
        return redirect("/admin/login")

    con = db()

    if request.method == "POST":

        title = request.form.get("title")
        subject = request.form.get("subject")

        try:
            duration = int(request.form.get("duration", 15))
        except:
            duration = 15

        try:
            passing = int(request.form.get("passing", 40))
        except:
            passing = 40

        con.execute("""
            INSERT INTO exams(
                title,subject,duration,passing
            )
            VALUES(?,?,?,?)
        """, (
            title,
            subject,
            duration,
            passing
        ))

        con.commit()

    exams = con.execute(
        "SELECT * FROM exams ORDER BY id DESC"
    ).fetchall()

    con.close()

    return render_template_string(STYLE + """
    <div class="layout">

        {{ sidebar|safe }}

        <main class="main">

            <div class="topbar">
                <h1>📝 Examination Management</h1>
            </div>

            <div class="grid">

                <div class="card">

                    <h2>Create New Paper</h2>

                    <p class="muted">
                        Create a new examination first.
                        Questions can then be added from Question Bank.
                    </p>

                    <form method="POST">

                        <label>Exam Title</label>
                        <input name="title"
                               placeholder="e.g. Cyber Security Assessment"
                               required>

                        <label>Subject</label>
                        <input name="subject"
                               placeholder="e.g. Cyber Security"
                               required>

                        <label>Duration (minutes)</label>
                        <input type="number"
                               name="duration"
                               value="30"
                               min="1">

                        <label>Passing Percentage</label>
                        <input type="number"
                               name="passing"
                               value="40"
                               min="1"
                               max="100">

                        <button class="btn primary">
                            + Create Examination
                        </button>

                    </form>

                </div>

                <div class="card">

                    <h2>Existing Papers</h2>

                    {% for e in exams %}

                    <div class="exam-card">

                        <span class="badge">
                            {{ e["subject"] }}
                        </span>

                        <h3>{{ e["title"] }}</h3>

                        <p class="muted">
                            ⏱ {{ e["duration"] }} minutes
                            • Passing {{ e["passing"] }}%
                        </p>

                    </div>

                    {% else %}

                    <p class="muted">
                        No exams created.
                    </p>

                    {% endfor %}

                </div>

            </div>

        </main>

    </div>
    """,
    sidebar=admin_sidebar(),
    exams=exams)


# =========================================================
# ADMIN QUESTION BANK
# =========================================================

@app.route("/admin/questions", methods=["GET", "POST"])
def admin_questions():

    if not session.get("admin"):
        return redirect("/admin/login")

    con = db()

    exams = con.execute(
        "SELECT * FROM exams ORDER BY id DESC"
    ).fetchall()

    if request.method == "POST":

        exam_id = request.form.get("exam_id")
        question = request.form.get("question")
        qtype = request.form.get("qtype")

        a = request.form.get("a", "")
        b = request.form.get("b", "")
        c = request.form.get("c", "")
        d = request.form.get("d", "")
        answer = request.form.get("answer", "")

        try:
            marks = int(request.form.get("marks", 1))
        except:
            marks = 1

        con.execute("""
            INSERT INTO questions(
                exam_id,question,qtype,
                option_a,option_b,option_c,
                option_d,answer,marks
            )
            VALUES(?,?,?,?,?,?,?,?,?)
        """, (
            exam_id,
            question,
            qtype,
            a,
            b,
            c,
            d,
            answer,
            marks
        ))

        con.commit()

    questions = con.execute("""
        SELECT questions.*, exams.title
        FROM questions
        JOIN exams ON exams.id=questions.exam_id
        ORDER BY questions.id DESC
    """).fetchall()

    con.close()

    return render_template_string(STYLE + """
    <div class="layout">

        {{ sidebar|safe }}

        <main class="main">

            <div class="topbar">
                <h1>❓ Question Bank</h1>
            </div>

            <div class="grid">

                <div class="card">

                    <h2>Add New Question</h2>

                    <p class="muted">
                        This allows the administrator to create
                        examination papers without changing the Python code.
                    </p>

                    <form method="POST">

                        <label>Exam / Paper</label>

                        <select name="exam_id" required>

                            {% for e in exams %}

                            <option value="{{ e['id'] }}">
                                {{ e["title"] }}
                            </option>

                            {% endfor %}

                        </select>

                        <label>Question Type</label>

                        <select name="qtype">
                            <option value="mcq">
                                Multiple Choice Question
                            </option>
                            <option value="subjective">
                                Subjective Question
                            </option>
                        </select>

                        <label>Question</label>

                        <textarea name="question"
                                  placeholder="Enter question..."
                                  required></textarea>

                        <label>Option A</label>
                        <input name="a">

                        <label>Option B</label>
                        <input name="b">

                        <label>Option C</label>
                        <input name="c">

                        <label>Option D</label>
                        <input name="d">

                        <label>Correct Answer</label>
                        <input name="answer"
                               placeholder="For MCQ enter exact correct option text">

                        <label>Marks</label>
                        <input type="number"
                               name="marks"
                               value="1"
                               min="1">

                        <button class="btn primary">
                            + Add Question
                        </button>

                    </form>

                </div>

                <div class="card">

                    <h2>Question Bank</h2>

                    {% for q in questions %}

                    <div class="exam-card">

                        <span class="badge">
                            {{ q["title"] }}
                        </span>

                        <h3>{{ q["question"] }}</h3>

                        <p class="muted">
                            Type: {{ q["qtype"] }}
                            • Marks: {{ q["marks"] }}
                        </p>

                    </div>

                    {% else %}

                    <p class="muted">
                        No questions added yet.
                    </p>

                    {% endfor %}

                </div>

            </div>

        </main>

    </div>
    """,
    sidebar=admin_sidebar(),
    exams=exams,
    questions=questions)


# =========================================================
# ADMIN RESULTS
# =========================================================

@app.route("/admin/results")
def admin_results():

    if not session.get("admin"):
        return redirect("/admin/login")

    con = db()

    rows = con.execute("""
        SELECT
            attempts.*,
            students.name,
            students.roll,
            exams.title
        FROM attempts
        JOIN students ON students.id=attempts.student_id
        JOIN exams ON exams.id=attempts.exam_id
        ORDER BY attempts.id DESC
    """).fetchall()

    con.close()

    return render_template_string(STYLE + """
    <div class="layout">

        {{ sidebar|safe }}

        <main class="main">

            <div class="topbar">
                <h1>📈 Examination Results</h1>
            </div>

            <div class="card">

                <table>

                    <tr>
                        <th>STUDENT</th>
                        <th>ROLL</th>
                        <th>EXAM</th>
                        <th>SCORE</th>
                        <th>%</th>
                        <th>STATUS</th>
                    </tr>

                    {% for r in rows %}

                    <tr>
                        <td>{{ r["name"] }}</td>
                        <td>{{ r["roll"] }}</td>
                        <td>{{ r["title"] }}</td>
                        <td>{{ r["score"] }}/{{ r["total"] }}</td>
                        <td>{{ r["percentage"] }}%</td>
                        <td>{{ r["status"] }}</td>
                    </tr>

                    {% else %}

                    <tr>
                        <td colspan="6">
                            No examination attempts yet.
                        </td>
                    </tr>

                    {% endfor %}

                </table>

            </div>

        </main>

    </div>
    """,
    sidebar=admin_sidebar(),
    rows=rows)


# =========================================================
# ADMIN ATTENDANCE
# =========================================================

@app.route("/admin/attendance")
def admin_attendance():

    if not session.get("admin"):
        return redirect("/admin/login")

    con = db()

    students = con.execute(
        "SELECT * FROM students ORDER BY name"
    ).fetchall()

    con.close()

    return render_template_string(STYLE + """
    <div class="layout">

        {{ sidebar|safe }}

        <main class="main">

            <div class="topbar">
                <h1>📅 Attendance Management</h1>
            </div>

            <div class="card">

                <table>

                    <tr>
                        <th>STUDENT</th>
                        <th>ROLL NUMBER</th>
                        <th>STATUS</th>
                    </tr>

                    {% for s in students %}

                    <tr>
                        <td>{{ s["name"] }}</td>
                        <td>{{ s["roll"] }}</td>
                        <td>
                            {{ "PRESENT" if s["present"] else "ABSENT" }}
                        </td>
                    </tr>

                    {% else %}

                    <tr>
                        <td colspan="3">
                            No students registered yet.
                        </td>
                    </tr>

                    {% endfor %}

                </table>

            </div>

        </main>

    </div>
    """,
    sidebar=admin_sidebar(),
    students=students)


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("                 QUIZNOVA")
    print("       SMART ONLINE EXAMINATION SYSTEM")
    print("=" * 60)
    print("Database : quiznova.db")
    print("Student  : http://127.0.0.1:5000/login")
    print("Admin    : http://127.0.0.1:5000/admin/login")
    print("Website  : http://127.0.0.1:5000")
    print("=" * 60)
    print()

    app.run(host="0.0.0.0", port=5000, debug=True)