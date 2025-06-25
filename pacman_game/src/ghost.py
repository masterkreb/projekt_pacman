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
        self.direction = UP
        self.next_direction = None
        self.speed = GHOST_SPEED * 1.25  # HARDMODE: 25% faster
        self.base_speed = GHOST_SPEED * 1.25
        self.size = GHOST_SIZE

        # AI behavior
        self.mode = SCATTER
        self.previous_mode = SCATTER
        self.mode_timer = 0
        self.scatter_timer = 0
        self.target_x = 0
        self.target_y = 0

        # Ghost state
        self.in_house = True
        self.house_exit_timer = 0
        self.house_exit_delay = 480  # 8 seconds at 60 FPS (doubled from 4)
        self.dots_eaten_counter = 0

        # Speed Buff System
        self.speed_buff_active = False
        self.speed_buff_timer = 0
        self.speed_buff_duration = 180  # 3 seconds at 60 FPS

        # Progressive Speed System
        self.progressive_speed_timer = 0
        self.progressive_speed_multiplier = 1.0
        self.speed_increase_interval = 480  # 8 seconds at 60 FPS
        self.max_speed_multiplier = 1.5  # Max 50% faster

        # Start debuff - 25% slower for first 5 seconds
        self.start_debuff_timer = 300  # 5 seconds at 60 FPS
        self.has_start_debuff = True

        # Position tracking
        self.pixel_x = float(self.x)
        self.pixel_y = float(self.y)

        # Set initial positions based on ghost type
        if name == "blinky":
            self.in_house = False
            self.start_y = start_y - 3
            self.y = self.start_y * GRID_SIZE
            self.pixel_y = float(self.y)
            self.grid_y = self.start_y
        elif name == "pinky":
            self.start_x = start_x
            self.start_y = start_y
        elif name == "inky":
            self.start_x = start_x - 2
            self.x = self.start_x * GRID_SIZE
            self.pixel_x = float(self.x)
            self.grid_x = self.start_x
        elif name == "clyde":
            self.start_x = start_x + 2
            self.x = self.start_x * GRID_SIZE
            self.pixel_x = float(self.x)
            self.grid_x = self.start_x

        # Animation
        self.animation_frame = 0
        self.animation_speed = 0.1

        # Movement
        self.can_reverse = False
        self.trigger_speed_buff_after = True

        # Movement stuck prevention
        self.last_grid_position = (self.grid_x, self.grid_y)
        self.stuck_timer = 0
        self.max_stuck_time = 60  # 1 second at 60 FPS

    def update(self, maze, pacman, all_ghosts=None):
        """Update ghost position and AI"""
        self.mode_timer += 1

        # Update start debuff timer
        if self.has_start_debuff and self.start_debuff_timer > 0:
            self.start_debuff_timer -= 1
            if self.start_debuff_timer <= 0:
                self.has_start_debuff = False
                print(f"{self.name} start debuff ended!")

        # Progressive speed increase
        if not self.in_house and not self.has_start_debuff:
            self.progressive_speed_timer += 1
            if self.progressive_speed_timer >= self.speed_increase_interval:
                if self.progressive_speed_multiplier < self.max_speed_multiplier:
                    self.progressive_speed_multiplier += 0.05
                    if not self.speed_buff_active:
                        self.update_current_speed()
                    print(f"{self.name} speed increased to {self.progressive_speed_multiplier:.0%}")
                self.progressive_speed_timer = 0

        # Update speed buff
        if self.speed_buff_active:
            self.speed_buff_timer -= 1
            if self.speed_buff_timer <= 0:
                self.speed_buff_active = False
                self.update_current_speed()
                print(f"{self.name} speed buff ended")

        # House exit logic
        if self.in_house:
            self.handle_house_exit(pacman)
            if self.in_house:
                self.move_in_house()
                return

        # Mode switching - Classic Pac-Man pattern
        if self.mode == FRIGHTENED:
            # Check for frightened timeout
            frightened_duration = 360  # 6 seconds default
            if hasattr(self, 'short_frightened') and self.short_frightened:
                frightened_duration = 120  # 2 seconds for speed pellet

            if self.mode_timer > frightened_duration:
                print(f"{self.name} exiting frightened mode after {self.mode_timer} ticks")
                if self.trigger_speed_buff_after:
                    self.activate_speed_buff()
                self.switch_mode(CHASE)  # Always go to CHASE after frightened
                if hasattr(self, 'short_frightened'):
                    self.short_frightened = False

        elif self.mode != EATEN:
            # Classic Pac-Man wave pattern
            wave_times = [
                (SCATTER, 420),  # 7 seconds scatter
                (CHASE, 1200),  # 20 seconds chase
                (SCATTER, 420),  # 7 seconds scatter
                (CHASE, 1200),  # 20 seconds chase
                (SCATTER, 300),  # 5 seconds scatter
                (CHASE, 1200),  # 20 seconds chase
                (SCATTER, 300),  # 5 seconds scatter
                (CHASE, -1)  # Chase forever
            ]

            # Only apply pattern if not permanently in chase mode
            if self.scatter_timer < 4:
                current_wave = self.scatter_timer * 2 + (0 if self.mode == SCATTER else 1)
                if current_wave < len(wave_times):
                    expected_mode, duration = wave_times[current_wave]
                    if self.mode != expected_mode:
                        self.switch_mode(expected_mode)
                    elif duration > 0 and self.mode_timer > duration:
                        # Time to switch to next phase
                        next_wave = current_wave + 1
                        if next_wave < len(wave_times):
                            next_mode = wave_times[next_wave][0]
                            self.switch_mode(next_mode)

        # Eaten ghosts return home
        if self.mode == EATEN:
            center_x = MAZE_WIDTH // 2
            center_y = MAZE_HEIGHT // 2
            if abs(self.grid_x - center_x) <= 1 and abs(self.grid_y - center_y) <= 2:
                self.mode = SCATTER  # Start with scatter after respawn
                self.in_house = True
                self.grid_x = center_x
                self.grid_y = center_y
                self.x = self.grid_x * GRID_SIZE
                self.y = self.grid_y * GRID_SIZE
                self.pixel_x = float(self.x)
                self.pixel_y = float(self.y)
                self.house_exit_timer = 0
                self.update_current_speed()

        # Update AI target
        self.set_target(pacman, maze, all_ghosts)

        # Move ghost
        self.move(maze)

        # Check if stuck
        current_position = (self.grid_x, self.grid_y)
        if current_position == self.last_grid_position:
            self.stuck_timer += 1
            if self.stuck_timer > self.max_stuck_time:
                print(f"{self.name} is stuck at {current_position}, forcing direction change")
                self.can_reverse = True
                self.direction = self.get_opposite_direction(self.direction)
                self.stuck_timer = 0
        else:
            self.stuck_timer = 0
            self.last_grid_position = current_position

        # Update animation
        self.animation_frame += self.animation_speed
        if self.animation_frame >= 2:
            self.animation_frame = 0

    def get_opposite_direction(self, direction):
        """Get the opposite direction"""
        opposites = {
            UP: DOWN,
            DOWN: UP,
            LEFT: RIGHT,
            RIGHT: LEFT,
            STOP: STOP
        }
        return opposites.get(direction, STOP)

    def update_current_speed(self):
        """Update the current speed based on all modifiers"""
        base = self.base_speed * self.progressive_speed_multiplier

        # Apply debuffs
        if self.has_start_debuff:
            base *= 0.75  # 25% slower at start

        # Apply buffs
        if self.speed_buff_active:
            base *= 1.5  # 50% faster after frightened

        self.speed = base

    def activate_speed_buff(self):
        """Activate speed buff after frightened mode"""
        self.speed_buff_active = True
        self.speed_buff_timer = self.speed_buff_duration
        self.update_current_speed()
        print(f"{self.name} activated speed buff!")

    def handle_house_exit(self, pacman):
        """Handle ghost leaving the house"""
        self.house_exit_timer += 1
        if self.house_exit_timer >= self.house_exit_delay:
            self.exit_house()

    def exit_house(self):
        """Ghost exits the house"""
        self.in_house = False
        self.grid_x = MAZE_WIDTH // 2
        self.grid_y = MAZE_HEIGHT // 2 - 3
        self.x = self.grid_x * GRID_SIZE
        self.y = self.grid_y * GRID_SIZE
        self.pixel_x = float(self.x)
        self.pixel_y = float(self.y)
        self.direction = LEFT
        self.can_reverse = False

    def move_in_house(self):
        """Movement while in house"""
        center_x = MAZE_WIDTH // 2
        center_y = MAZE_HEIGHT // 2

        if abs(self.grid_x - center_x) > 0:
            if self.grid_x < center_x:
                self.pixel_x += 0.5
            else:
                self.pixel_x -= 0.5
            self.x = int(self.pixel_x)
            self.grid_x = self.x // GRID_SIZE
        else:
            self.pixel_y -= 0.5
            self.y = int(self.pixel_y)
            self.grid_y = self.y // GRID_SIZE

            if self.grid_y <= center_y - 3:
                self.exit_house()

    def switch_mode(self, new_mode):
        """Switch ghost mode and force direction reversal"""
        print(f"{self.name} switching from {self.mode} to {new_mode}")
        self.previous_mode = self.mode
        self.mode = new_mode
        self.mode_timer = 0

        # Increment scatter timer when entering scatter mode
        if new_mode == SCATTER:
            self.scatter_timer += 1

        if not self.in_house and new_mode != EATEN:
            self.can_reverse = True
            # Only reverse direction for mode changes, not for EATEN
            if self.direction != STOP:
                self.direction = self.get_opposite_direction(self.direction)

    def set_target(self, pacman, maze, all_ghosts=None):
        """Set target position based on ghost behavior"""
        pacman_x, pacman_y = pacman.grid_x, pacman.grid_y

        if self.mode == SCATTER:
            corners = {
                "blinky": (MAZE_WIDTH - 2, 0),
                "pinky": (2, 0),
                "inky": (MAZE_WIDTH - 1, MAZE_HEIGHT - 1),
                "clyde": (0, MAZE_HEIGHT - 1)
            }
            self.target_x, self.target_y = corners.get(self.name, (0, 0))

        elif self.mode == CHASE:
            if self.name == "blinky":
                # Direct targeting
                self.target_x, self.target_y = pacman_x, pacman_y

            elif self.name == "pinky":
                # Target 4 tiles ahead
                direction_offsets = {
                    'up': (0, -4),
                    'down': (0, 4),
                    'left': (-4, 0),
                    'right': (4, 0),
                    None: (0, 0)
                }
                offset = direction_offsets.get(pacman.current_direction, (0, 0))
                if pacman.current_direction == 'up':
                    offset = (-4, -4)  # Classic Pinky bug

                self.target_x = pacman_x + offset[0]
                self.target_y = pacman_y + offset[1]

            elif self.name == "inky":
                # Complex targeting using Blinky
                direction_offsets = {
                    'up': (0, -2),
                    'down': (0, 2),
                    'left': (-2, 0),
                    'right': (2, 0),
                    None: (0, 0)
                }
                offset = direction_offsets.get(pacman.current_direction, (0, 0))
                if pacman.current_direction == 'up':
                    offset = (-2, -2)

                pivot_x = pacman_x + offset[0]
                pivot_y = pacman_y + offset[1]

                blinky_x, blinky_y = self.find_blinky_position(all_ghosts)

                self.target_x = pivot_x + (pivot_x - blinky_x)
                self.target_y = pivot_y + (pivot_y - blinky_y)

            elif self.name == "clyde":
                # Shy behavior
                distance = math.sqrt((self.grid_x - pacman_x) ** 2 +
                                     (self.grid_y - pacman_y) ** 2)

                if distance > 8:
                    self.target_x, self.target_y = pacman_x, pacman_y
                else:
                    self.target_x, self.target_y = (0, MAZE_HEIGHT - 1)

        elif self.mode == FRIGHTENED:
            # Random movement when frightened
            if self.mode_timer % 30 == 0:  # Change target every 0.5 seconds
                self.target_x = random.randint(0, MAZE_WIDTH - 1)
                self.target_y = random.randint(0, MAZE_HEIGHT - 1)

        elif self.mode == EATEN:
            self.target_x = MAZE_WIDTH // 2
            self.target_y = MAZE_HEIGHT // 2

    def find_blinky_position(self, all_ghosts):
        """Find Blinky's position for Inky's targeting"""
        if all_ghosts:
            for ghost in all_ghosts:
                if ghost.name == "blinky":
                    return (ghost.grid_x, ghost.grid_y)
        return (MAZE_WIDTH - 2, 0)

    def move(self, maze):
        """Move the ghost using classic Pac-Man movement rules"""
        # Set speed based on mode
        if self.mode == EATEN:
            speed = self.base_speed * 2
        elif self.mode == FRIGHTENED:
            speed = self.base_speed * 0.5  # Half speed when frightened
        else:
            speed = self.speed

        # Always try to choose direction at intersections
        if self.at_intersection() or self.direction == STOP:
            self.choose_direction_at_intersection(maze)
            self.can_reverse = False

        # Move in current direction
        if self.direction != STOP:
            self.pixel_x += self.direction[0] * speed
            self.pixel_y += self.direction[1] * speed

            self.x = int(self.pixel_x)
            self.y = int(self.pixel_y)
            self.grid_x = int((self.pixel_x + GRID_SIZE // 2) // GRID_SIZE)
            self.grid_y = int((self.pixel_y + GRID_SIZE // 2) // GRID_SIZE)

        # Tunnel wrapping
        if self.x < -GRID_SIZE:
            self.x = SCREEN_WIDTH
            self.pixel_x = float(self.x)
            self.grid_x = self.x // GRID_SIZE
        elif self.x > SCREEN_WIDTH:
            self.x = -GRID_SIZE
            self.pixel_x = float(self.x)
            self.grid_x = self.x // GRID_SIZE

    def at_intersection(self):
        """Check if ghost is at tile center"""
        center_offset_x = abs(self.pixel_x - (self.grid_x * GRID_SIZE))
        center_offset_y = abs(self.pixel_y - (self.grid_y * GRID_SIZE))
        return center_offset_x < 2 and center_offset_y < 2

    def choose_direction_at_intersection(self, maze):
        """Choose direction at intersection using Pac-Man AI rules"""
        possible_directions = []

        for direction in [UP, DOWN, LEFT, RIGHT]:
            next_x = self.grid_x + direction[0]
            next_y = self.grid_y + direction[1]

            # Skip reverse direction unless allowed
            reverse_direction = self.get_opposite_direction(self.direction)
            if direction == reverse_direction and not self.can_reverse:
                continue

            # Check if direction is valid
            if (0 <= next_x < MAZE_WIDTH and 0 <= next_y < MAZE_HEIGHT and
                    not maze.is_wall(next_x, next_y)):
                possible_directions.append(direction)

        # If no directions available, allow reverse
        if not possible_directions:
            reverse_direction = self.get_opposite_direction(self.direction)
            if reverse_direction != STOP:
                possible_directions = [reverse_direction]
            else:
                # Emergency: try all directions
                for direction in [UP, DOWN, LEFT, RIGHT]:
                    next_x = self.grid_x + direction[0]
                    next_y = self.grid_y + direction[1]
                    if (0 <= next_x < MAZE_WIDTH and 0 <= next_y < MAZE_HEIGHT and
                            not maze.is_wall(next_x, next_y)):
                        possible_directions.append(direction)

        if possible_directions:
            if self.mode == FRIGHTENED:
                # Random movement when frightened
                self.direction = random.choice(possible_directions)
            else:
                # Choose best direction based on target
                best_direction = possible_directions[0]
                best_distance = float('inf')

                for direction in possible_directions:
                    next_x = self.grid_x + direction[0]
                    next_y = self.grid_y + direction[1]

                    distance = math.sqrt((next_x - self.target_x) ** 2 +
                                         (next_y - self.target_y) ** 2)

                    if distance < best_distance:
                        best_distance = distance
                        best_direction = direction
                    elif distance == best_distance:
                        # Priority: UP > LEFT > DOWN > RIGHT
                        priority = {UP: 0, LEFT: 1, DOWN: 2, RIGHT: 3}
                        if priority.get(direction, 4) < priority.get(best_direction, 4):
                            best_direction = direction

                self.direction = best_direction

    def draw(self, screen):
        """Draw the ghost"""
        draw_x = self.x + GRID_SIZE // 2
        draw_y = self.y + GRID_SIZE // 2
        radius = self.size // 2

        color = self.color
        if self.mode == FRIGHTENED:
            color = BLUE
            # Flash white in last 1.5 seconds
            frightened_duration = 360
            if hasattr(self, 'short_frightened') and self.short_frightened:
                frightened_duration = 120

            if self.mode_timer > frightened_duration - 90:  # Last 1.5 seconds
                if int(self.animation_frame * 4) % 2 == 0:
                    color = WHITE
        elif self.mode == EATEN:
            color = None

        if color:
            # Body
            pygame.draw.circle(screen, color, (int(draw_x), int(draw_y)), radius)

            # Bottom wavy part
            bottom_y = draw_y + radius
            wave_points = []
            for i in range(-radius, radius + 1, 4):
                wave_y = bottom_y + (3 if (i + int(self.animation_frame * 10)) % 8 < 4 else 0)
                wave_points.append((draw_x + i, wave_y))

            if len(wave_points) > 1:
                pygame.draw.polygon(screen, color,
                                    [(draw_x - radius, draw_y)] + wave_points + [(draw_x + radius, draw_y)])

        # Eyes (always visible)
        eye_color = WHITE
        pupil_color = BLACK

        # Determine eye direction based on movement or target
        if self.direction != STOP:
            pupil_offset_x = self.direction[0] * 2
            pupil_offset_y = self.direction[1] * 2
        else:
            # Look towards target when stopped
            dx = self.target_x - self.grid_x
            dy = self.target_y - self.grid_y
            if dx != 0 or dy != 0:
                length = math.sqrt(dx * dx + dy * dy)
                pupil_offset_x = (dx / length) * 2
                pupil_offset_y = (dy / length) * 2
            else:
                pupil_offset_x = 0
                pupil_offset_y = 0

        # Left eye
        pygame.draw.circle(screen, eye_color, (int(draw_x - 6), int(draw_y - 4)), 3)
        pygame.draw.circle(screen, pupil_color,
                           (int(draw_x - 6 + pupil_offset_x), int(draw_y - 4 + pupil_offset_y)), 1)

        # Right eye
        pygame.draw.circle(screen, eye_color, (int(draw_x + 6), int(draw_y - 4)), 3)
        pygame.draw.circle(screen, pupil_color,
                           (int(draw_x + 6 + pupil_offset_x), int(draw_y - 4 + pupil_offset_y)), 1)

        # Speed buff effect
        if self.speed_buff_active:
            glow_intensity = int(50 + math.sin(self.speed_buff_timer * 0.3) * 30)

            for i in range(3):
                glow_radius = radius + 4 + (i * 3)
                glow_alpha = glow_intensity - (i * 20)
                if glow_alpha > 0:
                    glow_surface = pygame.Surface((glow_radius * 2 + 10, glow_radius * 2 + 10), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, (255, 0, 0, glow_alpha),
                                       (glow_radius + 5, glow_radius + 5), glow_radius, 2)
                    screen.blit(glow_surface, (int(draw_x - glow_radius - 5), int(draw_y - glow_radius - 5)))

    def get_position(self):
        """Get current grid position"""
        return (self.grid_x, self.grid_y)

    def get_center(self):
        """Get center pixel coordinates"""
        return (self.x + self.size // 2, self.y + self.size // 2)

    def reset(self, start_x, start_y):
        """Reset ghost to starting position"""
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
        self.speed_buff_active = False
        self.speed_buff_timer = 0
        self.stuck_timer = 0
        self.last_grid_position = (self.grid_x, self.grid_y)
        # Don't reset start debuff on death - only on new game
        # Progressive speed is NOT reset on death
        self.update_current_speed()

    def full_reset(self, start_x, start_y):
        """Full reset including progressive speed (new game only)"""
        self.reset(start_x, start_y)
        self.progressive_speed_timer = 0
        self.progressive_speed_multiplier = 1.0
        self.has_start_debuff = True
        self.start_debuff_timer = 300  # Reset 5 second debuff
        self.update_current_speed()

    def set_frightened(self, trigger_speed_buff=True):
        """Set ghost to frightened mode"""
        if self.mode != EATEN and not self.in_house:
            self.previous_mode = self.mode if self.mode != FRIGHTENED else self.previous_mode
            self.switch_mode(FRIGHTENED)
            self.mode_timer = 0
            self.trigger_speed_buff_after = trigger_speed_buff
            print(f"{self.name} set to frightened mode (speed buff after: {trigger_speed_buff})")


class CrankyGhost(Ghost):
    """Special hunter ghost that spawns after 30 seconds"""

    def __init__(self, start_x, start_y):
        super().__init__(start_x, start_y, (128, 0, 128), "cranky")
        self.player_speed_multiplier = 0.95  # 95% of player speed
        self.in_house = True  # START IN HOUSE like other ghosts
        self.mode = SCATTER  # Start in scatter to exit house properly
        self.progressive_speed_multiplier = 1.0
        self.has_start_debuff = False  # Cranky has no start debuff
        self.start_debuff_timer = 0
        self.house_exit_delay = 60  # Exit house quickly (1 second)

        # Cranky specific properties
        self.is_cranky = True  # Flag to identify Cranky
        self.always_chase = True  # Always chase after leaving house

    def update(self, maze, pacman, all_ghosts=None):
        """Update Cranky - uses parent update but with modifications"""
        self.mode_timer += 1

        # Update speed buff
        if self.speed_buff_active:
            self.speed_buff_timer -= 1
            if self.speed_buff_timer <= 0:
                self.speed_buff_active = False
                self.update_speed(pacman)
                print(f"{self.name} speed buff ended")

        # House exit logic - use parent's logic
        if self.in_house:
            self.handle_house_exit(pacman)
            if self.in_house:
                self.move_in_house()
                return

        # Always update speed to match player
        if not self.speed_buff_active and self.mode != FRIGHTENED and self.mode != EATEN:
            self.update_speed(pacman)

        # Cranky ALWAYS chases after leaving house (override scatter/chase pattern)
        if self.mode != FRIGHTENED and self.mode != EATEN and hasattr(self, 'always_chase'):
            if self.mode != CHASE:
                self.mode = CHASE
                self.mode_timer = 0

        # Frightened mode timeout
        if self.mode == FRIGHTENED:
            frightened_duration = 120 if hasattr(self, 'short_frightened') and self.short_frightened else 360
            if self.mode_timer > frightened_duration:
                print(f"{self.name} exiting frightened mode")
                if self.trigger_speed_buff_after:
                    self.activate_speed_buff()
                self.switch_mode(CHASE)  # Always back to CHASE
                if hasattr(self, 'short_frightened'):
                    self.short_frightened = False

        # Eaten ghosts return home
        if self.mode == EATEN:
            self.speed = self.base_speed * 2
            center_x = MAZE_WIDTH // 2
            center_y = MAZE_HEIGHT // 2
            if abs(self.grid_x - center_x) <= 1 and abs(self.grid_y - center_y) <= 2:
                # Return to house like normal ghosts
                self.mode = SCATTER
                self.in_house = True
                self.grid_x = center_x
                self.grid_y = center_y
                self.x = self.grid_x * GRID_SIZE
                self.y = self.grid_y * GRID_SIZE
                self.pixel_x = float(self.x)
                self.pixel_y = float(self.y)
                self.house_exit_timer = 0
                self.house_exit_delay = 60  # Quick exit

        # Set target
        self.set_target(pacman, maze, all_ghosts)

        # Move
        self.move(maze)

        # Check if stuck
        current_position = (self.grid_x, self.grid_y)
        if current_position == self.last_grid_position:
            self.stuck_timer += 1
            if self.stuck_timer > self.max_stuck_time:
                print(f"{self.name} is stuck, forcing direction change")
                self.can_reverse = True
                self.direction = self.get_opposite_direction(self.direction)
                self.stuck_timer = 0
        else:
            self.stuck_timer = 0
            self.last_grid_position = current_position

        # Animation
        self.animation_frame += self.animation_speed
        if self.animation_frame >= 2:
            self.animation_frame = 0

    def update_speed(self, pacman):
        """Update speed based on Pac-Man's current speed"""
        # Get Pac-Man's actual current speed (including all boosts)
        pacman_current_speed = pacman.speed

        # Cranky matches 95% of Pac-Man's speed
        self.speed = pacman_current_speed * self.player_speed_multiplier

        # Update base speed for other calculations
        self.base_speed = self.speed

        # Apply frightened speed reduction if needed
        if self.mode == FRIGHTENED:
            self.speed = self.base_speed * 0.5

    def set_target(self, pacman, maze, all_ghosts=None):
        """Cranky always hunts Pac-Man directly"""
        if self.mode == FRIGHTENED:
            if self.mode_timer % 30 == 0:
                self.target_x = random.randint(0, MAZE_WIDTH - 1)
                self.target_y = random.randint(0, MAZE_HEIGHT - 1)
        elif self.mode == EATEN:
            self.target_x = MAZE_WIDTH // 2
            self.target_y = MAZE_HEIGHT // 2
        else:
            # Always chase Pac-Man directly
            self.target_x, self.target_y = pacman.grid_x, pacman.grid_y

    def reset(self, start_x, start_y):
        """Reset Cranky to house like other ghosts"""
        # Reset to house position
        self.in_house = True
        self.grid_x = start_x
        self.grid_y = start_y
        self.x = self.grid_x * GRID_SIZE
        self.y = self.grid_y * GRID_SIZE
        self.pixel_x = float(self.x)
        self.pixel_y = float(self.y)
        self.direction = UP
        self.mode = SCATTER  # Start in scatter to exit house properly
        self.previous_mode = SCATTER
        self.mode_timer = 0
        self.house_exit_timer = 0
        self.house_exit_delay = 60  # Quick exit (1 second)
        self.animation_frame = 0
        self.can_reverse = False
        self.speed_buff_active = False
        self.speed_buff_timer = 0
        self.stuck_timer = 0
        self.last_grid_position = (self.grid_x, self.grid_y)

    def full_reset(self, start_x, start_y):
        """Full reset for Cranky"""
        self.reset(start_x, start_y)
        # Cranky doesn't have progressive speed system

    def set_frightened_short(self):
        """Set Cranky to frightened for 2 seconds (from Speed Pellet)"""
        if self.mode != EATEN:
            self.previous_mode = CHASE
            self.switch_mode(FRIGHTENED)
            self.mode_timer = 0
            self.trigger_speed_buff_after = False
            self.short_frightened = True
            print(f"{self.name} set to SHORT frightened mode (2 seconds)")

    def move(self, maze):
        """Use parent's move method"""
        # Just call the parent move method
        super().move(maze)

    def draw(self, screen):
        """Draw Cranky with special visual effects"""
        # Call parent draw method
        super().draw(screen)

        # Add extra visual effects for Cranky
        draw_x = self.x + GRID_SIZE // 2
        draw_y = self.y + GRID_SIZE // 2
        radius = self.size // 2

        # Add a pulsing aura effect
        if self.mode != FRIGHTENED and self.mode != EATEN:
            pulse = int(math.sin(self.animation_frame * 2) * 3)
            for i in range(2):
                aura_radius = radius + 8 + (i * 4) + pulse
                aura_alpha = 30 - (i * 10)
                if aura_alpha > 0:
                    aura_surface = pygame.Surface((aura_radius * 2 + 10, aura_radius * 2 + 10), pygame.SRCALPHA)
                    pygame.draw.circle(aura_surface, (128, 0, 128, aura_alpha),
                                       (aura_radius + 5, aura_radius + 5), aura_radius, 2)
                    screen.blit(aura_surface, (int(draw_x - aura_radius - 5), int(draw_y - aura_radius - 5)))