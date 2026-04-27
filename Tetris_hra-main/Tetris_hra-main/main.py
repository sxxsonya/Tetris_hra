import pygame
from settings import WIDTH, HEIGHT
from menu import MainMenu
from game import Game

def main():
    pygame.init()
    pygame.display.set_caption("AI Tetris OOP")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    menu = MainMenu(screen)
    state = "MENU" # Možné stavy: "MENU", "GAME"
    game = None

    running = True
    while running:
        dt = clock.tick(60) # Pevných 60 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if state == "MENU":
                action = menu.handle_input(event)
                if action == "Start Game":
                    game = Game(screen)
                    state = "GAME"
                elif action == "Quit":
                    running = False
            
            elif state == "GAME":
                if event.type == pygame.KEYDOWN:
                    game.handle_input(event)

        # Vykreslování a update podle aktuálního stavu
        if state == "MENU":
            menu.draw()
        elif state == "GAME":
            game.update(dt)
            game.draw()
            if not game.running: # Hráč odešel do menu po game over
                state = "MENU"

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()