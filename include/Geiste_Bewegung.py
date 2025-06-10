import pygame
import random

# Pygame initialisieren
pygame.init()

# Fenstergröße und Spielfeld
WIDTH, HEIGHT = 600, 600
TILE_SIZE = 30
ROWS, COLS = HEIGHT // TILE_SIZE, WIDTH // TILE_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WakaWakaWaka Geiste Bewegungen")

# Farben
BLACK = (0, 0, 0)
WALL_COLOR = (50, 50, 255)
WHITE = (255, 255, 255)
GHOST_COLORS = [(255, 0, 0), (255, 128, 0), (255, 0, 255), (0, 255, 255)]

# Einfaches Labyrinth (1 = Wand, 0 = Weg)
maze = [
    [0]*20,
    [1]+[0]*18+[1],
    [1]+[0]*18+[1],
    [1]+[0]*18+[1],
    [1]*20,
]
while len(maze) < ROWS:
    maze.append([1] + [0]*18 + [1])
maze[-1] = [1]*20

# Prüft, ob ein Feld begehbar ist
def is_valid(x, y):
    col, row = int(x // TILE_SIZE), int(y // TILE_SIZE)
    if 0 <= col < COLS and 0 <= row < ROWS:
        return maze[row][col] == 0
    return False

# Klasse für einen Geist
class Ghost:
    def __init__(self, color, x, y):
        self.color = color
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.speed = 1  # langsame, flüssige Bewegung
        self.dir = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        self.change_dir_counter = random.randint(30, 100)  # sorgt für zufällige Bewegungen

    def draw(self):
        px = int(self.x)
        py = int(self.y)

        # Körper zeichnen
        pygame.draw.circle(screen, self.color, (px + TILE_SIZE//2, py + TILE_SIZE//2), TILE_SIZE//2)

        # Untere "Füße" (Wellenform)
        foot_radius = TILE_SIZE // 6
        for i in range(3):
            cx = px + foot_radius + i * 2 * foot_radius
            cy = py + TILE_SIZE - foot_radius
            pygame.draw.circle(screen, self.color, (cx, cy), foot_radius)

        # Augen
        eye_offset_x = TILE_SIZE // 5
        eye_offset_y = TILE_SIZE // 4
        eye_radius = TILE_SIZE // 6
        pygame.draw.circle(screen, WHITE, (px + eye_offset_x, py + eye_offset_y), eye_radius)
        pygame.draw.circle(screen, WHITE, (px + TILE_SIZE - eye_offset_x, py + eye_offset_y), eye_radius)

    def move(self):
        self.change_dir_counter -= 1

        # Neue Position berechnen
        nx = self.x + self.dir[0] * self.speed
        ny = self.y + self.dir[1] * self.speed

        # Prüfen, ob die nächste Kachel begehbar ist
        next_tile_x = int((nx + TILE_SIZE // 2) // TILE_SIZE)
        next_tile_y = int((ny + TILE_SIZE // 2) // TILE_SIZE)

        if is_valid(nx, ny):
            self.x = nx
            self.y = ny
        else:
            self.choose_new_dir()

        # Zufälliger Richtungswechsel nach Ablauf des Zählers
        if self.change_dir_counter <= 0:
            self.choose_new_dir()
            self.change_dir_counter = random.randint(60, 120)

    def choose_new_dir(self):
        dirs = [(1,0), (-1,0), (0,1), (0,-1)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx = self.x + dx * TILE_SIZE
            ny = self.y + dy * TILE_SIZE
            if is_valid(nx, ny):
                self.dir = (dx, dy)
                return

# Geister erstellen (mit unterschiedlichen Startpositionen)
ghosts = [
    Ghost(GHOST_COLORS[i], 10 + i, 10 + i) for i in range(4)
]

# Hauptspielschleife
clock = pygame.time.Clock()
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    # Geister bewegen und zeichnen
    for ghost in ghosts:
        ghost.move()
        ghost.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
