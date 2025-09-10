from flask import (
    Blueprint, render_template, request, redirect, url_for, session, current_app
)
from flask_login import UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import login_manager

auth_bp = Blueprint('auth', __name__)

# Przechowywanie użytkowników (teraz pobiera dane z konfiguracji aplikacji)
def get_users():
    return {
        current_app.config['ADMIN_USERNAME']: {
            "password": generate_password_hash(current_app.config['ADMIN_PASSWORD'])
        }
    }

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id in get_users():
        return User(user_id)
    return None

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('auth.login'))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        users = get_users()
        user_record = users.get(username)

        if user_record and check_password_hash(user_record["password"], password):
            login_user(User(username))
            session.permanent = True
            return redirect(url_for("main.index"))
        else:
            error = "Invalid credentials. Please try again."
    return render_template("login.html", error=error)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))