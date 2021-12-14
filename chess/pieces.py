from abc import ABC

from chess.square import Square


class Piece(ABC):
    def __init__(self, color: str):
        self.color = color
        if color == 'w':
            self.letter = self.letter.upper()

    def valid_move(self, source: Square, target: Square):
        pass

    def moved_throught_piece(self, source: Square, target: Square, pos: list):
        pass


class King(Piece):
    letter = 'k'

    def valid_move(self, source: Square, target: Square):
        if abs(target.i - source.i) <= 1 and abs(target.j - source.j) <= 1:
            return True
        else:
            return False

    def moved_throught_piece(self, source: Square, target: Square, pos: list):
        return False


class Queen(Piece):
    letter = 'q'

    def valid_move(self, source: Square, target: Square):
        if (source.i == target.i) ^ (source.j == target.j):
            return True
        if target.i == target.j + source.i - source.j or target.i == -target.j + source.i + source.j:
            return True
        return False

    def moved_throught_piece(self, source: Square, target: Square, pos: list):
        left_sq, right_sq = min(source.j, target.j), max(source.j, target.j)
        if source.i > target.i and source.j < target.j or source.i < target.i and source.j > target.j:  # y = -x + b
            for j in range(left_sq + 1, right_sq):
                i = -j + source.i + source.j
                if i < 8 and pos[i][j] != "":
                    return True
        else:                           # y = x + b
            for j in range(left_sq + 1, right_sq):
                i = j + source.i - source.j
                if i < 8 and pos[i][j] != "":
                    return True

        for j in range(min(source.j, target.j) + 1, max(source.j, target.j)):
            if pos[source.i][j] != "":
                return True

        for i in range(min(source.i, target.i) + 1, max(source.i, target.i)):
            if pos[i][source.j] != "":
                return True

        return False


class Rook(Piece):
    letter = 'r'

    def valid_move(self, source: Square, target: Square):
        if (source.i == target.i) ^ (source.j == target.j):
            return True
        return False

    def moved_throught_piece(self, source: Square, target: Square, pos: list):
        for j in range(min(source.j, target.j) + 1, max(source.j, target.j)):
            if pos[source.i][j] != "":
                return True

        for i in range(min(source.i, target.i) + 1, max(source.i, target.i)):
            if pos[i][source.j] != "":
                return True

        return False


class Bishop(Piece):
    letter = 'b'

    def valid_move(self, source: Square, target: Square):
        if target.i == target.j + source.i - source.j or target.i == -target.j + source.i + source.j:
            return True
        return False

    def moved_throught_piece(self, source: Square, target: Square, pos: list):
        left_sq, right_sq = min(source.j, target.j), max(source.j, target.j)
        if source.i > target.i and source.j < target.j or source.i < target.i and source.j > target.j:  # y = -x + b
            for j in range(left_sq + 1, right_sq):
                i = -j + source.i + source.j
                if i < 8 and pos[i][j] != "":
                    return True
        else:                           # y = x + b
            for j in range(left_sq + 1, right_sq):
                i = j + source.i - source.j
                if i < 8 and pos[i][j] != "":
                    return True

        return False


class Knight(Piece):
    letter = 'n'

    def valid_move(self, source: Square, target: Square):
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
        if abs(source.i - target.i) == 2 and pos[(source.i + target.i) // 2][source.j] != "":
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
