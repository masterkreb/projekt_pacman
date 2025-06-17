"""
Main Game Class
Handles game logic, state management, and coordination between components
"""

import pygame
from src.constants import *
from src.player import Pacman
from src.ghost import Ghost
from src.maze import Maze
from src.pellets import PelletManager
from src.menu import Menu

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.state = MENU
        self.score = 0
        self.lives = 3
        
        # Sound-System aus dem ursprünglichen Code
        self.sound_enabled = True
        self.sound_loaded = False
        self.wakawaka_sound = None
        self.wakawaka_channel = None
        self.is_moving = False
        self.last_moving_state = False
        
        # Lade Sounds
        self.load_sounds()
          # Initialize game components
        self.maze = Maze()
        self.pacman = Pacman(11, 15)  # Bessere Startposition im Labyrinth
        self.pellet_manager = PelletManager(self.maze)
        self.menu = Menu()
        
        # Initialize ghosts - Geister-Startbereich
        ghost_start_x = self.maze.width // 2
        ghost_start_y = self.maze.height // 2
        self.ghosts = [
            Ghost(ghost_start_x, ghost_start_y, RED, "blinky"),
            Ghost(ghost_start_x, ghost_start_y, PINK, "pinky"),
            Ghost(ghost_start_x, ghost_start_y, CYAN, "inky"),
            Ghost(ghost_start_x, ghost_start_y, ORANGE, "clyde")
        ]
        
        # Font for UI
        self.font = pygame.font.Font(None, 36)
        
    def load_sounds(self):
        """Lade Sound-Dateien - aus dem ursprünglichen Code"""
        try:
            pygame.mixer.init()
            # Versuche verschiedene Pfade
            sound_paths = [
                "../feature/sounds/wakawaka.wav",
                "feature/sounds/wakawaka.wav",
                "assets/sounds/effects/wakawaka.wav"
            ]
            
            for path in sound_paths:
                try:
                    self.wakawaka_sound = pygame.mixer.Sound(path)
                    self.wakawaka_sound.set_volume(0.2)  # 20% Lautstärke
                    self.sound_loaded = True
                    print(f"WakaWaka sound loaded successfully from {path} at 20% volume!")
                    break
                except (pygame.error, FileNotFoundError):
                    continue
                    
            if not self.sound_loaded:
                print("Could not load wakawaka.wav from any location")
                print("Sound will be disabled")
                
        except Exception as e:
            print(f"Sound system error: {e}")
            self.sound_loaded = False
    
    def play_wakawaka_sound(self):
        """Spiele WakaWaka Sound ab wenn Pac-Man sich bewegt"""
        if self.sound_enabled and self.sound_loaded and self.wakawaka_sound:
            if not self.wakawaka_channel or not self.wakawaka_channel.get_busy():
                self.wakawaka_channel = self.wakawaka_sound.play(-1)  # Loop indefinitely
    
    def stop_wakawaka_sound(self):
        """Stoppe WakaWaka Sound"""
        if self.wakawaka_channel and self.wakawaka_channel.get_busy():
            self.wakawaka_channel.stop()
    
    def handle_event(self, event):
        """Handle input events"""
        if self.state == MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.start_game()
                elif event.key == pygame.K_q:
                    return False
        
        elif self.state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = PAUSED
                elif event.key == pygame.K_UP:
                    self.pacman.set_direction(UP)
                elif event.key == pygame.K_DOWN:
                    self.pacman.set_direction(DOWN)
                elif event.key == pygame.K_LEFT:
                    self.pacman.set_direction(LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.pacman.set_direction(RIGHT)
        
        elif self.state == PAUSED:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = PLAYING
                elif event.key == pygame.K_q:
                    self.state = MENU
        
        elif self.state == GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.restart_game()
                elif event.key == pygame.K_q:
                    self.state = MENU    
    def start_game(self):
        """Start a new game"""
        self.state = PLAYING
        self.score = 0
        self.lives = 3
        self.pacman.reset(11, 15)  # Gleiche Startposition
        self.pellet_manager.reset()
        ghost_start_x = self.maze.width // 2
        ghost_start_y = self.maze.height // 2
        for ghost in self.ghosts:
            ghost.reset(ghost_start_x, ghost_start_y)
    
    def restart_game(self):
        """Restart the current game"""
        self.start_game()    
    def update(self):
        """Update game logic"""
        if self.state == PLAYING:
            # Update Pac-Man
            self.pacman.update(self.maze)
            
            # Sound-Steuerung aus dem ursprünglichen Code
            self.is_moving = (self.pacman.velocity_x != 0 or self.pacman.velocity_y != 0)
            
            if self.is_moving and not self.last_moving_state:
                # Pac-Man hat angefangen sich zu bewegen
                self.play_wakawaka_sound()
            elif not self.is_moving and self.last_moving_state:
                # Pac-Man hat aufgehört sich zu bewegen
                self.stop_wakawaka_sound()
            
            self.last_moving_state = self.is_moving
            
            # Update ghosts
            for ghost in self.ghosts:
                ghost.update(self.maze, self.pacman)
            
            # Check pellet collection
            collected_pellets = self.pellet_manager.check_collection(self.pacman)
            self.score += collected_pellets
            
            # Check ghost collisions
            for ghost in self.ghosts:
                if self.pacman.collides_with(ghost):
                    if ghost.mode == FRIGHTENED:
                        ghost.mode = EATEN
                        self.score += 200
                    else:
                        self.lives -= 1
                        self.stop_wakawaka_sound()  # Stoppe Sound bei Kollision
                        if self.lives <= 0:
                            self.state = GAME_OVER
                        else:
                            self.pacman.reset(11, 15)
            
            # Check victory condition
            if self.pellet_manager.all_collected():
                self.state = VICTORY
                self.stop_wakawaka_sound()
    
    def draw(self):
        """Draw everything to the screen"""
        self.screen.fill(BLACK)
        
        if self.state == MENU:
            self.menu.draw(self.screen)
        
        elif self.state in [PLAYING, PAUSED]:
            # Draw maze
            self.maze.draw(self.screen)
            
            # Draw pellets
            self.pellet_manager.draw(self.screen)
            
            # Draw Pac-Man
            self.pacman.draw(self.screen)
            
            # Draw ghosts
            for ghost in self.ghosts:
                ghost.draw(self.screen)
            
            # Draw UI
            self.draw_ui()
            
            if self.state == PAUSED:
                self.draw_pause_screen()
        
        elif self.state == GAME_OVER:
            self.draw_game_over()
        
        elif self.state == VICTORY:
            self.draw_victory()
    
    def draw_ui(self):
        """Draw game UI (score, lives, etc.)"""
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, SCREEN_HEIGHT - 50))
        
        # Lives
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, SCREEN_HEIGHT - 25))
    
    def draw_pause_screen(self):
        """Draw pause overlay"""
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
        """Draw game over screen"""
        self.screen.fill(BLACK)
        
        game_over_text = self.font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
        self.screen.blit(game_over_text, text_rect)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.font.render("Press SPACE to restart or Q for menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_victory(self):
        """Draw victory screen"""
        self.screen.fill(BLACK)
        
        victory_text = self.font.render("VICTORY!", True, GREEN)
        text_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
        self.screen.blit(victory_text, text_rect)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.font.render("Press SPACE to play again or Q for menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        self.screen.blit(restart_text, restart_rect)
