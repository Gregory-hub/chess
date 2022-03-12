from abc import ABC

from chess.square import Square
from chess.excepitons import ColorError


class Piece(ABC):
    def __init__(self, color: str, sq: Square = None):
        if color not in ['w', 'b']:
            raise ColorError(color=color)
        self.color = color
        if color == 'w':
            self.letter = self.letter.upper()
        self.square = sq

    def valid_move(self, source: Square, target: Square, pos: list, castling: str):
        pass

    def moved_throught_piece(self, source: Square, target: Square, pos: list):
        pass

    def available_squares(self, pos: list):
        return generate_available_squares(pos, self)

    def __eq__(self, other):
        if self is None and other is None:
            return True
        elif self is None and other is not None or self is not None and other is None:
            return False
        else:
            return self.letter == other.letter and self.color == other.color

    def __repr__(self):
        return f"{self.__class__.__name__}<color={self.color}, square={self.square.name}>"


class King(Piece):
    letter = 'k'

    def valid_move(self, source: Square, target: Square, pos: list, castling: str):
        if source is None or target is None:
            return False

        if castling != '-':
            if self.__valid_castling(source, target, pos, castling):
                return True

        if abs(target.i - source.i) <= 1 and abs(target.j - source.j) <= 1:
            return True
        else:
            return False

    def moved_throught_piece(self, source: Square, target: Square, pos: list):
        return False

    def check(self, target: Square, pos: list):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == j == 0 or not 0 <= target.i + i <= 7 or not 0 <= target.j + j <= 7:
                    continue

        potential_evil_pieces = self.__pieces_attacking_sq(target, pos)
        for piece in potential_evil_pieces:
            if self.color != piece.color:
                return True

        return False

    def checkmate(self, target: Square, pos: list):
        if not self.check(target, pos):
            return False
        if not self.__king_cannot_move(target, pos):
            return False

        evil_pieces = self.__pieces_attacking_sq(target, pos)
        if len(evil_pieces) == 1:
            evil_piece = evil_pieces[0]
            if self.__piece_can_be_taken(evil_piece, pos) or self.__check_can_be_blocked(target, evil_piece, pos):
                return False
        return True

    def stalemate(self, target: Square, pos: list):
        if self.__no_moves(target, pos) and not self.check(target, pos):
            return True
        return False

    def castles(self, source: Square, target: Square, pos: list, castling: str):
        return self.__valid_castling(source, target, pos, castling)

    def castles_short(self, target: Square):
        return target.j in [6, 7]
    
    def castles_long(self, target: Square):
        return target.j in [0, 1, 2]

    def __no_moves(self, target: Square, pos: list):
        pieces = get_pieces(pos)
        pieces = self.__filter_pieces(pieces, color=self.color)
        kings = [piece for piece in pieces if isinstance(piece, King)]
        pieces = [piece for piece in pieces if not isinstance(piece, King)]

        available_moves = self.__get_all_available_squares(pieces, pos)
        for king in kings:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    sq = Square(king.square.i + i, king.square.j + j)
                    if i == 0 and j == 0 or not 0 <= sq.i <= 7 or not 0 <= sq.j <= 7:
                        continue
                    if (not pos[sq.i][sq.j] or pos[sq.i][sq.j].color != king.color) and not self.__gets_in_check(king.square, sq, pos):
                        available_moves.append(sq)

        if available_moves == []:
            return True
        return False

    def __filter_pieces(self, pieces: list, color: str):
        filtered_pieces = []
        for piece in pieces:
            if piece.color == color:
                filtered_pieces.append(piece)
        return filtered_pieces

    def __get_all_available_squares(self, pieces: list, pos: list):
        squares = []
        for piece in pieces:
            squares.extend(piece.available_squares(pos))
        return squares

    def __king_cannot_move(self, target: Square, pos: list):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == j == 0 or not 0 <= target.i + i <= 7 or not 0 <= target.j + j <= 7:
                    continue
                sq = Square(target.i + i, target.j + j)
                if not pos[sq.i][sq.j] or pos[sq.i][sq.j].color != self.color:
                    if not self.__gets_in_check(target, sq, pos):
                        return False
        return True

    def __piece_can_be_taken(self, piece: Piece, pos: list):
        for evil_piece in self.__pieces_attacking_sq(piece.square, pos):
            if piece.color != evil_piece.color and not isinstance(evil_piece, King):
                return True
            elif isinstance(evil_piece, King):
                if not self.__gets_in_check(evil_piece.square, piece.square, pos):
                    return True
        return False

    def __check_can_be_blocked(self, target: Square, evil_piece: Piece, pos: list):
        if isinstance(evil_piece, (Bishop, Queen)):
            return self.__diagonal_check_can_be_blocked(target, evil_piece, pos)
        elif isinstance(evil_piece, (Rook, Queen)):
            return self.__straight_check_can_be_blocked(target, evil_piece, pos)
        else:
            return False

    def __diagonal_check_can_be_blocked(self, target: Square, evil_piece: Piece, pos: list):
        evil_target = evil_piece.square
        squares_to_check = []
        if target.i < evil_target.i and target.j < evil_target.j:
            squares_to_check = [Square(target.i + i, target.j + i) for i in range(1, evil_target.i - target.i)]
        elif target.i < evil_target.i and target.j > evil_target.j:
            squares_to_check = [Square(target.i + i, target.j - i) for i in range(1, evil_target.i - target.i)]
        elif target.i > evil_target.i and target.j < evil_target.j:
            squares_to_check = [Square(target.i - i, target.j + i) for i in range(1, evil_target.i - target.i)]
        elif target.i > evil_target.i and target.j > evil_target.j:
            squares_to_check = [Square(target.i - i, target.j - i) for i in range(1, evil_target.i - target.i)]

        for sq in squares_to_check:
            for piece in self.__pieces_attacking_sq(sq, pos):
                if piece.color != evil_piece.color and not isinstance(piece, King):
                    return True

        return False

    def __straight_check_can_be_blocked(self, target: Square, evil_piece: Piece, pos: list):
        evil_target = evil_piece.square
        if target.i == evil_target.i:
            for j in range(min(target.j, evil_target.j) + 1, max(target.j, evil_target.j)):
                for piece in self.__pieces_attacking_sq(Square(target.i, j), pos):
                    if piece.color != evil_piece.color and not isinstance(piece, King):
                        return True
        elif target.j == evil_target.j:
            for i in range(min(target.i, evil_target.i) + 1, max(target.i, evil_target.i)):
                for piece in self.__pieces_attacking_sq(Square(i, target.j), pos):
                    if piece.color != evil_piece.color and not isinstance(piece, King):
                        return True
        return False

    def __sq_contains_piece(self, sq: Square, pos: list, evil_pieces: list):
        not_empty = False
        is_evil_piece = False
        if sq and pos[sq.i][sq.j] is not None:
            not_empty = True
            for piece in evil_pieces:
                if isinstance(pos[sq.i][sq.j], piece):
                    is_evil_piece = True
                    break
        return not_empty, is_evil_piece

    def __pieces_attacking_sq(self, target: Square, pos: list):
        pieces = get_pieces(pos)
        evil_pieces = []
        for piece in pieces:
            if target in piece.available_squares(pos):
                evil_pieces.append(piece)
        return evil_pieces

    def __generate_temp_pos(self, king_sq: Square, sq: Square, pos: list):
        temp_pos = [x[:] for x in pos]
        temp_pos[sq.i][sq.j] = pos[king_sq.i][king_sq.j]
        temp_pos[king_sq.i][king_sq.j] = None
        return temp_pos

    def __gets_in_check(self, king_sq, sq, pos):
        temp_pos = self.__generate_temp_pos(king_sq, sq, pos)
        if self.check(sq, temp_pos):
            return True
        return False

    def __can_castle(self, castling: str):
        long, short = False, False
        q, k = 'q', 'k'
        if self.color == 'w':
            q = q.upper()
            k = k.upper()

        if q in castling:
            long = True
        if k in castling:
            short = True

        return long, short

    def __valid_castling(self, source: Square, target: Square, pos: list, castling: str):
        if self.check(target, pos):
            return False
        long, short = self.__can_castle(castling)
        if self.color == 'b' and not (source.name == 'e8' and target.i == 0):
            return False
        if self.color == 'w' and not (source.name == 'e1' and target.i == 7):
            return False
        if self.castles_long(target) and long:
            if pos[target.i][1]:
                return False
            if pos[target.i][2] or self.__gets_in_check(source, Square(target.i, 2), pos):
                return False
            if pos[target.i][3] or self.__gets_in_check(source, Square(target.i, 3), pos):
                return False
            return True
        if self.castles_short(target) and short:
            if pos[target.i][5] or self.__gets_in_check(source, Square(target.i, 5), pos):
                return False
            if pos[target.i][6] or self.__gets_in_check(source, Square(target.i, 6), pos):
                return False
            return True
        return False


