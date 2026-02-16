from flask import Flask, render_template, request, redirect, session, url_for, Response
import csv
import io

app = Flask(__name__)
app.secret_key = "sastra_secret"

# 🔐 LOGIN DATA
admins = [{"id": "admin01", "pass": "admin123"}]
staff = [{"id": "staff101", "pass": "staff123"}]

# 🎓 MASTER STUDENT LIST (70)
students = []
names = [
    "Abishek U S", "Akshath", "Akash", "Ajay", "Arun", "Bala", "Charan", "Dinesh", "Eswar",
    "Gokul", "Hari", "Irfan", "Jagan", "Karthik", "Lokesh", "Manoj", "Naveen", "Prakash",
    "Raghul", "Sanjay", "Tarun", "Vignesh", "Yash", "Zubair"
]

# auto-generate upto 70
for i in range(70):
    name = names[i] if i < len(names) else f"Student{i+1}"
    students.append({
        "reg": f"3122{i:03}",
        "name": name,
        "dept": "CSE",
        "year": "II",
        "sem": "4",
        "section": "A",
        "course": "CSE401"
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
        session["exam_date"] = request.form["exam_date"]
        session["hall"] = request.form["hall"]
        session["slot"] = request.form["slot"]
        session["subject"] = request.form["subject"]
        session["subject_code"] = request.form["subject_code"]
        session["staff_name"] = request.form["staff_name"]
        session["staff_id"] = request.form["staff_id"]

        return redirect(url_for("attendance"))

    return render_template("dashboard.html")

# 📝 ATTENDANCE PAGE
@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if "user" not in session:
        return redirect(url_for("login"))

    subject_students = [s for s in students if s["course"] == session["subject_code"]]

    if request.method == "POST":
        present_regs = request.form.getlist("present")
        absent_list = [s for s in subject_students if s["reg"] not in present_regs]

        session["absent"] = absent_list
        session["present_count"] = len(present_regs)
        session["absent_count"] = len(absent_list)

    return render_template("attendance.html",
                           students=subject_students,
                           data=session)

# 📥 DOWNLOAD ABSENT CSV
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
