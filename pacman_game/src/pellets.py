"""
Pellets and Power Pellets
Handles pellet placement, collection, and scoring
"""

import pygame
import random
import math
from .constants import *

class Pellet:
    def __init__(self, x, y, is_power_pellet=False):
        self.x = x
        self.y = y
        self.grid_x = x
        self.grid_y = y
        self.is_power_pellet = is_power_pellet
        self.collected = False

        # Eigenschaften aus dem ursprünglichen Code
        # Power Pellets sind WEISS/ROSA (wie im Original), normale Pellets GELB
        self.color = (255, 184, 255) if is_power_pellet else YELLOW  # Rosa-weißlich für Power Pellet
        self.points = LARGE_PELLET_POINTS if is_power_pellet else SMALL_PELLET_POINTS
        self.radius = LARGE_PELLET_SIZE if is_power_pellet else SMALL_PELLET_SIZE
        self.visible = True

        # Animation für Power-Pellets
        self.flash_time = 0.2
        self.timer = 0
        self.animation_frame = 0
        self.animation_speed = 0.1

        # Normale Pellets sind immer gespawnt
        self.spawned = True

    def update(self, dt=1/60):
        """Update pellet animation"""
        # Animation für Power-Pellets
        if self.is_power_pellet and not self.collected:
            self.timer += dt
            if self.timer >= self.flash_time:
                self.visible = not self.visible
                self.timer = 0

            self.animation_frame += self.animation_speed
            if self.animation_frame >= 2:
                self.animation_frame = 0

    def draw(self, screen):
        """Draw the pellet - verbesserte Version aus dem ursprünglichen Code"""
        if not self.collected and self.visible and self.spawned:
            pixel_x = self.x * GRID_SIZE + GRID_SIZE // 2
            pixel_y = self.y * GRID_SIZE + GRID_SIZE // 2

            if self.is_power_pellet:
                # Animiertes Power-Pellet mit Glow-Effekt
                size = LARGE_PELLET_SIZE + int(self.animation_frame * 2)
                pygame.draw.circle(screen, self.color, (pixel_x, pixel_y), size)
                # Glow-Effekt
                pygame.draw.circle(screen, (255, 220, 255), (pixel_x, pixel_y), size + 2, 1)
            else:
                # Normales Pellet
                pygame.draw.circle(screen, self.color, (pixel_x, pixel_y), self.radius)

    def get_points(self):
        """Get points value for this pellet"""
        return self.points

    def respawn(self, new_position=None):
        """Respawn power pellet at new position"""
        if self.is_power_pellet and new_position:
            self.x, self.y = new_position
            self.grid_x, self.grid_y = new_position
            self.collected = False
            self.spawned = False
            self.spawn_timer = 0
            self.spawn_delay = 720  # 12 Sekunden nach dem Essen
            self.visible = True


