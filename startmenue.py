import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.SysFont(None, 60)
clock = pygame.time.Clock()

START_MENU = True

def draw_start_menu():
    text = font.render("Pacman", True, (255, 255, 0))
    rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 60))
    screen.blit(text, rect)
    text2 = font.render("Drücke SPACE zum Starten", True, (255,255,255))
    rect2 = text2.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
    screen.blit(text2, rect2)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if START_MENU and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            START_MENU = False  # Spiel beginnt

    screen.fill((0,0,0))

    if START_MENU:
        draw_start_menu()
    else:
        # Hier beginnt dein eigentliches Spiel!
        text = font.render("Spiel läuft...", True, (0,255,0))
        rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(text, rect)

    pygame.display.flip()
    clock.tick(60)