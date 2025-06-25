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
        
        # Position
        self.x = start_x * GRID_SIZE
        self.y = start_y * GRID_SIZE
        self.grid_x = self.x // GRID_SIZE
        self.grid_y = self.y // GRID_SIZE

        # Node-based movement
        self.pos = None
        self.target = None
        self.all_nodes = []

        # Movement
        self.current_direction = None
        self.next_direction = None
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = PACMAN_SPEED
        self.base_speed = PACMAN_SPEED
        self.size = PACMAN_SIZE

        # Speed Boost System
        self.speed_boost_active = False
        self.speed_boost_timer = 0
        self.speed_boost_duration = 180  # 3 seconds at 60 FPS

        # Progressive Speed Stack System
        self.speed_stacks = 0
        self.max_speed_stacks = 5
        self.speed_per_stack = 0.07  # 7% per stack
        self.stacked_speed_multiplier = 1.0

        # Animation
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.mouth_open = True

        # Movement keys
        self.move_keys = {
            'up': [pygame.K_w, pygame.K_UP],
            'down': [pygame.K_s, pygame.K_DOWN],
            'left': [pygame.K_a, pygame.K_LEFT],
            'right': [pygame.K_d, pygame.K_RIGHT]
        }

        # Status
        self.is_moving = False
        self.is_eating = False

        # Load sprite
        try:
            self.sprite_sheet = pygame.image.load(
                'assets/images/maze/Teil_017_Pacman_Tileset.png'
            ).convert_alpha()
            sheet_width, sheet_height = self.sprite_sheet.get_size()
            self.frame_count = 4
            self.direction_count = 4
            self.frame_width = sheet_width // self.frame_count
            self.frame_height = sheet_height // self.direction_count
            self.sprite_loaded = True
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load Pacman sprite: {e}")
            self.sprite_sheet = None
            self.sprite_loaded = False

    def get_pressed_direction(self, keys):
        """Check which direction key is pressed"""
        for direction, key_list in self.move_keys.items():
            for key in key_list:
                if keys[key]:
                    return direction
        return None

    def set_velocity_from_direction(self, direction):
        """Set velocity based on direction"""
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
        """Set the next direction for Pac-Man"""
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

    def add_speed_stack(self):
        """Add a speed stack (max 5 stacks = 35% speed)"""
        if self.speed_stacks < self.max_speed_stacks:
            self.speed_stacks += 1
            self.stacked_speed_multiplier = 1.0 + (self.speed_stacks * self.speed_per_stack)
            self.base_speed = PACMAN_SPEED * self.stacked_speed_multiplier
            if not self.speed_boost_active:
                self.speed = self.base_speed
            print(f"Pacman speed stack: {self.speed_stacks}/5 ({(self.stacked_speed_multiplier-1)*100:.0f}% bonus)")

    def activate_speed_boost(self):
        """Activate speed boost for 3 seconds"""
        self.speed_boost_active = True
        self.speed_boost_timer = self.speed_boost_duration
        self.speed = self.base_speed * 2.15  # 115% extra speed
        print("Speed boost activated!")

    def activate_power_speed_boost(self):
        """Activate 20% speed boost from power pellet"""
        if self.speed_boost_active:
            self.speed *= 1.2
        else:
            self.speed_boost_active = True
            self.speed_boost_timer = self.speed_boost_duration
            self.speed = self.base_speed * 1.2
        print("Power pellet speed boost!")

    def update(self, maze):
        """Update Pac-Man's position and state"""
        # Update speed boost
        if self.speed_boost_active:
            self.speed_boost_timer -= 1
            if self.speed_boost_timer <= 0:
                self.speed_boost_active = False
                self.speed = self.base_speed
                print("Speed boost ended")

        # Update grid position
        self.grid_x = int(self.x // GRID_SIZE)
        self.grid_y = int(self.y // GRID_SIZE)

        # Initialize node if needed
        if self.pos is None and maze.node_map:
            self.pos = find_nearest_node(maze.node_map, self.grid_x, self.grid_y)
            if self.pos:
                self.x = self.pos.grid_x * GRID_SIZE
                self.y = self.pos.grid_y * GRID_SIZE
                self.grid_x = self.pos.grid_x
                self.grid_y = self.pos.grid_y

        # Check if target reached
        if self.target and self.reached_target():
            self.pos = self.target
            self.target = None

            self.x = self.pos.grid_x * GRID_SIZE
            self.y = self.pos.grid_y * GRID_SIZE
            self.grid_x = self.pos.grid_x
            self.grid_y = self.pos.grid_y

            self.velocity_x = 0
            self.velocity_y = 0

            # Tunnel check
            tunnel_exit = None
            if self.current_direction == 'left':
                tunnel_exit = maze.get_tunnel_exit(self.grid_x, self.grid_y, -1, 0)
            elif self.current_direction == 'right':
                tunnel_exit = maze.get_tunnel_exit(self.grid_x, self.grid_y, 1, 0)

            if tunnel_exit:
                tx, ty = tunnel_exit
                self.x = tx * GRID_SIZE
                self.y = ty * GRID_SIZE
                self.grid_x = tx
                self.grid_y = ty
                self.pos = find_node_by_grid(maze.node_map, tx, ty)

        # Choose next direction
        if self.pos and not self.target:
            if self.next_direction:
                next_node = self.pos.get_neighbor_in_direction(self.next_direction)
                if next_node:
                    self.target = next_node
                    self.set_velocity_from_direction(self.next_direction)
                    self.current_direction = self.next_direction
                else:
                    if self.current_direction:
                        next_node = self.pos.get_neighbor_in_direction(self.current_direction)
                        if next_node:
                            self.target = next_node
                            self.set_velocity_from_direction(self.current_direction)
            elif self.current_direction:
                next_node = self.pos.get_neighbor_in_direction(self.current_direction)
                if next_node:
                    self.target = next_node
                    self.set_velocity_from_direction(self.current_direction)

        # Move if we have a target
        if self.target:
            self.x += self.velocity_x
            self.y += self.velocity_y
            self.is_moving = True
        else:
            self.velocity_x = 0
            self.velocity_y = 0
            self.is_moving = False

        # Update animation
        self.update_animation()

    def reached_target(self):
        """Check if target node is reached"""
        if not self.target:
            return False

        target_x = self.target.px
        target_y = self.target.py

        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2

        distance = math.sqrt((center_x - target_x) ** 2 + (center_y - target_y) ** 2)
        return distance < 5

    def update_animation(self):
        """Update animation frame"""
        if self.is_moving:
            self.animation_frame += self.animation_speed
            if self.animation_frame >= 4:
                self.animation_frame = 0

            frame_int = int(self.animation_frame)
            self.mouth_open = (frame_int == 0 or frame_int == 2)

    def set_eating(self, eating):
        """Set eating status"""
        self.is_eating = eating

    def draw(self, screen):
        """Draw Pacman"""
        center_x = int(self.x + self.size / 2)
        center_y = int(self.y + self.size / 2)

        color = CYAN if self.speed_boost_active else YELLOW

        if self.mouth_open and self.is_moving:
            # Draw Pac-Man shape
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
                start_angle = 45
                end_angle = 315

            points = [(center_x, center_y)]

            if start_angle > end_angle:
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
                for angle in range(start_angle, end_angle + 1, 5):
                    rad = math.radians(angle)
                    x = center_x + int(self.size/2 * math.cos(rad))
                    y = center_y + int(self.size/2 * math.sin(rad))
                    points.append((x, y))

            points.append((center_x, center_y))

            if len(points) > 2:
                pygame.draw.polygon(screen, color, points)
                pygame.draw.polygon(screen, color, points, 2)
        else:
            # Draw full circle
            pygame.draw.circle(screen, color, (center_x, center_y), int(self.size / 2))
            pygame.draw.circle(screen, color, (center_x, center_y), int(self.size / 2), 2)

        # Speed boost effect
        if self.speed_boost_active:
            pulse = int(math.sin(self.speed_boost_timer * 0.1) * 3)
            pygame.draw.circle(screen, (150, 255, 255), (center_x, center_y),
                             int(self.size / 2) + 5 + pulse, 1)

    def reset(self, start_x=None, start_y=None):
        """Reset Pacman to starting position"""
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
        self.speed_boost_active = False
        self.speed_boost_timer = 0
        # Speed stacks are NOT reset on death
        self.base_speed = PACMAN_SPEED * self.stacked_speed_multiplier
        self.speed = self.base_speed

    def full_reset(self, start_x=None, start_y=None):
        """Full reset including speed stacks (new game only)"""
        self.speed_stacks = 0
        self.stacked_speed_multiplier = 1.0
        self.base_speed = PACMAN_SPEED
        self.reset(start_x, start_y)

    def initialize_nodes(self, nodes):
        """Initialize node list and position"""
        self.all_nodes = nodes
        self.pos = find_nearest_node(nodes, self.grid_x, self.grid_y)
        if self.pos:
            self.x = self.pos.grid_x * GRID_SIZE
            self.y = self.pos.grid_y * GRID_SIZE

    def get_position(self):
        """Get current grid position"""
        return (self.grid_x, self.grid_y)

    def get_pixel_position(self):
        """Get current pixel position (center)"""
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        return (center_x, center_y)

    def collides_with(self, other):
        """Check collision with another object"""
        pacman_x, pacman_y = self.get_pixel_position()

        if hasattr(other, 'get_center'):
            other_x, other_y = other.get_center()
        else:
            other_x = other.x + getattr(other, 'size', 16) / 2
            other_y = other.y + getattr(other, 'size', 16) / 2

        distance = math.sqrt((pacman_x - other_x) ** 2 + (pacman_y - other_y) ** 2)
        collision_distance = (self.size + getattr(other, 'size', 16)) / 2 * 0.8

        return distance < collision_distance