class ColorError(ValueError):
    def __init__(self, color: str = None):
        self.message = "Color can be only 'b' or 'w'"
        self.color = color
        super().__init__(self.message)

    def __str__(self):
        if self.color:
            return f"'{self.color}' -> {self.message}"
        else:
            return self.message


class KingInitializingException(ValueError):
    def __init__(self):
        self.message = "Invalid king initialization"
        super().__init__(self.message)
