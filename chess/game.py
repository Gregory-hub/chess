from datetime import datetime, timezone, timedelta

from flask_login import current_user

from chess import db
from chess.auth import get_user_from_username_or_email
from chess.models import Game, Player


def create_game(length: int, supplement: int, opponent_username: str, current_player_color: str):
    game = Game(
        start_time=datetime.now(timezone.utc),
        game_length=timedelta(seconds=length),
        supplement=timedelta(seconds=supplement)
    )
    game.players = create_players(opponent_username, current_player_color)

    db.session.add(game)
    db.session.commit()

    return game


def get_game_conf(game_id: int):
    game = Game.query.get(game_id)
    game_conf = {
        'game_length': game.game_length,
        'supplement': game.supplement,
        'current_player': game.players[0] if game.players[0].user == current_user else game.players[1],
        'opponent': game.players[0] if game.players[0].user != current_user else game.players[1]
    } if game else None
    return game_conf


def create_players(opponent_username: str, current_player_color: str):
    player1 = Player(
        color=current_player_color,
    )
    player1.user = current_user

    colors = ['black', 'white']
    colors.remove(current_player_color)
    player2_color = colors[0]

    player2 = Player(
        color=player2_color,
    )
    player2.user = get_user_from_username_or_email(opponent_username)

    return [player1, player2]


def get_my_games():
    user = current_user
    return [player.game for player in user.players]
