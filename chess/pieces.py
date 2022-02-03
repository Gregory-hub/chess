from abc import ABC

from chess.square import Square
from chess.excepitons import ColorError


class Piece(ABC):
    def __init__(self, color: str):
        if color not in ['w', 'b']:
            raise ColorError(color=color)
        self.color = color
        if color == 'w':
            self.letter = self.letter.upper()

    def valid_move(self, source: Square, target: Square):
        pass

    def moved_throught_piece(self, source: Square, target: Square, pos: list):
        pass

    def __eq__(self, other):
        if self is None and other is None:
            return True
        elif self is None and other is not None or self is not None and other is None:
            return False
        else:
            return self.letter == other.letter and self.color == other.color


class King(Piece):
    letter = 'k'

    def valid_move(self, source: Square, target: Square):
        if source is None or target is None:
            return False

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
                if isinstance(pos[target.i + i][target.j + j], King) and pos[target.i + i][target.j + j].color != self.color:
                    return True

        potential_evil_pieces = self.__pieces_attacking_sq(target, pos)
        if potential_evil_pieces is not None:
            for piece in potential_evil_pieces:
                if self.color != piece.color:
                    return True

        return False

    def checkmate(self, target: Square, pos: list):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not 0 <= target.i + i <= 7 or not 0 <= target.j + j <= 7:
                    continue
                if not pos[target.i + i][target.j + j] and not self.is_check(pos[target.i + i][target.j + j], pos):
                    return False

        evil_pieces = self.__get_evil_pieces_and_squares(target, pos)
        if len(evil_pieces) == 1:
            evil_piece, evil_sq = evil_pieces[0][0], evil_pieces[0][1]
            if self.__can_block_check(target, evil_piece, evil_sq, pos):
                return False
        return True

    def __get_evil_pieces_and_squares(self, target: Square, pos: list):
        pass

    def __piece_can_be_taken(self, sq: Square, pos: list):
        pass

    def __can_block_check(self, target: Square, evil_piece: Piece, evil_sq: Square, pos: list):
        pass

    def __can_block_diagonal_check(self, target: Square, evil_piece: Piece, evil_sq: Square, pos: list):
        pass

    def __can_block_straight_check(self, target: Square, evil_piece: Piece, evil_sq: Square, pos: list):
        pass

    def __sq_contains_piece(self, sq: Square, pos: list, evil_pieces: list):
        not_empty = False
        is_evil_piece = False
        if 0 <= sq.i <= 7 and 0 <= sq.j <= 7 and pos[sq.i][sq.j] is not None:
            not_empty = True
            for piece in evil_pieces:
                if isinstance(pos[sq.i][sq.j], piece):
                    is_evil_piece = True
                    break
        return not_empty, is_evil_piece

    def __pieces_attacking_sq(self, target: Square, pos: list):
        empty_up_l = True
        empty_down_l = True
        empty_up_r = True
        empty_down_r = True
        empty_up = True
        empty_down = True
        empty_left = True
        empty_right = True

        pieces = []

        diagonal_pieces = [Bishop, Queen]
        straight_pieces = [Rook, Queen]

        for k in range(1, 8):
            sq = Square(target.i + k, target.j - k)
            not_empty, is_evil_piece = self.__sq_contains_piece(sq, pos, diagonal_pieces)
            if empty_up_l and not_empty:
                empty_up_l = False
                if is_evil_piece:
                    pieces.append(pos[sq.i][sq.j])

            sq = Square(target.i - k, target.j - k)
            not_empty, is_evil_piece = self.__sq_contains_piece(sq, pos, diagonal_pieces)
            if empty_down_l and not_empty:
                empty_down_l = False
                if is_evil_piece:
                    pieces.append(pos[sq.i][sq.j])

            sq = Square(target.i + k, target.j + k)
            not_empty, is_evil_piece = self.__sq_contains_piece(sq, pos, diagonal_pieces)
            if empty_up_r and not_empty:
                empty_up_r = False
                if is_evil_piece:
                    pieces.append(pos[sq.i][sq.j])

            sq = Square(target.i - k, target.j + k)
            not_empty, is_evil_piece = self.__sq_contains_piece(sq, pos, diagonal_pieces)
            if empty_down_r and not_empty:
                empty_down_r = False
                if is_evil_piece:
                    pieces.append(pos[sq.i][sq.j])

            sq = Square(target.i + k, target.j)
            not_empty, is_evil_piece = self.__sq_contains_piece(sq, pos, straight_pieces)
            if empty_up and not_empty:
                empty_up = False
                if is_evil_piece:
                    pieces.append(pos[sq.i][sq.j])

            sq = Square(target.i - k, target.j)
            not_empty, is_evil_piece = self.__sq_contains_piece(sq, pos, straight_pieces)
            if empty_down and not_empty:
                empty_down = False
                if is_evil_piece:
                    pieces.append(pos[sq.i][sq.j])

            sq = Square(target.i, target.j + k)
            not_empty, is_evil_piece = self.__sq_contains_piece(sq, pos, straight_pieces)
            if empty_right and not_empty:
                empty_right = False
                if is_evil_piece:
                    pieces.append(pos[sq.i][sq.j])

            sq = Square(target.i, target.j - k)
            not_empty, is_evil_piece = self.__sq_contains_piece(sq, pos, straight_pieces)
            if empty_left and not_empty:
                empty_left = False
                if is_evil_piece:
                    pieces.append(pos[sq.i][sq.j])

            not_empty_straight = not empty_up and not empty_down and not empty_left and not empty_right
            not_empty_diagonal = not empty_down_l and not empty_down_r and not empty_up_l and not empty_up_r
            if not_empty_diagonal and not_empty_straight:
                break

        sq = Square(target.i - 2, target.j - 1)
        if self.__sq_contains_piece(sq, pos, [Knight])[1]:
            pieces.append(pos[sq.i][sq.j])
        sq = Square(target.i - 2, target.j + 1)
        if self.__sq_contains_piece(sq, pos, [Knight])[1]:
            pieces.append(pos[sq.i][sq.j])
        sq = Square(target.i - 1, target.j - 2)
        if self.__sq_contains_piece(sq, pos, [Knight])[1]:
            pieces.append(pos[sq.i][sq.j])
        sq = Square(target.i - 1, target.j + 2)
        if self.__sq_contains_piece(sq, pos, [Knight])[1]:
            pieces.append(pos[sq.i][sq.j])
        sq = Square(target.i + 1, target.j - 2)
        if self.__sq_contains_piece(sq, pos, [Knight])[1]:
            pieces.append(pos[sq.i][sq.j])
        sq = Square(target.i + 1, target.j + 2)
        if self.__sq_contains_piece(sq, pos, [Knight])[1]:
            pieces.append(pos[sq.i][sq.j])
        sq = Square(target.i + 2, target.j - 1)
        if self.__sq_contains_piece(sq, pos, [Knight])[1]:
            pieces.append(pos[sq.i][sq.j])
        sq = Square(target.i + 2, target.j + 1)
        if self.__sq_contains_piece(sq, pos, [Knight])[1]:
            pieces.append(pos[sq.i][sq.j])

        sq = Square(target.i + 1, target.j - 1)
        if target.j > 0 and target.i < 7 and self.color == 'b' and isinstance(pos[sq.i][sq.j], Pond):
            pieces.append(pos[sq.i][sq.j])
        sq = Square(target.i + 1, target.j + 1)
        if target.j < 7 and target.i < 7 and self.color == 'b' and isinstance(pos[sq.i][sq.j], Pond):
            pieces.append(pos[sq.i][sq.j])
        sq = Square(target.i - 1, target.j - 1)
        if target.j > 0 and target.i > 0 and self.color == 'w' and isinstance(pos[sq.i][sq.j], Pond):
            pieces.append(pos[sq.i][sq.j])
        sq = Square(target.i - 1, target.j + 1)
        if target.j < 7 and target.i > 0 and self.color == 'w' and isinstance(pos[sq.i][sq.j], Pond):
            pieces.append(pos[sq.i][sq.j])

        if pieces != []:
            return pieces
        else:
            return None


class Queen(Piece):
    letter = 'q'

    def valid_move(self, source: Square, target: Square):
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

    def valid_move(self, source: Square, target: Square):
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

    def valid_move(self, source: Square, target: Square):
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

    def valid_move(self, source: Square, target: Square):
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

    def valid_move(self, source: Square, target: Square):
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
