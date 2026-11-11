import math
from datetime import datetime, timedelta, timezone
from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

from . import db, limiter
from .models import User
from .forms import SignUpForm, LoginForm

auth = Blueprint('auth', __name__)

LOCKOUT_THRESHOLD = 3
LOCKOUT_MINUTES = 5

@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user:
            # Check lockout status
            now_utc = datetime.now(timezone.utc)
            locked_dt = user.locked_until
            if locked_dt and locked_dt.tzinfo is None:
                locked_dt = locked_dt.replace(tzinfo=timezone.utc)

            if locked_dt and now_utc < locked_dt:
                remaining_seconds = int((locked_dt - now_utc).total_seconds())
                remaining_minutes = max(1, math.ceil(remaining_seconds / 60))
                flash(
                    f'Your account is locked due to 3 consecutive failed login attempts. '
                    f'Please try again in {remaining_minutes} minute(s).',
                    category='error'
                )
                return render_template('login.html', form=form, user=current_user)

            # If lockout period expired, reset the lockout state
            if locked_dt and now_utc >= locked_dt:
                user.failed_login_attempts = 0
                user.locked_until = None
                db.session.commit()

            # Verify password using PBKDF2-SHA256
            if check_password_hash(user.password_hash, password):
                # Successful login: reset attempts and lock
                user.failed_login_attempts = 0
                user.locked_until = None
                db.session.commit()

                login_user(user, remember=False)
                flash('Logged in successfully! Welcome back.', category='success')
                return redirect(url_for('views.home'))
            else:
                # Failed login attempt
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= LOCKOUT_THRESHOLD:
                    user.locked_until = now_utc + timedelta(minutes=LOCKOUT_MINUTES)
                    db.session.commit()
                    flash(
                        f'Account locked! You have failed {LOCKOUT_THRESHOLD} consecutive login attempts. '
                        f'Your account is locked for {LOCKOUT_MINUTES} minutes.',
                        category='error'
                    )
                else:
                    attempts_left = LOCKOUT_THRESHOLD - user.failed_login_attempts
                    db.session.commit()
                    flash(
                        f'Incorrect password. {attempts_left} attempt(s) remaining before account lockout.',
                        category='error'
                    )
        else:
            flash('No account found with this email address.', category='error')

    return render_template('login.html', form=form, user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', category='info')
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    form = SignUpForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()
        password = form.password.data

        # Duplicate account prevention
        existing_email = User.query.filter_by(email=email).first()
        existing_user = User.query.filter_by(username=username).first()

        if existing_email:
            flash('An account with this email already exists. Please log in.', category='error')
        elif existing_user:
            flash('This username is already taken. Please choose another.', category='error')
        else:
            # PBKDF2-SHA256 secure password hashing
            password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                failed_login_attempts=0,
                locked_until=None
            )
            db.session.add(new_user)
            db.session.commit()

            flash('Account created successfully! Please log in to continue.', category='success')
            return redirect(url_for('auth.login'))

    return render_template('sign_up.html', form=form, user=current_user)
