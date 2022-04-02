import copy

from chess.pieces import letter_to_piece, generate_available_squares, Pawn, King
from chess.square import Square
from chess.exceptions import InvalidMoveException


def fen_pos_to_pos(fen_pos: str):
    pos_matrix = [[] for i in range(8)]
    for i in range(8):
        row = fen_pos.split('/')[i]
        j = 0
        for sq in row:
            if sq.isdigit():
                pos_matrix[i].extend([None for j in range(int(sq))])
                j += int(sq)
            else:
                piece = letter_to_piece(sq)
                piece.square = Square(i, j)
                pos_matrix[i].append(piece)
                j += 1
    return pos_matrix


def pos_to_fen_pos(pos: list):
    fen_pos = ''
    for i in range(8):
        j = 0
        while j < 8:
            empty_count = 0
            while j < 8 and pos[i][j] is None:
                empty_count += 1
                j += 1
            if empty_count != 0:
                fen_pos += str(empty_count)
            if j < 8:
                fen_pos += pos[i][j].letter
                j += 1
        if i != 7:
            fen_pos += '/'
    return fen_pos


def move_to_an(source: Square, target: Square, old_pos: list, new_pos: list, promotion: str):
    """Returns move in algebraic notation format. Assuming move is valid"""
    piece = new_pos[target.i][target.j]
    init_square_name = ''
    final_square_name = target.name
    take_sign = ''
    end = ''

    if piece is None:
        raise InvalidMoveException
    piece_letter = piece.letter.upper()
    if piece_letter == 'P':
        piece_letter = ''

    if isinstance(piece, King) and source.j == 4:
        if piece.color == 'w' and target.j == 2:
            return 'O-O'
        if piece.color == 'b' and target.j == 2:
            return 'O-O-O'
        if piece.color == 'w' and target.j == 6:
            return 'O-O-O'
        if piece.color == 'b' and target.j == 6:
            return 'O-O'

    if piece.color == 'w' and isinstance(piece, Pawn):
        piece_behind = old_pos[target.i + 1][target.j]
    elif piece.color == 'b' and isinstance(piece, Pawn):
        piece_behind = old_pos[target.i - 1][target.j]
    else:
        piece_behind = None

    if abs(target.j - source.j) == 1 and isinstance(piece_behind, Pawn) and piece_behind.color != piece.color:
        take_sign = 'x'

    if old_pos[target.i][target.j]:
        if old_pos[target.i][target.j].color == piece.color:
            raise InvalidMoveException
        take_sign = 'x'
        if isinstance(piece, Pawn):
            init_square_name = source.name[0]

    temp_piece = copy.deepcopy(piece)
    temp_piece.color = 'w' if piece.color == 'b' else 'b'
    squares = generate_available_squares(new_pos, temp_piece)
    for sq in squares:
        if isinstance(old_pos[sq.i][sq.j], type(piece)) and sq != source and not isinstance(piece, Pawn):
            if sq.j == source.j and not piece.moved_through_piece(sq, target, old_pos):
                init_square_name += source.name[0]
            if sq.i == source.i and not piece.moved_through_piece(sq, target, old_pos):
                init_square_name += source.name[1]

    if promotion != '' and isinstance(piece, Pawn):
        end = '+=' + promotion

    for i in range(8):
        for j in range(8):
            if isinstance(new_pos[i][j], King):
                sq = Square(i, j)
                if new_pos[sq.i][sq.j].check(sq, new_pos):
                    end = '+'
                if new_pos[sq.i][sq.j].checkmate(sq, new_pos):
                    end = '#'

    return piece_letter + init_square_name + take_sign + final_square_name + end
