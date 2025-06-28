from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField, TextAreaField, SelectField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Length, Regexp
from models import ViewerScope, UserRole

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters')
    ], render_kw={'placeholder': 'Enter your username'})
    
    email = EmailField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ], render_kw={'placeholder': 'Enter your email address'})
    
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required'),
        Length(max=50, message='First name must not exceed 50 characters')
    ], render_kw={'placeholder': 'Enter your first name'})
    
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required'),
        Length(max=50, message='Last name must not exceed 50 characters')
    ], render_kw={'placeholder': 'Enter your last name'})
    
    submit = SubmitField('Sign In / Register')

class PageForm(FlaskForm):
    title = StringField('Page Title', validators=[
        DataRequired(message='Title is required'),
        Length(max=200, message='Title must not exceed 200 characters')
    ], render_kw={'placeholder': 'Enter page title'})
    
    slug = StringField('URL Slug', validators=[
        DataRequired(message='URL slug is required'),
        Length(max=100, message='Slug must not exceed 100 characters'),
        Regexp(r'^[a-z0-9-]+$', message='Slug must contain only lowercase letters, numbers, and hyphens')
    ], render_kw={'placeholder': 'e.g., mentor-guide'})
    
    content = TextAreaField('Content', validators=[
        DataRequired(message='Content is required')
    ], render_kw={'placeholder': 'Enter page content...', 'rows': 10})
    
    viewer_scope = SelectField('Who can view this page?', 
        choices=[
            (ViewerScope.ALL_USERS.value, 'All logged-in users'),
            (ViewerScope.MENTORS_ONLY.value, 'Mentors only'),
            (ViewerScope.MENTEES_ONLY.value, 'Mentees only'),
            (ViewerScope.ADMINS_ONLY.value, 'Admins only'),
            (ViewerScope.MATCHED_PAIR.value, 'Both users in a mentor–mentee match'),
            (ViewerScope.MENTOR_OF.value, 'Mentor of specific mentee'),
            (ViewerScope.MENTEE_OF.value, 'Mentee of specific mentor'),
            (ViewerScope.SELF_ONLY.value, 'The user themselves')
        ],
        default=ViewerScope.ALL_USERS.value,
        validators=[DataRequired()]
    )
    
    is_published = BooleanField('Published', default=True)
    
    submit = SubmitField('Save Page')

class UserEditForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required'),
        Length(max=50, message='First name must not exceed 50 characters')
    ])
    
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required'),
        Length(max=50, message='Last name must not exceed 50 characters')
    ])
    
    email = EmailField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    
    role = SelectField('Role', 
        choices=[
            (UserRole.MENTEE.value, 'Mentee'),
            (UserRole.MENTOR.value, 'Mentor'),
            (UserRole.BOTH.value, 'Both Mentor & Mentee')
        ],
        validators=[DataRequired()]
    )
    
    is_admin = BooleanField('Admin Access')
    
    submit = SubmitField('Update User')


class FormBuilderForm(FlaskForm):
    title = StringField('Form Title', validators=[
        DataRequired(message='Title is required'),
        Length(max=200, message='Title must not exceed 200 characters')
    ], render_kw={'placeholder': 'e.g., Mentorship Application'})
    
    slug = StringField('URL Slug', validators=[
        DataRequired(message='URL slug is required'),
        Length(max=100, message='Slug must not exceed 100 characters'),
        Regexp(r'^[a-z0-9-]+$', message='Slug must contain only lowercase letters, numbers, and hyphens')
    ], render_kw={'placeholder': 'e.g., mentorship-application'})
    
    viewer_scope = SelectField('Who can access this form?', 
        choices=[
            (ViewerScope.ALL_USERS.value, 'All logged-in users'),
            (ViewerScope.MENTORS_ONLY.value, 'Mentors only'),
            (ViewerScope.MENTEES_ONLY.value, 'Mentees only'),
            (ViewerScope.ADMINS_ONLY.value, 'Admins only')
        ],
        default=ViewerScope.ALL_USERS.value,
        validators=[DataRequired()]
    )
    
    is_active = BooleanField('Active', default=True)
    
    # Form fields will be handled dynamically in the template
    fields_json = HiddenField('Fields JSON')
    
    submit = SubmitField('Save Form')
