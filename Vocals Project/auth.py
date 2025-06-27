from flask import Blueprint, request, redirect, flash, render_template, session
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import Client
from models import db, User
from config import Config

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()

# Google OAuth
google_bp = make_google_blueprint(client_id=Config.GOOGLE_OAUTH_CLIENT_ID, client_secret=Config.GOOGLE_OAUTH_CLIENT_SECRET, redirect_to='auth.google_login')
auth_bp.register_blueprint(google_bp, url_prefix='/google_login')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/google_login')
def google_login():
    if not google.authorized:
        return redirect(url_for('auth.login'))
    resp = google.get('/plus/v1/people/me')
    assert resp.ok, resp.text
    email = resp.json()['emails'][0]['value']
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for('main.dashboard'))

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(email=email, password=hashed_password, phone=phone)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Login failed. Check your email and password.', 'danger')
    return render_template('login.html')

@auth_bp.route('/phone_verification', methods=['GET', 'POST'])
def phone_verification():
    if request.method == 'POST':
        phone = request.form['phone']
        verification_code = request.form['code']
        # Implement Twilio SMS verification logic here
        # If verified, log in the user
        return redirect(url_for('main.dashboard'))
    return render_template('phone_verification.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/password_management', methods=['GET', 'POST'])
@login_required
def password_management():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        user = current_user
        if check_password_hash(user.password, current_password):
            user.password = generate_password_hash(new_password, method='sha256')
            db.session.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Current password is incorrect.', 'danger')
    return render_template('password_management.html')