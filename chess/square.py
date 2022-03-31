class Square:
    i = -1
    j = -1

    def __init__(self, i: int, j: int):
        self.i = i
        self.j = j
        self.name = squarename(i, j)

    def valid_coords(self):
        if not 0 <= self.i <= 7 or not 0 <= self.j <= 7:
            return False
        return True

    def set_i(self, i: int):
        self.i = i
        self.name = squarename(self.i, self.j)

    def set_j(self, j: int):
        self.j = j
        self.name = squarename(self.i, self.j)

    def set_coords(self, i: int, j: int):
        self.i = i
        self.j = j
        self.name = squarename(i, j)

    def __repr__(self):
        return f"<Square({self.i}, {self.j}, name={self.name})>"

    def __eq__(self, other):
        if self.i == other.i and self.j == other.j:
            return True
        return False


def squarename(i: int, j: int):
    if not 0 <= i <= 7 or not 0 <= j <= 7:
        return "Err"
    return "abcdefgh"[j] + str(8 - i)


def squarename_to_square(name: str):
    if name[0] not in "abcdefgh" or name[1] not in "1234568":
        return None
    i = 8 - int(name[1])
    j = "abcdefgh".index(name[0])
    return Square(i, j)
