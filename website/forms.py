import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

def validate_password_strength(form, field):
    password = field.data or ''
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter.')
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one number.')
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        raise ValidationError('Password must contain at least one special character (!@#$%^&*...).')

def validate_username(form, field):
    username = field.data.strip()
    if not re.match(r'^[A-Za-z0-9_]{3,30}$', username):
        raise ValidationError('Username must be 3-30 characters and contain only letters, numbers, and underscores.')

class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Username is required.'),
        validate_username
    ])
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please provide a valid email address.'),
        Length(max=150)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        validate_password_strength
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Create Account')

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address.')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.')
    ])
    submit = SubmitField('Sign In')

class NoteForm(FlaskForm):
    content = TextAreaField('Note Content', validators=[
        DataRequired(message='Note content cannot be empty.'),
        Length(min=1, max=5000, message='Note must be between 1 and 5000 characters.')
    ])
    submit = SubmitField('Save Note')

class EditNoteForm(FlaskForm):
    note_id = HiddenField('Note ID', validators=[DataRequired()])
    content = TextAreaField('Updated Content', validators=[
        DataRequired(message='Note content cannot be empty.'),
        Length(min=1, max=5000, message='Note must be between 1 and 5000 characters.')
    ])
    submit = SubmitField('Update Note')
