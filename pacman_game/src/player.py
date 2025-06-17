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

        # Bewegungstasten wie im Original
        self.move_keys = {
            'up': [pygame.K_w, pygame.K_UP],
            'down': [pygame.K_s, pygame.K_DOWN],
            'left': [pygame.K_a, pygame.K_LEFT],
            'right': [pygame.K_d, pygame.K_RIGHT]
        }

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

        # Sound-System aus dem ursprünglichen Code
        try:
            self.wakawaka_sound = pygame.mixer.Sound("assets/sounds/effects/wakawaka.wav")
            self.wakawaka_sound.set_volume(0.2)  # 20% Lautstärke
            self.wakawaka_channel = None
            self.sound_loaded = True
            print("WakaWaka sound loaded successfully at 20% volume!")
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load wakawaka.wav: {e}")
            self.wakawaka_sound = None
            self.sound_loaded = False

        self.sound_enabled = True
        self.is_moving = False
        self.last_moving_state = False

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

        # Sound-Steuerung
        if self.is_moving and not self.last_moving_state:
            self.play_wakawaka()
        elif not self.is_moving and self.last_moving_state:
            self.stop_wakawaka()

        self.last_moving_state = self.is_moving

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

    def move_towards_target(self):
        """Bewegt Pacman in Richtung des Ziel-Nodes"""
        if not self.target:
            return

        # Berechne den Mittelpunkt von Pacman
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2

        # Berechne die Richtung zum Ziel
        target_x = self.target.px
        target_y = self.target.py

        # Setze die Geschwindigkeit basierend auf der aktuellen Richtung
        # Wir verwenden die voreingestellte Geschwindigkeit, nicht die genaue Richtung
        # Dies verhindert diagonale Bewegungen
        if self.current_direction == 'up':
            self.velocity_x, self.velocity_y = 0, -self.speed
        elif self.current_direction == 'down':
            self.velocity_x, self.velocity_y = 0, self.speed
        elif self.current_direction == 'left':
            self.velocity_x, self.velocity_y = -self.speed, 0
        elif self.current_direction == 'right':
            self.velocity_x, self.velocity_y = self.speed, 0

        # Bewegung ausführen
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Aktualisiere die Grid-Position
        self.grid_x = int(self.x // GRID_SIZE)
        self.grid_y = int(self.y // GRID_SIZE)

    def update_animation(self):
        """Aktualisiert den Animationsframe"""
        if self.is_moving:
            self.animation_frame += self.animation_speed
            if self.animation_frame >= 4:  # 4 Frames in der Animation
                self.animation_frame = 0

    def play_wakawaka(self):
        """Spielt den Wakawaka-Sound"""
        if self.sound_loaded and self.sound_enabled:
            if not self.wakawaka_channel or not self.wakawaka_channel.get_busy():
                self.wakawaka_channel = pygame.mixer.find_channel(True)
                if self.wakawaka_channel:
                    self.wakawaka_channel.play(self.wakawaka_sound, loops=-1)  # Loop infinitely

    def stop_wakawaka(self):
        """Stoppt den Wakawaka-Sound"""
        if self.wakawaka_channel and self.wakawaka_channel.get_busy():
            self.wakawaka_channel.stop()

    def draw(self, screen):
        """Zeichnet Pacman als einfachen gelben Ball (temporär)"""
        # Berechne den Mittelpunkt
        center_x = int(self.x + self.size / 2)
        center_y = int(self.y + self.size / 2)

        # Zeichne den gelben Ball
        pygame.draw.circle(screen, YELLOW, (center_x, center_y), int(self.size / 2))

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
        self.stop_wakawaka()

    def initialize_nodes(self, nodes):
        """Setzt die Node-Liste und initialisiert Pacman auf dem nächsten Node"""
        self.all_nodes = nodes
        self.pos = find_nearest_node(nodes, self.grid_x, self.grid_y)
        # Setze Pacman genau auf die Position des Nodes für sauberen Start
        if self.pos:
            self.x = self.pos.grid_x * GRID_SIZE
            self.y = self.pos.grid_y * GRID_SIZE

    def get_position(self):
        """Gibt die aktuelle Position von Pacman zurück"""
        # Berechne den Mittelpunkt von Pacman für genauere Kollisionserkennung
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        return (center_x, center_y)

    def collides_with(self, other):
        """Prüft, ob Pacman mit einem anderen Spielobjekt kollidiert"""
        # Berechne den Mittelpunkt von Pacman
        pacman_x, pacman_y = self.get_position()

        # Prüfe, ob das andere Objekt eine get_position Methode hat
        if hasattr(other, 'get_position'):
            other_x, other_y = other.get_position()
        else:
            # Fallback, falls das andere Objekt keine get_position Methode hat
            # Wir gehen davon aus, dass es x, y und size Attribute hat
            other_x = other.x + other.size / 2
            other_y = other.y + other.size / 2

        # Berechne die Distanz zwischen den Mittelpunkten
        distance = math.sqrt((pacman_x - other_x) ** 2 + (pacman_y - other_y) ** 2)

        # Prüfe, ob die Distanz kleiner ist als die Summe der Radien
        # (Bei Pacman und Geistern verwenden wir size/2 als Radius)
        collision_distance = (self.size + getattr(other, 'size', self.size)) / 2

        return distance < collision_distance
