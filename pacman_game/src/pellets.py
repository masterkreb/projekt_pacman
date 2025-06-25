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

        # Properties
        self.color = (255, 184, 255) if is_power_pellet else YELLOW
        self.points = LARGE_PELLET_POINTS if is_power_pellet else SMALL_PELLET_POINTS
        self.radius = LARGE_PELLET_SIZE if is_power_pellet else SMALL_PELLET_SIZE
        self.visible = True

        # Animation
        self.flash_time = 0.2
        self.timer = 0
        self.animation_frame = 0
        self.animation_speed = 0.1

        self.spawned = True

        # Load power pellet image
        if is_power_pellet:
            try:
                self.image = pygame.image.load('assets/images/pacman/ghostcherry.png').convert_alpha()
                self.image = pygame.transform.scale(self.image, (32, 32))
                self.use_image = True
                print("Ghost cherry image loaded for power pellet")
            except (pygame.error, FileNotFoundError) as e:
                print(f"Could not load ghostcherry.png: {e}")
                self.use_image = False
        else:
            self.use_image = False

    def update(self, dt=1/60):
        """Update pellet animation"""
        if self.is_power_pellet and not self.collected:
            self.animation_frame += self.animation_speed
            if self.animation_frame >= 2:
                self.animation_frame = 0

    def draw(self, screen):
        """Draw the pellet"""
        if not self.collected and self.visible and self.spawned:
            pixel_x = self.x * GRID_SIZE + GRID_SIZE // 2
            pixel_y = self.y * GRID_SIZE + GRID_SIZE // 2

            if self.is_power_pellet:
                # Warning blink in last 5 seconds
                if hasattr(self, 'despawn_timer') and self.despawn_timer > 600:
                    if int(self.despawn_timer / 10) % 2 == 0:
                        return

                if hasattr(self, 'use_image') and self.use_image and hasattr(self, 'image'):
                    # Draw image with pulse effect
                    scale_factor = 1.0 + (math.sin(self.animation_frame * 2) * 0.1)
                    scaled_size = (int(32 * scale_factor), int(32 * scale_factor))
                    scaled_image = pygame.transform.scale(self.image, scaled_size)
                    scaled_rect = scaled_image.get_rect(center=(pixel_x, pixel_y))
                    screen.blit(scaled_image, scaled_rect)
                else:
                    # Fallback circle
                    size = LARGE_PELLET_SIZE + int(self.animation_frame * 2)
                    pygame.draw.circle(screen, self.color, (pixel_x, pixel_y), size)
                    pygame.draw.circle(screen, (255, 220, 255), (pixel_x, pixel_y), size + 2, 1)
            else:
                # Normal pellet
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
            self.spawn_delay = 720
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

        # Speed pellet properties
        self.color = CYAN
        self.points = 25
        self.radius = LARGE_PELLET_SIZE

        # Animation
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.pulse_effect = 0

        # Despawn timer
        self.despawn_timer = 0
        self.despawn_time = 900  # 15 seconds at 60 FPS

        # Load speed pellet image
        try:
            self.image = pygame.image.load('assets/images/pacman/speedberry.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (32, 32))
            self.use_image = True
            print("Speed berry image loaded for speed pellet")
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load speedberry.png: {e}")
            self.use_image = False

    def update(self, dt=1/60):
        """Update special pellet animation"""
        if not self.collected:
            self.animation_frame += self.animation_speed
            if self.animation_frame >= 2:
                self.animation_frame = 0

            self.pulse_effect = math.sin(self.animation_frame * math.pi) * 1.5

            self.despawn_timer += 1
            if self.despawn_timer >= self.despawn_time:
                return True  # Signal to despawn
        return False

    def draw(self, screen):
        """Draw the special pellet"""
        if not self.collected and self.visible and self.spawned:
            pixel_x = self.x * GRID_SIZE + GRID_SIZE // 2
            pixel_y = self.y * GRID_SIZE + GRID_SIZE // 2

            # Warning blink in last 5 seconds
            if self.despawn_timer > self.despawn_time - 300:
                if int(self.despawn_timer / 10) % 2 == 0:
                    return

            if hasattr(self, 'use_image') and self.use_image and hasattr(self, 'image'):
                # Draw image with pulse effect
                scale_factor = 1.0 + (self.pulse_effect * 0.1)
                scaled_size = (int(32 * scale_factor), int(32 * scale_factor))
                scaled_image = pygame.transform.scale(self.image, scaled_size)
                scaled_rect = scaled_image.get_rect(center=(pixel_x, pixel_y))

                # Draw glow effect
                for i in range(2):
                    glow_radius = 16 + (i * 4) + int(self.pulse_effect)
                    glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, (0, 150, 255, 30 - (i * 10)),
                                     (glow_radius, glow_radius), glow_radius)
                    screen.blit(glow_surface, (pixel_x - glow_radius, pixel_y - glow_radius))

                screen.blit(scaled_image, scaled_rect)
            else:
                # Fallback circle
                size = self.radius + int(self.pulse_effect)

                for i in range(3):
                    glow_alpha = 60 - (i * 20)
                    glow_color = (0, 255 - (i * 50), 255 - (i * 50))
                    pygame.draw.circle(screen, glow_color, (pixel_x, pixel_y), size + (i * 3), 1)

                pygame.draw.circle(screen, self.color, (pixel_x, pixel_y), size)
                pygame.draw.circle(screen, (150, 255, 255), (pixel_x - 2, pixel_y - 2), size // 3)

    def get_points(self):
        """Get points value for this pellet"""
        return self.points


class PelletManager:
    def __init__(self, maze):
        self.maze = maze
        self.pellets = []
        self.power_pellet_positions = []
        self.active_power_pellets = []
        self.active_speed_pellet = None
        self.power_pellet_timer = 0
        self.speed_pellet_timer = 0

        # HARDMODE: 50% spawn rate
        self.power_pellet_spawn_delay = 360  # 6 seconds initial
        self.speed_pellet_spawn_delay = 480  # 8 seconds initial

        self.reset()

    def reset(self):
        """Reset all pellets"""
        self.pellets = []
        self.power_pellet_timer = 0
        self.speed_pellet_timer = 0
        self.active_power_pellets = []
        self.active_speed_pellet = None

        # Power pellet spawn positions (corners)
        self.power_pellet_positions = [
            (1, 3),
            (self.maze.width - 2, 3),
            (1, self.maze.height - 4),
            (self.maze.width - 2, self.maze.height - 4),
        ]

        self.create_pellets()

    def create_pellets(self):
        """Create pellets in all valid maze positions"""
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if not self.maze.is_wall(x, y):
                    # Skip ghost house area
                    center_x, center_y = self.maze.get_center_position()
                    if (abs(x - center_x) <= 3 and abs(y - center_y) <= 3):
                        continue

                    # Skip Pac-Man start
                    if x == 1 and y == 1:
                        continue

                    pellet = Pellet(x, y, False)
                    self.pellets.append(pellet)

    def update(self):
        """Update all pellets and spawn special pellets"""
        # Update normal pellets
        for pellet in self.pellets:
            pellet.update()

        # Update and despawn power pellets
        for pellet in self.active_power_pellets[:]:
            pellet.update()

            if hasattr(pellet, 'despawn_timer'):
                pellet.despawn_timer += 1
                if pellet.despawn_timer >= 900:  # 15 seconds
                    self.active_power_pellets.remove(pellet)
                    print(f"Power pellet despawned at ({pellet.x}, {pellet.y})")

        # Power pellet spawn logic (max 2)
        if len(self.active_power_pellets) < 2:
            self.power_pellet_timer += 1
            if self.power_pellet_timer >= self.power_pellet_spawn_delay:
                self.spawn_power_pellet()

        # Speed pellet spawn logic
        if self.active_speed_pellet is None:
            self.speed_pellet_timer += 1
            if self.speed_pellet_timer >= self.speed_pellet_spawn_delay:
                self.spawn_speed_pellet()
        else:
            # Check for despawn
            should_despawn = self.active_speed_pellet.update()
            if should_despawn:
                print(f"Speed pellet despawned at ({self.active_speed_pellet.x}, {self.active_speed_pellet.y})")
                self.active_speed_pellet = None
                self.speed_pellet_timer = 0
                self.speed_pellet_spawn_delay = random.randint(1200, 1800)  # 20-30 seconds

    def spawn_power_pellet(self):
        """Spawn a power pellet at available position"""
        occupied_positions = []

        for pellet in self.active_power_pellets:
            occupied_positions.append((pellet.x, pellet.y))
        if self.active_speed_pellet:
            occupied_positions.append((self.active_speed_pellet.x, self.active_speed_pellet.y))

        available_positions = [pos for pos in self.power_pellet_positions
                             if pos not in occupied_positions]

        if available_positions:
            position = random.choice(available_positions)

            power_pellet = Pellet(position[0], position[1], True)
            power_pellet.spawned = True
            power_pellet.visible = True
            power_pellet.color = (255, 184, 255)
            power_pellet.despawn_timer = 0
            self.active_power_pellets.append(power_pellet)

            self.power_pellet_timer = 0
            self.power_pellet_spawn_delay = random.randint(600, 960)  # 10-16 seconds

    def spawn_speed_pellet(self):
        """Spawn a speed pellet at available position"""
        occupied_positions = []

        for pellet in self.active_power_pellets:
            occupied_positions.append((pellet.x, pellet.y))

        available_positions = [pos for pos in self.power_pellet_positions
                             if pos not in occupied_positions]

        if available_positions:
            position = random.choice(available_positions)

            self.active_speed_pellet = SpecialPellet(position[0], position[1], 'speed')

            self.speed_pellet_timer = 0
            self.speed_pellet_spawn_delay = random.randint(1200, 1800)  # 20-30 seconds

    def draw(self, screen):
        """Draw all pellets"""
        # Draw normal pellets
        for pellet in self.pellets:
            pellet.draw(screen)

        # Draw power pellets
        for pellet in self.active_power_pellets:
            if not pellet.collected:
                if hasattr(pellet, 'despawn_timer') and pellet.despawn_timer > 600:
                    if int(pellet.despawn_timer / 10) % 2 == 0:
                        continue
                pellet.draw(screen)

        # Draw speed pellet
        if self.active_speed_pellet and not self.active_speed_pellet.collected:
            self.active_speed_pellet.draw(screen)

    def check_collection(self, pacman):
        """Check if Pac-Man collected any pellets"""
        total_points = 0
        power_pellet_eaten = False
        speed_pellet_eaten = False

        pacman_grid_x = pacman.grid_x
        pacman_grid_y = pacman.grid_y

        # Check multiple positions for better collision detection
        positions_to_check = [
            (pacman_grid_x, pacman_grid_y),
            (int(pacman.x // GRID_SIZE), int(pacman.y // GRID_SIZE)),
            (int((pacman.x + pacman.size/2) // GRID_SIZE), int((pacman.y + pacman.size/2) // GRID_SIZE))
        ]

        # Check normal pellets
        for pellet in self.pellets:
            if not pellet.collected and pellet.spawned:
                for check_x, check_y in positions_to_check:
                    if (pellet.grid_x == check_x and pellet.grid_y == check_y):
                        pellet.collected = True
                        total_points += pellet.get_points()
                        break

        # Check power pellets
        for pellet in self.active_power_pellets[:]:
            if not pellet.collected:
                for check_x, check_y in positions_to_check:
                    if (pellet.grid_x == check_x and pellet.grid_y == check_y):
                        pellet.collected = True
                        total_points += pellet.get_points()
                        power_pellet_eaten = True
                        self.active_power_pellets.remove(pellet)
                        self.power_pellet_timer = 0
                        self.power_pellet_spawn_delay = random.randint(720, 1200)  # 12-20 seconds
                        break

        # Check speed pellet
        if self.active_speed_pellet and not self.active_speed_pellet.collected:
            for check_x, check_y in positions_to_check:
                if (self.active_speed_pellet.grid_x == check_x and
                    self.active_speed_pellet.grid_y == check_y):
                    self.active_speed_pellet.collected = True
                    total_points += self.active_speed_pellet.get_points()
                    speed_pellet_eaten = True
                    self.active_speed_pellet = None
                    self.speed_pellet_timer = 0
                    self.speed_pellet_spawn_delay = random.randint(1440, 1800)  # 24-30 seconds
                    break

        # Return with different signals
        if speed_pellet_eaten:
            return -total_points - 1000  # Signal for speed pellet
        elif power_pellet_eaten:
            return -total_points  # Signal for power pellet
        return total_points

    def all_collected(self):
        """Check if all pellets have been collected"""
        for pellet in self.pellets:
            if not pellet.collected and not pellet.is_power_pellet:
                return False
        return True

    def get_remaining_count(self):
        """Get count of remaining pellets"""
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