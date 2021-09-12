from flask_login import current_user

from chess.auth import Client, get_current_client
from chess.models import Game


def create_game(game_time: int, supplement: int, player1_color: str, opponent: Client):
    player1 = current_user()
    print(player1)
