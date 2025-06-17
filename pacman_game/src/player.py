"""
Pacman Player Class
Handles Pac-Man character movement, animation, and behavior
"""

import pygame
import math
from src.constants import *

class Pacman:
    def __init__(self, start_x, start_y):
        self.start_x = start_x
        self.start_y = start_y
        
        # Pixel-Position (wie im ursprünglichen Code)
        self.x = 270  # Original Startposition
        self.y = 360  # Original Startposition
        
        # Grid-Position
        self.grid_x = self.x // GRID_SIZE
        self.grid_y = self.y // GRID_SIZE
        
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
        """Update Pac-Man's position and state - überarbeitete Version"""
        # Handle keyboard input
        keys = pygame.key.get_pressed()
        pressed_direction = self.get_pressed_direction(keys)
        
        # Set next direction if key is pressed
        if pressed_direction:
            self.next_direction = pressed_direction
        
        # Try to change direction if next_direction is set
        if self.next_direction and self.can_move_direction(maze, self.next_direction):
            self.set_velocity_from_direction(self.next_direction)
            self.next_direction = None
        
        # Continue moving in current direction
        if self.current_direction and self.can_move_direction(maze, self.current_direction):
            # Move Pac-Man
            self.x += self.velocity_x
            self.y += self.velocity_y
            
            # Update grid position
            self.grid_x = self.x // GRID_SIZE
            self.grid_y = self.y // GRID_SIZE
        else:
            # Stop if can't move
            self.velocity_x = 0
            self.velocity_y = 0
            self.current_direction = None
        
        # Handle screen wrapping (tunnel effect)
        if self.x < -GRID_SIZE:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = -GRID_SIZE
        
        # Update animation
        self.animation_frame += self.animation_speed
        if self.animation_frame >= 4:
            self.animation_frame = 0
        
        # Sound-Management aus dem ursprünglichen Code
        current_moving = (self.velocity_x != 0 or self.velocity_y != 0)
        
        if self.sound_enabled and self.sound_loaded:
            if current_moving and not self.last_moving_state:
                # Start sound when beginning to move
                if self.wakawaka_channel is None or not self.wakawaka_channel.get_busy():
                    self.wakawaka_channel = self.wakawaka_sound.play(-1)  # Loop indefinitely
            elif not current_moving and self.last_moving_state:
                # Stop sound when stopping
                if self.wakawaka_channel and self.wakawaka_channel.get_busy():
                    self.wakawaka_channel.stop()
                    self.wakawaka_channel = None
        
        self.last_moving_state = current_moving
        self.is_moving = current_moving
    
    def can_move_direction(self, maze, direction):
        """Check if Pac-Man can move in the given direction"""
        # Calculate next position based on direction
        test_x = self.x
        test_y = self.y
        
        if direction == 'up':
            test_y -= self.speed
        elif direction == 'down':
            test_y += self.speed
        elif direction == 'left':
            test_x -= self.speed
        elif direction == 'right':
            test_x += self.speed
        else:
            return True
        
        # Convert to grid position
        grid_x = test_x // GRID_SIZE
        grid_y = test_y // GRID_SIZE
        
        # Check bounds
        if (grid_x < 0 or grid_x >= maze.width or 
            grid_y < 0 or grid_y >= maze.height):
            return False
        
        # Check for walls
        return not maze.is_wall(grid_x, grid_y)
    
    def draw(self, screen):
        """Draw Pac-Man to the screen"""
        # Calculate drawing position (center the sprite)
        draw_x = self.x + GRID_SIZE // 2
        draw_y = self.y + GRID_SIZE // 2
        
        # Simple animated Pac-Man using circles
        mouth_angle = int(self.animation_frame) * 15  # Opening/closing mouth
        
        # Determine rotation based on direction
        rotation = 0
        if self.direction == RIGHT:
            rotation = 0
        elif self.direction == LEFT:
            rotation = 180
        elif self.direction == UP:
            rotation = 270
        elif self.direction == DOWN:
            rotation = 90
        
        # Draw Pac-Man as a circle with a mouth
        radius = self.size // 2
        
        if mouth_angle > 0:
            # Draw Pac-Man with mouth open
            start_angle = math.radians(rotation + mouth_angle)
            end_angle = math.radians(rotation + 360 - mouth_angle)
            
            # Create points for the Pac-Man shape
            points = [(draw_x, draw_y)]
            
            # Add arc points
            for angle in range(int(math.degrees(start_angle)), int(math.degrees(end_angle)), 5):
                x = draw_x + radius * math.cos(math.radians(angle))
                y = draw_y + radius * math.sin(math.radians(angle))
                points.append((x, y))
            
            points.append((draw_x, draw_y))
            
            if len(points) > 2:
                pygame.draw.polygon(screen, YELLOW, points)
        else:
            # Draw closed mouth (full circle)
            pygame.draw.circle(screen, YELLOW, (int(draw_x), int(draw_y)), radius)
        
        # Draw eye
        eye_x = draw_x + radius // 3 * math.cos(math.radians(rotation - 45))
        eye_y = draw_y + radius // 3 * math.sin(math.radians(rotation - 45))
        pygame.draw.circle(screen, BLACK, (int(eye_x), int(eye_y)), 2)
    
    def get_position(self):
        """Get current grid position"""
        return (self.grid_x, self.grid_y)
    
    def get_center(self):
        """Get center pixel coordinates"""
        return (self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2)
    
    def collides_with(self, other):
        """Check collision with another object"""
        distance = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        return distance < (self.size + other.size) // 2    
    def reset(self, start_x, start_y):
        """Reset Pac-Man to starting position"""
        self.start_x = start_x
        self.start_y = start_y
        
        # Reset to original starting position (pixel coordinates)
        self.x = 270  # Original Startposition
        self.y = 360  # Original Startposition
        
        # Update grid position
        self.grid_x = self.x // GRID_SIZE
        self.grid_y = self.y // GRID_SIZE
        
        # Reset movement
        self.current_direction = None
        self.next_direction = None
        self.velocity_x = 0
        self.velocity_y = 0
        self.animation_frame = 0
