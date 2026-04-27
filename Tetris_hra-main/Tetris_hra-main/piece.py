import random
from settings import SHAPES, COLUMNS

class Piece:
    def __init__(self, shape=None, color=None):
        if shape is None or color is None:
            shape, color = random.choice(SHAPES)
        self.shape = shape
        self.color = color
        self.x = COLUMNS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        # Vrátí novou matici (otočenou)
        return [list(row) for row in zip(*self.shape[::-1])]
    
    def clone(self):
        # Pomocná metoda pro AI
        p = Piece(self.shape, self.color)
        p.x = self.x
        p.y = self.y
        return p