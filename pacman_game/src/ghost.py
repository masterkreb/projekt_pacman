"""
Ghost Classes
Handles ghost AI, movement, and behavior patterns
"""

import pygame
import random
import math
from .constants import *

class Ghost:
    def __init__(self, start_x, start_y, color, name):
        self.start_x = start_x
        self.start_y = start_y
        self.x = start_x * GRID_SIZE
        self.y = start_y * GRID_SIZE
        self.grid_x = start_x
        self.grid_y = start_y
        
        self.color = color
        self.name = name
        self.direction = UP  # Geister starten nach oben schauend
        self.next_direction = None
        self.speed = GHOST_SPEED
        self.size = GHOST_SIZE

        # AI behavior
        self.mode = SCATTER
        self.previous_mode = SCATTER
        self.mode_timer = 0
        self.scatter_timer = 0
        self.target_x = 0
        self.target_y = 0

        # Ghost state
        self.in_house = True  # Startet im Geisterhaus
        self.house_exit_timer = 0  # Timer für das Verlassen des Hauses
        self.dots_eaten_counter = 0  # Zählt gefressene Punkte für Release-Timing

        # Position tracking für smooth movement
        self.pixel_x = float(self.x)
        self.pixel_y = float(self.y)

        # Release delays (in dots eaten) - nicht mehr verwendet, nur Timer
        self.dots_eaten_counter = 0

        # Setze initiale Positionen basierend auf Geist
        if name == "blinky":
            self.in_house = False
            self.start_y = start_y - 3  # Über dem Geisterhaus
            self.y = self.start_y * GRID_SIZE
            self.pixel_y = float(self.y)
            self.grid_y = self.start_y
        elif name == "pinky":
            # Pinky startet in der Mitte des Geisterhauses
            self.start_x = start_x
            self.start_y = start_y
        elif name == "inky":
            # Inky startet links im Geisterhaus
            self.start_x = start_x - 2
            self.x = self.start_x * GRID_SIZE
            self.pixel_x = float(self.x)
            self.grid_x = self.start_x
        elif name == "clyde":
            # Clyde startet rechts im Geisterhaus
            self.start_x = start_x + 2
            self.x = self.start_x * GRID_SIZE
            self.pixel_x = float(self.x)
            self.grid_x = self.start_x

        # Animation
        self.animation_frame = 0
        self.animation_speed = 0.1

        # Movement restrictions
        self.can_reverse = False  # Verhindert 180° Wendungen außer bei Mode-Wechsel

    def update(self, maze, pacman, all_ghosts=None):
        """Update ghost position and AI"""
        # Update mode timer
        self.mode_timer += 1

        # Ghost house release logic
        if self.in_house:
            self.handle_house_exit(pacman)
            if self.in_house:  # Immer noch im Haus
                self.move_in_house()
                return

        # Mode-Wechsel-Timing (basierend auf original Pac-Man Level 1)
        if self.mode != FRIGHTENED and self.mode != EATEN:
            if self.mode == SCATTER and self.mode_timer > 420:  # 7 Sekunden bei 60 FPS
                self.switch_mode(CHASE)
            elif self.mode == CHASE and self.mode_timer > 1200:  # 20 Sekunden
                self.switch_mode(SCATTER)
                self.scatter_timer += 1
                # Nach 4 Scatter-Phasen bleibt es permanent in CHASE
                if self.scatter_timer >= 4:
                    self.mode = CHASE
                    self.mode_timer = 999999  # Bleibt für immer in CHASE

        # Frightened mode endet nach Zeit
        if self.mode == FRIGHTENED and self.mode_timer > 480:  # 8 Sekunden
            # Zurück zum vorherigen Modus
            self.switch_mode(self.previous_mode)

        # Eaten ghosts kehren zum Geisterhaus zurück
        if self.mode == EATEN:
            # Prüfe ob wir am Geisterhaus angekommen sind
            center_x = MAZE_WIDTH // 2
            center_y = MAZE_HEIGHT // 2
            if abs(self.grid_x - center_x) <= 1 and abs(self.grid_y - center_y) <= 2:
                # Ghost ist am Eingang angekommen - wiedergeboren
                self.mode = self.previous_mode if self.previous_mode != FRIGHTENED else SCATTER
                self.in_house = True
                self.grid_x = center_x
                self.grid_y = center_y
                self.x = self.grid_x * GRID_SIZE
                self.y = self.grid_y * GRID_SIZE
                self.pixel_x = float(self.x)
                self.pixel_y = float(self.y)
                self.house_exit_timer = 120  # 2 Sekunden warten bevor wieder raus

        # Set target based on mode and ghost personality
        self.set_target(pacman, maze, all_ghosts)

        # Move ghost
        self.move(maze)

        # Update animation
        self.animation_frame += self.animation_speed
        if self.animation_frame >= 2:
            self.animation_frame = 0

    def handle_house_exit(self, pacman):
        """Handle when ghost should leave the house"""
        # Für diesen einfachen Ansatz: Timer-basiert
        self.house_exit_timer += 1

        exit_timers = {
            "blinky": 0,     # Sofort (ist schon draußen)
            "pinky": 60,     # 1 Sekunde
            "inky": 180,     # 3 Sekunden
            "clyde": 300     # 5 Sekunden
        }

        if self.house_exit_timer >= exit_timers.get(self.name, 0):
            self.exit_house()

    def exit_house(self):
        """Ghost exits the house"""
        self.in_house = False
        # Setze Position auf den Bereich über dem Geisterhaus
        self.grid_x = MAZE_WIDTH // 2
        self.grid_y = MAZE_HEIGHT // 2 - 3  # 3 Tiles über dem Zentrum
        self.x = self.grid_x * GRID_SIZE
        self.y = self.grid_y * GRID_SIZE
        self.pixel_x = float(self.x)
        self.pixel_y = float(self.y)
        self.direction = LEFT  # Geister gehen normalerweise nach links beim Verlassen
        self.can_reverse = False

    def move_in_house(self):
        """Simple up/down movement while in house"""
        # Bewegung zum Ausgang (nach oben)
        center_x = MAZE_WIDTH // 2
        center_y = MAZE_HEIGHT // 2

        # Bewege den Geist langsam zur Mitte und dann nach oben
        if abs(self.grid_x - center_x) > 0:
            # Bewege zur Mitte horizontal
            if self.grid_x < center_x:
                self.pixel_x += 0.5
            else:
                self.pixel_x -= 0.5
            self.x = int(self.pixel_x)
            self.grid_x = self.x // GRID_SIZE
        else:
            # Bewege nach oben zum Ausgang
            self.pixel_y -= 0.5
            self.y = int(self.pixel_y)
            self.grid_y = self.y // GRID_SIZE

            # Prüfe ob wir am Ausgang sind
            if self.grid_y <= center_y - 3:
                self.exit_house()

    def switch_mode(self, new_mode):
        """Switch ghost mode and force direction reversal"""
        self.previous_mode = self.mode
        self.mode = new_mode
        self.mode_timer = 0

        # Bei Mode-Wechsel dürfen Geister die Richtung umkehren
        if not self.in_house:
            self.can_reverse = True
            # Richtungsumkehr
            self.direction = (-self.direction[0], -self.direction[1])

    def set_target(self, pacman, maze, all_ghosts=None):
        """Set target position based on ghost behavior"""
        pacman_x, pacman_y = pacman.grid_x, pacman.grid_y

        if self.mode == SCATTER:
            # Each ghost has a fixed corner in scatter mode
            corners = {
                "blinky": (MAZE_WIDTH - 2, 0),              # Top-right
                "pinky": (2, 0),                            # Top-left
                "inky": (MAZE_WIDTH - 1, MAZE_HEIGHT - 1),  # Bottom-right
                "clyde": (0, MAZE_HEIGHT - 1)               # Bottom-left
            }
            self.target_x, self.target_y = corners.get(self.name, (0, 0))

        elif self.mode == CHASE:
            # Each ghost has different targeting behavior
            if self.name == "blinky":
                # Red ghost - targets Pac-Man directly
                self.target_x, self.target_y = pacman_x, pacman_y

            elif self.name == "pinky":
                # Pink ghost - targets 4 tiles ahead of Pac-Man
                direction_offsets = {
                    'up': (0, -4),
                    'down': (0, 4),
                    'left': (-4, 0),
                    'right': (4, 0),
                    None: (0, 0)
                }
                offset = direction_offsets.get(pacman.current_direction, (0, 0))

                # Berühmter Pinky "Bug" - bei UP geht sie 4 hoch und 4 links
                if pacman.current_direction == 'up':
                    offset = (-4, -4)

                self.target_x = pacman_x + offset[0]
                self.target_y = pacman_y + offset[1]

            elif self.name == "inky":
                # Cyan ghost - komplexestes Verhalten
                # 1. Finde Punkt 2 Tiles vor Pac-Man
                direction_offsets = {
                    'up': (0, -2),
                    'down': (0, 2),
                    'left': (-2, 0),
                    'right': (2, 0),
                    None: (0, 0)
                }
                offset = direction_offsets.get(pacman.current_direction, (0, 0))

                # Inky "Bug" - bei UP geht er 2 hoch und 2 links
                if pacman.current_direction == 'up':
                    offset = (-2, -2)

                pivot_x = pacman_x + offset[0]
                pivot_y = pacman_y + offset[1]

                # 2. Finde Blinky's Position
                blinky_x, blinky_y = self.find_blinky_position(all_ghosts)

                # 3. Verdopple den Vektor von Blinky zum Pivot-Punkt
                self.target_x = pivot_x + (pivot_x - blinky_x)
                self.target_y = pivot_y + (pivot_y - blinky_y)

            elif self.name == "clyde":
                # Orange ghost - schüchtern
                distance = math.sqrt((self.grid_x - pacman_x)**2 +
                                   (self.grid_y - pacman_y)**2)

                if distance > 8:
                    # Weit weg: Verhalte dich wie Blinky
                    self.target_x, self.target_y = pacman_x, pacman_y
                else:
                    # Zu nah: Gehe zur Scatter-Ecke
                    self.target_x, self.target_y = (0, MAZE_HEIGHT - 1)

        elif self.mode == FRIGHTENED:
            # Random movement when frightened
            self.target_x = random.randint(0, MAZE_WIDTH - 1)
            self.target_y = random.randint(0, MAZE_HEIGHT - 1)

        elif self.mode == EATEN:
            # Return to ghost house
            self.target_x = MAZE_WIDTH // 2
            self.target_y = MAZE_HEIGHT // 2

    def find_blinky_position(self, all_ghosts):
        """Find Blinky's position for Inky's targeting"""
        if all_ghosts:
            for ghost in all_ghosts:
                if ghost.name == "blinky":
                    return (ghost.grid_x, ghost.grid_y)

        # Fallback: Blinky's Scatter-Position
        return (MAZE_WIDTH - 2, 0)

    def move(self, maze):
        """Move the ghost using the classic Pac-Man movement rules"""
        # Für EATEN mode - schnellere Bewegung zum Geisterhaus
        if self.mode == EATEN:
            speed = self.speed * 2
        else:
            speed = self.speed

        # Nur an Kreuzungen kann die Richtung geändert werden
        if self.at_intersection():
            self.choose_direction_at_intersection(maze)
            self.can_reverse = False  # Reset nach möglicher Umkehr

        # Bewege den Geist in die aktuelle Richtung
        if self.direction != STOP:
            self.pixel_x += self.direction[0] * speed
            self.pixel_y += self.direction[1] * speed

            # Update grid position
            self.x = int(self.pixel_x)
            self.y = int(self.pixel_y)
            self.grid_x = int((self.pixel_x + GRID_SIZE // 2) // GRID_SIZE)
            self.grid_y = int((self.pixel_y + GRID_SIZE // 2) // GRID_SIZE)

        # Handle tunnel wrapping
        if self.x < -GRID_SIZE:
            self.x = SCREEN_WIDTH
            self.pixel_x = float(self.x)
            self.grid_x = self.x // GRID_SIZE
        elif self.x > SCREEN_WIDTH:
            self.x = -GRID_SIZE
            self.pixel_x = float(self.x)
            self.grid_x = self.x // GRID_SIZE

    def at_intersection(self):
        """Check if ghost is at the center of a tile where it can change direction"""
        # Prüfe ob wir in der Mitte eines Tiles sind
        center_offset_x = abs(self.pixel_x - (self.grid_x * GRID_SIZE))
        center_offset_y = abs(self.pixel_y - (self.grid_y * GRID_SIZE))

        return center_offset_x < 2 and center_offset_y < 2

    def choose_direction_at_intersection(self, maze):
        """Choose direction at intersection using Pac-Man ghost AI rules"""
        possible_directions = []

        # Check all four directions
        for direction in [UP, DOWN, LEFT, RIGHT]:
            next_x = self.grid_x + direction[0]
            next_y = self.grid_y + direction[1]

            # Geister können normalerweise nicht umkehren (180°)
            reverse_direction = (-self.direction[0], -self.direction[1])
            if direction == reverse_direction and not self.can_reverse:
                continue

            # Check if the direction is valid (not a wall)
            if (0 <= next_x < MAZE_WIDTH and 0 <= next_y < MAZE_HEIGHT and
                not maze.is_wall(next_x, next_y)):
                possible_directions.append(direction)

        if not possible_directions:
            # Sackgasse - erlaube Umkehr
            reverse_direction = (-self.direction[0], -self.direction[1])
            possible_directions = [reverse_direction]

        if possible_directions:
            if self.mode == FRIGHTENED:
                # Zufällige Bewegung wenn verängstigt
                self.direction = random.choice(possible_directions)
            else:
                # Wähle Richtung die am nächsten zum Ziel führt
                best_direction = possible_directions[0]
                best_distance = float('inf')

                for direction in possible_directions:
                    next_x = self.grid_x + direction[0]
                    next_y = self.grid_y + direction[1]

                    # Berechne Distanz zum Ziel (Pac-Man's Entfernungsberechnung)
                    distance = math.sqrt((next_x - self.target_x)**2 +
                                       (next_y - self.target_y)**2)

                    # Bei Gleichstand: Priorität UP > LEFT > DOWN > RIGHT
                    if distance < best_distance:
                        best_distance = distance
                        best_direction = direction
                    elif distance == best_distance:
                        # Richtungspriorität
                        priority = {UP: 0, LEFT: 1, DOWN: 2, RIGHT: 3}
                        if priority.get(direction, 4) < priority.get(best_direction, 4):
                            best_direction = direction

                self.direction = best_direction

    def draw(self, screen):
        """Draw the ghost to the screen"""
        draw_x = self.x + GRID_SIZE // 2
        draw_y = self.y + GRID_SIZE // 2
        radius = self.size // 2

        # Choose color based on mode
        color = self.color
        if self.mode == FRIGHTENED:
            color = BLUE
            # Blinken wenn Frightened-Mode bald endet
            if self.mode_timer > 360:  # Letzte 2 Sekunden
                if int(self.animation_frame * 4) % 2 == 0:
                    color = WHITE
        elif self.mode == EATEN:
            # Nur Augen sichtbar
            color = None

        if color:  # Zeichne Körper nur wenn nicht "gegessen"
            # Draw ghost body (circle)
            pygame.draw.circle(screen, color, (int(draw_x), int(draw_y)), radius)

            # Draw ghost bottom (wavy)
            bottom_y = draw_y + radius
            wave_points = []
            for i in range(-radius, radius + 1, 4):
                wave_y = bottom_y + (3 if (i + int(self.animation_frame * 10)) % 8 < 4 else 0)
                wave_points.append((draw_x + i, wave_y))

            if len(wave_points) > 1:
                pygame.draw.polygon(screen, color,
                                  [(draw_x - radius, draw_y)] + wave_points + [(draw_x + radius, draw_y)])

        # Draw eyes (always visible)
        eye_color = WHITE
        pupil_color = BLACK

        # Pupillen schauen in Bewegungsrichtung
        pupil_offset_x = self.direction[0] * 2
        pupil_offset_y = self.direction[1] * 2

        # Left eye
        pygame.draw.circle(screen, eye_color, (int(draw_x - 6), int(draw_y - 4)), 3)
        pygame.draw.circle(screen, pupil_color,
                         (int(draw_x - 6 + pupil_offset_x), int(draw_y - 4 + pupil_offset_y)), 1)

        # Right eye
        pygame.draw.circle(screen, eye_color, (int(draw_x + 6), int(draw_y - 4)), 3)
        pygame.draw.circle(screen, pupil_color,
                         (int(draw_x + 6 + pupil_offset_x), int(draw_y - 4 + pupil_offset_y)), 1)

    def get_position(self):
        """Get current grid position"""
        return (self.grid_x, self.grid_y)

    def get_center(self):
        """Get center pixel coordinates"""
        return (self.x + self.size // 2, self.y + self.size // 2)

    def reset(self, start_x, start_y):
        """Reset ghost to starting position"""
        # Blinky startet außerhalb
        if self.name == "blinky":
            self.in_house = False
            self.start_y = start_y - 3
            self.x = start_x * GRID_SIZE
            self.y = self.start_y * GRID_SIZE
        elif self.name == "pinky":
            self.in_house = True
            self.x = start_x * GRID_SIZE
            self.y = start_y * GRID_SIZE
        elif self.name == "inky":
            self.in_house = True
            self.x = (start_x - 2) * GRID_SIZE
            self.y = start_y * GRID_SIZE
        elif self.name == "clyde":
            self.in_house = True
            self.x = (start_x + 2) * GRID_SIZE
            self.y = start_y * GRID_SIZE

        self.pixel_x = float(self.x)
        self.pixel_y = float(self.y)
        self.grid_x = int(self.x // GRID_SIZE)
        self.grid_y = int(self.y // GRID_SIZE)
        self.direction = LEFT if self.name == "blinky" else UP
        self.mode = SCATTER
        self.previous_mode = SCATTER
        self.mode_timer = 0
        self.scatter_timer = 0
        self.house_exit_timer = 0
        self.animation_frame = 0
        self.can_reverse = False

    def set_frightened(self):
        """Set ghost to frightened mode"""
        if self.mode != EATEN and not self.in_house:  # Gegessene Geister und Geister im Haus werden nicht verängstigt
            self.previous_mode = self.mode if self.mode != FRIGHTENED else self.previous_mode
            self.switch_mode(FRIGHTENED)
            self.mode_timer = 0