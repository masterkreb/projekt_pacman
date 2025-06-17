"""
Pellets and Power Pellets
Handles pellet placement, collection, and scoring
"""

import pygame
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
        self.color = YELLOW
        self.points = LARGE_PELLET_POINTS if is_power_pellet else SMALL_PELLET_POINTS
        self.radius = LARGE_PELLET_SIZE if is_power_pellet else SMALL_PELLET_SIZE
        self.visible = True
        
        # Animation für Power-Pellets
        self.flash_time = 0.2
        self.timer = 0
        self.animation_frame = 0
        self.animation_speed = 0.1
    
    def update(self, dt=1/60):
        """Update pellet animation - aus dem ursprünglichen Code"""
        if self.is_power_pellet:
            self.timer += dt
            if self.timer >= self.flash_time:
                self.visible = not self.visible
                self.timer = 0
            
            self.animation_frame += self.animation_speed
            if self.animation_frame >= 2:
                self.animation_frame = 0    
    def draw(self, screen):
        """Draw the pellet - verbesserte Version aus dem ursprünglichen Code"""
        if not self.collected and self.visible:
            pixel_x = self.x * GRID_SIZE + GRID_SIZE // 2
            pixel_y = self.y * GRID_SIZE + GRID_SIZE // 2
            
            if self.is_power_pellet:
                # Animiertes Power-Pellet mit Glow-Effekt
                size = LARGE_PELLET_SIZE + int(self.animation_frame * 2)
                pygame.draw.circle(screen, self.color, (pixel_x, pixel_y), size)
                # Glow-Effekt
                pygame.draw.circle(screen, (255, 255, 100), (pixel_x, pixel_y), size + 2, 1)
            else:
                # Normales Pellet
                pygame.draw.circle(screen, self.color, (pixel_x, pixel_y), self.radius)
    
    def get_points(self):
        """Get points value for this pellet"""
        return LARGE_PELLET_POINTS if self.is_power_pellet else SMALL_PELLET_POINTS

class PelletManager:
    def __init__(self, maze):
        self.maze = maze
        self.pellets = []
        self.power_pellet_positions = [
            (1, 3), (38, 3), (1, 17), (38, 17)  # Corner positions
        ]
        self.reset()
    
    def reset(self):
        """Reset all pellets"""
        self.pellets = []
        self.create_pellets()
    
    def create_pellets(self):
        """Create pellets in all valid maze positions"""
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if not self.maze.is_wall(x, y):
                    # Skip ghost starting area (center area)
                    center_x, center_y = self.maze.get_center_position()
                    if (abs(x - center_x) <= 3 and abs(y - center_y) <= 3):
                        continue                    # Create power pellet at specific positions
                    is_power_pellet = (x, y) in self.power_pellet_positions
                    
                    # Don't place pellets too close to Pac-Man start
                    if x == 1 and y == 1:
                        continue
                    
                    pellet = Pellet(x, y, is_power_pellet)
                    self.pellets.append(pellet)

    def update(self):
        """Update all pellets"""
        for pellet in self.pellets:
            pellet.update()

    def draw(self, screen):
        """Draw all pellets"""
        for pellet in self.pellets:
            pellet.draw(screen)

    def check_collection(self, pacman):
        """Check if Pac-Man collected any pellets"""
        total_points = 0
        
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
        
        for pellet in self.pellets:
            if not pellet.collected:
                for check_x, check_y in positions_to_check:
                    if (pellet.grid_x == check_x and pellet.grid_y == check_y):
                        pellet.collected = True
                        total_points += pellet.get_points()
                        
                        # If it's a power pellet, make ghosts frightened
                        if pellet.is_power_pellet:
                            self.trigger_power_mode()
                        break  # Aus der inner loop ausbrechen
        
        return total_points
    
    def trigger_power_mode(self):
        """Called when a power pellet is collected"""
        # This will be handled by the game class
        # For now, just a placeholder
        pass
    
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
            if not pellet.collected:
                count += 1
        return count
    
    def get_pellet_at(self, x, y):
        """Get pellet at specific grid position"""
        for pellet in self.pellets:
            if pellet.grid_x == x and pellet.grid_y == y and not pellet.collected:
                return pellet
        return None
    
    def collect_pellet_at(self, x, y):
        """Manually collect pellet at position"""
        pellet = self.get_pellet_at(x, y)
        if pellet:
            pellet.collected = True
            return pellet.get_points()
        return 0
