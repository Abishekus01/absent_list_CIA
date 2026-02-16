from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

master_df = None
hall_df = None
attendance_data = {}

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for("dashboard"))
    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/upload_master", methods=["GET", "POST"])
def upload_master():
    global master_df

    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            return "No file selected"

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        master_df = pd.read_excel(path)

        # 🔴 CLEAN COLUMN NAMES (VERY IMPORTANT)
        master_df.columns = master_df.columns.str.strip()

        required_cols = ["Reg No", "Name", "Dept", "Year", "Semester", "Section", "Course Code"]

        for col in required_cols:
            if col not in master_df.columns:
                return f"Missing column in Excel: {col}"

        return redirect(url_for("dashboard"))

    return render_template("upload_master.html")

# ---------------- HALL ALLOCATION ----------------
@app.route("/hall_allocation", methods=["POST"])
def hall_allocation():
    global master_df, hall_df

    if master_df is None:
        return redirect(url_for("upload_master"))

    hall_number = request.form["hall"]
    exam_date = request.form["date"]
    slot = request.form["slot"]
    subject = request.form["subject"]

    subject_df = master_df[master_df["Course Code"] == subject].reset_index(drop=True)

    hall_data = []

    for i in range(len(subject_df)):
        hall_data.append({
            "Seat No": i + 1,
            "Reg No": subject_df.iloc[i]["Reg No"],
            "Name": subject_df.iloc[i]["Name"],
            "Course": subject,
            "Present": "P",
            "Hall": hall_number,
            "Date": exam_date,
            "Slot": slot
        })

    hall_df = pd.DataFrame(hall_data)

    return redirect(url_for("attendance"))


# ---------------- ATTENDANCE PAGE ----------------
@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    global hall_df

    if hall_df is None:
        return "No hall allocated"

    if request.method == "POST":
        for index in hall_df.index:
            for col in hall_df.columns:
                if "Present" in col:
                    value = request.form.get(f"{col}_{index}")
                    hall_df.at[index, col] = "A" if value == "A" else "P"

        return redirect(url_for("attendance"))

    return render_template("attendance.html", tables=hall_df.to_dict(orient="records"), columns=hall_df.columns)

# ---------------- DOWNLOAD ABSENT XLSX ----------------
@app.route("/download_absent")
def download_absent():
    global hall_df

    if hall_df is None:
        return "No attendance data"

    absent_df = hall_df[hall_df["Present"] == "A"]

    file_path = os.path.join(UPLOAD_FOLDER, "absent_list.xlsx")
    absent_df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    global master_df

    subjects = []
    if master_df is not None:
        subjects = sorted(master_df["Course Code"].dropna().unique())

    return render_template(
        "dashboard.html",
        subjects=subjects,
        data_loaded=(master_df is not None)
    )


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
