class Square:
    def __init__(self, i: int, j: int):
        self.i = i
        self.j = j
        self.name = squarename(i, j)


def squarename(i: int, j: int):
    if j > 7 or i > 7:
        return "Err"
    return "abcdefgh"[j] + str(8 - i)