class Queen(Piece):
    letter = 'q'

    def valid_move(self, source: Square, target: Square, pos: list, castling: str):
        if source is None or target is None:
            return False

        if (source.i == target.i) ^ (source.j == target.j):
            return True
        if target.i == target.j + source.i - source.j or target.i == -target.j + source.i + source.j:
            return True
        return False

    def moved_throught_piece(self, source: Square, target: Square, pos: list):
        left_sq, right_sq = min(source.j, target.j), max(source.j, target.j)
        upper_sq, lower_sq = min(source.i, target.i), max(source.i, target.i)

        if target.j == source.j and target.i == source.i:
            return False

        elif target.i == source.i:
            for j in range(left_sq + 1, right_sq):
                if pos[source.i][j] is not None:
                    return True

        elif target.j == source.j:
            for i in range(upper_sq + 1, lower_sq):
                if pos[i][source.j] is not None:
                    return True

        elif source.i > target.i and source.j < target.j or source.i < target.i and source.j > target.j:
            for j in range(left_sq + 1, right_sq):
                i = -j + source.i + source.j                        # y = -x + b
                if i < 8 and pos[i][j] is not None:
                    return True

        else:
            for j in range(left_sq + 1, right_sq):
                i = j + source.i - source.j                         # y = x + b
                if i < 8 and pos[i][j] is not None:
                    return True

        return False


