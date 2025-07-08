"""
Constants and Settings
Defines all game constants and settings
"""

import pygame

# Screen dimensions
SCREEN_WIDTH = 560  # 28 * 20 (korrekt: 28 Tiles × 20 Pixel)
SCREEN_HEIGHT = 680  # 620 (Spielfeld) + 60 (UI-Bereich)
GAME_AREA_HEIGHT = 620  # 31 * 20 (korrekt: 31 Tiles × 20 Pixel)

# Grid settings - aus dem alten Code
GRID_SIZE = 20  # Originalgröße beibehalten für exakte Kollisionserkennung
MAZE_WIDTH = 28
MAZE_HEIGHT = 31

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Game states
MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3
VICTORY = 4

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)

# Game settings
FPS = 60
LIVES = 3

# Geschwindigkeiten - angepasst für größeres Spielfeld
# Original Pac-Man: 80 Pixel/Sekunde = 1.33 Pixel/Frame bei 60 FPS
# Aber unser Spielfeld ist größer, also 1.3x schneller
PACMAN_SPEED = 1.733  # 1.33 * 1.3 für größeres Spielfeld
PACMAN_SPEED_BOOST = PACMAN_SPEED * 2  # Doppelte Geschwindigkeit mit Speed Pellet
GHOST_SPEED = 1.3  # 75% von Pac-Man's Geschwindigkeit

# Sizes
PACMAN_SIZE = 16
GHOST_SIZE = 16
SMALL_PELLET_SIZE = 2
LARGE_PELLET_SIZE = 6

# Points
SMALL_PELLET_POINTS = 10
LARGE_PELLET_POINTS = 50
GHOST_POINTS = 200

# Ghost AI states
SCATTER = 0
CHASE = 1
FRIGHTENED = 2
EATEN = 3
