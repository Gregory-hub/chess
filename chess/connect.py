import re
from flask_socketio import join_room, leave_room

from chess import socketio
from chess.auth import Client, get_current_client, get_client_by_username
from chess.models import User


def send_invitaion(inviting: Client, invited: Client, game_data: dict):
    join_room('invite', sid=invited.sid, namespace='/')
    socketio.emit('invite', {'game_data': game_data}, to='invite')
    leave_room('invite', sid=invited.sid, namespace='/')


def get_matched_users(query: str):
    query = query.strip(' ')
    if query == '':
        return []
    users = User.query.all()
    current_username = get_current_client().username
    matched_users = [user.username for user in users if user.username and re.search(query, user.username) and user.username != current_username]
    return matched_users


def invite_player(invited_username: str, game_data: dict):
    inviting = get_current_client()
    invited = get_client_by_username(invited_username)
    if inviting is None:
        return
    elif invited is None:
        emit_error('User is not online')
    else:
        game_data['opponent'] = get_current_client().username
        send_invitaion(inviting, invited, game_data)


def emit_error(message: str):
    inviting = get_current_client()
    socketio.emit('error', message, room=inviting.sid)
