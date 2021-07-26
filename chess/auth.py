import re

from flask_login import login_user
from wtforms.validators import ValidationError

from chess.models import db, User
from chess import hasher


def sign_up(form):
    username = form.username.data
    email = form.email.data
    password = form.password.data
    image = form.image.data if form.image.data else None
    password_hash = hasher.generate_password_hash(password).decode()

    user = User(
        username=username,
        email=email,
        password=password_hash
    )
    if image:
        image_path = upload_image(image)
        user.image = image_path
    add_user(user)


def sign_in(form):
    user = get_user_from_username_or_email(form.username_or_email.data)
    password = form.password.data

    # user's existence is checked in form validation
    if hasher.check_password_hash(user.password, password):
        login_user(user, remember=True)
    else:
        form.password.errors.append('Invalid password')


def login_on_registration(form):
    username = form.username.data
    user = User.query.filter(User.username == username).first()
    login_user(user, remember=True)


def add_user(user: User):
    db.session.add(user)
    db.session.commit()


def upload_image(image):
    pass


def get_user_from_username_or_email(username_or_email: str):
    pattern = re.compile(r'^[^@]+@[^@]+\.[^@]+$')
    is_email = pattern.match(username_or_email)
    if is_email:
        user = User.query.filter(User.email == username_or_email).first()
    else:
        user = User.query.filter(User.username == username_or_email).first()
    return user
