import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 60)

# Spielzustände
RUNNING = "running"
PAUSED = "paused"
GAME_OVER = "game over"
state = RUNNING

def draw_pause_menu():
    text = font.render("Pause - P für weiter", True, (255,255,255))
    rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, rect)

def draw_game_over():
    text = font.render("Game Over", True, (255,0,0))
    rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 40))
    screen.blit(text, rect)
    restart = font.render("R für Neustart", True, (255,255,255))
    rect2 = restart.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
    screen.blit(restart, rect2)

def reset_game():
    # Hier Pacman/Level zurücksetzen
    pass

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if state == RUNNING:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                state = PAUSED
            if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
                state = GAME_OVER  # Zum Testen: Game Over mit G

        elif state == PAUSED:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                state = RUNNING

        elif state == GAME_OVER:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                state = RUNNING
                reset_game()

    screen.fill((0,0,0))

    if state == RUNNING:
        # Hier Pacman, Punkte, Gegner usw. zeichnen
        text = font.render("Spiel läuft... P=Pause, G=GameOver", True, (255,255,255))
        rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(text, rect)
    elif state == PAUSED:
        draw_pause_menu()
    elif state == GAME_OVER:
        draw_game_over()

    pygame.display.flip()
    clock.tick(60)