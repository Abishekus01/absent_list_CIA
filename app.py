from flask import Flask, render_template, request, redirect, session, url_for, Response
import csv
import io

app = Flask(__name__)
app.secret_key = "sastra_secret"

# 🔐 LOGIN DATA
admins = [{"id": "admin01", "pass": "admin123"}]
staff = [{"id": "staff101", "pass": "staff123"}]

# 📚 SUBJECT + SLOT MAP
subjects = {
    "CSE401": {"name": "Data Structures", "slot": "9:15 - 10:45"},
    "CSE402": {"name": "Operating Systems", "slot": "11:15 - 12:45"},
    "CSE403": {"name": "Database Management Systems", "slot": "1:15 - 2:45"}
}

# 🎓 70 REAL STUDENTS WITH SECTIONS
students = [
    ("3122001","Abishek U S","A"), ("3122002","Akshath","A"), ("3122003","Akash","A"),
    ("3122004","Ajay","A"), ("3122005","Arun","A"), ("3122006","Bala","A"),
    ("3122007","Charan","A"), ("3122008","Dinesh","A"), ("3122009","Eswar","A"),
    ("3122010","Gokul","A"), ("3122011","Hari","A"), ("3122012","Irfan","A"),
    ("3122013","Jagan","A"), ("3122014","Karthik","A"), ("3122015","Lokesh","A"),
    ("3122016","Manoj","A"), ("3122017","Naveen","A"),

    ("3122018","Prakash","B"), ("3122019","Raghul","B"), ("3122020","Sanjay","B"),
    ("3122021","Tarun","B"), ("3122022","Vignesh","B"), ("3122023","Yash","B"),
    ("3122024","Zubair","B"), ("3122025","Aravind","B"), ("3122026","Bhaskar","B"),
    ("3122027","Chandru","B"), ("3122028","Deepak","B"), ("3122029","Ezhil","B"),
    ("3122030","Farhan","B"), ("3122031","Ganesh","B"), ("3122032","Harish","B"),
    ("3122033","Imran","B"), ("3122034","Jeeva","B"),

    ("3122035","Kishore","C"), ("3122036","Loganathan","C"), ("3122037","Madhan","C"),
    ("3122038","Nithin","C"), ("3122039","Praveen","C"), ("3122040","Rahul","C"),
    ("3122041","Sarath","C"), ("3122042","Tharun Kumar","C"), ("3122043","Uday","C"),
    ("3122044","Varun","C"), ("3122045","Vishal","C"), ("3122046","Yogesh","C"),
    ("3122047","Abdul Rahman","C"), ("3122048","Balaji","C"), ("3122049","Dharshan","C"),
    ("3122050","Elango","C"), ("3122051","Girish","C"),

    ("3122052","Hemanth","D"), ("3122053","Jayanth","D"), ("3122054","Kavin","D"),
    ("3122055","Lohith","D"), ("3122056","Mohamed Asif","D"), ("3122057","Naveed","D"),
    ("3122058","Om Prakash","D"), ("3122059","Pranav","D"), ("3122060","Rithik","D"),
    ("3122061","Sathish","D"), ("3122062","Surya","D"), ("3122063","Venkatesh","D"),
    ("3122064","Vimal","D"), ("3122065","Yaseen","D"), ("3122066","Zaid","D"),
    ("3122067","Adarsh","D"), ("3122068","Bharath","D"), ("3122069","Cyril","D"),
    ("3122070","Dharani","D")
]

# convert to dict with dept/year/sem/course
student_db = []
for reg, name, sec in students:
    student_db.append({
        "reg": reg,
        "name": name,
        "dept": "CSE",
        "year": "II",
        "sem": "4",
        "section": sec,
        "course": ["CSE401", "CSE402", "CSE403"][int(reg[-1]) % 3]
    })

# 🏠 LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form["role"]
        user_id = request.form["loginId"]
        password = request.form["loginPass"]

        if role == "admin":
            for a in admins:
                if a["id"] == user_id and a["pass"] == password:
                    session["user"] = user_id
                    session["role"] = "admin"
                    return redirect(url_for("dashboard"))

        if role == "staff":
            for s in staff:
                if s["id"] == user_id and s["pass"] == password:
                    session["user"] = user_id
                    session["role"] = "staff"
                    return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid Login")

    return render_template("login.html")

# 📊 DASHBOARD
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        subject_code = request.form["subject_code"]

        session["exam_date"] = request.form["exam_date"]
        session["hall"] = request.form["hall"]
        session["subject_code"] = subject_code
        session["subject_name"] = subjects[subject_code]["name"]
        session["slot"] = subjects[subject_code]["slot"]
        session["staff_name"] = request.form["staff_name"]
        session["staff_id"] = request.form["staff_id"]

        return redirect(url_for("attendance"))

    return render_template("dashboard.html", subjects=subjects)

# 📝 ATTENDANCE
@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if "user" not in session:
        return redirect(url_for("login"))

    subject_students = [s for s in student_db if s["course"] == session["subject_code"]]

    if request.method == "POST":
        present_regs = request.form.getlist("present")
        absent_list = [s for s in subject_students if s["reg"] not in present_regs]

        session["absent"] = absent_list
        session["present_count"] = len(present_regs)
        session["absent_count"] = len(absent_list)

    return render_template("attendance.html",
                           students=subject_students,
                           data=session)

# 📥 CSV DOWNLOAD
@app.route("/download_absent")
def download_absent():
    if "absent" not in session:
        return redirect(url_for("attendance"))

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Reg No", "Name", "Dept", "Year", "Sem", "Section"])

    for s in session["absent"]:
        writer.writerow([s["reg"], s["name"], s["dept"], s["year"], s["sem"], s["section"]])

    output.seek(0)

    return Response(output,
                    mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=absent_list.csv"})

# 🔓 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
