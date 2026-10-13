class LayoutCursor:
    def __init__(self, x: number = 0, y: number = 0):
        self.origin_x = x
        self.origin_y = y
        self.x = x
        self.y = y
        self._checkpoints: (int, int, int, int) = []

    def save(self, origin: bool = False):
        self._checkpoints.append((self.origin_x, self.origin_y, self.x, self.y))

        if origin:
            self.set_origin()

    def set_origin(self, t: literal["x", "y"] | None = None):
        if t != "y":
            self.origin_x = self.x
        if t != "x":
            self.origin_y = self.y

    def load(self):
        if self._checkpoints:
            self.origin_x, self.origin_y, self.x, self.y = self._checkpoints.pop()

    def reset_x(self):
        self.x = self.origin_x

    def reset_y(self):
        self.y = self.origin_y

    # def next(self, offset: number = None) -> number:
    #     """Springt zur nächsten Zeile und setzt X auf den Spaltenursprung zurück."""
    #     self.x = self.origin_x
    #     self.down(offset if offset is not None else self.line_height)
    #     return self.x, self.y

    # TODO: @deprecated - delete
    # def next_row(self, offset=None) -> number:
    #     """Springt zur nächsten Zeile und setzt X auf den Spaltenursprung zurück."""
    #     self.x = self.origin_x
    #     self.down(offset)
    #     return self.x, self.y

    # def down(self, offset: number = None) -> number:
    #     self.y += offset if offset is not None else self.line_height
    #     return self.y

    # def move_x(self, x: number) -> number:
    #     self.x += x
    #     return self.x

    # def set_x(self, x: number) -> number:
    #     self.x = x
    #     return self.x

    # @deprecated, use save()
    # def push(self):
    #     """Speichert den aktuellen Zustand (z. B. vor Beginn einer Spalte)."""
    #     self._checkpoints.append((self.origin_x, self.origin_y, self.x, self.y))

    # # @deprecated, use save()
    # def pop(self):
    #     """Stellt den vorherigen Zustand wieder her."""
    #     if self._checkpoints:
    #         self.origin_x, self.origin_y, self.x, self.y = self._checkpoints.pop()

    # def column(self, x_offset):
    #     """Erzeugt temporär einen neuen Spaltenursprung."""
    #     self.push()
    #     self.origin_x = self.x + x_offset
    #     self.x = self.origin_x

    # def reset(self, type: literal["x", "y"] | None = None):
    #     if type == "x":
    #         self.x = self.origin_x
    #     if type == "y":
    #         self.y = self.origin_y
    #     if type == None:

    #     self.reset_x()
    #     self.reset_y()
    #     self._checkpoints = []
