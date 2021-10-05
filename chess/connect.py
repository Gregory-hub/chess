import re
from flask_socketio import emit, join_room, leave_room

from chess.auth import Client, get_current_client, get_client_by_username
from chess.models import User


def send_invitaion(inviting: Client, invited: Client, game_data: dict):
    join_room('invite', sid=invited.sid)
    emit('invite', {'inviting': inviting, 'game_data': game_data}, room='invite')
    leave_room('invite', sid=invited.sid)


def get_matched_users(query: str):
    query = query.strip(' ')
    if query == '':
        return []
    users = User.query.all()
    current_username = get_current_client().username
    matched_users = [user.username for user in users if re.search(query, user.username) and user.username != current_username]
    return matched_users


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