class Rook(Piece):
    letter = 'r'

    def valid_move(self, source: Square, target: Square, pos: list, castling: str):
        if source is None or target is None:
            return False

        if (source.i == target.i) ^ (source.j == target.j):
            return True
        return False

    def moved_throught_piece(self, source: Square, target: Square, pos: list):
        for j in range(min(source.j, target.j) + 1, max(source.j, target.j)):
            if pos[source.i][j] is not None:
                return True

        for i in range(min(source.i, target.i) + 1, max(source.i, target.i)):
            if pos[i][source.j] is not None:
                return True

        return False


class Bishop(Piece):
    letter = 'b'

    def valid_move(self, source: Square, target: Square, pos: list, castling: str):
        if source is None or target is None:
            return False

        if target.i == target.j + source.i - source.j or target.i == -target.j + source.i + source.j:
            return True
        return False

    def moved_throught_piece(self, source: Square, target: Square, pos: list):
        left_sq, right_sq = min(source.j, target.j), max(source.j, target.j)
        if source.i > target.i and source.j < target.j or source.i < target.i and source.j > target.j:
            for j in range(left_sq + 1, right_sq):
                i = -j + source.i + source.j    # y = -x + b
                if i < 8 and pos[i][j] is not None:
                    return True
        else:
            for j in range(left_sq + 1, right_sq):
                i = j + source.i - source.j     # y = x + b
                if i < 8 and pos[i][j] is not None:
                    return True
        return False


class Knight(Piece):
    letter = 'n'

    def valid_move(self, source: Square, target: Square, pos: list, castling: str):
        if source is None or target is None:
            return False

        if abs(target.i - source.i) == 1 and abs(target.j - source.j) == 2:
            return True
        elif abs(target.i - source.i) == 2 and abs(target.j - source.j) == 1:
            return True
        return False

    def moved_throught_piece(self, source: Square, target: Square, pos: list):
        return False


