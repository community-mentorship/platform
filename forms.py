from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email, Length

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
