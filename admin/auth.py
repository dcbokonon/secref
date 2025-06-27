"""
Authentication module for admin panel
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from models import User
import time

auth_bp = Blueprint('auth', __name__)

# Rate limit login attempts
login_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_TIME = 300  # 5 minutes

class LoginForm(FlaskForm):
    """Login form with CSRF protection"""
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=20)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=4, max=100)
    ])
    submit = SubmitField('Login')

def check_rate_limit(ip):
    """Check if IP is rate limited"""
    current_time = time.time()
    
    # Clean old entries
    for key in list(login_attempts.keys()):
        if current_time - login_attempts[key]['last_attempt'] > LOCKOUT_TIME:
            del login_attempts[key]
    
    # Check current IP
    if ip in login_attempts:
        attempts = login_attempts[ip]
        if attempts['count'] >= MAX_ATTEMPTS:
            time_left = LOCKOUT_TIME - (current_time - attempts['last_attempt'])
            if time_left > 0:
                return False, int(time_left)
    
    return True, 0

def record_attempt(ip, success=False):
    """Record login attempt"""
    current_time = time.time()
    
    if success:
        # Clear attempts on successful login
        if ip in login_attempts:
            del login_attempts[ip]
    else:
        # Record failed attempt
        if ip not in login_attempts:
            login_attempts[ip] = {'count': 0, 'last_attempt': current_time}
        
        login_attempts[ip]['count'] += 1
        login_attempts[ip]['last_attempt'] = current_time

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    client_ip = request.remote_addr
    
    # Check rate limit
    allowed, time_left = check_rate_limit(client_ip)
    if not allowed:
        flash(f'Too many login attempts. Please try again in {time_left} seconds.', 'danger')
        return render_template('login.html', form=form)
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Verify credentials
        if User.verify_password(username, password):
            user = User.get(username)
            login_user(user)
            record_attempt(client_ip, success=True)
            
            # Log successful login
            from app import app
            app.logger.info(f'Successful login for user {username} from {client_ip}')
            
            # Redirect to next page or index
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            record_attempt(client_ip, success=False)
            
            # Log failed attempt
            from app import app
            app.logger.warning(f'Failed login attempt for user {username} from {client_ip}')
            
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    username = current_user.username
    logout_user()
    
    # Log logout
    from app import app
    app.logger.info(f'User {username} logged out')
    
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))