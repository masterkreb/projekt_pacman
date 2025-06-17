"""
Menu System
Handles start menu, pause menu, and other UI screens
"""

import pygame
from .constants import *

class Menu:
    def __init__(self):
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        # Animation
        self.animation_frame = 0
        self.animation_speed = 0.05
    
    def update(self):
        """Update menu animations"""
        self.animation_frame += self.animation_speed
        if self.animation_frame >= 2:
            self.animation_frame = 0
    
    def draw(self, screen):
        """Draw the main menu"""
        screen.fill(BLACK)
        
        # Title
        title_text = self.font_large.render("PAC-MAN", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        screen.blit(title_text, title_rect)
        
        # Animated subtitle
        glow_intensity = int(128 + 127 * abs(self.animation_frame - 1))
        subtitle_color = (255, 255, glow_intensity)
        
        # Instructions
        start_text = self.font_medium.render("Press SPACE to Start", True, subtitle_color)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(start_text, start_rect)
        
        quit_text = self.font_small.render("Press Q to Quit", True, WHITE)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
        screen.blit(quit_text, quit_rect)
        
        # Controls
        controls_y = SCREEN_HEIGHT//2 + 120
        controls_text = self.font_small.render("Use Arrow Keys to Move", True, WHITE)
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH//2, controls_y))
        screen.blit(controls_text, controls_rect)
        
        # Draw some decorative elements
        self.draw_decorations(screen)
    
    def draw_decorations(self, screen):
        """Draw decorative elements for the menu"""
        # Draw some dots around the title
        for i in range(8):
            angle = i * 45 + self.animation_frame * 20
            x = SCREEN_WIDTH//2 + 200 * pygame.math.Vector2(1, 0).rotate(angle).x
            y = SCREEN_HEIGHT//2 - 100 + 200 * pygame.math.Vector2(1, 0).rotate(angle).y
            
            if 0 <= x <= SCREEN_WIDTH and 0 <= y <= SCREEN_HEIGHT:
                pygame.draw.circle(screen, YELLOW, (int(x), int(y)), 4)
        
        # Draw border
        border_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        pygame.draw.rect(screen, BLUE, border_rect, 3)
    
    def draw_pause_menu(self, screen):
        """Draw pause menu overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.font_large.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(pause_text, pause_rect)
        
        # Instructions
        resume_text = self.font_medium.render("Press ESC to Resume", True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        screen.blit(resume_text, resume_rect)
        
        quit_text = self.font_small.render("Press Q to Quit to Menu", True, WHITE)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
        screen.blit(quit_text, quit_rect)
    
    def draw_game_over(self, screen, score):
        """Draw game over screen"""
        screen.fill(BLACK)
        
        # Game Over text
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
        screen.blit(game_over_text, game_over_rect)
        
        # Score
        score_text = self.font_medium.render(f"Final Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
        screen.blit(score_text, score_rect)
        
        # Instructions
        restart_text = self.font_small.render("Press SPACE to Play Again", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        screen.blit(restart_text, restart_rect)
        
        menu_text = self.font_small.render("Press Q for Main Menu", True, WHITE)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
        screen.blit(menu_text, menu_rect)
    
    def draw_victory(self, screen, score):
        """Draw victory screen"""
        screen.fill(BLACK)
        
        # Victory text with animation
        glow_intensity = int(128 + 127 * abs(self.animation_frame - 1))
        victory_color = (0, 255, glow_intensity)
        
        victory_text = self.font_large.render("VICTORY!", True, victory_color)
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
        screen.blit(victory_text, victory_rect)
        
        # Congratulations
        congrats_text = self.font_medium.render("You ate all the pellets!", True, YELLOW)
        congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
        screen.blit(congrats_text, congrats_rect)
        
        # Score
        score_text = self.font_medium.render(f"Final Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        screen.blit(score_text, score_rect)
        
        # Instructions
        restart_text = self.font_small.render("Press SPACE to Play Again", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
        screen.blit(restart_text, restart_rect)
        
        menu_text = self.font_small.render("Press Q for Main Menu", True, WHITE)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 120))
        screen.blit(menu_text, menu_rect)
        
        # Draw celebration effects
        self.draw_celebration_effects(screen)
    
    def draw_celebration_effects(self, screen):
        """Draw celebration particle effects"""
        import random
        
        # Draw some floating particles
        for i in range(20):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            color = random.choice([YELLOW, WHITE, GREEN, CYAN])
            size = random.randint(2, 6)
            
            # Make particles move based on animation frame
            offset_x = int(self.animation_frame * 50) % SCREEN_WIDTH
            offset_y = int(self.animation_frame * 30) % SCREEN_HEIGHT
            
            final_x = (x + offset_x) % SCREEN_WIDTH
            final_y = (y + offset_y) % SCREEN_HEIGHT
            
            pygame.draw.circle(screen, color, (final_x, final_y), size)
