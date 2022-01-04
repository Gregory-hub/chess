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

    def delivers_check(self, target: Square, current_color: str, pos: list):
        pass

    def __eq__(self, other):
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

    def delivers_check(self, target: Square, current_color: str, pos: list):
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

        if target.j == source.j and target.i == source.i:
            return False

        elif target.i == source.i:
            for j in range(left_sq + 1, right_sq):
                if pos[source.i][j] != "":
                    return True

        elif target.j == source.j:
            for i in range(left_sq + 1, right_sq):
                if pos[i][source.j] != "":
                    return True

        elif source.i > target.i and source.j < target.j or source.i < target.i and source.j > target.j:
            for j in range(left_sq + 1, right_sq):
                i = -j + source.i + source.j                        # y = -x + b
                if i < 8 and pos[i][j] != "":
                    return True

        else:
            for j in range(left_sq + 1, right_sq):                  # y = x + b
                i = j + source.i - source.j
                if i < 8 and pos[i][j] != "":
                    return True

        return False

    def delivers_check(self, target: Square, current_color: str, pos: list):
        empty_up_l = True
        empty_down_l = True
        empty_up_r = True
        empty_down_r = True
        empty_up = True
        empty_down = True
        empty_left = True
        empty_right = True

        if current_color == 'b':
            king_let = 'K'
        elif current_color == 'w':
            king_let = 'k'
        else:
            raise ColorError(color=current_color)

        for k in range(1, 8):
            if empty_up_l and 0 <= target.i + k <= 7 and 0 <= target.j - k <= 7 and pos[target.i + k][target.j - k] != "":
                if pos[target.i + k][target.j - k] == king_let:
                    return True
                else:
                    empty_up_l = False

            if empty_down_l and 0 <= target.i - k <= 7 and 0 <= target.j - k <= 7 and pos[target.i - k][target.j - k] != "":
                if pos[target.i - k][target.j - k] == king_let:
                    return True
                else:
                    empty_down_l = False

            if empty_up_r and 0 <= target.i + k <= 7 and 0 <= target.j + k <= 7 and pos[target.i + k][target.j + k] != "":
                if pos[target.i + k][target.j + k] == king_let:
                    return True
                else:
                    empty_up_r = False

            if empty_down_r and 0 <= target.i - k <= 7 and 0 <= target.j + k <= 7 and pos[target.i - k][target.j + k] != "":
                if pos[target.i - k][target.j + k] == king_let:
                    return True
                else:
                    empty_down_r = False

            if empty_up and 0 <= target.i + k <= 7 and pos[target.i + k][target.j] != "":
                if pos[target.i + k][target.j] == king_let:
                    return True
                else:
                    empty_up = False

            if empty_down and 0 <= target.i - k <= 7 and pos[target.i - k][target.j] != "":
                if pos[target.i - k][target.j] == king_let:
                    return True
                else:
                    empty_down = False

            if empty_right and 0 <= target.j + k <= 7 and pos[target.i][target.j + k] != "":
                if pos[target.i][target.j + k] == king_let:
                    return True
                else:
                    empty_right = False

            if empty_left and 0 <= target.j - k <= 7 and pos[target.i][target.j - k] != "":
                if pos[target.i][target.j - k] == king_let:
                    return True
                else:
                    empty_left = False

            if not empty_up and not empty_down and not empty_left and not empty_right:
                break

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
            if pos[source.i][j] != "":
                return True

        for i in range(min(source.i, target.i) + 1, max(source.i, target.i)):
            if pos[i][source.j] != "":
                return True

        return False

    def delivers_check(self, target: Square, current_color: str, pos: list):
        empty_up = True
        empty_down = True
        empty_left = True
        empty_right = True

        if current_color == 'b':
            king_let = 'K'
        elif current_color == 'w':
            king_let = 'k'
        else:
            raise ColorError(color=current_color)

        for k in range(1, 8):
            if empty_up and 0 <= target.i + k <= 7 and pos[target.i + k][target.j] != "":
                if pos[target.i + k][target.j] == king_let:
                    return True
                else:
                    empty_up = False

            if empty_down and 0 <= target.i - k <= 7 and pos[target.i - k][target.j] != "":
                if pos[target.i - k][target.j] == king_let:
                    return True
                else:
                    empty_down = False

            if empty_right and 0 <= target.j + k <= 7 and pos[target.i][target.j + k] != "":
                if pos[target.i][target.j + k] == king_let:
                    return True
                else:
                    empty_right = False

            if empty_left and 0 <= target.j - k <= 7 and pos[target.i][target.j - k] != "":
                if pos[target.i][target.j - k] == king_let:
                    return True
                else:
                    empty_left = False

            if not empty_up and not empty_down and not empty_left and not empty_right:
                break

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
                if i < 8 and pos[i][j] != "":
                    return True
        else:
            for j in range(left_sq + 1, right_sq):
                i = j + source.i - source.j     # y = x + b
                if i < 8 and pos[i][j] != "":
                    return True
        return False

    def delivers_check(self, target: Square, current_color: str, pos: list):
        empty_up_l = True
        empty_down_l = True
        empty_up_r = True
        empty_down_r = True

        if current_color == 'b':
            king_let = 'K'
        elif current_color == 'w':
            king_let = 'k'
        else:
            raise ColorError(color=current_color)

        for k in range(1, 8):
            if empty_up_l and 0 <= target.i + k <= 7 and 0 <= target.j - k <= 7 and pos[target.i + k][target.j - k] != "":
                if pos[target.i + k][target.j - k] == king_let:
                    return True
                else:
                    empty_up_l = False

            if empty_down_l and 0 <= target.i - k <= 7 and 0 <= target.j - k <= 7 and pos[target.i - k][target.j - k] != "":
                if pos[target.i - k][target.j - k] == king_let:
                    return True
                else:
                    empty_down_l = False

            if empty_up_r and 0 <= target.i + k <= 7 and 0 <= target.j + k <= 7 and pos[target.i + k][target.j + k] != "":
                if pos[target.i + k][target.j + k] == king_let:
                    return True
                else:
                    empty_up_r = False

            if empty_down_r and 0 <= target.i - k <= 7 and 0 <= target.j + k <= 7 and pos[target.i - k][target.j + k] != "":
                if pos[target.i - k][target.j + k] == king_let:
                    return True
                else:
                    empty_down_r = False

            if not empty_up_l and not empty_down_l and not empty_up_r and not empty_down_r:
                break

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

    def delivers_check(self, target: Square, current_color: str, pos: list):
        if current_color == 'b':
            king_let = 'K'
        elif current_color == 'w':
            king_let = 'k'
        else:
            raise ColorError(color=current_color)

        if target.i >= 2 and target.j >= 1 and pos[target.i - 2][target.j - 1] == king_let:
            return True
        elif target.i >= 2 and target.j <= 6 and pos[target.i - 2][target.j + 1] == king_let:
            return True
        elif target.i >= 1 and target.j <= 5 and pos[target.i - 1][target.j + 2] == king_let:
            return True
        elif target.i <= 6 and target.j <= 5 and pos[target.i + 1][target.j + 2] == king_let:
            return True
        elif target.i <= 5 and target.j <= 6 and pos[target.i + 2][target.j + 1] == king_let:
            return True
        elif target.i <= 5 and target.j >= 1 and pos[target.i + 2][target.j - 1] == king_let:
            return True
        elif target.i <= 6 and target.j >= 2 and pos[target.i + 1][target.j - 2] == king_let:
            return True
        elif target.i >= 1 and target.j >= 2 and pos[target.i - 1][target.j - 2] == king_let:
            return True

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
        if abs(source.i - target.i) == 2 and pos[(source.i + target.i) // 2][source.j] != "":
            return True

        return False

    def delivers_check(self, target: Square, current_color: str, pos: list):
        if current_color == 'b':
            king_let = 'K'
        elif current_color == 'w':
            king_let = 'k'
        else:
            raise ColorError(color=current_color)

        if target.i not in [0, 7]:
            if current_color == 'b':
                if target.j > 0 and pos[target.i + 1][target.j - 1] == king_let:
                    return True
                elif target.j < 7 and pos[target.i + 1][target.j + 1] == king_let:
                    return True
            elif current_color == 'w':
                if target.j > 0 and pos[target.i - 1][target.j - 1] == king_let:
                    return True
                elif target.j < 7 and pos[target.i - 1][target.j + 1] == king_let:
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
