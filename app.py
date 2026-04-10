from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os
import PyPDF2

app = Flask(__name__)
app.secret_key = "placement_secret"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

try:
    db = mysql.connector.connect(
        host="localhost",
        user="placement_user",
        password="placement123",
        database="placement_db"
    )
    cursor = db.cursor()
    print("Database connected successfully!")
except mysql.connector.Error as err:
    print(f"Database connection error: {err}")

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        cursor.execute("INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",(name,email,password))
        db.commit()
        return redirect("/")
    return render_template("register.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s",(email,password))
    user = cursor.fetchone()
    if user:
        session["user"] = user[1]
        return redirect("/dashboard")
    return "Invalid credentials"

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html", user=session["user"])

@app.route("/upload", methods=["POST"])
def upload():
    if "user" not in session:
        return redirect("/")

    file = request.files["resume"]
    path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(path)

    text = ""
    reader = PyPDF2.PdfReader(path)
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content

    skills = ["python","java","sql","html","css","javascript","git","machine learning","docker","aws"]
    found, missing = [], []

    for s in skills:
        if s in text.lower():   # ✅ FIXED
            found.append(s)
        else:
            missing.append(s)

    score = int((len(found)/len(skills))*100)

    cursor.execute(
        "INSERT INTO resume_results(username, score) VALUES(%s,%s)",
        (session["user"], score)
    )
    db.commit()

    recommended = missing[:3]

    return render_template("result.html", score=score, found=found, missing=missing, recommended=recommended)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/skill/<skill_name>")
def skill_detail(skill_name):

    skill_info = {
        "python": {
            "desc": "Python is widely used in AI, Data Science, and Web Development.",
            "features": [
                "Easy to learn & readable",
                "Used in AI & Machine Learning",
                "Automation scripting",
                "Web frameworks like Flask & Django"
            ]
        },
        "java": {
            "desc": "Java is used for enterprise and Android applications.",
            "features": [
                "Object Oriented Programming",
                "Used in banking systems",
                "Android app development",
                "Platform independent (JVM)"
            ]
        },
        "sql": {
            "desc": "SQL is required to manage databases.",
            "features": [
                "Data storage & retrieval",
                "Backend development",
                "Used in almost every IT job",
                "Database querying"
            ]
        },
        "docker": {
            "desc": "Docker helps in containerization.",
            "features": [
                "App deployment",
                "Environment consistency",
                "Used in DevOps",
                "Cloud deployment"
            ]
        },
        "aws": {
            "desc": "AWS (Amazon Web Services) is a cloud platform used widely in IT and DevOps.",
            "features": [
                "Cloud computing services",
                "Scalable infrastructure",
                "DevOps and deployment tools",
                "Storage and database solutions"
            ]
        },
        "html": {
            "desc": "HTML is the standard markup language to create web pages.",
            "features": [
                "Structures web content",
                "Forms, tables, and links",
                "Semantic tags for SEO",
                "Supports embedding images and videos"
            ]
        },
        "css": {
            "desc": "CSS is used to style HTML content and make web pages visually appealing.",
            "features": [
                "Control colors, fonts, and layout",
                "Responsive design with media queries",
                "Animations and transitions",
                "Flexbox and Grid for layouts"
            ]
        },
        "javascript": {
            "desc": "JavaScript adds interactivity and dynamic behavior to web pages.",
            "features": [
                "Manipulate HTML/CSS dynamically",
                "Event handling and animations",
                "AJAX and API integration",
                "Used in front-end frameworks like React, Vue, Angular"
            ]
        }
    }

    skill = skill_info.get(skill_name.lower())

    if not skill:
        return f"No data available for {skill_name}"

    return render_template("skill.html", skill_name=skill_name, skill=skill, skill_info = skill_info)

if __name__ == "__main__":
    app.run(debug=True)
