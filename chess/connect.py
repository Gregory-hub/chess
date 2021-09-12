import re
from flask_socketio import emit, join_room, leave_room

from chess.auth import Client
from chess import socketio
from chess.models import User


def send_invitaion(inviting: Client, invited: Client, game_data: dict):
    join_room('invite', sid=invited.sid)
    emit('invite', {'inviting': inviting, 'game_data': game_data}, room='invite')
    leave_room('invite', sid=invited.sid)


def get_matched_users(query: str):
    users = User.query.all()
    matched_users = [user.username for user in users if re.search(query, user.username)]
    if len(users) == len(matched_users):
        matched_users = []
    return matched_users
