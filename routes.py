from flask import render_template, request, redirect, url_for, session, flash
from app import app, db
from models import User
from forms import LoginForm
from datetime import datetime

@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in, otherwise to login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Fake login system - creates users on the fly"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data.strip().lower()
        email = form.email.data.strip().lower()
        first_name = form.first_name.data.strip()
        last_name = form.last_name.data.strip()
        
        # Check if user exists
        user = User.query.filter_by(username=username).first()
        
        if not user:
            # Create new user (fake registration)
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            flash(f'Welcome to the mentorship platform, {first_name}! Your account has been created.', 'success')
        else:
            # Update existing user info
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            flash(f'Welcome back, {first_name}!', 'success')
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Set session
        session['user_id'] = user.id
        session['username'] = user.username
        session['first_name'] = user.first_name
        
        return redirect(url_for('dashboard'))
    
    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    """Protected dashboard route"""
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        # User was deleted, clear session
        session.clear()
        flash('User account not found. Please log in again.', 'error')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user=user)

@app.route('/logout')
def logout():
    """Logout and clear session"""
    if 'first_name' in session:
        flash(f'Goodbye, {session["first_name"]}! You have been logged out.', 'info')
    session.clear()
    return redirect(url_for('login'))

@app.context_processor
def inject_user():
    """Make user info available in all templates"""
    user_info = {}
    if 'user_id' in session:
        user_info = {
            'logged_in': True,
            'user_id': session['user_id'],
            'username': session.get('username', ''),
            'first_name': session.get('first_name', '')
        }
    else:
        user_info = {'logged_in': False}
    
    return dict(current_user=user_info)
