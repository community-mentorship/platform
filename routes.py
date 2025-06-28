from flask import render_template, request, redirect, url_for, session, flash, abort
from app import app, db
from models import User, Page, ViewerScope, UserRole, Match, UserChangeLog, Form, Submission
from forms import LoginForm, PageForm, UserEditForm, FormBuilderForm
from datetime import datetime
from functools import wraps
import markdown
import re
import json

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

def process_form_label(text):
    """Process form labels with simple markdown-like formatting"""
    if not text:
        return ''
    
    # Bold: **text** -> <strong>text</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Italic: *text* -> <em>text</em>
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # Links: [text](url) -> <a href="url" target="_blank" rel="noopener">text</a>
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    
    # Line breaks
    text = text.replace('\n', '<br>')
    
    return text

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


@app.route('/admin/forms')
@admin_required
@login_required
def admin_forms():
    """List all application forms for admin"""
    forms = Form.query.order_by(Form.created_at.desc()).all()
    return render_template('admin/forms.html', forms=forms)


@app.route('/admin/forms/new', methods=['GET', 'POST'])
@admin_required
@login_required
def admin_new_form():
    """Create new form"""
    form = FormBuilderForm()
    
    if form.validate_on_submit():
        # Parse fields from JSON
        try:
            fields_data = form.fields_json.data
            if fields_data:
                import json
                fields = json.loads(fields_data)
            else:
                # Default starter fields if none provided
                fields = [
                    {
                        'id': 'field_1',
                        'type': 'text',
                        'label': 'Full Name',
                        'name': 'full_name',
                        'required': True,
                        'placeholder': 'Enter your full name'
                    },
                    {
                        'id': 'field_2',
                        'type': 'email',
                        'label': 'Email Address',
                        'name': 'email',
                        'required': True,
                        'placeholder': 'Enter your email address'
                    }
                ]
        except json.JSONDecodeError:
            flash('Invalid form field configuration.', 'error')
            return render_template('admin/form_builder.html', form=form, form_obj=None)
        
        new_form = Form(
            title=form.title.data,
            slug=form.slug.data,
            fields=fields,
            viewer_scope=ViewerScope(form.viewer_scope.data),
            is_active=form.is_active.data,
            created_by_id=session['user_id']
        )
        
        try:
            db.session.add(new_form)
            db.session.commit()
            flash(f'Form "{new_form.title}" created successfully!', 'success')
            return redirect(url_for('admin_forms'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating form: {str(e)}', 'error')
    
    return render_template('admin/form_builder.html', form=form, form_obj=None)


@app.route('/admin/forms/<int:form_id>/edit', methods=['GET', 'POST'])
@admin_required
@login_required
def admin_edit_form(form_id):
    """Edit existing form"""
    form_obj = Form.query.get_or_404(form_id)
    form = FormBuilderForm()
    
    if form.validate_on_submit():
        # Parse fields from JSON
        try:
            fields_data = form.fields_json.data
            if fields_data:
                import json
                fields = json.loads(fields_data)
            else:
                fields = form_obj.fields  # Keep existing fields if no new data
        except json.JSONDecodeError:
            flash('Invalid form field configuration.', 'error')
            return render_template('admin/form_builder.html', form=form, form_obj=form_obj)
        
        form_obj.title = form.title.data
        form_obj.slug = form.slug.data
        form_obj.fields = fields
        form_obj.viewer_scope = ViewerScope(form.viewer_scope.data)
        form_obj.is_active = form.is_active.data
        form_obj.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash(f'Form "{form_obj.title}" updated successfully!', 'success')
            return redirect(url_for('admin_forms'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating form: {str(e)}', 'error')
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        form.title.data = form_obj.title
        form.slug.data = form_obj.slug
        form.viewer_scope.data = form_obj.viewer_scope.value
        form.is_active.data = form_obj.is_active
    
    return render_template('admin/form_builder.html', form=form, form_obj=form_obj)


@app.route('/admin/forms/<int:form_id>/delete', methods=['POST'])
@admin_required
@login_required
def admin_delete_form(form_id):
    """Delete application form"""
    form_obj = Form.query.get_or_404(form_id)
    
    try:
        # Check if form has submissions
        submission_count = form_obj.submissions.count()
        if submission_count > 0:
            flash(f'Cannot delete form "{form_obj.title}" - it has {submission_count} submission(s).', 'error')
        else:
            db.session.delete(form_obj)
            db.session.commit()
            flash(f'Application form "{form_obj.title}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting form: {str(e)}', 'error')
    
    return redirect(url_for('admin_forms'))


@app.route('/form/<slug>')
@login_required
def form_view(slug):
    """Show form to users"""
    form_obj = Form.query.filter_by(slug=slug, is_active=True).first_or_404()
    user = User.query.get(session['user_id'])
    
    # Check if user can access this form based on viewer scope
    if form_obj.viewer_scope == ViewerScope.ADMINS_ONLY and not user.is_admin:
        abort(403)
    elif form_obj.viewer_scope == ViewerScope.MENTORS_ONLY and user.role not in [UserRole.MENTOR, UserRole.BOTH]:
        abort(403)
    elif form_obj.viewer_scope == ViewerScope.MENTEES_ONLY and user.role not in [UserRole.MENTEE, UserRole.BOTH]:
        abort(403)
    
    # Check if user already submitted this form
    existing_submission = Submission.query.filter_by(
        user_id=user.id, 
        form_id=form_obj.id
    ).first()
    
    if existing_submission:
        return render_template('application_submitted.html', 
                             form=form_obj, 
                             submission=existing_submission)
    
    # Process form labels for rich text formatting
    processed_form = {
        'id': form_obj.id,
        'title': form_obj.title,
        'slug': form_obj.slug,
        'fields': []
    }
    
    for field in form_obj.fields:
        processed_field = field.copy()
        processed_field['label'] = process_form_label(field.get('label', ''))
        processed_form['fields'].append(processed_field)
    
    return render_template('apply.html', form=processed_form)


@app.route('/form/<slug>/submit', methods=['POST'])
@login_required
def submit_form(slug):
    """Process form submission"""
    form_obj = Form.query.filter_by(slug=slug, is_active=True).first_or_404()
    user = User.query.get(session['user_id'])
    
    # Check if user can access this form based on viewer scope
    if form_obj.viewer_scope == ViewerScope.ADMINS_ONLY and not user.is_admin:
        abort(403)
    elif form_obj.viewer_scope == ViewerScope.MENTORS_ONLY and user.role not in [UserRole.MENTOR, UserRole.BOTH]:
        abort(403)
    elif form_obj.viewer_scope == ViewerScope.MENTEES_ONLY and user.role not in [UserRole.MENTEE, UserRole.BOTH]:
        abort(403)
    
    # Check if user already submitted this form
    existing_submission = Submission.query.filter_by(
        user_id=user.id, 
        form_id=form_obj.id
    ).first()
    
    if existing_submission:
        flash('You have already submitted this form.', 'warning')
        return redirect(url_for('form_view', slug=slug))
    
    # Collect form responses
    responses = {}
    for field in form_obj.fields:
        field_name = field['name']
        field_type = field.get('type', 'text')
        
        # Handle different field types
        if field_type == 'checkbox':
            # Get all selected values for checkbox groups
            field_values = request.form.getlist(field_name)
            max_selections = field.get('max_selections', 1)
            
            # Validate max selections
            if len(field_values) > max_selections:
                flash(f'{field["label"]}: Maximum {max_selections} selection(s) allowed.', 'error')
                return render_template('apply.html', form=form_obj)
            
            # Check if required
            if field.get('required', False) and not field_values:
                flash(f'{field["label"]} is required.', 'error')
                return render_template('apply.html', form=form_obj)
            
            responses[field_name] = field_values
        else:
            # Single value fields
            field_value = request.form.get(field_name, '').strip()
            
            # Basic required validation
            if field.get('required', False) and not field_value:
                flash(f'{field["label"]} is required.', 'error')
                return render_template('apply.html', form=form_obj)
            
            # Type-specific validation
            if field_value:  # Only validate if value is provided
                # Character length validation for text fields
                if field_type in ['text', 'textarea']:
                    min_length = field.get('min_length')
                    max_length = field.get('max_length')
                    
                    if min_length and len(field_value) < min_length:
                        flash(f'{field["label"]}: Must be at least {min_length} characters long.', 'error')
                        return render_template('apply.html', form=form_obj)
                    
                    if max_length and len(field_value) > max_length:
                        flash(f'{field["label"]}: Must not exceed {max_length} characters.', 'error')
                        return render_template('apply.html', form=form_obj)
                
                # Email format validation
                if field_type == 'email':
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not re.match(email_pattern, field_value):
                        flash(f'{field["label"]}: Please enter a valid email address.', 'error')
                        return render_template('apply.html', form=form_obj)
                
                # URL format validation
                elif field_type == 'url':
                    url_pattern = r'^https?://.+\..+'
                    if not re.match(url_pattern, field_value):
                        flash(f'{field["label"]}: Please enter a valid URL (starting with http:// or https://).', 'error')
                        return render_template('apply.html', form=form_obj)
            
            responses[field_name] = field_value
    
    # Create submission
    try:
        submission = Submission(
            user_id=user.id,
            form_id=form_obj.id,
            responses=responses
        )
        db.session.add(submission)
        db.session.commit()
        
        flash('Your submission has been submitted successfully!', 'success')
        return render_template('application_submitted.html', 
                             form=form_obj, 
                             submission=submission)
    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting form: {str(e)}', 'error')
        return render_template('apply.html', form=form_obj)


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
