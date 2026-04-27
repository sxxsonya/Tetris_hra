import pygame
import os
from settings import *
from piece import Piece
from ai_helper import AIHelper

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 18)
        self.font_large = pygame.font.SysFont("Arial", 36, bold=True)
        
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
        self.game_over = False

        self.highscore = self.load_highscore()
        self.ai = AIHelper()
        self.ai_hint_active = True # Přepínač pro zobrazení AI nápovědy

    def load_highscore(self):
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as f:
                return int(f.read())
        return 0

    def save_highscore(self):
        with open("highscore.txt", "w") as f:
            f.write(str(max(self.score, self.highscore)))

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

    def get_ghost_y(self, piece_obj=None):
        target = piece_obj if piece_obj else self.piece
        ghost_y = target.y
        while not self.check_collision(dy=(ghost_y - target.y) + 1, shape=target.shape):
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
            else:
                new_grid.append(self.grid[y])
                new_colors.append(self.colors[y])

        while len(new_grid) < ROWS:
            new_grid.insert(0, [0]*COLUMNS)
            new_colors.insert(0, [None]*COLUMNS)

        self.grid = new_grid
        self.colors = new_colors

        self.lines += cleared
        # Bodování se zvyšuje s levelem
        if cleared > 0:
            points = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += points.get(cleared, 800) * self.level

        if self.score > self.highscore:
            self.highscore = self.score

        # Zvýšení levelu každých 10 řad
        self.level = (self.lines // 10) + 1

    def hold(self):
        if not self.can_hold: return
        if self.hold_piece is None:
            self.hold_piece = self.piece
            self.piece = self.next_piece
            self.next_piece = Piece()
        else:
            self.hold_piece, self.piece = self.piece, self.hold_piece
            self.piece.x = COLUMNS // 2 - len(self.piece.shape[0]) // 2
            self.piece.y = 0
        self.can_hold = False

    def update(self, dt):
        if self.game_over: return
        
        self.drop_time += dt
        speed = max(50, 500 - (self.level - 1) * 50)

        if self.drop_time > speed:
            self.piece.y += 1
            if self.check_collision():
                self.piece.y -= 1
                self.merge()
                self.clear_lines()
                self.piece = self.next_piece
                self.next_piece = Piece()
                self.can_hold = True
                
                # Zkontrolujeme prohru ihned po spawnu
                if self.check_collision():
                    self.game_over = True
                    self.save_highscore()
            self.drop_time = 0

    def handle_input(self, event):
        if self.game_over:
            if event.key == pygame.K_RETURN:
                self.running = False # Návrat do menu
            return

        if event.key == pygame.K_LEFT and not self.check_collision(dx=-1):
            self.piece.x -= 1
        elif event.key == pygame.K_RIGHT and not self.check_collision(dx=1):
            self.piece.x += 1
        elif event.key == pygame.K_DOWN and not self.check_collision(dy=1):
            self.piece.y += 1
            self.score += 1 # Bod za soft drop
        elif event.key == pygame.K_UP:
            rotated = self.piece.rotate()
            if not self.check_collision(shape=rotated):
                self.piece.shape = rotated
        elif event.key == pygame.K_SPACE:
            self.piece.y = self.get_ghost_y()
            self.score += 2 # Body za hard drop
            self.drop_time = 1000 # Okamžitý merge v dalším updatu
        elif event.key == pygame.K_c:
            self.hold()
        elif event.key == pygame.K_h:
            self.ai_hint_active = not self.ai_hint_active # Zapnutí/vypnutí AI

    def draw(self):
        self.screen.fill(BLACK)
        
        # Pozadí levelu
        bg_color = LEVEL_THEMES.get((self.level % 5) or 5, (10, 10, 20))
        pygame.draw.rect(self.screen, bg_color, (0, 0, PLAY_WIDTH, HEIGHT))

        # Vykreslení mřížky padlých kostek
        for y in range(ROWS):
            for x in range(COLUMNS):
                if self.grid[y][x]:
                    pygame.draw.rect(self.screen, self.colors[y][x], 
                                     (x*GRID_SIZE, y*GRID_SIZE, GRID_SIZE-1, GRID_SIZE-1))

        # Vykreslení Ghost Piece (uživatel)
        ghost_y = self.get_ghost_y()
        for y, row in enumerate(self.piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, GRAY, 
                                     ((self.piece.x+x)*GRID_SIZE, (ghost_y+y)*GRID_SIZE, GRID_SIZE-1, GRID_SIZE-1), 1)

        # AI NÁPOVĚDA (Vykreslí se světle zeleně na ideálním místě)
        if self.ai_hint_active:
            ai_x, ai_shape = self.ai.get_best_move(self.grid, self.piece)
            ai_mock_piece = Piece(ai_shape, GREEN)
            ai_mock_piece.x = ai_x
            ai_mock_piece.y = self.piece.y
            ai_ghost_y = self.get_ghost_y(ai_mock_piece)
            
            for y, row in enumerate(ai_shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, (0, 255, 0), 
                                         ((ai_x+x)*GRID_SIZE, (ai_ghost_y+y)*GRID_SIZE, GRID_SIZE-1, GRID_SIZE-1), 2)

        # Vykreslení aktuální kostky
        for y, row in enumerate(self.piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.piece.color,
                                     ((self.piece.x+x)*GRID_SIZE, (self.piece.y+y)*GRID_SIZE, GRID_SIZE-1, GRID_SIZE-1))

        # UI panel
        pygame.draw.rect(self.screen, (30, 30, 30), (PLAY_WIDTH, 0, WIDTH-PLAY_WIDTH, HEIGHT))
        
        def draw_preview(piece, px, py):
            if not piece: return
            for y, row in enumerate(piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, piece.color,
                                         (px + x*GRID_SIZE, py + y*GRID_SIZE, GRID_SIZE-1, GRID_SIZE-1))

        self.screen.blit(self.font.render("NEXT", True, WHITE), (310, 20))
        draw_preview(self.next_piece, 310, 50)

        self.screen.blit(self.font.render("HOLD", True, WHITE), (310, 150))
        draw_preview(self.hold_piece, 310, 180)

        self.screen.blit(self.font.render(f"Score: {self.score}", True, WHITE), (310, 300))
        self.screen.blit(self.font.render(f"Level: {self.level}", True, WHITE), (310, 330))
        self.screen.blit(self.font.render(f"Lines: {self.lines}", True, WHITE), (310, 360))
        self.screen.blit(self.font.render(f"High: {self.highscore}", True, (255, 215, 0)), (310, 390))
        
        # Instrukce
        self.screen.blit(self.font.render("[H] AI Hint", True, GREEN if self.ai_hint_active else GRAY), (310, 500))
        self.screen.blit(self.font.render("[C] Hold", True, GRAY), (310, 530))

        if self.game_over:
            s = pygame.Surface((WIDTH, HEIGHT))
            s.set_alpha(150)
            s.fill(BLACK)
            self.screen.blit(s, (0,0))
            go_text = self.font_large.render("GAME OVER", True, RED)
            ret_text = self.font.render("Press ENTER for Menu", True, WHITE)
            self.screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 30))
            self.screen.blit(ret_text, (WIDTH//2 - ret_text.get_width()//2, HEIGHT//2 + 20))