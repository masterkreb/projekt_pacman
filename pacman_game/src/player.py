"""
Pacman Player Class
Handles Pac-Man character movement, animation, and behavior
"""

import pygame
import math
from .constants import *
from .nodes import find_nearest_node, find_node_by_grid

class Pacman:
    def __init__(self, start_x, start_y):
        self.start_x = start_x
        self.start_y = start_y
        
        # Pixel-Position - angepasst auf die übergebenen Startkoordinaten
        self.x = start_x * GRID_SIZE
        self.y = start_y * GRID_SIZE

        # Grid-Position
        self.grid_x = self.x // GRID_SIZE
        self.grid_y = self.y // GRID_SIZE
        
        # Node-basierte Bewegung (analog zum ursprünglichen Code)
        self.pos = None  # Aktueller Node
        self.target = None  # Ziel-Node
        self.all_nodes = []

        # Bewegungssystem aus dem ursprünglichen Code
        self.current_direction = None
        self.next_direction = None
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = PACMAN_SPEED  # 3 wie im Original
        self.size = PACMAN_SIZE   # 20 wie im Original
        
        # Animation
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.mouth_open = True

        # Bewegungstasten wie im Original
        self.move_keys = {
            'up': [pygame.K_w, pygame.K_UP],
            'down': [pygame.K_s, pygame.K_DOWN],
            'left': [pygame.K_a, pygame.K_LEFT],
            'right': [pygame.K_d, pygame.K_RIGHT]
        }

        # Status flags
        self.is_moving = False
        self.is_eating = False  # NEU: Flag für das Essen von Pellets

        # Sprite laden
        try:
            self.sprite_sheet = pygame.image.load(
                'assets/images/maze/Teil_017_Pacman_Tileset.png'
            ).convert_alpha()
            # Frame-Größe automatisch bestimmen (4 Frames horizontal, 4 Zeilen für Richtungen)
            sheet_width, sheet_height = self.sprite_sheet.get_size()
            self.frame_count = 4
            self.direction_count = 4
            self.frame_width = sheet_width // self.frame_count
            self.frame_height = sheet_height // self.direction_count
            self.sprite_loaded = True
        except (pygame.error, FileNotFoundError) as e:
            print(f"Konnte Pacman-Sprite nicht laden: {e}")
            self.sprite_sheet = None
            self.sprite_loaded = False

    def get_pressed_direction(self, keys):
        """Checkt welche Richtungstaste gedrückt wird - aus dem Original"""
        for direction, key_list in self.move_keys.items():
            for key in key_list:
                if keys[key]:
                    return direction
        return None

    def set_velocity_from_direction(self, direction):
        """Setzt die Geschwindigkeit basierend auf Richtung - originales Pacman Movement"""
        if direction == 'up':
            self.velocity_x, self.velocity_y = 0, -self.speed
            self.current_direction = 'up'
        elif direction == 'down':
            self.velocity_x, self.velocity_y = 0, self.speed
            self.current_direction = 'down'
        elif direction == 'left':
            self.velocity_x, self.velocity_y = -self.speed, 0
            self.current_direction = 'left'
        elif direction == 'right':
            self.velocity_x, self.velocity_y = self.speed, 0
            self.current_direction = 'right'

    def set_direction(self, direction):
        """Set the next direction for Pac-Man - kompatibel mit neuem System"""
        if direction == UP:
            self.next_direction = 'up'
        elif direction == DOWN:
            self.next_direction = 'down'
        elif direction == LEFT:
            self.next_direction = 'left'
        elif direction == RIGHT:
            self.next_direction = 'right'
        elif direction == STOP:
            self.next_direction = None

    def update(self, maze):
        """Update Pac-Man's position and state - Strikt Node-basierte Bewegung"""
        # Grid-Position aktualisieren
        self.grid_x = int(self.x // GRID_SIZE)
        self.grid_y = int(self.y // GRID_SIZE)

        # Aktuellen Node ermitteln, falls noch nicht gesetzt
        if self.pos is None and maze.node_map:
            self.pos = find_nearest_node(maze.node_map, self.grid_x, self.grid_y)
            if self.pos:
                # Setze Pacman genau auf die Position des Nodes
                self.x = self.pos.grid_x * GRID_SIZE
                self.y = self.pos.grid_y * GRID_SIZE
                self.grid_x = self.pos.grid_x
                self.grid_y = self.pos.grid_y

        # Wenn wir einen Zielpunkt haben und ihn erreicht haben
        if self.target and self.reached_target():
            # Wir sind am Ziel angekommen
            self.pos = self.target
            self.target = None

            # Setze die Position exakt auf den Node
            self.x = self.pos.grid_x * GRID_SIZE
            self.y = self.pos.grid_y * GRID_SIZE
            self.grid_x = self.pos.grid_x
            self.grid_y = self.pos.grid_y

            # Stoppe die Bewegung
            self.velocity_x = 0
            self.velocity_y = 0

            # Tunnel-Check
            tunnel_exit = None
            if self.current_direction == 'left':
                tunnel_exit = maze.get_tunnel_exit(self.grid_x, self.grid_y, -1, 0)
            elif self.current_direction == 'right':
                tunnel_exit = maze.get_tunnel_exit(self.grid_x, self.grid_y, 1, 0)

            if tunnel_exit:
                # Teleportiere Pacman zum Tunnelausgang
                tx, ty = tunnel_exit
                self.x = tx * GRID_SIZE
                self.y = ty * GRID_SIZE
                self.grid_x = tx
                self.grid_y = ty
                self.pos = find_node_by_grid(maze.node_map, tx, ty)

        # Wenn wir an einem Node sind aber kein Ziel haben
        if self.pos and not self.target:
            # Versuche, in die gewünschte Richtung zu gehen
            if self.next_direction:
                next_node = self.pos.get_neighbor_in_direction(self.next_direction)
                if next_node:
                    self.target = next_node
                    self.set_velocity_from_direction(self.next_direction)
                    self.current_direction = self.next_direction
                else:
                    # Wenn nicht möglich, versuche in aktueller Richtung weiterzugehen
                    if self.current_direction:
                        next_node = self.pos.get_neighbor_in_direction(self.current_direction)
                        if next_node:
                            self.target = next_node
                            self.set_velocity_from_direction(self.current_direction)
            # Wenn keine neue Richtung gesetzt, versuche in aktueller weiterzugehen
            elif self.current_direction:
                next_node = self.pos.get_neighbor_in_direction(self.current_direction)
                if next_node:
                    self.target = next_node
                    self.set_velocity_from_direction(self.current_direction)

        # Wenn wir ein Ziel haben, bewege uns in diese Richtung
        if self.target:
            self.x += self.velocity_x
            self.y += self.velocity_y
            self.is_moving = True
        else:
            self.velocity_x = 0
            self.velocity_y = 0
            self.is_moving = False

        # Animation aktualisieren
        self.update_animation()

    def reached_target(self):
        """Prüft, ob der Ziel-Node erreicht wurde"""
        if not self.target:
            return False

        # Berechne die Distanz zum Ziel
        target_x = self.target.px
        target_y = self.target.py

        # Berechne den Mittelpunkt von Pacman
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2

        # Prüfe, ob wir nahe genug am Ziel sind (5 Pixel Toleranz)
        distance = math.sqrt((center_x - target_x) ** 2 + (center_y - target_y) ** 2)
        return distance < 5

    def update_animation(self):
        """Aktualisiert den Animationsframe"""
        if self.is_moving:
            self.animation_frame += self.animation_speed
            if self.animation_frame >= 4:  # 4 Frames in der Animation
                self.animation_frame = 0

            # Mund öffnen/schließen Animation (Frame 0 und 2 = offen)
            frame_int = int(self.animation_frame)
            self.mouth_open = (frame_int == 0 or frame_int == 2)

    def set_eating(self, eating):
        """Setzt den Eating-Status für Waka-Waka Sound"""
        self.is_eating = eating

    def draw(self, screen):
        """Zeichnet Pacman"""
        # Berechne den Mittelpunkt
        center_x = int(self.x + self.size / 2)
        center_y = int(self.y + self.size / 2)

        # Zeichne Pac-Man immer gelb (kein Flimmern)
        if self.mouth_open and self.is_moving:
            # Mund offen - Pac-Man Form
            # Winkel basierend auf Richtung
            if self.current_direction == 'right':
                start_angle = 45
                end_angle = 315
            elif self.current_direction == 'left':
                start_angle = 225
                end_angle = 135
            elif self.current_direction == 'up':
                start_angle = 315
                end_angle = 225
            elif self.current_direction == 'down':
                start_angle = 135
                end_angle = 45
            else:
                # Fallback wenn keine Richtung
                start_angle = 45
                end_angle = 315

            # Zeichne Pac-Man als Kreissegment
            # Erstelle Punkte für den Pac-Man
            points = [(center_x, center_y)]

            # Berechne die Punkte entlang des Kreisbogens
            # Gehe in die richtige Richtung (im oder gegen Uhrzeigersinn)
            if start_angle > end_angle:
                # Über 0 Grad hinweg
                for angle in range(start_angle, 360, 5):
                    rad = math.radians(angle)
                    x = center_x + int(self.size/2 * math.cos(rad))
                    y = center_y + int(self.size/2 * math.sin(rad))
                    points.append((x, y))
                for angle in range(0, end_angle + 1, 5):
                    rad = math.radians(angle)
                    x = center_x + int(self.size/2 * math.cos(rad))
                    y = center_y + int(self.size/2 * math.sin(rad))
                    points.append((x, y))
            else:
                # Normaler Bogen
                for angle in range(start_angle, end_angle + 1, 5):
                    rad = math.radians(angle)
                    x = center_x + int(self.size/2 * math.cos(rad))
                    y = center_y + int(self.size/2 * math.sin(rad))
                    points.append((x, y))

            # Schließe die Form
            points.append((center_x, center_y))

            if len(points) > 2:
                pygame.draw.polygon(screen, YELLOW, points)
                # Zeichne Umriss für bessere Sichtbarkeit
                pygame.draw.polygon(screen, YELLOW, points, 2)
        else:
            # Mund geschlossen - voller Kreis
            pygame.draw.circle(screen, YELLOW, (center_x, center_y), int(self.size / 2))
            pygame.draw.circle(screen, YELLOW, (center_x, center_y), int(self.size / 2), 2)

    def reset(self, start_x=None, start_y=None):
        """Setzt Pacman auf die Startposition zurück"""
        # Aktualisiere die Startposition, wenn neue Werte übergeben werden
        if start_x is not None:
            self.start_x = start_x
        if start_y is not None:
            self.start_y = start_y

        self.x = self.start_x * GRID_SIZE
        self.y = self.start_y * GRID_SIZE
        self.grid_x = self.x // GRID_SIZE
        self.grid_y = self.y // GRID_SIZE
        self.velocity_x = 0
        self.velocity_y = 0
        self.current_direction = None
        self.next_direction = None
        self.pos = None
        self.target = None
        self.is_moving = False
        self.is_eating = False
        self.animation_frame = 0
        self.mouth_open = True

    def initialize_nodes(self, nodes):
        """Setzt die Node-Liste und initialisiert Pacman auf dem nächsten Node"""
        self.all_nodes = nodes
        self.pos = find_nearest_node(nodes, self.grid_x, self.grid_y)
        # Setze Pacman genau auf die Position des Nodes für sauberen Start
        if self.pos:
            self.x = self.pos.grid_x * GRID_SIZE
            self.y = self.pos.grid_y * GRID_SIZE

    def get_position(self):
        """Gibt die aktuelle Grid-Position von Pacman zurück"""
        return (self.grid_x, self.grid_y)

    def get_pixel_position(self):
        """Gibt die aktuelle Pixel-Position (Mittelpunkt) von Pacman zurück"""
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        return (center_x, center_y)

    def collides_with(self, other):
        """Prüft, ob Pacman mit einem anderen Spielobjekt kollidiert"""
        # Berechne den Mittelpunkt von Pacman
        pacman_x, pacman_y = self.get_pixel_position()

        # Hol die Position des anderen Objekts
        if hasattr(other, 'get_center'):
            other_x, other_y = other.get_center()
        else:
            # Fallback
            other_x = other.x + getattr(other, 'size', 16) / 2
            other_y = other.y + getattr(other, 'size', 16) / 2

        # Berechne die Distanz zwischen den Mittelpunkten
        distance = math.sqrt((pacman_x - other_x) ** 2 + (pacman_y - other_y) ** 2)

        # Prüfe, ob die Distanz kleiner ist als die Summe der Radien
        collision_distance = (self.size + getattr(other, 'size', 16)) / 2 * 0.8  # 80% für besseres Gameplay

        return distance < collision_distance