from flask import render_template, request, redirect, url_for, session, flash, abort
from app import app, db
from models import User, Page, ViewerScope, UserRole, Match, UserChangeLog
from forms import LoginForm, PageForm, UserEditForm
from datetime import datetime
from functools import wraps
import markdown
import re

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
        print("Form validation passed")
        try:
            username = (form.username.data or '').strip().lower()
            email = (form.email.data or '').strip().lower()
            first_name = (form.first_name.data or '').strip()
            last_name = (form.last_name.data or '').strip()
            print(f"Form data processed: {username}, {email}, {first_name}, {last_name}")
            
            # Check if user exists by username or email
            user = User.query.filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if not user:
                # Create new user (fake registration)
                # Make first user admin for demo purposes
                is_first_user = User.query.count() == 0
                user = User()
                user.username = username
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.is_admin = is_first_user
                user.role = UserRole.MENTEE
                user.created_at = datetime.utcnow()
                db.session.add(user)
                flash(f'Welcome to the mentorship platform, {first_name}! Your account has been created.', 'success')
            else:
                # Update existing user info (but keep username and email if they match existing)
                if user.username != username and user.email == email:
                    # Same email, different username - update username
                    user.username = username
                elif user.username == username and user.email != email:
                    # Same username, different email - update email
                    user.email = email
                
                # Always update name fields
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
            session['is_admin'] = user.is_admin
            session['role'] = user.role.value
            
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            print(f"Error during login: {e}")
            flash(f'Error during login: {e}', 'error')
            db.session.rollback()
            return render_template('login.html', form=form)
    
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

# Admin Routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    user = User.query.get(session['user_id'])
    total_users = User.query.count()
    total_pages = Page.query.count()
    published_pages = Page.query.filter_by(is_published=True).count()
    recent_pages = Page.query.order_by(Page.updated_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         user=user,
                         total_users=total_users,
                         total_pages=total_pages,
                         published_pages=published_pages,
                         recent_pages=recent_pages)

@app.route('/admin/pages')
@admin_required
def admin_pages():
    """List all pages for admin"""
    pages = Page.query.order_by(Page.updated_at.desc()).all()
    return render_template('admin/pages.html', pages=pages)

@app.route('/admin/pages/new', methods=['GET', 'POST'])
@admin_required
def admin_new_page():
    """Create new page"""
    form = PageForm()
    
    if form.validate_on_submit():
        # Check if slug already exists
        existing_page = Page.query.filter_by(slug=form.slug.data).first()
        if existing_page:
            flash('A page with this URL slug already exists.', 'error')
            return render_template('admin/edit_page.html', form=form, page=None)
        
        page = Page()
        page.title = form.title.data
        page.slug = form.slug.data
        page.content = form.content.data
        page.viewer_scope = ViewerScope(form.viewer_scope.data)
        page.is_published = form.is_published.data
        page.created_by_id = session['user_id']
        
        db.session.add(page)
        db.session.commit()
        
        flash(f'Page "{page.title}" created successfully!', 'success')
        return redirect(url_for('admin_pages'))
    
    return render_template('admin/edit_page.html', form=form, page=None)

@app.route('/admin/pages/<int:page_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_page(page_id):
    """Edit existing page"""
    page = Page.query.get_or_404(page_id)
    form = PageForm(obj=page)
    
    # Set the form's viewer_scope to the string value
    form.viewer_scope.data = page.viewer_scope.value
    
    if form.validate_on_submit():
        # Check if slug conflicts with other pages
        existing_page = Page.query.filter(Page.slug == form.slug.data, Page.id != page_id).first()
        if existing_page:
            flash('A page with this URL slug already exists.', 'error')
            return render_template('admin/edit_page.html', form=form, page=page)
        
        page.title = form.title.data
        page.slug = form.slug.data
        page.content = form.content.data
        page.viewer_scope = ViewerScope(form.viewer_scope.data)
        page.is_published = form.is_published.data
        page.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'Page "{page.title}" updated successfully!', 'success')
        return redirect(url_for('admin_pages'))
    
    return render_template('admin/edit_page.html', form=form, page=page)

@app.route('/admin/pages/<int:page_id>/delete', methods=['POST'])
@admin_required
def admin_delete_page(page_id):
    """Delete page"""
    page = Page.query.get_or_404(page_id)
    title = page.title
    
    db.session.delete(page)
    db.session.commit()
    
    flash(f'Page "{title}" deleted successfully!', 'success')
    return redirect(url_for('admin_pages'))

def process_content(content):
    """Process markdown content with limited HTML support"""
    # Configure markdown with extensions
    md = markdown.Markdown(extensions=['fenced_code', 'tables', 'nl2br'])
    
    # Convert markdown to HTML
    html = md.convert(content)
    
    # Allow basic HTML color styling (sanitize input)
    color_pattern = r'<span\s+style="color:\s*((?:#[0-9a-fA-F]{3,6})|(?:rgb\([^)]+\))|(?:[a-zA-Z]+))"\s*>'
    html = re.sub(color_pattern, r'<span style="color: \1">', html)
    
    return html

