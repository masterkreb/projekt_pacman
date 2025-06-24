"""
Main Game Class
Handles game logic, state management, and coordination between components
School Project - Pac-Man Clone
"""

import pygame
import os
import math
from .constants import *
from .player import Pacman
from .ghost import Ghost
from .maze import Maze
from .pellets import PelletManager
from .menu import Menu

class MusicManager:
    """
    Manages background music for the Pac-Man game
    Handles loading, playing, pausing and volume control
    """

    def __init__(self):
        self.music_loaded = False
        self.music_playing = False
        self.music_volume = 0.3  # Reduziert von 0.5 auf 0.3
        self.music_files = {
            'background': 'assets/sounds//effects/background_music.mp3',
            'game_start': 'assets/audio/game_start.ogg',
            'game_over': 'assets/audio/game_over.ogg',
            'level_complete': 'assets/audio/level_complete.ogg'
        }

    def load_background_music(self, music_file=None):
        """Load background music from file"""
        try:
            if music_file is None:
                music_file = self.music_files['background']

            if os.path.exists(music_file):
                pygame.mixer.music.load(music_file)
                # Drastisch reduzierte Lautstärke: nur 15% der Original-Lautstärke
                pygame.mixer.music.set_volume(self.music_volume * 0.15)
                self.music_loaded = True
                print(f"Background music loaded: {music_file} (15% volume)")
            else:
                print(f"Music file not found: {music_file}")
                self.music_loaded = False

        except pygame.error as e:
            print(f"Error loading music: {e}")
            self.music_loaded = False

    def play_background_music(self, loops=-1):
        """Start playing background music in a loop"""
        if self.music_loaded and not self.music_playing:
            try:
                pygame.mixer.music.play(loops)
                self.music_playing = True
                print("Background music started")
            except pygame.error as e:
                print(f"Error playing music: {e}")

    def stop_background_music(self):
        """Stop background music completely"""
        pygame.mixer.music.stop()
        self.music_playing = False
        print("Background music stopped")

    def pause_background_music(self):
        """Pause background music (can be resumed)"""
        if self.music_playing:
            pygame.mixer.music.pause()
            print("Background music paused")

    def unpause_background_music(self):
        """Resume paused background music"""
        pygame.mixer.music.unpause()
        print("Background music resumed")

    def set_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume * 0.15)  # Nur 15% der Lautstärke
        print(f"Music volume set to: {self.music_volume * 0.15}")  # Show actual volume

    def toggle_music(self):
        """Toggle music on/off - properly handles mute/unmute"""
        if self.music_playing:
            self.pause_background_music()
            self.music_playing = False
        else:
            if self.music_loaded:
                self.unpause_background_music()
                self.music_playing = True
            else:
                # Try to load and start music if not loaded
                self.load_background_music()
                if self.music_loaded:
                    self.play_background_music()

    def is_playing(self):
        """Check if music is currently playing"""
        return pygame.mixer.music.get_busy()

