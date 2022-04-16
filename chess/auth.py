import re
import os
import functools

from flask import request, flash, redirect, url_for
from flask_login import login_user, current_user
from werkzeug.datastructures import FileStorage

from chess import UPLOAD_FOLDER, hasher, clients, app, logger
from chess.models import db, User


class Client:
    def __init__(self, username: str, sid: str, user_agent: str):
        self.username = username
        self.sid = sid
        self.user_agent = user_agent

    def add(self):
        clients.append(self)

    def remove(self):
        for client in clients:
            if client == self:
                clients.remove(client)

    def __repr__(self):
        return f'Client(username="{self.username}", sid="{self.sid}", user_agent="{self.user_agent}")'

    def __eq__(self, other):
        # for client comparison
        if not isinstance(other, Client):
            return NotImplemented

        return self.username == other.username and self.sid == other.sid and self.user_agent == other.user_agent


def sign_up(form):
    # browser registration
    username = form.username.data
    email = form.email.data
    password = form.password.data
    image = request.files['image']

    user = User.query.filter_by(email=email).first()
    if not user:
        register(
            email=email,
            image=image,
            username=username,
            password=password
        )
    else:
        user.set_username(username)
        user.set_password(hasher.generate_password_hash(password).decode())

        if isinstance(image, FileStorage) and image.filename != '' and allowed_file(image):
            filename = upload_image(image, username)
            user.image = filename
            user.set_image(image)


def sign_in(form):
    user = get_user_from_username_or_email(form.username_or_email.data)
    password = form.password.data

    # user's existence is checked in form validation
    if hasher.check_password_hash(user.password, password):
        login_user(user, remember=True)
    else:
        form.password.errors.append('Invalid password')


def register(email: str, image: str = None, username: str = None, password: str = None, tg_user_id: int = None):
    # both browser and telegram registration
    # if you pass username, you have to pass password(and vice versa)
    success = True

    if not (tg_user_id or username and password):
        success = False
        return success

    user = User(
        email=email,
    )

    if username:
        user.username = username
        user.password = hasher.generate_password_hash(password).decode()
        print(user.username)
        print(type(user.username))
    else:
        user.tg_user_id = tg_user_id

    if isinstance(image, FileStorage) and image.filename != '' and allowed_file(image):
        filename = upload_image(image, username)
        user.image = filename

    add_user(user)

    return success


def login_on_registration(form):
    username = form.username.data
    user = User.query.filter(User.username == username).first()
    login_user(user, remember=True)


def add_user(user: User):
    db.session.add(user)
    db.session.commit()


def get_user_from_username_or_email(username_or_email: str):
    pattern = re.compile(r'^[^@]+@[^@]+\.[^@]+$')
    is_email = pattern.match(username_or_email)
    if is_email:
        user = User.query.filter(User.email == username_or_email).first()
    else:
        user = User.query.filter(User.username == username_or_email).first()
    return user


def get_current_client():
    if not current_user.is_authenticated:
        return None
    client = get_client_by_username(current_user.username)
    if client is None:
        logger.error('No current client(current user is authenticated)')
    return client


def create_client():
    if not current_user.is_authenticated:
        return None
    username = current_user.username
    sid = request.sid
    return Client(username, sid, request.headers.get('User-Agent'))


def get_client_by_username(username: str):
    for client in clients:
        if client.username == username:
            return client
    return None


def allowed_file(file):
    ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']
    filename = file.filename
    return '.' in filename and os.path.splitext(filename)[1].strip('.') in ALLOWED_EXTENSIONS


def upload_image(image: FileStorage, username: str):
    ext = os.path.splitext(image.filename)[1]
    filename = username + ext
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    if filename in os.listdir(UPLOAD_FOLDER):
        os.remove(upload_path)
    image.save(upload_path)
    return filename


def authentication_required(fun):
    @functools.wraps(fun)
    def inner(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Authentication required')
            return redirect(url_for('login'))
        else:
            return fun(*args, **kwargs)

    return inner
