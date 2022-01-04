from math import ceil
from random import choice
from datetime import datetime, timezone, timedelta

from flask_login import current_user

from chess import db, socketio
from chess.auth import get_user_from_username_or_email
from chess.models import Game, Player
from chess.pieces import letter_to_piece, King
from chess.square import Square


# game creation
def create_game(length: int, supplement: int, opponent_username: str, current_player_color: str):
    game = Game(
        start_time=datetime.now(timezone.utc),
        game_length=timedelta(seconds=length),
        supplement=timedelta(seconds=supplement),
        fen="3qk3/8/8/8/8/8/8/3QK3 w KQkq - 0 1"    # "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    )
    if current_player_color == 'random':
        current_player_color = choice(['black', 'white'])
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
        'opponent': game.players[0] if game.players[0].user != current_user else game.players[1],
        'fen_pos': game.get_fen_pos()
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
    return [player.game for player in user.players if player.game is not None]


# move processing
def move(game_id: int, new_fen_pos: str):
    game = Game.query.get(game_id)
    old_fen_pos = game.get_fen_pos()
    old_pos = get_pos(old_fen_pos)
    new_pos = get_pos(new_fen_pos)
    for i in range(8):
        for j in range(8):
            print(old_pos[i][j].letter if old_pos[i][j] is not None else '*', end=' ')
        print(end=' ' * 2)
        for j in range(8):
            print(new_pos[i][j].letter if new_pos[i][j] is not None else '*', end=' ')
        print()

    if fen_pos_is_valid(new_fen_pos) and move_is_legal(game, old_pos, new_pos):
        piece, source, target = get_move_info(old_pos, new_pos)
        game.add_move(piece.letter, source.name, target.name)
        game.update_fen(new_fen_pos)
        socketio.emit('fen_pos', new_fen_pos)
    else:
        socketio.emit('fen_pos', old_fen_pos)


def fen_pos_is_valid(fen_pos: str):
    rows = fen_pos.split('/')
    for row in rows:
        if len(row) > 8:
            print('Invalid fen_pos')
            return False
        for fig in row:
            if fig not in 'rnbqkpRNBQKP12345678':
                print('Invalid fen_pos')
                return False
    return True


def move_is_legal(game: Game, old_pos: list, new_pos: list):
    # castling = game.get_castling_availability()
    # enpassand_target = game.get_enpassand_target()
    # halfmove_clock = game.get_halfmove_clock()
    # moves_number = game.get_fullmove_number()

    if moves_count(old_pos, new_pos) != 1:
        return False

    piece, source, target = get_move_info(old_pos, new_pos)
    if source and target and piece:
        print('Piece:', piece)
        print('Piece letter:', piece.letter)
        print('Source:', source.name)
        print('Target:', target.name)
        print('Move color:', piece.color)
        print('Checks opponent:', piece.delivers_check(target, piece.color, new_pos))
        print()

    if game.get_active_color() != piece.color:
        print("Invalid color")
        return False
    if not piece.valid_move(source, target):
        print("Invalid move")
        return False
    if piece.moved_throught_piece(source, target, old_pos):
        print("Moved throught piece")
        return False
    if takes_their_own_piece(target, old_pos, new_pos):
        print("Takes wrong piece")
        return False
    if takes_king(target, old_pos, new_pos):
        print("Takes king")
        return False

    return True


def get_pos(fen_pos: str):
    pos_matrix = [[] for i in range(8)]
    for i in range(8):
        for sq in fen_pos.split('/')[i]:
            if sq.isdigit():
                pos_matrix[i].extend([None for j in range(int(sq))])
            else:
                pos_matrix[i].append(letter_to_piece(sq))
    return pos_matrix


def moves_count(old_pos: list, new_pos: list):
    changes_count = 0
    for i in range(8):
        for j in range(8):
            if old_pos[i][j] != new_pos[i][j]:
                changes_count += 1
    return ceil(changes_count / 2)


def get_move_info(old_pos: list, new_pos: list):
    piece, source, target = None, None, None
    for i in range(8):
        for j in range(8):
            if old_pos[i][j] is not None and new_pos[i][j] is None:
                piece = old_pos[i][j]
                source = Square(i, j)
            elif old_pos[i][j] != new_pos[i][j]:
                target = Square(i, j)
    return piece, source, target


def takes_their_own_piece(target: Square, old_pos: list, new_pos: list):
    i = target.i
    j = target.j
    return old_pos[i][j] and new_pos[i][j] and old_pos[i][j].color == new_pos[i][j].color


def takes_king(target: Square, old_pos: list, new_pos: list):
    if isinstance(old_pos[target.i][target.j], King) and new_pos[target.i][target.j] != old_pos[target.i][target.j]:
        return True
