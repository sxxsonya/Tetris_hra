import pygame
from settings import WIDTH, HEIGHT, WHITE, GRAY, RED

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_options = pygame.font.SysFont("Arial", 28)
        self.options = ["Start Game", "Quit"]
        self.selected_index = 0

    def draw(self):
        self.screen.fill((15, 15, 15))
        title = self.font_title.render("AI TETRIS", True, WHITE)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))

        for i, option in enumerate(self.options):
            color = RED if i == self.selected_index else GRAY
            text = self.font_options.render(option, True, color)
            self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + i * 50))
        
        info = pygame.font.SysFont("Arial", 16).render("Press ENTER to select", True, GRAY)
        self.screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT - 50))

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected_index]
        return None