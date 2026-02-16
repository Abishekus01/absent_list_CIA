from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

master_df = None
hall_df = None

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for("dashboard"))
    return render_template("login.html")

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

# ---------------- UPLOAD MASTER EXCEL ----------------
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

        master_df.columns = master_df.columns.str.strip().str.lower()

        column_map = {
            "reg no": "Reg No",
            "name": "Name",
            "dept": "Dept",
            "year": "Year",
            "semester": "Semester",
            "sem": "Semester",
            "section": "Section",
            "course code": "Course Code",
            "coursecode": "Course Code"
        }

        master_df.rename(columns=column_map, inplace=True)

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

    subjects = request.form.getlist("subject")

    combined_list = []

    for sub in subjects:
        sub_df = master_df[master_df["Course Code"] == sub].reset_index(drop=True)
        sub_df["Course"] = sub
        combined_list.append(sub_df)

    if not combined_list:
        return "No subjects selected"

    # 🔁 TRUE ALTERNATE SEATING
    grouped = [df.reset_index(drop=True) for df in combined_list]
    max_len = max(len(df) for df in grouped)

    rows = []
    for i in range(max_len):
        for df in grouped:
            if i < len(df):
                rows.append(df.iloc[i])

    merged_df = pd.DataFrame(rows).reset_index(drop=True)

    hall_data = []
    for i in range(len(merged_df)):
        hall_data.append({
            "Seat No": i + 1,
            "Reg No": merged_df.iloc[i]["Reg No"],
            "Name": merged_df.iloc[i]["Name"],
            "Course": merged_df.iloc[i]["Course"],
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
            value = request.form.get(f"present_{index}")
            hall_df.at[index, "Present"] = "A" if value == "A" else "P"

        return redirect(url_for("attendance"))

    # ✅ CALCULATE COUNTS IN PYTHON
    present_count = len(hall_df[hall_df["Present"] == "P"])
    absent_count = len(hall_df[hall_df["Present"] == "A"])
    absent_list = hall_df[hall_df["Present"] == "A"].to_dict(orient="records")

    hall_info = {
        "hall": hall_df["Hall"].iloc[0],
        "exam_date": hall_df["Date"].iloc[0],
        "slot": hall_df["Slot"].iloc[0]
    }

    return render_template(
        "attendance.html",
        tables=hall_df.to_dict(orient="records"),
        columns=hall_df.columns,
        data=hall_info,
        present_count=present_count,
        absent_count=absent_count,
        absent_list=absent_list
    )


# ---------------- DOWNLOAD ABSENT XLSX ----------------
@app.route("/download_absent")
def download_absent():
    global hall_df

    if hall_df is None or hall_df.empty:
        return "No attendance data"

    absent_df = hall_df[hall_df["Present"] == "A"]

    file_path = os.path.join(UPLOAD_FOLDER, "absent_list.xlsx")
    absent_df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
