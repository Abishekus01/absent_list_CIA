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
@app.route("/dashboard")
def dashboard():
    global master_df

    subjects = {}

    if master_df is not None:
        unique_subs = master_df["Course Code"].unique()
        for sub in unique_subs:
            subjects[sub] = sub

    return render_template("dashboard.html", subjects=subjects)

# ---------------- UPLOAD MASTER EXCEL ----------------
@app.route("/upload_master", methods=["GET", "POST"])
def upload_master():
    global master_df

    if request.method == "POST":
        file = request.files["file"]
        if file:
            path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(path)

            master_df = pd.read_excel(path)

            return redirect(url_for("hall_allocation"))

    return render_template("upload_master.html")

# ---------------- HALL ALLOCATION ----------------
@app.route("/hall_allocation", methods=["GET", "POST"])
def hall_allocation():
    global master_df, hall_df

    if master_df is None:
        return "Upload master sheet first"

    if request.method == "POST":
        hall_number = request.form["hall"]
        exam_date = request.form["date"]
        slot = request.form["slot"]

        # Separate subjects
        subjects = master_df["Course Code"].unique()

        subject_groups = []
        for sub in subjects:
            subject_groups.append(master_df[master_df["Course Code"] == sub].reset_index(drop=True))

        # Alternate seating (column-wise)
        max_len = max(len(g) for g in subject_groups)

        hall_data = []

        for i in range(max_len):
            row = {"Seat No": i + 1}
            for col, group in enumerate(subject_groups):
                if i < len(group):
                    row[f"Sub{col+1}_Reg"] = group.iloc[i]["Reg No"]
                    row[f"Sub{col+1}_Name"] = group.iloc[i]["Name"]
                    row[f"Sub{col+1}_Course"] = group.iloc[i]["Course Code"]
                    row[f"Sub{col+1}_Present"] = "P"
                else:
                    row[f"Sub{col+1}_Reg"] = ""
                    row[f"Sub{col+1}_Name"] = ""
                    row[f"Sub{col+1}_Course"] = ""
                    row[f"Sub{col+1}_Present"] = ""

            hall_data.append(row)

        hall_df = pd.DataFrame(hall_data)

        # Save hall info
        hall_df["Hall"] = hall_number
        hall_df["Date"] = exam_date
        hall_df["Slot"] = slot

        return redirect(url_for("attendance"))

    return render_template("hall_allocation.html")

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

    absent_rows = []

    for _, row in hall_df.iterrows():
        for col in hall_df.columns:
            if "Present" in col and row[col] == "A":
                sub = col.replace("_Present", "")
                reg = row[f"{sub}_Reg"]
                name = row[f"{sub}_Name"]
                course = row[f"{sub}_Course"]

                absent_rows.append({
                    "Reg No": reg,
                    "Name": name,
                    "Course": course,
                    "Hall": row["Hall"],
                    "Date": row["Date"],
                    "Slot": row["Slot"]
                })

    absent_df = pd.DataFrame(absent_rows)

    file_path = os.path.join(UPLOAD_FOLDER, "absent_list.xlsx")
    absent_df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
