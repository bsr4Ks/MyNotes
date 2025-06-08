from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
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

# Sirope
srp = sirope.Sirope()

# Flask-Login configuration
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return srp.find_first(User, lambda u: u.username == user_id)


# You need to add UserMixin to your model for Flask-Login
class UserLogin(User, UserMixin):
    def get_id(self):
        return self.username


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("notes"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if srp.find_first(User, lambda u: u.username == username):
            return render_template("error.html", error_msg="Username already exists")

        if not re.match(r"^[a-zA-Z]{3,}$", username):
            return render_template("error.html", error_msg="Invalid username. Use at least 3 letters.")
        if not re.match(r"^[a-zA-Z0-9@#$%^&+=]{6,}$", password):
            return render_template("error.html", error_msg="Invalid password. Use at least 6 characters.")

        password_hash = generate_password_hash(password)
        user = User(username, password_hash)
        srp.save(user)
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = srp.find_first(User, lambda u: u.username == username)
        if user and check_password_hash(user.password_hash, password):
            user_login = UserLogin(user.username, user.password_hash)
            login_user(user_login)
            return redirect(url_for("notes"))
        else:
            return render_template("error.html", error_msg="Invalid credentials")
    return render_template("login.html")


@app.route('/notes')
@login_required
def notes():
    user_notes = srp.load_all(Note)
    user_notes = filter(lambda n: n.user == current_user.username, user_notes)
    return render_template('notes.html', notes=user_notes)


@app.route("/notes/new", methods=["GET", "POST"])
@login_required
def new_note():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        note = Note(current_user.username, title, content)
        srp.save(note)
        return redirect(url_for("notes"))
    return render_template("new_note.html")


@app.route("/notes/<note_id>")
@login_required
def note_detail(note_id):
    note = srp.find_first(Note, lambda n: n.id == note_id)
    if not note or note.user != current_user.username:
        return render_template("error.html", error_msg="Note does not exist")
    return render_template("note_detail.html", note=note)


@app.route('/notes/<note_id>/delete')
@login_required
def delete_note(note_id):
    note = srp.find_first(Note, lambda n: n.id == note_id)
    if note and note.user == current_user.username:
        srp.delete(note.__oid__)
    return redirect(url_for("notes"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