# Static Page Routes
@app.route('/page/<slug>')
@login_required
def view_page(slug):
    """View a static page"""
    page = Page.query.filter_by(slug=slug, is_published=True).first_or_404()
    user = User.query.get(session['user_id'])
    
    # Check if user can view this page
    if not user.can_view_page(page):
        flash('You do not have permission to view this page.', 'error')
        return redirect(url_for('dashboard'))
    
    # Process the content (markdown + limited HTML)
    processed_content = process_content(page.content)
    
    return render_template('page.html', page=page, processed_content=processed_content)

@app.route('/logout')
def logout():
    """Logout and clear session"""
    if 'first_name' in session:
        flash(f'Goodbye, {session["first_name"]}! You have been logged out.', 'info')
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin/users')
@admin_required
def admin_users():
    """Admin user management"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    """Edit user details"""
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    
    if form.validate_on_submit():
        # Log changes
        current_user = User.query.get(session['user_id'])
        
        # Check each field for changes and log them
        if user.first_name != form.first_name.data:
            log_change = UserChangeLog()
            log_change.user_id = user.id
            log_change.field_changed = 'first_name'
            log_change.old_value = user.first_name
            log_change.new_value = form.first_name.data
            log_change.updated_by = current_user.id
            db.session.add(log_change)
        
        if user.last_name != form.last_name.data:
            log_change = UserChangeLog()
            log_change.user_id = user.id
            log_change.field_changed = 'last_name'
            log_change.old_value = user.last_name
            log_change.new_value = form.last_name.data
            log_change.updated_by = current_user.id
            db.session.add(log_change)
        
        if user.email != form.email.data:
            log_change = UserChangeLog()
            log_change.user_id = user.id
            log_change.field_changed = 'email'
            log_change.old_value = user.email
            log_change.new_value = form.email.data
            log_change.updated_by = current_user.id
            db.session.add(log_change)
        
        if user.role.value != form.role.data:
            log_change = UserChangeLog()
            log_change.user_id = user.id
            log_change.field_changed = 'role'
            log_change.old_value = user.role.value
            log_change.new_value = form.role.data
            log_change.updated_by = current_user.id
            db.session.add(log_change)
        
        if user.is_admin != form.is_admin.data:
            log_change = UserChangeLog()
            log_change.user_id = user.id
            log_change.field_changed = 'is_admin'
            log_change.old_value = str(user.is_admin)
            log_change.new_value = str(form.is_admin.data)
            log_change.updated_by = current_user.id
            db.session.add(log_change)
        
        # Update user
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.role = UserRole(form.role.data)
        user.is_admin = form.is_admin.data
        
        db.session.commit()
        flash(f'User {user.full_name} updated successfully!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/edit_user.html', form=form, user=user)

@app.route('/my-mentees')
@login_required
def my_mentees():
    """Show mentees for current mentor"""
    current_user = User.query.get(session['user_id'])
    
    if current_user.role not in [UserRole.MENTOR, UserRole.BOTH]:
        flash('You must be a mentor to access this page.', 'error')
        return redirect(url_for('dashboard'))
    
    matches = current_user.get_active_matches_as_mentor()
    mentees = [match.mentee for match in matches]
    
    return render_template('my_mentees.html', mentees=mentees)

@app.route('/my-mentor')
@login_required
def my_mentor():
    """Show mentor for current mentee"""
    current_user = User.query.get(session['user_id'])
    
    if current_user.role not in [UserRole.MENTEE, UserRole.BOTH]:
        flash('You must be a mentee to access this page.', 'error')
        return redirect(url_for('dashboard'))
    
    matches = current_user.get_active_matches_as_mentee()
    mentor = matches[0].mentor if matches else None
    
    return render_template('my_mentor.html', mentor=mentor)

@app.context_processor
def inject_user():
    """Make user info available in all templates"""
    user_info = {}
    if 'user_id' in session:
        user_info = {
            'logged_in': True,
            'user_id': session['user_id'],
            'username': session.get('username', ''),
            'first_name': session.get('first_name', ''),
            'is_admin': session.get('is_admin', False),
            'role': session.get('role', 'user')
        }
    else:
        user_info = {'logged_in': False}
    
    # Get available pages for navigation
    available_pages = []
    if user_info.get('logged_in'):
        user = User.query.get(user_info['user_id'])
        if user:
            all_pages = Page.query.filter_by(is_published=True).all()
            available_pages = [page for page in all_pages if user.can_view_page(page)]
    
    return dict(current_user=user_info, available_pages=available_pages)
