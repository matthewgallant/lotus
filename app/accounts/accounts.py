from flask import Blueprint, render_template, redirect, request, url_for, abort
from flask_login import login_required, login_user, logout_user
from urllib.parse import urlparse

from app.extensions import db, bcrypt
from app.models.user import User
from app.models.message_log import MessageLog

account_bp = Blueprint('account', __name__, template_folder="templates")

@account_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        error = None

        if request.form.get("email") and request.form.get("password"):
            email = request.form.get("email")
            password = request.form.get("password")
            remember = request.form.get("remember")

            user = db.session.execute(db.select(User).where(User.email == email)).scalar_one_or_none()
            if user:
                if bcrypt.check_password_hash(user.password, password):
                    # Add message log entry
                    message = MessageLog(f"User '{user}' has been logged in.")
                    db.session.add(message)
                    db.session.commit()

                    if remember:
                        login_user(user, remember=True)
                    else:
                        login_user(user)
                else:
                    error = "The password provided is incorrect."
            else:
                error = "Could not find an account for the specified email address."
        else:
            error = "An email address and password are required."

        if error:
            return render_template("login.html", error=error)
        else:
            return redirect(url_for("home.home", message="Your account has been logged in successfully."))
    else:
        return render_template("login.html")

@account_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        error = None

        if request.form.get("name") and request.form.get("email") and request.form.get("password"):
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")

            # Attempt to find existing user
            existing_user = db.session.execute(db.select(User).where(User.email == email)).scalar_one_or_none()
            if existing_user:
                error = "A user with this email already exists."
            else:
                if len(password) < 10:
                    error = "The password must be at least 10 characters long."
                else:
                    hasNumber = False
                    hasLower = False
                    hasUpper = False
                    hasSpecial = False
                    for char in password:
                        if char.isnumeric():
                            hasNumber = True
                        if char.islower():
                            hasLower = True
                        if char.isupper():
                            hasUpper = True
                        if char in ['!', '#', '$', '%', '&', '*', '<', '>', '?', '@']:
                            hasSpecial = True
                    
                    if not hasNumber:
                        error = "The password must contain at least 1 number."
                    elif not hasLower:
                        error = "The password must contain at least 1 lowercase letter."
                    elif not hasUpper:
                        error = "The password must contain at least 1 uppercase letter."
                    elif not hasSpecial:
                        error = "The password must contain at least 1 special symbol (!, #, $, %, &, *, <, >, ?, @)."
                    else:
                        # Create user in database
                        user = User(name=name, email=email, password=password)
                        db.session.add(user)
                        db.session.commit()

                        # Add message log entry
                        message = MessageLog(f"User '{user}' has been registered.")
                        db.session.add(message)
                        db.session.commit()

                        # Log the user in and go home
                        login_user(user)
        else:
            error = "A name, email, and password are required."
        
        if error:
            return render_template("register.html", error=error)
        else:
            return redirect(url_for("home.home", message="Your account has been registered successfully."))
    else:
        return render_template("register.html")
    
@account_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("account.login", message="You have been logged out."))
