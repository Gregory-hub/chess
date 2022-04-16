# from chess.game import move
from chess.models import User
from chess.auth import register


def add_tg_user(tg_user_id: int, email: str):
    success = None
    user = User.query.filter_by(email=email).first()
    if user is None:
        success = register(
            email=email,
            tg_user_id=tg_user_id,
        )
        if success:
            message = "Registration successful"
        else:
            message = "Registration failed"
    elif user.tg_user_id is not None:
        success = False
        message = "User already exists and has tg_user_id"
    else:
        user.set_tg_user_id(tg_user_id)
        success = True
        message = "Telegram user_id added"

    if success is None:
        message = "Registration failed"

    return success, message
