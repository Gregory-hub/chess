from flask import render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import current_user, logout_user
from flask_socketio import emit

from chess import app, socketio, clients
from chess.forms import RegistrationForm, LoginForm, StartGameForm
from chess.auth import sign_in, sign_up, login_on_registration, get_current_client, create_client, authentication_required
from chess.models import User
from chess.connect import get_matched_users, invite_player
from chess.game import get_game_conf, create_game, get_my_games, move


# sockets
@socketio.event
def connect():
    client = create_client()
    if client:
        client.add()


@socketio.event
@authentication_required
def disconnect():
    client = get_current_client()
    if client:
        client.remove()


@socketio.event
def search(query: str):
    matched_users = get_matched_users(query)
    emit('search_result', matched_users)


@socketio.event
@authentication_required
def invite(data: dict):
    print('\n', data, '\n', type(data), '\n')
    invited_username = data['opponent']
    print(*clients, sep='\n', end='\n\n')
    invite_player(invited_username, data)


@socketio.event
@authentication_required
def fen_pos(fen_pos: str):
    game_id = int(request.referrer.split('/')[-1])
    move(game_id, fen_pos)


# routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/my_games/', methods=['GET'])
@authentication_required
def my_games():
    my_games = get_my_games()
    games = []
    for game in my_games:
        opponent = [player for player in game.players if player.user != current_user][0]

        games.append({
            'id': game.id,
            'opponent_username': opponent.user.username,
            'game_length': game.game_length,
            'supplement': game.supplement
        })

    return render_template('my_games.html', games=games)


@app.route('/game_config/', methods=['GET', 'POST'])
@authentication_required
def game_config():
    form = StartGameForm()

    if request.method == 'GET':
        return render_template('game_config.html', form=form)

    elif request.method == 'POST' and form.validate():
        opponent_username = form['opponent'].data
        supplement = int(form['supplement'].data)
        length = int(form['game_time'].data)
        current_player_color = form['player_color'].data

        game = create_game(
            length=length,
            supplement=supplement,
            opponent_username=opponent_username,
            current_player_color=current_player_color
        )

        return redirect(url_for('game', id=game.id))

    return render_template('game_config.html', form=form)


@app.route('/game/<int:id>', methods=['GET'])
@authentication_required
def game(id: int):
    game_conf = get_game_conf(id)
    if game_conf:
        return render_template(
            'game.html',
            current_player=game_conf['current_player'],
            opponent=game_conf['opponent']
        )
    else:
        flash('Error: game does not exist')
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
        if 'image' not in request.files:
            flash('No image part')
            return render_template('register.html', form=form)
        sign_up(form)
        if form.errors == {}:
            login_on_registration(form)
            flash("You signed up")
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
            flash("You logged in")
            return redirect(url_for('index'))

    return render_template('login.html', form=form)


@app.route('/logout/', methods=['GET'])
def logout():
    logout_user()
    flash("You logged out")
    return redirect(url_for('index'))


# media url
@app.route('/media/<filename>', methods=['GET'])
def upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
