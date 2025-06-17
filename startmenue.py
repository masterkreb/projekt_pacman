import pygame
import sys

# --- Globale Variablen & Konstanten ---
WIDTH, HEIGHT = 640, 480
MAX_LIVES = 3

# Spielzustände
RUNNING = "running"
PAUSED = "paused"
GAME_OVER = "game over"
START_MENU = "start"

# --- Initialisierung ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 60)

# --- Spielstatus ---
state = START_MENU
lives = MAX_LIVES

# --- Zeichnen-Funktionen ---
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

def draw_lives():
    lives_text = font.render(f"Leben: {lives}", True, (255,255,0))
    rect = lives_text.get_rect(topleft=(10, 10))
    screen.blit(lives_text, rect)

def draw_start_menu():
    title = font.render("Pacman", True, (255,255,0))
    rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 60))
    screen.blit(title, rect)
    info = font.render("Drücke SPACE zum Starten", True, (255,255,255))
    rect2 = info.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
    screen.blit(info, rect2)

def draw_game_screen():
    # Hier Pacman, Punkte, Gegner usw. zeichnen
    text = font.render("Spiel läuft... P=Pause, L=Leben verlieren", True, (255,255,255))
    rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, rect)
    draw_lives()

def draw():
    screen.fill((0,0,0))
    if state == START_MENU:
        draw_start_menu()
    elif state == RUNNING:
        draw_game_screen()
    elif state == PAUSED:
        draw_pause_menu()
        draw_lives()
    elif state == GAME_OVER:
        draw_game_over()
    pygame.display.flip()

# --- Reset-Funktion ---
def reset_game():
    global lives, state
    lives = MAX_LIVES
    state = RUNNING
    # Hier alles für den Neustart deines Spiels zurücksetzen

# --- Eventhandling ---
def handle_events():
    global state, lives
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if state == START_MENU:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                state = RUNNING
                lives = MAX_LIVES

        elif state == RUNNING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    state = PAUSED
                # Dummy: Drücke L um Leben zu verlieren (simuliere Pacman-Tod)
                if event.key == pygame.K_l:
                    lives -= 1
                    if lives <= 0:
                        state = GAME_OVER

        elif state == PAUSED:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                state = RUNNING

        elif state == GAME_OVER:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game()

# --- Hauptschleife ---
def main():
    global state
    while True:
        handle_events()
        draw()
        clock.tick(60)

if __name__ == "__main__":
    main()