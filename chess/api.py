# from chess.game import move
from chess.models import User
from chess.auth import register


def add_tg_user(tg_user_id, email):
    success = False
    user = User.query.filter_by(email=email).first()
    if user is None:
        success = register(
            email=email,
            tg_user_id=tg_user_id
        )
        message = "Registration successful"
    else:
        user.set_tg_user_id(tg_user_id)
        success = True
        message = "Telegram user_id added"

    if not success:
        message = "Registration failed"

    return success, message
