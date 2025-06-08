from flask import Flask, render_template, request, redirect, url_for, session, flash
import sirope
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import re


import os
from dotenv import load_dotenv

from models.user import User
from models.note import Note

load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
srp = sirope.Sirope()


# Homepage - if logged in, redirect
@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("notes"))
    return redirect(url_for("login"))

# Registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if srp.find_first(User, lambda u: u.username == username):
            return render_template("error.html", error_msg="Username exists")
        
        if not re.match(r"^[a-zA-Z]{3,}$", username):
            return render_template("error.html", error_msg="Invalid username. Use at least 3 letters (a-z, A-Z).")
        if not re.match(r"^[a-zA-Z0-9@#$%^&+=]{6,}$", password):
            return render_template("error.html", error_msg="Invalid password. Use at least 6 characters.")

        if srp.find_first(User, lambda u: u.username == username):
            return render_template("error.html", error_msg="Username exists")

        password_hash = generate_password_hash(password)
        user = User(username, password_hash)
        srp.save(user)
        return redirect(url_for("login"))
    return render_template("register.html")


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = srp.find_first(User, lambda u: u.username == username)
        if user and check_password_hash(user.password_hash, password):
            session["username"] = username
            return redirect(url_for("notes"))
        else:
            return render_template("error.html", error_msg="Invalid credentials")
    return render_template("login.html")


# List notes
@app.route('/notes')
def notes():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    # Filter only notes that belong to that user
    user_notes = srp.load_all(Note)
    user_notes = filter(lambda n: n.user == username, user_notes)

    return render_template('notes.html', notes=user_notes)


# Create new note
@app.route("/notes/new", methods=["GET", "POST"])
def new_note():
    if "username" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        note = Note(session["username"], title, content)
        srp.save(note)
        return redirect(url_for("notes"))
    return render_template("new_note.html")


# Note detail page
@app.route("/notes/<note_id>")
def note_detail(note_id):
    note = srp.find_first(Note, lambda n: n.id == note_id)
    if not note or note.user != session.get("username"):
        return render_template("error.html", error_msg="Note does not exist")
    return render_template("note_detail.html", note=note)


@app.route('/notes/<note_id>/delete')
def delete_note(note_id):
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))

    note = srp.find_first(Note, lambda n: n.id == note_id)
    if note:
        srp.delete(note.__oid__)
    return redirect(url_for("notes"))


# Logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run()
