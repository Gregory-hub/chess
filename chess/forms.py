from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from chess.models import User
from chess.auth import get_user_from_username_or_email


def no_space(form, field):
    if ' ' in field.data:
        raise ValidationError(f'{field.name.capitalize()} must not contain spaces')


def not_None(form, username):
    if username.data == 'None':
        raise ValidationError('Username cannot be "None"')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20), no_space, not_None])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), Length(min=8), EqualTo('password', message="Passwords must match")])
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


class StartGameForm(FlaskForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.opponent.choices = []
        users = User.query.order_by(User.username)
        for user in users:
            choice = (user, user.username)
            self.opponent.choices.append(choice)

    game_time = SelectField('Game time', choices=[
        (10, '10 sec'),
        (20, '20 sec'),
        (30, '30 sec'),
        (60, '1 min'),
        (120, '2 min'),
        (180, '3 min'),
        (300, '5 min'),
        (600, '10 min'),
        (900, '15 min'),
        (1800, '30 min')
    ])
    supplement = SelectField('Supplement time', choices=[
        (1, '1 sec'),
        (2, '2 sec'),
        (3, '3 sec'),
        (5, '5 sec'),
        (10, '10 sec'),
        (15, '15 sec'),
        (20, '20 sec'),
        (30, '30 sec'),
        (60, '60 sec')
    ])
    player_color = SelectField('Your color', choices=[
        ('black', 'black'),
        ('white', 'white'),
        ('random', 'random'),
    ])
    opponent = SelectField('Opponent')
    submit = SubmitField('Play')
