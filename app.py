from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = "sastra_secret_key"

# Dummy DB (replace with MySQL later)
admins = [
    {"id": "admin01", "pass": "admin123"}
]

staff = [
    {"id": "staff101", "pass": "staff123", "slot": "9:15 - 10:45"}
]


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
                    return redirect(url_for("admin"))

            return render_template("login.html", error="Invalid Admin Login")

        if role == "staff":
            for s in staff:
                if s["id"] == user_id and s["pass"] == password:
                    session["user"] = user_id
                    session["role"] = "staff"
                    session["slot"] = s["slot"]
                    return redirect(url_for("staff_page"))

            return render_template("login.html", error="Invalid Staff Login")

    return render_template("login.html")


@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    return render_template("admin.html", user=session["user"])


@app.route("/staff")
def staff_page():
    if session.get("role") != "staff":
        return redirect(url_for("login"))
    return render_template("staff.html",
                           user=session["user"],
                           slot=session["slot"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
