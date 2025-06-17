"""
Game Constants
All game-wide constants and configuration values
"""

# Exakte Layout-Dimensionen aus dem Spielfeld
LAYOUT_WIDTH = 28  # Spalten im Spielfeld
LAYOUT_HEIGHT = 31  # Zeilen im Spielfeld
TILE = 24  # Tile-Größe aus dem ursprünglichen spielfeld.py

# Screen dimensions - angepasst an das Spielfeld
SCREEN_WIDTH = LAYOUT_WIDTH * TILE  # 28 * 24 = 672
SCREEN_HEIGHT = LAYOUT_HEIGHT * TILE  # 31 * 24 = 744
FPS = 60

# Grid settings
GRID_SIZE = TILE
MAZE_WIDTH = LAYOUT_WIDTH
MAZE_HEIGHT = LAYOUT_HEIGHT

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

# Ghost modes
SCATTER = "scatter"
CHASE = "chase"
FRIGHTENED = "frightened"
EATEN = "eaten"

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
