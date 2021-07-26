from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from chess.models import User
from chess.auth import get_user_from_username_or_email


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), Length(min=8), EqualTo('password')])
    image = FileField('Image')
    submit = SubmitField('Sign up')

    def validate_username(self, username):
        user = User.query.filter(User.username == username.data).first()
        if user:
            raise ValidationError('This username is already taken')

    def validate_email(self, email):
        user = User.query.filter(User.email == email.data).first()
        if user:
            raise ValidationError('This email is already taken')


class LoginForm(FlaskForm):
    username_or_email = StringField('Username or email', validators=[DataRequired(), Length(min=2)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Log in')

    def validate_username_or_email(self, username_or_email):
        user = get_user_from_username_or_email(username_or_email.data)
        if not user:
            raise ValidationError("Invalid username or email")
