from math import ceil
from random import choice
from datetime import datetime, timezone, timedelta

from flask_login import current_user

from chess import db
from chess.models import Game, Player, User
from chess.pieces import get_pieces, Piece, King, Pawn, Knight, Rook, Bishop, Queen
from chess.square import Square, squarename_to_square
from chess.notations import fen_pos_to_pos, pos_to_fen_pos, move_to_an


# game creation
def create_browser_game(length: int, supplement: int, opponent_username: str, current_player_color: str):
    game = Game(
        start_time=datetime.now(timezone.utc),
        game_length=timedelta(seconds=length),
        supplement=timedelta(seconds=supplement),
    )
    if current_player_color == 'random':
        current_player_color = choice(['b', 'w'])
    opponent = User.query.filter(User.username == opponent_username).first()
    game.players = create_players(opponent, current_user, current_player_color)

    return create_game(game)


def create_tg_game(current_player_user_id, current_player_color, opponent_user_id: int = None, opponent_email: str = None):
    success = None
    message = None
    game = Game(
        start_time=datetime.now(timezone.utc),
        telegram_game=True
    )
    if opponent_user_id:
        opponent = User.query.filter(User.user_id == opponent_user_id)
    elif opponent_email:
        opponent = User.query.filter(User.email == opponent_email)
    else:
        success = False
        message = "Neither opponent's email nor opponent's user_id is provided"
    current = User.query.filter(User.user_id == current_player_user_id)

    game.players = create_players(opponent, current, current_player_color)

    game = create_game(game)

    if game is None:
        success = False
        message = "Game creation failed"
    elif success is None:
        success = True
        message = 'Game creation successful'

    return success, message


def create_game(game: Game):
    if not (game.telegram_game and not game.game_length and not game.supplement or game.game_length and game.supplement):
        return None
    db.session.add(game)
    db.session.commit()

    return game


def get_game_conf(game_id: int):
    # for browser
    game = Game.query.get(game_id)
    game_conf = {
        'game_length': game.game_length,
        'supplement': game.supplement,
        'current_player': game.players[0] if game.players[0].user == current_user else game.players[1],
        'opponent': game.players[0] if game.players[0].user != current_user else game.players[1],
        'fen': game.fen
    } if game and not game.telegram_game else None
    return game_conf


def create_players(opponent: User, current: User, current_player_color: str):
    player1 = Player(
        color=current_player_color,
    )
    player1.user = current

    colors = ['b', 'w']
    colors.remove(current_player_color)
    player2_color = colors[0]
    player2 = Player(
        color=player2_color,
    )
    player2.user = opponent

    return [player1, player2]


def get_my_games():
    user = current_user
    games = [player.game for player in user.players if player.game is not None]
    return games[::-1]


# move processing
def move(game_id: int, new_fen_pos: str, promotion: str):
    game = Game.query.get(game_id)
    old_fen_pos = game.get_fen_pos()
    old_pos = fen_pos_to_pos(old_fen_pos)
    new_pos = fen_pos_to_pos(new_fen_pos)

    for i in range(8):
        for j in range(8):
            print(old_pos[i][j].letter if old_pos[i][j] is not None else '*', end=' ')
        print(end=' ' * 2)
        for j in range(8):
            print(new_pos[i][j].letter if new_pos[i][j] is not None else '*', end=' ')
        print()

    success = False
    if fen_pos_is_valid(new_fen_pos) and move_is_legal(game, old_pos, new_pos, promotion):

        piece, source, target, tries_to_castle = get_move_info(old_pos, new_pos, game)
        castling_str = get_castling_str(source, target, new_pos, game)

        en_passand_target = game.get_enpassand_target()
        if en_passand(source, target, piece, en_passand_target):
            new_fen_pos = get_en_passand_fen_pos(target, new_fen_pos)
        new_en_passand_target = generate_en_passand_target(source, target, piece)

        game.add_move(piece.letter, source.name, target.name)
        game.update_fen(new_fen_pos, castling_str, new_en_passand_target)

        success = True

    return success


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


