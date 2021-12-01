class Square:
    def __init__(self, i: int, j: int):
        self.i = i
        self.j = j
        self.name = squarename(i, j)


def squarename(i: int, j: int):
    return 'abcdefgh'[j] + str(8 - i)
