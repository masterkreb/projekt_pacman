"""
Maze Class
Handles the game maze/level layout, walls, and pathfinding
"""

import pygame
from src.constants import *

class Maze:
    def __init__(self):
        # Original Spielfeld-Layout aus spielfeld.py
        self.layout_strings = [
            "############################",
            "#............##............#",
            "#.####.#####.##.#####.####.#",
            "#.####.#####.##.#####.####.#",
            "#.####.#####.##.#####.####.#",
            "#..........................#",
            "#.####.##.########.##.####.#",
            "#.####.##.########.##.####.#",
            "#......##....##....##......#",
            "######.#####.##.#####.######",
            "######.#####.##.#####.######",
            "######.##..........##.######",
            "######.##.########.##.######",
            "######.##.########.##.######",
            "..........########..........",
            "######.##.########.##.######",
            "######.##.########.##.######",
            "######.##..........##.######",
            "######.##.########.##.######",
            "######.##.########.##.######",
            "#............##............#",
            "#.####.#####.##.#####.####.#",
            "#.####.#####.##.#####.####.#",
            "#...##................##...#",
            "###.##.##.########.##.##.###",
            "###.##.##.########.##.##.###",
            "#......##....##....##......#",
            "#.##########.##.##########.#",
            "#.##########.##.##########.#",
            "#..........................#",
            "############################",
        ]
        
        # Konvertiere String-Layout zu 2D Array
        self.layout = []
        for row_string in self.layout_strings:
            row = []
            for char in row_string:
                if char == '#':
                    row.append(1)  # Wand
                else:
                    row.append(0)  # Leer
            self.layout.append(row)
        
        # Maze-Dimensionen
        self.height = len(self.layout)
        self.width = len(self.layout[0]) if self.layout else 0
    
    def is_wall(self, x, y):
        """Check if the given grid position is a wall"""
        if (x < 0 or x >= self.width or y < 0 or y >= self.height):
            return True
        return self.layout[y][x] == 1
    
    def is_empty(self, x, y):
        """Check if the given grid position is empty"""
        return not self.is_wall(x, y)
    
    def get_valid_positions(self):
        """Get all valid (non-wall) positions in the maze"""
        positions = []
        for y in range(self.height):
            for x in range(self.width):
                if not self.is_wall(x, y):
                    positions.append((x, y))
        return positions
    
    def draw(self, screen):
        """Draw the maze to the screen"""
        for y in range(self.height):
            for x in range(self.width):
                pixel_x = x * GRID_SIZE
                pixel_y = y * GRID_SIZE
                
                if self.is_wall(x, y):
                    # Draw wall
                    wall_rect = pygame.Rect(pixel_x, pixel_y, GRID_SIZE, GRID_SIZE)
                    pygame.draw.rect(screen, BLUE, wall_rect)
                    
                    # Add some depth with border
                    border_rect = pygame.Rect(pixel_x + 1, pixel_y + 1, 
                                            GRID_SIZE - 2, GRID_SIZE - 2)
                    pygame.draw.rect(screen, (0, 0, 150), border_rect)
    
    def get_neighbors(self, x, y):
        """Get valid neighboring positions"""
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < self.width and 0 <= new_y < self.height and
                not self.is_wall(new_x, new_y)):
                neighbors.append((new_x, new_y))
        return neighbors
    
    def find_path(self, start, end):
        """Simple pathfinding using BFS (for AI)"""
        from collections import deque
        
        if self.is_wall(start[0], start[1]) or self.is_wall(end[0], end[1]):
            return []
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            (x, y), path = queue.popleft()
            
            if (x, y) == end:
                return path
            
            for next_x, next_y in self.get_neighbors(x, y):
                if (next_x, next_y) not in visited:
                    visited.add((next_x, next_y))
                    queue.append(((next_x, next_y), path + [(next_x, next_y)]))
        
        return []  # No path found
    
    def get_center_position(self):
        """Get the center position of the maze"""
        return (self.width // 2, self.height // 2)
    
    def get_tunnel_positions(self):
        """Get positions for tunnel entrances (screen wrapping)"""
        # Look for empty spaces at the edges
        left_tunnel = None
        right_tunnel = None
        
        for y in range(self.height):
            if not self.is_wall(0, y):
                left_tunnel = (0, y)
                break
        
        for y in range(self.height):
            if not self.is_wall(self.width - 1, y):
                right_tunnel = (self.width - 1, y)
                break
        
        return left_tunnel, right_tunnel
