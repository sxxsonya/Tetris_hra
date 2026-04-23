import pygame
import random
import os

WIDTH, HEIGHT = 400, 600
GRID_SIZE = 30
PLAY_WIDTH = 300

COLUMNS, ROWS = PLAY_WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE

BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)

SHAPES = [
    ([[1, 1, 1, 1]], (0, 255, 255)),
    ([[1, 1], [1, 1]], (255, 255, 0)),
    ([[0, 1, 0], [1, 1, 1]], (128, 0, 128)),
    ([[1, 0, 0], [1, 1, 1]], (0, 0, 255)),
    ([[0, 0, 1], [1, 1, 1]], (255, 165, 0)),
    ([[1, 1, 0], [0, 1, 1]], (0, 255, 0)),
    ([[0, 1, 1], [1, 1, 0]], (255, 0, 0)),
]

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)


class Piece:
    def __init__(self):
        shape, color = random.choice(SHAPES)
        self.shape = shape
        self.color = color
        self.x = COLUMNS // 2 - 1
        self.y = 0

    def rotate(self):
        return [list(row) for row in zip(*self.shape[::-1])]


class Game:
    def __init__(self):
        self.grid = [[0]*COLUMNS for _ in range(ROWS)]
        self.colors = [[None]*COLUMNS for _ in range(ROWS)]

        self.piece = Piece()
        self.next_piece = Piece()
        self.hold_piece = None
        self.can_hold = True

        self.score = 0
        self.level = 1
        self.lines = 0

        self.drop_time = 0
        self.running = True

        self.highscore = self.load_highscore()

    def load_highscore(self):
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as f:
                return int(f.read())
        return 0

    def save_highscore(self):
        with open("highscore.txt", "w") as f:
            f.write(str(self.highscore))

    def check_collision(self, dx=0, dy=0, shape=None):
        shape = shape or self.piece.shape
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    nx = self.piece.x + x + dx
                    ny = self.piece.y + y + dy

                    if nx < 0 or nx >= COLUMNS or ny >= ROWS:
                        return True
                    if ny >= 0 and self.grid[ny][nx]:
                        return True
        return False

    def get_ghost_y(self):
        ghost_y = self.piece.y
        while not self.check_collision(dy=(ghost_y - self.piece.y) + 1):
            ghost_y += 1
        return ghost_y
    def merge(self):
        for y, row in enumerate(self.piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    ny = self.piece.y + y
                    nx = self.piece.x + x
                    if 0 <= ny < ROWS:
                        self.grid[ny][nx] = 1
                        self.colors[ny][nx] = self.piece.color

    def clear_lines(self):
        cleared = 0
        new_grid = []
        new_colors = []

        for y in range(ROWS):
            if all(self.grid[y]):
                cleared += 1
                # animace
                for x in range(COLUMNS):
                    self.colors[y][x] = WHITE
                self.draw()
                pygame.time.delay(50)
            else:
                new_grid.append(self.grid[y])
                new_colors.append(self.colors[y])

        while len(new_grid) < ROWS:
            new_grid.insert(0, [0]*COLUMNS)
            new_colors.insert(0, [None]*COLUMNS)

        self.grid = new_grid
        self.colors = new_colors

        self.lines += cleared
        self.score += cleared * 100

        if self.score > self.highscore:
            self.highscore = self.score

        if self.lines // 10 > self.level:
            self.level += 1

    def hold(self):
        if not self.can_hold:
            return

        if self.hold_piece is None:
            self.hold_piece = self.piece
            self.piece = self.next_piece
            self.next_piece = Piece()
        else:
            self.hold_piece, self.piece = self.piece, self.hold_piece
            self.piece.x = COLUMNS // 2 - 1
            self.piece.y = 0

        self.can_hold = False

    def update(self):
        self.drop_time += clock.get_time()
        speed = max(100, 500 - (self.level-1)*40)

        if self.drop_time > speed:
            self.piece.y += 1
            if self.check_collision():
                self.piece.y -= 1
                self.merge()
                self.clear_lines()

                self.piece = self.next_piece
                self.next_piece = Piece()
                self.can_hold = True

                if self.check_collision():
                    self.running = False

            self.drop_time = 0

    def handle_input(self, event):
        if event.key == pygame.K_LEFT:
            if not self.check_collision(dx=-1):
                self.piece.x -= 1
        elif event.key == pygame.K_RIGHT:
            if not self.check_collision(dx=1):
                self.piece.x += 1
        elif event.key == pygame.K_DOWN:
            if not self.check_collision(dy=1):
                self.piece.y += 1
        elif event.key == pygame.K_UP:
            rotated = self.piece.rotate()
            if not self.check_collision(shape=rotated):
                self.piece.shape = rotated
        elif event.key == pygame.K_SPACE:
            self.piece.y = self.get_ghost_y()
        elif event.key == pygame.K_c:
            self.hold()

    def draw(self):
        screen.fill(BLACK)

        for y in range(ROWS):
            for x in range(COLUMNS):
                if self.grid[y][x]:
                    pygame.draw.rect(screen, self.colors[y][x],
                                     (x*GRID_SIZE, y*GRID_SIZE, GRID_SIZE, GRID_SIZE))

        ghost_y = self.get_ghost_y()
        for y, row in enumerate(self.piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        screen, GRAY,
                        ((self.piece.x+x)*GRID_SIZE,
                         (ghost_y+y)*GRID_SIZE,
                         GRID_SIZE, GRID_SIZE), 1)

        for y, row in enumerate(self.piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, self.piece.color,
                                     ((self.piece.x+x)*GRID_SIZE,
                                      (self.piece.y+y)*GRID_SIZE,
                                      GRID_SIZE, GRID_SIZE))

        pygame.draw.rect(screen, (30,30,30), (PLAY_WIDTH, 0, WIDTH-PLAY_WIDTH, HEIGHT))

        def draw_piece_preview(piece, px, py):
            for y, row in enumerate(piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(screen, piece.color,
                                         (px + x*GRID_SIZE, py + y*GRID_SIZE,
                                          GRID_SIZE, GRID_SIZE))

        screen.blit(font.render("NEXT", True, WHITE), (310, 20))
        draw_piece_preview(self.next_piece, 310, 50)

        screen.blit(font.render("HOLD", True, WHITE), (310, 150))
        if self.hold_piece:
            draw_piece_preview(self.hold_piece, 310, 180)

        screen.blit(font.render(f"Score: {self.score}", True, WHITE), (310, 300))
        screen.blit(font.render(f"Level: {self.level}", True, WHITE), (310, 330))
        screen.blit(font.render(f"High: {self.highscore}", True, WHITE), (310, 360))

        pygame.display.flip()


def main():
    game = Game()

    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            elif event.type == pygame.KEYDOWN:
                game.handle_input(event)

        game.update()
        game.draw()
        clock.tick(30)

    game.save_highscore()

    screen.fill(BLACK)
    text = font.render("GAME OVER", True, (255,0,0))
    screen.blit(text, (WIDTH//2 - 60, HEIGHT//2))
    pygame.display.flip()
    pygame.time.wait(2000)

    pygame.quit()


if __name__ == "__main__":
    main()