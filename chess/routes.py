from flask import render_template, request, redirect, url_for
from flask_login import current_user, logout_user

from chess import app
from chess.forms import RegistrationForm, LoginForm
from chess.auth import sign_in, sign_up, login_on_registration


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create/', methods=['POST'])
def create_game():
    return render_template('game_awaiting_page.html')


@app.route('/join/')
def join_game():
    pass


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if request.method == 'POST' and form.validate():
        sign_up(form)
        if form.errors == {}:
            login_on_registration(form)
            return redirect(url_for('index'))

    return render_template('register.html', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if request.method == 'POST' and form.validate():
        sign_in(form)
        if current_user.is_authenticated:
            return redirect(url_for('index'))

    return render_template('login.html', form=form)


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))
