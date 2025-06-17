"""
Game Constants
All game-wide constants and configuration values
"""

# Screen dimensions - aus dem ursprünglichen Projekt
SCREEN_WIDTH = 540
SCREEN_HEIGHT = 720
FPS = 60

# Grid settings - passt zu dem originalen Spielfeld
TILE = 24  # Tile-Größe aus dem ursprünglichen spielfeld.py
GRID_SIZE = TILE
MAZE_WIDTH = SCREEN_WIDTH // GRID_SIZE
MAZE_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)

# Pac-Man settings - aus dem ursprünglichen Projekt
PACMAN_SPEED = 3  # Originalgeschwindigkeit
PACMAN_SIZE = 20  # Originalgröße

# Ghost settings
GHOST_SPEED = 1.5
GHOST_SIZE = 16

# Pellet settings
SMALL_PELLET_SIZE = 2
LARGE_PELLET_SIZE = 8
SMALL_PELLET_POINTS = 10
LARGE_PELLET_POINTS = 50

# Game states
MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"
VICTORY = "victory"

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)

# Ghost modes
SCATTER = "scatter"
CHASE = "chase"
FRIGHTENED = "frightened"
EATEN = "eaten"
