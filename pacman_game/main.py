"""
Pac-Man Game - Main Entry Point
Simple Pac-Man game implementation using Pygame
"""

import pygame
import sys
from src.game import Game
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


def main():
    """Main function to start the Pac-Man game"""
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()

    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pac-Man Game")

    # Try to set icon if available
    try:
        icon = pygame.image.load("assets/images/ui/icon.png")
        pygame.display.set_icon(icon)
        print("Game icon loaded successfully!")
    except (pygame.error, FileNotFoundError) as e:
        print(f"Could not load game icon: {e}")

    # Create clock for FPS control
    clock = pygame.time.Clock()

    # Create game instance
    game = Game(screen)

    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                # Handle game events and check for quit signal
                result = game.handle_event(event)
                if result == "quit":
                    running = False

        # Update game state and check for quit signal
        result = game.update()
        if result == "quit":
            running = False

        # Draw everything
        game.draw()

        # Update display
        pygame.display.flip()

        # Control frame rate
        clock.tick(FPS)

    # Clean up
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