class Pond(Piece):
    letter = 'p'

    def valid_move(self, source: Square, target: Square, pos: list, castling: str):
        if source is None or target is None:
            return False

        if self.color == 'w':
            if source.i == 7 or target.i == 7:
                return False
            elif source.i == 6 and target.i == 4:
                if target.j != source.j:
                    return False
            elif source.i - target.i != 1:
                return False
            elif abs(target.j - source.j) > 1:
                return False

            return True

        elif self.color == 'b':
            if source.i == 0 or target.i == 0:
                return False
            elif source.i == 1 and target.i == 3:
                if target.j != source.j:
                    return False
            elif target.i - source.i != 1:
                return False
            elif abs(target.j - source.j) > 1:
                return False

            return True

    def moved_throught_piece(self, source: Square, target: Square, pos: list):
        if abs(source.i - target.i) == 2 and pos[(source.i + target.i) // 2][source.j] is not None:
            return True

        return False


def letter_to_piece(letter: str):
    if letter.isupper():
        color = 'w'
    else:
        color = 'b'

    if letter.upper() == 'K':
        return King(color=color)
    elif letter.upper() == 'Q':
        return Queen(color=color)
    elif letter.upper() == 'R':
        return Rook(color=color)
    elif letter.upper() == 'B':
        return Bishop(color=color)
    elif letter.upper() == 'N':
        return Knight(color=color)
    elif letter.upper() == 'P':
        return Pond(color=color)
    else:
        return None


def generate_available_squares(pos: list, piece: Piece):
    squares = []

    if isinstance(piece, Rook) or isinstance(piece, Queen):
        squares.extend(rook_squares(pos, piece))
    if isinstance(piece, Bishop) or isinstance(piece, Queen):
        squares.extend(bishop_squares(pos, piece))
    if isinstance(piece, Knight):
        squares.extend(knight_squares(pos, piece))
    if isinstance(piece, Pond):
        squares.extend(pond_squares(pos, piece))
    if isinstance(piece, King):
        squares.extend(king_squares(pos, piece))

    return squares


def rook_squares(pos: list, piece: [Rook, Queen]):
    squares = []
    empty_up = empty_down = empty_left = empty_right = True
    for k in range(1, 8):
        if empty_up:
            sq = Square(piece.square.i + k, piece.square.j)
            if not sq.valid_coords():
                empty_up = False
            else:
                not_empty = True if pos[sq.i][sq.j] else False
                if not_empty:
                    empty_up = False
                    if pos[sq.i][sq.j].color != piece.color:
                        squares.append(sq)
                else:
                    squares.append(sq)

        if empty_down:
            sq = Square(piece.square.i - k, piece.square.j)
            if not sq.valid_coords():
                empty_down = False
            else:
                not_empty = True if pos[sq.i][sq.j] else False
                if not_empty:
                    empty_down = False
                    if pos[sq.i][sq.j].color != piece.color:
                        squares.append(sq)
                else:
                    squares.append(sq)

        if empty_right:
            sq = Square(piece.square.i, piece.square.j + k)
            if not sq.valid_coords():
                empty_right = False
            else:
                not_empty = True if pos[sq.i][sq.j] else False
                if not_empty:
                    empty_right = False
                    if pos[sq.i][sq.j].color != piece.color:
                        squares.append(sq)
                else:
                    squares.append(sq)

        if empty_left:
            sq = Square(piece.square.i, piece.square.j - k)
            if not sq.valid_coords():
                empty_left = False
            else:
                not_empty = True if pos[sq.i][sq.j] else False
                if not_empty:
                    empty_left = False
                    if pos[sq.i][sq.j].color != piece.color:
                        squares.append(sq)
                else:
                    squares.append(sq)

        not_empty_straight = not empty_up and not empty_down and not empty_left and not empty_right
        if not_empty_straight:
            break

    return squares


def bishop_squares(pos: list, piece: [Bishop, Queen]):
    squares = []
    empty_up_l = empty_down_l = empty_up_r = empty_down_r = True

    for k in range(1, 8):
        if empty_up_l:
            sq = Square(piece.square.i + k, piece.square.j - k)
            if not sq.valid_coords():
                empty_up_l = False
            else:
                not_empty = True if pos[sq.i][sq.j] else False
                if not_empty:
                    empty_up_l = False
                    if pos[sq.i][sq.j].color != piece.color:
                        squares.append(sq)
                else:
                    squares.append(sq)

        if empty_up_r:
            sq = Square(piece.square.i + k, piece.square.j + k)
            if not sq.valid_coords():
                empty_up_r = False
            else:
                not_empty = True if pos[sq.i][sq.j] else False
                if not_empty:
                    empty_up_r = False
                    if pos[sq.i][sq.j].color != piece.color:
                        squares.append(sq)
                else:
                    squares.append(sq)

        if empty_down_l:
            sq = Square(piece.square.i - k, piece.square.j - k)
            if not sq.valid_coords():
                empty_down_l = False
            else:
                not_empty = True if pos[sq.i][sq.j] else False
                if not_empty:
                    empty_down_l = False
                    if pos[sq.i][sq.j].color != piece.color:
                        squares.append(sq)
                else:
                    squares.append(sq)

        if empty_down_r:
            sq = Square(piece.square.i - k, piece.square.j + k)
            if not sq.valid_coords():
                empty_down_r = False
            else:
                not_empty = True if pos[sq.i][sq.j] else False
                if not_empty:
                    empty_down_r = False
                    if pos[sq.i][sq.j].color != piece.color:
                        squares.append(sq)
                else:
                    squares.append(sq)

        not_empty_diagonal = not empty_down_l and not empty_down_r and not empty_up_l and not empty_up_r
        if not_empty_diagonal:
            break

    return squares


def knight_squares(pos: list, piece: Knight):
    squares = []

    sq = Square(piece.square.i - 2, piece.square.j - 1)
    if sq.valid_coords() and (not pos[sq.i][sq.j] or pos[sq.i][sq.j].color != piece.color):
        squares.append(sq)
    sq = Square(piece.square.i - 2, piece.square.j + 1)
    if sq.valid_coords() and (not pos[sq.i][sq.j] or pos[sq.i][sq.j].color != piece.color):
        squares.append(sq)
    sq = Square(piece.square.i - 1, piece.square.j - 2)
    if sq.valid_coords() and (not pos[sq.i][sq.j] or pos[sq.i][sq.j].color != piece.color):
        squares.append(sq)
    sq = Square(piece.square.i - 1, piece.square.j + 2)
    if sq.valid_coords() and (not pos[sq.i][sq.j] or pos[sq.i][sq.j].color != piece.color):
        squares.append(sq)
    sq = Square(piece.square.i + 1, piece.square.j - 2)
    if sq.valid_coords() and (not pos[sq.i][sq.j] or pos[sq.i][sq.j].color != piece.color):
        squares.append(sq)
    sq = Square(piece.square.i + 1, piece.square.j + 2)
    if sq.valid_coords() and (not pos[sq.i][sq.j] or pos[sq.i][sq.j].color != piece.color):
        squares.append(sq)
    sq = Square(piece.square.i + 2, piece.square.j - 1)
    if sq.valid_coords() and (not pos[sq.i][sq.j] or pos[sq.i][sq.j].color != piece.color):
        squares.append(sq)
    sq = Square(piece.square.i + 2, piece.square.j + 1)
    if sq.valid_coords() and (not pos[sq.i][sq.j] or pos[sq.i][sq.j].color != piece.color):
        squares.append(sq)

    return squares


def pond_squares(pos: list, piece: Pond):
    squares = []

    if piece.color == 'w':
        sq = Square(piece.square.i - 1, piece.square.j - 1)
        if sq.valid_coords() and (not pos[sq.i][sq.j] or pos[sq.i][sq.j].color != piece.color):
            squares.append(sq)
        sq = Square(piece.square.i - 1, piece.square.j + 1)
        if sq.valid_coords() and (not pos[sq.i][sq.j] or pos[sq.i][sq.j].color != piece.color):
            squares.append(sq)
    elif piece.color == 'b':
        sq = Square(piece.square.i + 1, piece.square.j - 1)
        if sq.valid_coords() and (not pos[sq.i][sq.j] or pos[sq.i][sq.j].color != piece.color):
            squares.append(sq)
        sq = Square(piece.square.i + 1, piece.square.j + 1)
        if sq.valid_coords() and (not pos[sq.i][sq.j] or pos[sq.i][sq.j].color != piece.color):
            squares.append(sq)

    return squares


def king_squares(pos: list, piece: King):
    squares = []

    for i in range(-1, 2):
        for j in range(-1, 2):
            sq = Square(piece.square.i + i, piece.square.j + j)
            if i == 0 and j == 0 or not 0 <= sq.i <= 7 or not 0 <= sq.j <= 7:
                continue
            if not pos[sq.i][sq.j] or pos[sq.i][sq.j].color != piece.color:
                squares.append(sq)

    return squares


def get_pieces(pos: list, color: str = None):
    pieces = []
    for i in range(8):
        for j in range(8):
            if pos[i][j] and (color is None or color == pos[i][j].color):
                pieces.append(pos[i][j])
    return pieces