def move_is_legal(game: Game, old_pos: list, new_pos: list, promotion: str):
    castling = game.get_castling_availability()
    en_passand_target = game.get_enpassand_target()
    # halfmove_clock = game.get_halfmove_clock()
    # moves_number = game.get_fullmove_number()

    number_of_moves = moves_count(old_pos, new_pos)
    if not 1 <= number_of_moves <= 2:
        print("Invalid number of moves:", number_of_moves)
        return False
    if number_of_moves == 2 and get_castle_code(old_pos, new_pos, game) is None and not move_is_en_passand(old_pos, new_pos, en_passand_target):
        print("Invalid number of moves: 2(move is not castles and not en passand)")
        return False

    piece, source, target, tries_to_castle = get_move_info(old_pos, new_pos, game)
    kings = find_kings(new_pos)
    check = ''
    checkmate = ''
    stalemate = ''
    for king in kings:
        if king.check(king.square, new_pos):
            check += king.color
        if king.checkmate(king.square, new_pos):
            checkmate += king.color
        if king.stalemate(king.square, new_pos):
            stalemate += king.color
        if king.color == piece.color:
            current_players_king = king
    if check == '':
        check = 'False'
    if checkmate == '':
        checkmate = 'False'
    if stalemate == '':
        stalemate = 'False'

    if source and target and piece:
        print('Move:', move_to_an(source, target, old_pos, new_pos, promotion))
        print('Piece:', piece)
        print('Piece letter:', piece.letter)
        print('Source:', source.name)
        print('Target:', target.name)
        print('Move color:', piece.color)
        print('Check:', check)
        print('Stalemate:', stalemate)
        print('Checkmate:', checkmate)
        print('Insufficient material:', insufficient_material(new_pos))
        print()

    if game.get_active_color() != piece.color:
        print("Invalid color")
        return False
    if not piece.valid_move(source, target, old_pos, castling, en_passand_target):
        print("Invalid move")
        return False
    if piece.moved_through_piece(source, target, old_pos):
        print("Moved throught piece")
        return False
    if takes_their_own_piece(target, old_pos, new_pos):
        print("Takes same colored piece")
        return False
    if takes_king(target, old_pos, new_pos):
        print("Takes king")
        return False
    if current_players_king.check(current_players_king.square, new_pos):
        print("Cannot move this because it's check")
        return False
    if isinstance(piece, Pawn) and not pawn_takes_in_valid_way(source, target, old_pos, en_passand_target):
        print("Pawn tries to take piece in front")
        return False
    if isinstance(piece, Pawn) and not valid_diagonal_pawn_move(source, target, old_pos, en_passand_target):
        print("Pawn steps on empty square diagonally")
        return False

    return True


def moves_count(old_pos: list, new_pos: list):
    changes_count = 0
    for i in range(8):
        for j in range(8):
            if old_pos[i][j] != new_pos[i][j]:
                changes_count += 1
    return ceil(changes_count / 2)


def get_move_info(old_pos: list, new_pos: list, game: Game):
    piece, source, target = None, None, None
    castle_code = get_castle_code(old_pos, new_pos, game)
    if castle_code is not None:
        source, target = Square(-1, -1), Square(-1, -1)
        source.set_j(4)
        if castle_code[0] == 'b':
            source.set_i(0), target.set_i(0)
        else:
            source.set_i(7), target.set_i(7)
        if castle_code[1] == 'l':
            target.set_j(2)
        else:
            target.set_j(6)
        piece = King(castle_code[0], sq=source)
        return piece, source, target, True

    en_passand_sq = squarename_to_square(game.get_enpassand_target())
    if move_is_en_passand(old_pos, new_pos, game.get_enpassand_target()):
        piece = new_pos[en_passand_sq.i][en_passand_sq.j]
        target = en_passand_sq

        if piece.color == 'w' and en_passand_sq.j > 0 and old_pos[3][en_passand_sq.j - 1] and not new_pos[3][en_passand_sq.j - 1]:
            source = old_pos[3][en_passand_sq.j - 1].square
        if piece.color == 'w' and en_passand_sq.j < 7 and old_pos[3][en_passand_sq.j + 1] and not new_pos[3][en_passand_sq.j + 1]:
            source = old_pos[3][en_passand_sq.j + 1].square
        if piece.color == 'b' and en_passand_sq.j > 0 and old_pos[4][en_passand_sq.j - 1] and not new_pos[4][en_passand_sq.j - 1]:
            source = old_pos[4][en_passand_sq.j - 1].square
        if piece.color == 'b' and en_passand_sq.j < 7 and old_pos[4][en_passand_sq.j + 1] and not new_pos[4][en_passand_sq.j + 1]:
            source = old_pos[4][en_passand_sq.j + 1].square

        return piece, source, target, False

    for i in range(8):
        for j in range(8):
            if old_pos[i][j] is not None and new_pos[i][j] is None:
                piece = old_pos[i][j]
                source = Square(i, j)
            elif old_pos[i][j] != new_pos[i][j]:
                target = Square(i, j)

    return piece, source, target, False


