from datetime import datetime, timezone, timedelta

from flask_login import current_user

from chess import db
from chess.auth import get_user_from_username_or_email
from chess.models import Game, Player
from chess.forms import StartGameForm


def create_game(game_conf: dict):
    game = Game(
        start_time=datetime.now(timezone.utc),
        game_length=timedelta(seconds=game_conf['game_length']),
        supplement=timedelta(seconds=game_conf['supplement'])
    )
    game_conf['player1'].game = game
    game_conf['player2'].game = game

    db.session.add(game)
    db.session.commit()

    return game


def get_game_conf(form: StartGameForm):
    player1_color = form['player_color'].data
    game_length = int(form['game_time'].data)
    opponent_username = form['opponent'].data
    supplement = int(form['supplement'].data)

    # player1
    player1 = Player(
        color=player1_color,
        time_left=timedelta(seconds=game_length),
    )
    player1.user = current_user

    # player2 color
    colors = ['black', 'white']
    colors.remove(player1_color)
    player2_color = colors[0]

    # player2
    player2 = Player(
        color=player2_color,
        time_left=timedelta(seconds=game_length),
    )
    player2.user = get_user_from_username_or_email(opponent_username)

    game_conf = {
        'game_length': game_length,
        'supplement': supplement,
        'player1': player1,
        'player2': player2
    }

    return game_conf


def get_my_games():
    user = current_user
    return [player.game for player in user.players]


def get_game_by_id(game_id: int):
    return Game.query.get(1)
