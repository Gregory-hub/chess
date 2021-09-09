from flask import render_template, request, redirect, url_for
from flask_login import current_user, logout_user
from flask_socketio import emit

from chess import app, socketio, clients
from chess.forms import RegistrationForm, LoginForm, StartGameForm
from chess.auth import sign_in, sign_up, login_on_registration, get_current_client, get_client_by_username
from chess.models import User
from chess.start_game import send_invitaion


# sockets
@socketio.event
def connect():
    client = get_current_client()
    if client:
        client.add()
        print('\nConnected:', client)
        print(*clients, sep='\n')
        print()


@socketio.event
def disconnect():
    client = get_current_client()
    if client:
        client.remove()
        print('\nDisconnected:', client)
        print(*clients, sep='\n')
        print()


@socketio.event
def invite(username, game_data):
    inviting = get_current_client()
    invited = get_client_by_username(username)
    if inviting is None:
        emit('error', 'First login')
    elif invited is None:
        emit('error', 'User is not online')
    else:
        print(f'Invitation from "{inviting}" to "{invited}"')
        send_invitaion(inviting, invited, game_data)
        emit('success', 'Invited')


# routes
@app.route('/')
def index():
    form = StartGameForm()
    return render_template('index.html', form=form)


@app.route('/game/', methods=['POST'])
def game():
    return render_template('game.html')


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


@app.route('/logout/', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<username>/', methods=['GET'])
def user(username):
    user = User.query.filter_by(username=username).first()
    return render_template('user.html', user=user)


@app.route('/game_config/', methods=['GET', 'POST'])
def game_config():
    form = StartGameForm()
    return render_template('game_config.html', form=form)
