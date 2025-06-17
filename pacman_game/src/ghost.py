"""
Ghost Classes
Handles ghost AI, movement, and behavior patterns
"""

import pygame
import random
import math
from src.constants import *

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
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.speed = GHOST_SPEED
        self.size = GHOST_SIZE
        
        # AI behavior
        self.mode = SCATTER
        self.mode_timer = 0
        self.target_x = 0
        self.target_y = 0
        
        # Animation
        self.animation_frame = 0
        self.animation_speed = 0.1
        
    def update(self, maze, pacman):
        """Update ghost position and AI"""
        self.mode_timer += 1
        
        # Switch between modes
        if self.mode == SCATTER and self.mode_timer > 300:  # 5 seconds at 60 FPS
            self.mode = CHASE
            self.mode_timer = 0
        elif self.mode == CHASE and self.mode_timer > 600:  # 10 seconds
            self.mode = SCATTER
            self.mode_timer = 0
        
        # Set target based on mode and ghost personality
        self.set_target(pacman)
        
        # Choose next direction
        self.choose_direction(maze)
        
        # Move ghost
        self.move(maze)
        
        # Update animation
        self.animation_frame += self.animation_speed
        if self.animation_frame >= 2:
            self.animation_frame = 0
    
    def set_target(self, pacman):
        """Set target coordinates based on ghost mode and personality"""
        if self.mode == SCATTER:
            # Each ghost has a different corner to target
            corners = {
                "blinky": (MAZE_WIDTH - 1, 0),
                "pinky": (0, 0),
                "inky": (MAZE_WIDTH - 1, MAZE_HEIGHT - 1),
                "clyde": (0, MAZE_HEIGHT - 1)
            }
            self.target_x, self.target_y = corners.get(self.name, (0, 0))
        
        elif self.mode == CHASE:
            # Each ghost has different targeting behavior
            if self.name == "blinky":
                # Target Pac-Man directly
                self.target_x, self.target_y = pacman.get_position()
            
            elif self.name == "pinky":
                # Target 4 spaces ahead of Pac-Man
                target_x = pacman.grid_x + pacman.direction[0] * 4
                target_y = pacman.grid_y + pacman.direction[1] * 4
                self.target_x = max(0, min(MAZE_WIDTH - 1, target_x))
                self.target_y = max(0, min(MAZE_HEIGHT - 1, target_y))
            
            elif self.name == "inky":
                # More complex targeting (simplified)
                self.target_x, self.target_y = pacman.get_position()
            
            elif self.name == "clyde":
                # Target Pac-Man if far away, otherwise scatter
                distance = math.sqrt((self.grid_x - pacman.grid_x)**2 + 
                                   (self.grid_y - pacman.grid_y)**2)
                if distance > 8:
                    self.target_x, self.target_y = pacman.get_position()
                else:
                    self.target_x, self.target_y = (0, MAZE_HEIGHT - 1)
        
        elif self.mode == FRIGHTENED:
            # Random targeting when frightened
            self.target_x = random.randint(0, MAZE_WIDTH - 1)
            self.target_y = random.randint(0, MAZE_HEIGHT - 1)
        
        elif self.mode == EATEN:
            # Return to start position
            self.target_x, self.target_y = (MAZE_WIDTH // 2, MAZE_HEIGHT // 2)
    
    def choose_direction(self, maze):
        """Choose the best direction to reach target"""
        possible_directions = []
        
        # Check all four directions
        for direction in [UP, DOWN, LEFT, RIGHT]:
            next_x = self.grid_x + direction[0]
            next_y = self.grid_y + direction[1]
            
            # Don't reverse direction (unless necessary)
            reverse_direction = (-self.direction[0], -self.direction[1])
            if direction == reverse_direction:
                continue
            
            # Check if the direction is valid
            if (0 <= next_x < MAZE_WIDTH and 0 <= next_y < MAZE_HEIGHT and
                not maze.is_wall(next_x, next_y)):
                possible_directions.append(direction)
        
        if not possible_directions:
            # If no valid directions, allow reversing
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
                # Choose direction that gets closest to target
                best_direction = possible_directions[0]
                best_distance = float('inf')
                
                for direction in possible_directions:
                    next_x = self.grid_x + direction[0]
                    next_y = self.grid_y + direction[1]
                    
                    distance = math.sqrt((next_x - self.target_x)**2 + 
                                       (next_y - self.target_y)**2)
                    
                    if distance < best_distance:
                        best_distance = distance
                        best_direction = direction
                
                self.direction = best_direction
    
    def move(self, maze):
        """Move the ghost in its current direction"""
        if self.direction != STOP:
            new_x = self.x + self.direction[0] * self.speed
            new_y = self.y + self.direction[1] * self.speed
            
            # Update grid position
            grid_x = new_x // GRID_SIZE
            grid_y = new_y // GRID_SIZE
            
            # Check bounds and walls
            if (0 <= grid_x < MAZE_WIDTH and 0 <= grid_y < MAZE_HEIGHT and
                not maze.is_wall(grid_x, grid_y)):
                self.x = new_x
                self.y = new_y
                self.grid_x = int(self.x // GRID_SIZE)
                self.grid_y = int(self.y // GRID_SIZE)
        
        # Handle screen wrapping
        if self.x < -GRID_SIZE:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = -GRID_SIZE
    
    def draw(self, screen):
        """Draw the ghost to the screen"""
        draw_x = self.x + GRID_SIZE // 2
        draw_y = self.y + GRID_SIZE // 2
        radius = self.size // 2
        
        # Choose color based on mode
        color = self.color
        if self.mode == FRIGHTENED:
            color = BLUE
        elif self.mode == EATEN:
            color = WHITE
        
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
        
        # Draw eyes
        eye_color = WHITE if self.mode != EATEN else BLACK
        pupil_color = BLACK if self.mode != EATEN else WHITE
        
        # Left eye
        pygame.draw.circle(screen, eye_color, (int(draw_x - 6), int(draw_y - 4)), 3)
        pygame.draw.circle(screen, pupil_color, (int(draw_x - 6), int(draw_y - 4)), 1)
        
        # Right eye
        pygame.draw.circle(screen, eye_color, (int(draw_x + 6), int(draw_y - 4)), 3)
        pygame.draw.circle(screen, pupil_color, (int(draw_x + 6), int(draw_y - 4)), 1)
    
    def get_position(self):
        """Get current grid position"""
        return (self.grid_x, self.grid_y)
    
    def get_center(self):
        """Get center pixel coordinates"""
        return (self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2)
    
    def reset(self, start_x, start_y):
        """Reset ghost to starting position"""
        self.start_x = start_x
        self.start_y = start_y
        self.x = start_x * GRID_SIZE
        self.y = start_y * GRID_SIZE
        self.grid_x = start_x
        self.grid_y = start_y
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.mode = SCATTER
        self.mode_timer = 0
        self.animation_frame = 0
    
    def set_frightened(self):
        """Set ghost to frightened mode"""
        self.mode = FRIGHTENED
        self.mode_timer = 0
        # Reverse direction
        self.direction = (-self.direction[0], -self.direction[1])