def takes_their_own_piece(target: Square, old_pos: list, new_pos: list):
    i = target.i
    j = target.j
    return old_pos[i][j] and new_pos[i][j] and old_pos[i][j].color == new_pos[i][j].color


def takes_king(target: Square, old_pos: list, new_pos: list):
    if isinstance(old_pos[target.i][target.j], King) and new_pos[target.i][target.j] != old_pos[target.i][target.j]:
        return True


def find_kings(pos: list):
    kings = []
    for i in range(8):
        for j in range(8):
            if isinstance(pos[i][j], King):
                kings.append(pos[i][j])
    return kings


def pawn_takes_in_valid_way(source: Square, target: Square, old_pos: list, en_passand_target: str):
    if old_pos[source.i][source.j].color == 'w':
        if source.i == 3 and target.i == 2 and abs(source.j - target.j) == 1 and target.name == en_passand_target:
            return True
    elif old_pos[source.i][source.j].color == 'b':
        if source.i == 4 and target.i == 5 and abs(source.j - target.j) == 1 and target.name == en_passand_target:
            return True
    if source.j == target.j and old_pos[target.i][target.j] is not None:
        return False
    return True


def valid_diagonal_pawn_move(source: Square, target: Square, old_pos: list, en_passand_target: str):
    if abs(source.j - target.j) == 1 and old_pos[target.i][target.j] is None and target.name != en_passand_target:
        return False
    return True


def insufficient_material(pos: list):
    w_pieces = get_pieces(pos, color='w')
    b_pieces = get_pieces(pos, color='b')
    w_insufficient = insufficient_material_for_color(w_pieces, b_pieces, 'w')
    b_insufficient = insufficient_material_for_color(b_pieces, w_pieces, 'b')
    if w_insufficient and b_insufficient:
        return True
    return False


def insufficient_material_for_color(pieces: list, opponents_pieces: str, color: str):
    knights_count = count_pieces(pieces, Knight)
    bishops_count = count_pieces(pieces, Bishop)
    enough_to_mate_pieces_count = count_pieces(pieces, Queen)
    enough_to_mate_pieces_count += count_pieces(pieces, Rook)
    enough_to_mate_pieces_count += count_pieces(pieces, Pawn)

    if len(pieces) == 1:
        return True
    if enough_to_mate_pieces_count != 0:
        return False
    if knights_count == 1 and bishops_count == 0:
        return True
    if knights_count == 0 and bishops_count == 1:
        return True
    if len(opponents_pieces) == 1 and len(pieces) == 3 and knights_count == 2:
        return True

    return False


def count_pieces(pieces: list, piece_type: Piece):
    piece_count = 0
    for piece in pieces:
        if isinstance(piece, piece_type):
            piece_count += 1
    return piece_count


def get_castle_code(old_pos: list, new_pos: list, game: Game):
    b_king_gone = isinstance(old_pos[0][4], King) and not isinstance(new_pos[0][4], King)
    b_king_moved_l = b_king_gone and isinstance(new_pos[0][2], King)
    b_rook_gone_l = isinstance(old_pos[0][0], Rook) and not isinstance(new_pos[0][0], Rook)
    b_rook_moved_l = b_rook_gone_l and isinstance(new_pos[0][3], Rook)

    if b_king_moved_l and b_rook_moved_l:
        return "bl"

    b_king_moved_r = b_king_gone and isinstance(new_pos[0][6], King)
    b_rook_gone_r = isinstance(old_pos[0][7], Rook) and not isinstance(new_pos[0][7], Rook)
    b_rook_moved_r = b_rook_gone_r and isinstance(new_pos[0][5], Rook)

    if b_king_moved_r and b_rook_moved_r:
        return "br"

    w_king_gone = isinstance(old_pos[7][4], King) and not isinstance(new_pos[7][4], King)
    w_king_moved_l = w_king_gone and isinstance(new_pos[7][2], King)
    w_rook_gone_l = isinstance(old_pos[7][0], Rook) and not isinstance(new_pos[7][0], Rook)
    w_rook_moved_l = w_rook_gone_l and isinstance(new_pos[7][3], Rook)

    if w_king_moved_l and w_rook_moved_l:
        return "wl"

    w_king_moved_r = w_king_gone and isinstance(new_pos[7][6], King)
    w_rook_gone_r = isinstance(old_pos[7][7], Rook) and not isinstance(new_pos[7][7], Rook)
    w_rook_moved_r = w_rook_gone_r and isinstance(new_pos[7][5], Rook)

    if w_king_moved_r and w_rook_moved_r:
        return "wr"

    return None


