# 🎓 Exam Hall Allocation & Attendance System

A Flask-based web application to manage **exam hall seating**, **alternate subject allocation**, and **attendance tracking** using an uploaded Excel master sheet.

---

## 🚀 Features

✅ Upload master student Excel sheet  
✅ Multi-subject selection for same hall  
✅ Automatic **alternate seating arrangement**  
✅ Seat number generation  
✅ Attendance marking (Present / Absent)  
✅ Live present & absent count  
✅ Absent student verification table  
✅ Download absent list as **Excel (.xlsx)**  
✅ Hall, date, and slot metadata support  

---

## 🧩 Tech Stack

- Python 🐍
- Flask 🌐
- Pandas 📊
- HTML + CSS 🎨
- Excel (.xlsx) as input/output

---

## 📂 Project Structure

```
exam-hall-system/
│
├── app.py
├── uploads/
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── upload_master.html
│   └── attendance.html
│
├── static/
│   └── style.css
│
└── README.md
```

---

## 📄 Required Excel Format (Master Sheet)

Upload an Excel file with **exact column names**:

| Reg No | Name | Dept | Year | Semester | Section | Course Code |
|--------|------|------|------|----------|---------|-------------|

✔ Column names are **case-insensitive**  
✔ `Sem` will be auto-mapped to `Semester`  

---

## 🧠 How Seating Works

If multiple subjects are selected for the same hall:

- Students are arranged in **true alternate order**
- Example:

```
Math → Physics → Math → Physics → Math → Physics
```

This prevents same-subject students sitting together.

---

## ▶️ How to Run the Project

### 1️⃣ Install dependencies

```bash
pip install flask pandas openpyxl
```

### 2️⃣ Run the app

```bash
python app.py
```

### 3️⃣ Open in browser

```
http://127.0.0.1:5000
```

---

## 🔐 Login

Currently supports role selection:

- **Admin** → Upload master + hall allocation  
- **Staff** → Attendance marking  

(Default authentication logic can be extended.)

---

## 🪑 Hall Allocation Workflow

1. Upload master Excel  
2. Go to dashboard  
3. Enter:
   - Hall number  
   - Exam date  
   - Slot  
   - Select multiple subjects  
4. Generate hall plan  

System will:

- Merge selected subjects  
- Apply alternate seating  
- Assign seat numbers  

---

## 📝 Attendance Workflow

- All students default to **Present**
- Tick checkbox to mark **Absent**
- Click **Save Attendance**
- View:
  - Present count  
  - Absent count  
  - Absent student table  
- Download absent list as Excel  

---

## 📥 Output File

Absent list is saved in:

```
/uploads/absent_list.xlsx
```

---

## ⚠️ Common Errors & Fixes

### ❌ Missing column in Excel
Ensure all required columns exist:
```
Reg No, Name, Dept, Year, Semester, Section, Course Code
```

### ❌ Subjects not visible
Make sure:
- Master sheet uploaded
- `Course Code` column contains values

### ❌ Present/Absent count showing 0
Click **Save Attendance** after marking absentees.

---

## 🔮 Future Enhancements

- Bench layout seating view  
- Multiple halls per slot  
- PDF hall ticket generation  
- Staff-wise hall assignment  
- Database integration (MySQL)  
- Barcode attendance scanning  

---

## 👨‍💻 Author

**Abishek U S**  
SASTRA University  
Exam Automation Mini Project

---

## 📜 License

This project is for academic and institutional use.
