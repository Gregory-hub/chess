class Square:
    i = -1
    j = -1

    def __init__(self, i: int, j: int):
        if not 0 <= i <= 7 or not 0 <= j <= 7:
            return None
        self.i = i
        self.j = j
        self.name = squarename(i, j)

    def valid_coords(self):
        if not 0 <= self.i <= 7 or not 0 <= self.j <= 7:
            return False
        return True


def squarename(i: int, j: int):
    if not 0 <= i <= 7 or not 0 <= j <= 7:
        return "Err"
    return "abcdefgh"[j] + str(8 - i)