def get_castling_str(source: Square, target: Square, pos: list, game: Game):
    piece = pos[target.i][target.j]
    castling_str = ""
    castling = game.get_castling_availability()

    if isinstance(piece, King):
        if 'K' in castling and piece.color != 'w':
            castling_str += 'K'
        if 'Q' in castling and piece.color != 'w':
            castling_str += 'Q'
        if 'k' in castling and piece.color != 'b':
            castling_str += 'k'
        if 'q' in castling and piece.color != 'b':
            castling_str += 'q'

    elif isinstance(piece, Rook):
        if 'K' in castling and not (source.j == 7 and pos[target.i][target.j].color == 'w'):
            castling_str += 'K'
        if 'Q' in castling and not (source.j == 0 and pos[target.i][target.j].color == 'w'):
            castling_str += 'Q'
        if 'k' in castling and not (source.j == 7 and pos[target.i][target.j].color == 'b'):
            castling_str += 'k'
        if 'q' in castling and not (source.j == 0 and pos[target.i][target.j].color == 'b'):
            castling_str += 'q'

    else:
        castling_str = game.get_castling_availability()

    if castling_str == "":
        castling_str = "-"

    return castling_str


def move_is_en_passand(old_pos: list, new_pos: list, en_passand_target: str):
    if en_passand_target == '-':
        return False
    sq = squarename_to_square(en_passand_target)
    if old_pos[sq.i][sq.j] is not None or not isinstance(new_pos[sq.i][sq.j], Pawn):
        return False
    if sq.i == 2:
        if not (old_pos[3][sq.j].color == 'b' and new_pos[sq.i][sq.j].color == 'w'):
            return False
        if new_pos[3][sq.j]:
            return False
        if sq.j > 0 and isinstance(old_pos[3][sq.j - 1], Pawn) and new_pos[3][sq.j - 1] is None and old_pos[3][sq.j - 1].color != old_pos[3][sq.j].color:
            return True
        if sq.j < 7 and isinstance(old_pos[3][sq.j + 1], Pawn) and new_pos[3][sq.j + 1] is None and old_pos[3][sq.j + 1].color != old_pos[3][sq.j].color:
            return True
    elif sq.i == 5:
        if not (old_pos[4][sq.j].color == 'w' and new_pos[sq.i][sq.j].color == 'b'):
            return False
        if new_pos[4][sq.j]:
            return False
        if sq.j > 0 and isinstance(old_pos[4][sq.j - 1], Pawn) and new_pos[4][sq.j - 1] is None and old_pos[4][sq.j - 1].color != old_pos[4][sq.j].color:
            return True
        if sq.j < 7 and isinstance(old_pos[4][sq.j + 1], Pawn) and new_pos[4][sq.j + 1] is None and old_pos[4][sq.j + 1].color != old_pos[4][sq.j].color:
            return True

    return False


def en_passand(source: Square, target: Square, piece: Piece, en_passand_target: str):
    if en_passand_target == '-':
        return False
    if not isinstance(piece, Pawn):
        return False
    if target.name != en_passand_target:
        return False
    if source.i == 3 and target.i == 2 and piece.color == 'w' and abs(target.j - source.j == 1):
        return True
    if source.i == 4 and target.i == 5 and piece.color == 'b' and abs(target.j - source.j == 1):
        return True
    return True


def get_en_passand_fen_pos(target: Square, fen_pos: str):
    pos = fen_pos_to_pos(fen_pos)
    piece = pos[target.i][target.j]
    if piece.color == 'w' and target.i == 2:
        pos[3][target.j] = None
    elif piece.color == 'b' and target.i == 5:
        pos[4][target.j] = None
    else:
        raise ValueError("No En Passand")
    return pos_to_fen_pos(pos)


def generate_en_passand_target(source: Square, target: Square, piece: Piece):
    en_passand_target = '-'
    if isinstance(piece, Pawn) and abs(source.i - target.i) == 2:
        en_passand_target = Square((target.i + source.i) // 2, target.j).name
    return en_passand_target
