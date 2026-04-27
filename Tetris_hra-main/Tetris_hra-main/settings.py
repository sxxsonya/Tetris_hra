import os
ASSETS_DIR = "assets"
BACKGROUND_IMG_PATH = os.path.join(ASSETS_DIR, "background.png")


WIDTH, HEIGHT = 400, 600
GRID_SIZE = 30
PLAY_WIDTH = 300
COLUMNS, ROWS = PLAY_WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE

# Barvy
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Témata levelů (barva pozadí hrací plochy)
LEVEL_THEMES = {
    1: (10, 10, 20),
    2: (20, 10, 10),
    3: (10, 20, 10),
    4: (20, 20, 10),
    5: (20, 10, 20)
}

# Tvary
SHAPES = [
    ([[1, 1, 1, 1]], (0, 255, 255)), # I
    ([[1, 1], [1, 1]], (255, 255, 0)), # O
    ([[0, 1, 0], [1, 1, 1]], (128, 0, 128)), # T
    ([[1, 0, 0], [1, 1, 1]], (0, 0, 255)), # J
    ([[0, 0, 1], [1, 1, 1]], (255, 165, 0)), # L
    ([[1, 1, 0], [0, 1, 1]], (0, 255, 0)), # S
    ([[0, 1, 1], [1, 1, 0]], (255, 0, 0)), # Z
]