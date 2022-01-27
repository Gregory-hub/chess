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

    def __sq_contains_piece(self, sq: Square, pos: list, evil_pieces: list):
        not_empty = False
        evil_piece = False
        is_check = False
        if 0 <= sq.i <= 7 and 0 <= sq.j <= 7 and pos[sq.i][sq.j] is not None:
            not_empty = True
            for piece in evil_pieces:
                if isinstance(pos[sq.i][sq.j], piece):
                    evil_piece = True
                    break
            if evil_piece and pos[sq.i][sq.j].color != self.color:
                is_check = True
        return not_empty, is_check

    def in_check(self, target: Square, pos: list):
        empty_up_l = True
        empty_down_l = True
        empty_up_r = True
        empty_down_r = True
        empty_up = True
        empty_down = True
        empty_left = True
        empty_right = True

        diagonal_pieces = [Bishop, Queen]
        straight_pieces = [Rook, Queen]

        for k in range(1, 8):
            sq = Square(target.i + k, target.j - k)
            not_empty, is_check = self.__sq_contains_piece(sq, pos, diagonal_pieces)
            if empty_up_l and not_empty:
                empty_up_l = False
                if is_check:
                    return True

            sq = Square(target.i - k, target.j - k)
            not_empty, is_check = self.__sq_contains_piece(sq, pos, diagonal_pieces)
            if empty_down_l and not_empty:
                empty_down_l = False
                if is_check:
                    return True

            sq = Square(target.i + k, target.j + k)
            not_empty, is_check = self.__sq_contains_piece(sq, pos, diagonal_pieces)
            if empty_up_r and not_empty:
                empty_up_r = False
                if is_check:
                    return True

            sq = Square(target.i - k, target.j + k)
            not_empty, is_check = self.__sq_contains_piece(sq, pos, diagonal_pieces)
            if empty_down_r and not_empty:
                empty_down_r = False
                if is_check:
                    return True

            sq = Square(target.i + k, target.j)
            not_empty, is_check = self.__sq_contains_piece(sq, pos, straight_pieces)
            if empty_up and not_empty:
                empty_up = False
                if is_check:
                    return True

            sq = Square(target.i - k, target.j)
            not_empty, is_check = self.__sq_contains_piece(sq, pos, straight_pieces)
            if empty_down and not_empty:
                empty_down = False
                if is_check:
                    return True

            sq = Square(target.i, target.j + k)
            not_empty, is_check = self.__sq_contains_piece(sq, pos, straight_pieces)
            if empty_right and not_empty:
                empty_right = False
                if is_check:
                    return True

            sq = Square(target.i, target.j - k)
            not_empty, is_check = self.__sq_contains_piece(sq, pos, straight_pieces)
            if empty_left and not_empty:
                empty_left = False
                if is_check:
                    return True

            not_empty_straight = not empty_up and not empty_down and not empty_left and not empty_right
            not_empty_diagonal = not empty_down_l and not empty_down_r and not empty_up_l and not empty_up_r
            if not_empty_diagonal and not_empty_straight:
                break

        sq = Square(target.i - 2, target.j - 1)
        if self.__sq_contains_piece(sq, pos, [Knight])[1]:
            return True
        sq = Square(target.i - 2, target.j + 1)
        if self.__sq_contains_piece(sq, pos, [Knight])[1]:
            return True
        sq = Square(target.i - 1, target.j - 2)
        if self.__sq_contains_piece(sq, pos, [Knight])[1]:
            return True
        sq = Square(target.i - 1, target.j + 2)
        if self.__sq_contains_piece(sq, pos, [Knight])[1]:
            return True
        sq = Square(target.i + 1, target.j - 2)
        if self.__sq_contains_piece(sq, pos, [Knight])[1]:
            return True
        sq = Square(target.i + 1, target.j + 2)
        if self.__sq_contains_piece(sq, pos, [Knight])[1]:
            return True
        sq = Square(target.i + 2, target.j - 1)
        if self.__sq_contains_piece(sq, pos, [Knight])[1]:
            return True
        sq = Square(target.i + 2, target.j + 1)
        if self.__sq_contains_piece(sq, pos, [Knight])[1]:
            return True

        if target.j > 0 and target.i < 7 and isinstance(pos[target.i + 1][target.j - 1], Pond) and pos[target.i + 1][target.j - 1].color != self.color:
            return True
        elif target.j < 7 and target.i < 7 and isinstance(pos[target.i + 1][target.j + 1], Pond) and pos[target.i + 1][target.j + 1].color != self.color:
            return True

        if target.j > 0 and target.i > 0 and isinstance(pos[target.i - 1][target.j - 1], Pond) and pos[target.i - 1][target.j - 1].color != self.color:
            return True
        elif target.j < 7 and target.i > 0 and isinstance(pos[target.i - 1][target.j + 1], Pond) and pos[target.i - 1][target.j + 1].color != self.color:
            return True

        return False


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
