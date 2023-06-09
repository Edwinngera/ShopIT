from flask_login import login_required, login_manager
from flask import Blueprint, render_template, request, flash, redirect, url_for,abort
from .models import User
from functools import wraps
from flask_login import (
    login_required,
    logout_user,
    current_user,
    login_user,
)
from .forms import (
    LoginForm,
    SignupForm,
)
from . import db

auth = Blueprint('auth', __name__)

# Custom role_required decorator
def role_required(role_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.role!=role_name:
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator
            


@auth.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect('/')
    else:
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(password=form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('views.home'))
        flash('Invalid username/password combination')
    return render_template("login.html", title="", form=form)


@auth.route("/register", methods=["POST", "GET"])
def register():
    form = SignupForm(request.form)
    if request.method == 'POST':
        print("Ngera")
        existing_user = User.query.filter_by(email=form.email.data).first()
        print(existing_user)
        if existing_user is None:
            user = User(
                email=form.email.data,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()  # Create new user
            login_user(user)  # Log in as newly created user
            return redirect(url_for('views.home'))
        else:
            flash('A user already exists with that email address.')
            return render_template("register.html", form=form)

    else:
        return render_template("register.html", form=form)


@login_required
@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