class Game:
    """
    Main game class that manages the entire game state
    Handles all game logic, rendering, and state transitions
    """

    def __init__(self, screen):
        self.screen = screen
        self.state = MENU
        self.score = 0
        self.lives = 3

        # Sound system initialization
        self.sound_enabled = True
        self.sound_loaded = False
        self.wakawaka_sound = None
        self.wakawaka_channel = None
        self.eat_ghost_sound = None
        self.death_sound = None

        # Waka-waka timer for controlled sound playback
        self.wakawaka_timer = 0
        self.wakawaka_interval = 200  # Milliseconds between sounds

        # Initialize music manager
        self.music_manager = MusicManager()

        # Load sound effects
        self.load_sounds()

        # Initialize game components
        self.maze = Maze()
        self.pacman = Pacman(11, 15)  # Starting position optimized for gameplay
        self.pellet_manager = PelletManager(self.maze)
        self.menu = Menu()

        # Initialize ghosts with classic names at center position
        ghost_start_x = self.maze.width // 2
        ghost_start_y = self.maze.height // 2
        self.ghosts = [
            Ghost(ghost_start_x, ghost_start_y, RED, "blinky"),
            Ghost(ghost_start_x, ghost_start_y, PINK, "pinky"),
            Ghost(ghost_start_x, ghost_start_y, CYAN, "inky"),
            Ghost(ghost_start_x, ghost_start_y, ORANGE, "clyde")
        ]

        # Font for UI elements
        self.font = pygame.font.Font(None, 36)

    def load_sounds(self):
        """Load all game sound effects"""
        try:
            pygame.mixer.init()

            # Set global volume limit
            pygame.mixer.set_num_channels(8)  # Set number of sound channels

            # Main sound effects directory
            sound_path = "assets/sounds/effects/"

            try:
                # Waka-waka sound for eating pellets
                self.wakawaka_sound = pygame.mixer.Sound(sound_path + "wakawaka.wav")
                self.wakawaka_sound.set_volume(0.05)  # Drastisch reduziert auf 5%
                print("Waka-waka sound loaded!")
            except:
                print("Could not load wakawaka.wav")

            try:
                # Ghost eating sound
                self.eat_ghost_sound = pygame.mixer.Sound(sound_path + "eat_ghost.wav")
                self.eat_ghost_sound.set_volume(0.08)  # Reduziert auf 8%
                print("Eat ghost sound loaded!")
            except:
                print("Could not load eat_ghost.wav")

            try:
                # Death sound effect
                self.death_sound = pygame.mixer.Sound(sound_path + "death.wav")
                self.death_sound.set_volume(0.1)  # Reduziert auf 10%
                print("Death sound loaded!")
                self.sound_loaded = True
            except:
                print("Could not load death.wav")

        except Exception as e:
            print(f"Sound system error: {e}")
            self.sound_loaded = False

    def setup_music(self):
        """Initialize and start background music"""
        self.music_manager.load_background_music()
        self.music_manager.play_background_music()

    def play_wakawaka_sound(self):
        """Play waka-waka sound when eating pellets"""
        if self.sound_enabled and self.sound_loaded and self.wakawaka_sound:
            current_time = pygame.time.get_ticks()
            # Only play if enough time has passed since last sound
            if current_time - self.wakawaka_timer > self.wakawaka_interval:
                self.wakawaka_sound.play()
                self.wakawaka_timer = current_time

    def stop_wakawaka_sound(self):
        """Stop waka-waka sound playback"""
        if self.wakawaka_channel and self.wakawaka_channel.get_busy():
            self.wakawaka_channel.stop()

    def play_eat_ghost_sound(self):
        """Play sound effect when eating a ghost"""
        if self.sound_enabled and self.sound_loaded and self.eat_ghost_sound:
            self.eat_ghost_sound.play()

    def play_death_sound(self):
        """Play death sound effect when Pac-Man dies"""
        if self.sound_enabled and self.sound_loaded and self.death_sound:
            self.death_sound.play()

    def handle_event(self, event):
        """
        Handle all input events based on current game state
        Returns False if game should quit, True otherwise
        """
        if self.state == MENU:
            # Forward events to menu system
            menu_result = self.menu.handle_event(event)
            if menu_result == 'start_game':
                self.start_game()
                return True
            elif menu_result == 'quit':
                return False

            # Keyboard fallback for menu
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.start_game()
                elif event.key == pygame.K_q:
                    return False

        elif self.state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = PAUSED
                    # Pause music when game is paused
                    self.music_manager.pause_background_music()
                # Music controls
                elif event.key == pygame.K_m:
                    self.music_manager.toggle_music()
                elif event.key == pygame.K_MINUS:
                    # Decrease volume
                    current_vol = self.music_manager.music_volume
                    self.music_manager.set_volume(current_vol - 0.1)
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    # Increase volume
                    current_vol = self.music_manager.music_volume
                    self.music_manager.set_volume(current_vol + 0.1)
                # Movement controls - WASD or arrow keys
                elif event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.pacman.set_direction(UP)
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.pacman.set_direction(DOWN)
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.pacman.set_direction(LEFT)
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.pacman.set_direction(RIGHT)

        elif self.state == PAUSED:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = PLAYING
                    # Resume music when unpausing
                    self.music_manager.unpause_background_music()
                elif event.key == pygame.K_q:
                    self.state = MENU
                    # Stop game music and restart menu music
                    self.music_manager.stop_background_music()
                    # Reset menu to initial state
                    self.menu.menu_system.current_state = self.menu.menu_system.MENU
                    self.menu.menu_system.darkness_overlay = 0
                    self.menu.menu_system.start_menu_music()

        elif self.state == GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_q:
                    self.state = MENU
                    self.music_manager.stop_background_music()
                    # Reset menu to initial state
                    self.menu.menu_system.current_state = self.menu.menu_system.MENU
                    self.menu.menu_system.darkness_overlay = 0
                    # Restart menu music
                    self.menu.menu_system.start_menu_music()

        elif self.state == VICTORY:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.restart_game()
                elif event.key == pygame.K_q:
                    self.state = MENU
                    self.music_manager.stop_background_music()
                    # Reset menu to initial state
                    self.menu.menu_system.current_state = self.menu.menu_system.MENU
                    self.menu.menu_system.darkness_overlay = 0
                    # Restart menu music
                    self.menu.menu_system.start_menu_music()

        return True

    def start_game(self):
        """Initialize a new game with fresh state"""
        self.state = PLAYING
        self.score = 0
        self.lives = 3

        # Reset Pac-Man to starting position (top-left corner)
        self.pacman.reset(1, 1)

        # Initialize Pac-Man with navigation nodes
        self.pacman.initialize_nodes(self.maze.node_map)

        # Reset all pellets
        self.pellet_manager.reset()

        # Reset ghosts to their starting positions
        ghost_start_x = self.maze.width // 2
        ghost_start_y = self.maze.height // 2
        for ghost in self.ghosts:
            ghost.reset(ghost_start_x, ghost_start_y)

        # Start background music
        self.setup_music()

    def restart_game(self):
        """Restart the game with fresh state"""
        self.start_game()

    def update(self):
        """
        Main game logic update
        Called every frame to update game state
        """
        # Check for menu state changes
        if self.state == MENU:
            menu_result = self.menu.menu_system.update()
            if menu_result == 'start_game':
                self.start_game()

        if self.state == PLAYING:
            # Update Pac-Man movement and animation
            self.pacman.update(self.maze)

            # Update all ghosts with AI
            for ghost in self.ghosts:
                ghost.update(self.maze, self.pacman, self.ghosts)

            # Update pellet animations
            self.pellet_manager.update()

            # Check pellet collection
            collected_points = self.pellet_manager.check_collection(self.pacman)
            if collected_points != 0:
                if collected_points < 0:
                    if collected_points < -1000:
                        # Speed pellet eaten (signal: < -1000)
                        actual_points = abs(collected_points + 1000)
                        self.score += actual_points
                        self.pacman.activate_speed_boost()
                    else:
                        # Power pellet eaten (signal: negative)
                        self.score += abs(collected_points)
                        # Make all ghosts frightened
                        for ghost in self.ghosts:
                            ghost.set_frightened()
                else:
                    # Normal pellet eaten
                    self.score += collected_points

                # Play eating sound
                self.play_wakawaka_sound()
                self.pacman.set_eating(True)
            else:
                # Not eating
                self.pacman.set_eating(False)

            # Check ghost collisions
            for ghost in self.ghosts:
                if self.pacman.collides_with(ghost):
                    if ghost.mode == FRIGHTENED:
                        # Eat the ghost
                        ghost.mode = EATEN
                        self.score += 200
                        self.play_eat_ghost_sound()
                    elif ghost.mode != EATEN:  # Eaten ghosts can't kill
                        # Pac-Man dies
                        self.lives -= 1

                        # Play death sound
                        self.play_death_sound()

                        # Pause for death animation
                        pygame.time.wait(1500)  # 1.5 second pause

                        if self.lives <= 0:
                            self.state = GAME_OVER
                            self.music_manager.stop_background_music()
                        else:
                            # Reset level - positions reset but pellets remain eaten
                            self.reset_after_death()

            # Check victory condition
            if self.pellet_manager.all_collected():
                self.state = VICTORY
                self.music_manager.stop_background_music()

    def draw(self):
        """
        Main rendering function
        Draws all game elements based on current state
        """
        self.screen.fill(BLACK)

        if self.state == MENU:
            self.menu.draw(self.screen)

        elif self.state in [PLAYING, PAUSED]:
            # Draw game elements
            self.maze.draw(self.screen)

            # Debug: Show nodes (set to True for debugging pathfinding)
            self.maze.draw_nodes(self.screen, show_nodes=False)

            # Draw all pellets
            self.pellet_manager.draw(self.screen)

            # Draw Pac-Man
            self.pacman.draw(self.screen)

            # Draw all ghosts
            for ghost in self.ghosts:
                ghost.draw(self.screen)

            # Draw UI elements
            self.draw_ui()

            if self.state == PAUSED:
                self.draw_pause_screen()

        elif self.state == GAME_OVER:
            self.draw_game_over()

        elif self.state == VICTORY:
            self.draw_victory()

    def draw_ui(self):
        """
        Draw the user interface elements
        Includes score, lives, legend, and music status
        """
        # UI area starts after the game field
        ui_y_start = GAME_AREA_HEIGHT + 5

        # Background for UI area
        ui_rect = pygame.Rect(0, GAME_AREA_HEIGHT, SCREEN_WIDTH, 60)
        pygame.draw.rect(self.screen, (10, 10, 30), ui_rect)
        pygame.draw.rect(self.screen, (50, 50, 100), ui_rect, 3)

        # Score - Centered at top
        score_font = pygame.font.Font(None, 32)
        score_text = score_font.render(f"SCORE: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(centerx=SCREEN_WIDTH//2, y=ui_y_start + 5)
        self.screen.blit(score_text, score_rect)

        # Lives - Top right as hearts or Pac-Man symbols
        lives_x_start = SCREEN_WIDTH - 100
        lives_y = ui_y_start + 15

        # Draw heart symbols for lives
        for i in range(self.lives):
            heart_x = lives_x_start + (i * 25)
            # Simple heart shape using circles and triangle
            pygame.draw.circle(self.screen, RED, (heart_x - 4, lives_y), 5)
            pygame.draw.circle(self.screen, RED, (heart_x + 4, lives_y), 5)
            pygame.draw.polygon(self.screen, RED, [
                (heart_x - 8, lives_y + 2),
                (heart_x + 8, lives_y + 2),
                (heart_x, lives_y + 12)
            ])

        # Legend - Bottom area
        legend_font = pygame.font.Font(None, 20)
        legend_y = ui_y_start + 35

        # Power pellet legend (pink/white circle)
        pygame.draw.circle(self.screen, (255, 184, 255), (20, legend_y + 5), 6)
        pygame.draw.circle(self.screen, (255, 220, 255), (20, legend_y + 5), 7, 1)
        power_text = legend_font.render("= Power Up", True, WHITE)
        self.screen.blit(power_text, (30, legend_y))

        # Speed pellet legend (cyan circle)
        pygame.draw.circle(self.screen, CYAN, (150, legend_y + 5), 6)
        # Speed effect rings
        pygame.draw.circle(self.screen, (150, 255, 255), (150, legend_y + 5), 8, 1)
        speed_text = legend_font.render("= Speed Boost", True, WHITE)
        self.screen.blit(speed_text, (160, legend_y))

        # Dot legend
        pygame.draw.circle(self.screen, YELLOW, (300, legend_y + 5), 2)
        dot_text = legend_font.render("= 10 pts", True, WHITE)
        self.screen.blit(dot_text, (310, legend_y))

        # Music status - Bottom right corner
        music_font = pygame.font.Font(None, 18)
        music_status = "ON" if self.music_manager.music_playing else "OFF"
        music_color = GREEN if self.music_manager.music_playing else RED
        music_text = music_font.render(f"Press M for Mute", True, music_color)
        music_rect = music_text.get_rect(right=SCREEN_WIDTH - 10, bottom=SCREEN_HEIGHT - 5)
        self.screen.blit(music_text, music_rect)

    def draw_pause_screen(self):
        """Draw pause overlay with instructions"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        pause_text = self.font.render("PAUSED", True, WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(pause_text, text_rect)

        resume_text = self.font.render("Press ESC to resume", True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        self.screen.blit(resume_text, resume_rect)

    def draw_game_over(self):
        """Draw game over screen with menu background"""
        # Draw menu in background
        self.menu.draw(self.screen)

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Game over text
        game_over_text = self.font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
        self.screen.blit(game_over_text, text_rect)

        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(score_text, score_rect)

        restart_text = self.font.render("Press SPACE or Q for menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        self.screen.blit(restart_text, restart_rect)

    def draw_victory(self):
        """Draw victory screen with menu background"""
        # Draw menu in background
        self.menu.draw(self.screen)

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        victory_text = self.font.render("VICTORY!", True, GREEN)
        text_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
        self.screen.blit(victory_text, text_rect)

        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(score_text, score_rect)

        restart_text = self.font.render("Press SPACE to play again or Q for menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        self.screen.blit(restart_text, restart_rect)

    def reset_after_death(self):
        """
        Reset positions after Pac-Man dies
        Important: Pellets remain eaten to maintain game progress
        """
        # Reset Pac-Man to starting position
        self.pacman.reset(1, 1)
        self.pacman.initialize_nodes(self.maze.node_map)

        # Reset all ghosts to their starting positions
        ghost_start_x = self.maze.width // 2
        ghost_start_y = self.maze.height // 2
        for ghost in self.ghosts:
            ghost.reset(ghost_start_x, ghost_start_y)
            # Reset ghost modes
            ghost.mode = SCATTER
            ghost.mode_timer = 0
            ghost.scatter_timer = 0

        # IMPORTANT: Pellets remain eaten - no pellet_manager.reset() here!

    def cleanup(self):
        """Clean up resources when closing the game"""
        self.music_manager.stop_background_music()