# from chess.game import move
from chess.models import User
from chess.auth import register


def add_tg_user(tg_user_id, email):
    user = User.query.filter_by(email=email).first()
    if user is None:
        register(
            email=email,
            tg_user_id=tg_user_id
        )
    else:
        user.set_tg_user_id(tg_user_id)
