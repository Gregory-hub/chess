from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, logout_user
from flask_socketio import emit

from chess import app, socketio, logger
from chess.forms import RegistrationForm, LoginForm, StartGameForm
from chess.auth import sign_in, sign_up, login_on_registration, get_current_client
from chess.models import User
from chess.connect import get_matched_users, invite
from chess.game import create_game


# sockets
@socketio.event
def connect():
    client = get_current_client()
    if client:
        client.add()
        logger.info(f'connected: {client}')


@socketio.event
def disconnect():
    client = get_current_client()
    if client:
        client.remove()
        logger.info(f'disconnected: {client}')


@socketio.event
def search(query):
    matched_users = get_matched_users(query)
    emit('search_result', matched_users)


# routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/game_config/', methods=['GET'])
def game_config():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = StartGameForm()
    return render_template('game_config.html', form=form)


@app.route('/game/', methods=['POST'])
def game():
    form = StartGameForm()
    if form.validate():
        game_time = form['game_time']
        supplement = form['supplement']
        color = form['player_color']
        opponent_username = form['opponent']

        create_game(game_time, supplement, color, opponent_username)
        return render_template('game.html')

    return redirect(url_for('game_config'))


@app.route('/user/<username>/', methods=['GET'])
def user(username):
    user = User.query.filter_by(username=username).first()
    return render_template('user.html', user=user)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if request.method == 'POST' and form.validate():
        sign_up(form)
        if form.errors == {}:
            login_on_registration(form)
            flash("Succesfull registration")
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
            flash("Succesfull login")
            return redirect(url_for('index'))

    return render_template('login.html', form=form)


@app.route('/logout/', methods=['GET'])
def logout():
    logout_user()
    flash("Successful logout")
    return redirect(url_for('index'))
