from flask_socketio import emit, join_room, leave_room

from chess.auth import Client
from chess import socketio


def send_invitaion(inviting: Client, invited: Client, game_data: dict):
    join_room('invite', sid=invited.sid)
    emit('invite', {'inviting': inviting, 'game_data': game_data}, room='invite')
    leave_room('invite', sid=invited.sid)