class SpecialPellet:
    """Special pellet for speed boost"""
    def __init__(self, x, y, pellet_type='speed'):
        self.x = x
        self.y = y
        self.grid_x = x
        self.grid_y = y
        self.pellet_type = pellet_type
        self.collected = False
        self.spawned = True
        self.visible = True

        # Speed Pellet eigenschaften - CYAN/TÜRKIS wie ein Speed-Boost
        self.color = CYAN  # Türkis für Speed
        self.points = 25  # Weniger Punkte als Power Pellet
        self.radius = LARGE_PELLET_SIZE  # Gleiche Größe wie Power Pellet

        # Animation
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.pulse_effect = 0

    def update(self, dt=1/60):
        """Update special pellet animation"""
        if not self.collected:
            self.animation_frame += self.animation_speed
            if self.animation_frame >= 2:
                self.animation_frame = 0

            # Sanfter pulsierender Effekt
            self.pulse_effect = math.sin(self.animation_frame * math.pi) * 1.5

    def draw(self, screen):
        """Draw the special pellet as a circle with special effects"""
        if not self.collected and self.visible and self.spawned:
            pixel_x = self.x * GRID_SIZE + GRID_SIZE // 2
            pixel_y = self.y * GRID_SIZE + GRID_SIZE // 2

            # Zeichne türkisen Kreis mit Puls-Effekt
            size = self.radius + int(self.pulse_effect)

            # Innerer Glow für Speed-Effekt
            for i in range(3):
                glow_alpha = 60 - (i * 20)
                glow_color = (0, 255 - (i * 50), 255 - (i * 50))
                pygame.draw.circle(screen, glow_color, (pixel_x, pixel_y), size + (i * 3), 1)

            # Hauptkreis
            pygame.draw.circle(screen, self.color, (pixel_x, pixel_y), size)
            # Highlight
            pygame.draw.circle(screen, (150, 255, 255), (pixel_x - 2, pixel_y - 2), size // 3)

    def get_points(self):
        """Get points value for this pellet"""
        return self.points


class PelletManager:
    def __init__(self, maze):
        self.maze = maze
        self.pellets = []
        self.power_pellet_positions = []  # Mögliche Power Pellet Positionen
        self.active_power_pellets = []  # Liste aktiver Power Pellets (max 2)
        self.active_speed_pellet = None  # Nur EIN Speed Pellet
        self.power_pellet_timer = 0
        self.speed_pellet_timer = 0
        self.power_pellet_spawn_delay = 180  # 3 Sekunden initial
        self.speed_pellet_spawn_delay = 240  # 4 Sekunden initial
        self.reset()

    def reset(self):
        """Reset all pellets"""
        self.pellets = []
        self.power_pellet_timer = 0
        self.speed_pellet_timer = 0
        self.active_power_pellets = []
        self.active_speed_pellet = None

        # Definiere mögliche Power Pellet Positionen (alle Ecken)
        self.power_pellet_positions = [
            (1, 3),                              # Oben links
            (self.maze.width - 2, 3),           # Oben rechts
            (1, self.maze.height - 4),          # Unten links
            (self.maze.width - 2, self.maze.height - 4),  # Unten rechts
        ]

        self.create_pellets()

    def create_pellets(self):
        """Create pellets in all valid maze positions"""
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if not self.maze.is_wall(x, y):
                    # Skip ghost starting area (center area)
                    center_x, center_y = self.maze.get_center_position()
                    if (abs(x - center_x) <= 3 and abs(y - center_y) <= 3):
                        continue

                    # Don't place pellets too close to Pac-Man start
                    if x == 1 and y == 1:
                        continue

                    # Erstelle normale Pellets an allen Positionen
                    # Power Pellets werden separat gehandhabt
                    pellet = Pellet(x, y, False)
                    self.pellets.append(pellet)

    def update(self):
        """Update all pellets and spawn special pellets"""
        # Update normale Pellets
        for pellet in self.pellets:
            pellet.update()

        # Power Pellet spawn logic (max 2)
        if len(self.active_power_pellets) < 2:
            self.power_pellet_timer += 1
            if self.power_pellet_timer >= self.power_pellet_spawn_delay:
                self.spawn_power_pellet()

        # Update active power pellets
        for pellet in self.active_power_pellets[:]:  # Copy list to allow removal during iteration
            pellet.update()

        # Speed Pellet spawn logic (max 1)
        if self.active_speed_pellet is None:
            self.speed_pellet_timer += 1
            if self.speed_pellet_timer >= self.speed_pellet_spawn_delay:
                self.spawn_speed_pellet()
        else:
            self.active_speed_pellet.update()

    def spawn_power_pellet(self):
        """Spawn a power pellet at available position"""
        # Finde verfügbare Positionen (nicht von anderen Special Pellets besetzt)
        occupied_positions = []

        # Sammle besetzte Positionen
        for pellet in self.active_power_pellets:
            occupied_positions.append((pellet.x, pellet.y))
        if self.active_speed_pellet:
            occupied_positions.append((self.active_speed_pellet.x, self.active_speed_pellet.y))

        # Finde freie Positionen
        available_positions = [pos for pos in self.power_pellet_positions
                             if pos not in occupied_positions]

        if available_positions:
            # Wähle eine zufällige freie Position
            position = random.choice(available_positions)

            # Erstelle das Power Pellet
            power_pellet = Pellet(position[0], position[1], True)
            power_pellet.spawned = True
            power_pellet.visible = True
            power_pellet.color = (255, 184, 255)  # Rosa-weißlich wie im Original
            self.active_power_pellets.append(power_pellet)

            # Reset timer
            self.power_pellet_timer = 0
            # Nächstes Pellet nach 5-8 Sekunden
            self.power_pellet_spawn_delay = random.randint(300, 480)

    def spawn_speed_pellet(self):
        """Spawn a speed pellet at available position"""
        # Finde verfügbare Positionen
        occupied_positions = []

        for pellet in self.active_power_pellets:
            occupied_positions.append((pellet.x, pellet.y))

        available_positions = [pos for pos in self.power_pellet_positions
                             if pos not in occupied_positions]

        if available_positions:
            position = random.choice(available_positions)

            # Erstelle Speed Pellet als SpecialPellet
            self.active_speed_pellet = SpecialPellet(position[0], position[1], 'speed')

            # Reset timer
            self.speed_pellet_timer = 0
            # Nächstes nach 10-15 Sekunden
            self.speed_pellet_spawn_delay = random.randint(600, 900)

    def draw(self, screen):
        """Draw all pellets"""
        # Zeichne normale Pellets
        for pellet in self.pellets:
            pellet.draw(screen)

        # Zeichne aktive Power Pellets
        for pellet in self.active_power_pellets:
            if not pellet.collected:
                pellet.draw(screen)

        # Zeichne Speed Pellet
        if self.active_speed_pellet and not self.active_speed_pellet.collected:
            self.active_speed_pellet.draw(screen)

    def check_collection(self, pacman):
        """Check if Pac-Man collected any pellets"""
        total_points = 0
        power_pellet_eaten = False
        speed_pellet_eaten = False

        # Hole Pac-Mans aktuelle Grid-Position
        pacman_grid_x = pacman.grid_x
        pacman_grid_y = pacman.grid_y

        # Zusätzlich prüfen wir auch die umgebenden Grid-Positionen
        # für bessere Kollisionserkennung während der Bewegung
        positions_to_check = [
            (pacman_grid_x, pacman_grid_y),
            # Prüfe auch basierend auf Pac-Mans exakter Pixel-Position
            (int(pacman.x // GRID_SIZE), int(pacman.y // GRID_SIZE)),
            # Prüfe Mittelpunkt von Pac-Man
            (int((pacman.x + pacman.size/2) // GRID_SIZE), int((pacman.y + pacman.size/2) // GRID_SIZE))
        ]

        # Prüfe normale Pellets
        for pellet in self.pellets:
            if not pellet.collected and pellet.spawned:
                for check_x, check_y in positions_to_check:
                    if (pellet.grid_x == check_x and pellet.grid_y == check_y):
                        pellet.collected = True
                        total_points += pellet.get_points()
                        break  # Aus der inner loop ausbrechen

        # Prüfe Power Pellets
        for pellet in self.active_power_pellets[:]:  # Copy list for safe removal
            if not pellet.collected:
                for check_x, check_y in positions_to_check:
                    if (pellet.grid_x == check_x and pellet.grid_y == check_y):
                        pellet.collected = True
                        total_points += pellet.get_points()
                        power_pellet_eaten = True
                        # Entferne gegessenes Power Pellet
                        self.active_power_pellets.remove(pellet)
                        # Reset timer für nächstes
                        self.power_pellet_timer = 0
                        self.power_pellet_spawn_delay = random.randint(360, 600)  # 6-10 Sekunden
                        break

        # Prüfe Speed Pellet
        if self.active_speed_pellet and not self.active_speed_pellet.collected:
            for check_x, check_y in positions_to_check:
                if (self.active_speed_pellet.grid_x == check_x and
                    self.active_speed_pellet.grid_y == check_y):
                    self.active_speed_pellet.collected = True
                    total_points += self.active_speed_pellet.get_points()
                    speed_pellet_eaten = True
                    # Reset für nächstes Speed Pellet
                    self.active_speed_pellet = None
                    self.speed_pellet_timer = 0
                    self.speed_pellet_spawn_delay = random.randint(720, 900)  # 12-15 Sekunden
                    break

        # Rückgabe mit verschiedenen Signalen
        if speed_pellet_eaten:
            return -total_points - 1000  # Signal für Speed Pellet
        elif power_pellet_eaten:
            return -total_points  # Signal für Power Pellet
        return total_points

    def schedule_power_pellet_respawn(self, pellet):
        """Schedule power pellet to respawn at new location"""
        # Diese Methode wird nicht mehr benötigt, da wir nur ein Power Pellet haben
        pass

    def trigger_power_mode(self):
        """Called when a power pellet is collected"""
        # This is handled by the game class
        pass

    def all_collected(self):
        """Check if all pellets have been collected"""
        for pellet in self.pellets:
            if not pellet.collected and not pellet.is_power_pellet:
                return False
        # Prüfe auch ob noch nicht-gespawnte normale Pellets existieren
        for pellet in self.pellets:
            if not pellet.collected and not pellet.is_power_pellet and not pellet.spawned:
                return False
        return True

    def get_remaining_count(self):
        """Get count of remaining pellets (nur normale Pellets)"""
        count = 0
        for pellet in self.pellets:
            if not pellet.collected and not pellet.is_power_pellet:
                count += 1
        return count

    def get_pellet_at(self, x, y):
        """Get pellet at specific grid position"""
        for pellet in self.pellets:
            if pellet.grid_x == x and pellet.grid_y == y and not pellet.collected and pellet.spawned:
                return pellet
        return None

    def collect_pellet_at(self, x, y):
        """Manually collect pellet at position"""
        pellet = self.get_pellet_at(x, y)
        if pellet:
            pellet.collected = True
            return pellet.get_points()
        return 0