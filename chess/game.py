from math import ceil
from random import choice
from datetime import datetime, timezone, timedelta

from flask_login import current_user

from chess import db, socketio
from chess.auth import get_user_from_username_or_email
from chess.models import Game, Player
from chess.pieces import letter_to_piece
from chess.square import Square


# game creation
def create_game(length: int, supplement: int, opponent_username: str, current_player_color: str):
    game = Game(
        start_time=datetime.now(timezone.utc),
        game_length=timedelta(seconds=length),
        supplement=timedelta(seconds=supplement),
        fen="rnbkkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBKKBNR w KQkq - 0 1"
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
        'fen_pos': game.get_pos()
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
def move(game_id: int, new_pos: str):
    game = Game.query.get(game_id)
    old_pos = game.get_pos()

    if fen_pos_is_valid(new_pos) and move_is_legal(game, fen_pos_to_matrix(new_pos)):
        piece_letter, source, target = get_move_info(fen_pos_to_matrix(old_pos), fen_pos_to_matrix(new_pos))
        game.add_move(piece_letter, source.name, target.name)
        new_fen = get_new_fen(game, new_pos)
        game.update_fen(new_fen)
        socketio.emit('fen_pos', new_pos)
    else:
        old_pos = game.get_pos()
        socketio.emit('fen_pos', old_pos)


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


def move_is_legal(game: Game, new_pos: list):
    old_pos = fen_pos_to_matrix(game.get_pos())
    # castling = game.get_castling_availability()
    # enpassand_target = game.get_enpassand_target()
    # halfmove_clock = game.get_halfmove_clock()
    # moves_number = game.get_fullmove_number()

    if moves_count(old_pos, new_pos) != 1:
        return False

    piece_letter, source, target = get_move_info(old_pos, new_pos)

    piece = letter_to_piece(piece_letter)
    if source is not None and target is not None and piece_letter is not None and piece.valid_move(source, target) and not piece.moved_throught_piece(source, target, old_pos) and not takes_their_own_piece(target, old_pos, new_pos):
        print('Piece:', piece)
        print('Piece letter:', piece.letter)
        print('Source:', source.name)
        print('Target:', target.name)
        print('Move color:', move_color(piece_letter))
        print()

    # if game.get_active_color() != move_color(piece_letter):
    #     return False
    if not piece.valid_move(source, target):
        return False
    if piece.moved_throught_piece(source, target, old_pos):
        return False
    if takes_their_own_piece(target, old_pos, new_pos):
        return False

    return True


def fen_pos_to_matrix(fen_pos: str):
    pos_matrix = [[] for i in range(8)]
    for i in range(8):
        for sq in fen_pos.split('/')[i]:
            if sq.isdigit():
                pos_matrix[i].extend(['' for j in range(int(sq))])
            else:
                pos_matrix[i].append(sq)
    return pos_matrix


def get_new_fen(game: Game, new_pos: str):
    return new_pos + ' w KQkq - 0 1'


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
            if old_pos[i][j] != '' and new_pos[i][j] == '':
                piece = old_pos[i][j]
                source = Square(i, j)
            elif old_pos[i][j] != new_pos[i][j]:
                target = Square(i, j)
    return piece, source, target


def move_color(piece: str):
    if piece.isupper():
        return 'w'
    return 'b'


def takes_their_own_piece(target: Square, old_pos: list, new_pos: list):
    if old_pos[target.i][target.j] != "":
        if move_color(old_pos[target.i][target.j]) == move_color(new_pos[target.i][target.j]):
            if old_pos[target.i][target.j] != new_pos[target.i][target.j]:
                return True
    return False


# def takes_opponents_piece(target: Square, old_pos: list, new_pos: list):
#     if old_pos[target.i][target.j] != "":
#         if move_color(old_pos[target.i][target.j]) != move_color(new_pos[target.i][target.j]):
#             return True
#     return False
