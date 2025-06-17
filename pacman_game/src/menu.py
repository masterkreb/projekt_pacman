#!/usr/bin/env python3
"""
Menu System for Pac-Man Game
Includes main menu, credits, and horror transition effects
"""

import pygame
import pygame_gui
import os
from typing import Optional, Dict, List, Tuple


class MenuSystem:
    """Main menu system with credits and horror effects"""

    # Game States
    MENU = 0
    HORROR_EFFECT = 1
    GAMEPLAY = 2

    def __init__(self, screen_width: int = 540, screen_height: int = 720):
        """Initialize the menu system"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_state = self.MENU

        # Initialize pygame components
        self._init_display()
        self._load_assets()
        self._init_ui_elements()

        # Game state variables
        self.start_effect_timer = 0
        self.start_effect_duration = 5000  # 5 seconds
        self.darkness_overlay = 0

        # Player variables (for gameplay demo)
        self.player_x = screen_width // 2
        self.player_y = screen_height // 2
        self.player_size = 10
        self.player_speed = 5

        # Sound control
        self.last_move_time = 0
        self.move_sound_delay = 200
        self.last_hovered_button = None

        # Button hover states
        self.start_hovered = False
        self.exit_hovered = False

    def _init_display(self):
        """Initialize display and UI manager"""
        self.manager = pygame_gui.UIManager((self.screen_width, self.screen_height))

    def _load_assets(self):
        """Load all assets (images, sounds, fonts)"""
        self._load_background()
        self._load_sounds()
        self._load_fonts()

    def _load_background(self):
        """Load and prepare background image"""
        try:
            original_image = pygame.image.load('../assets/images/ui/background.png')
            img_width, img_height = original_image.get_size()
            target_ratio = self.screen_width / self.screen_height
            current_ratio = img_width / img_height

            if current_ratio > target_ratio:
                # Image is too wide - crop sides
                new_width = int(img_height * target_ratio)
                crop_x = (img_width - new_width) // 2
                cropped_image = original_image.subsurface((crop_x, 0, new_width, img_height))
            else:
                # Image is too tall - crop top and bottom
                new_height = int(img_width / target_ratio)
                crop_y = (img_height - new_height) // 2
                cropped_image = original_image.subsurface((0, crop_y, img_width, new_height))

            self.background_image = pygame.transform.scale(cropped_image, (self.screen_width, self.screen_height))
            self.has_background_image = True
            print("Background image loaded successfully!")
        except Exception as e:
            # Fallback: dark purple background
            self.background_image = pygame.Surface((self.screen_width, self.screen_height))
            self.background_image.fill(pygame.Color('#1a0d2e'))
            self.has_background_image = False
            print(f"Background image not found, using fallback: {e}")

    def _load_sounds(self):
        """Load all sound effects and music"""
        self.sounds = {}

        # Background music
        try:
            pygame.mixer.music.load('../assets/sounds/effects/menu_music.mp3')
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play(-1)
            print("Background music loaded!")
        except Exception as e:
            print(f"Background music not found: {e}")

        # Sound effects
        sound_files = {
            'horror_start': ('../assets/sounds/effects/horror_start.wav', 0.5),
            'menu_hover': ('menu_hover.wav', 0.3),
            'menu_click': ('menu_click.wav', 0.4),
            'pacman_move': ('pacman_move.wav', 0.2)
        }

        for sound_name, (filename, volume) in sound_files.items():
            try:
                sound = pygame.mixer.Sound(filename)
                sound.set_volume(volume)
                self.sounds[sound_name] = sound
                print(f"{sound_name} sound loaded!")
            except Exception as e:
                self.sounds[sound_name] = None
                print(f"{sound_name} sound not found: {e}")

    def _load_fonts(self):
        """Load fonts for different UI elements"""
        try:
            self.title_font = pygame.font.Font(None, 80)
            self.subtitle_font = pygame.font.Font(None, 28)
            self.button_font = pygame.font.Font(None, 32)
        except Exception:
            # Fallback to default font
            default_font = pygame.font.get_default_font()
            self.title_font = default_font
            self.subtitle_font = default_font
            self.button_font = default_font

    def _init_ui_elements(self):
        """Initialize UI elements and button positions"""
        # Title surfaces
        self.title_surface = self.title_font.render("PACMAN", True, pygame.Color('#FF0000'))
        self.subtitle_surface = self.subtitle_font.render("The Return of the Blue Ghost", True, pygame.Color('#00FFFF'))

        # Button rectangles
        center_x = self.screen_width // 2
        self.start_button_rect = pygame.Rect(center_x - 50, 525, 100, 40)
        self.exit_button_rect = pygame.Rect(center_x - 50, 575, 100, 40)

    def _init_team_data(self):
        """Initialize team member data and load their images"""
        self.team_members = [
            {"name": "Imad", "role": "Sound Designer & Creative Producer", "image": "imad.png"},
            {"name": "Mathias", "role": "Executive Producer", "image": "mathias.png"},
            {"name": "Ricardo", "role": "Co Executive Producer", "image": "ricardo.png"},
            {"name": "Leon", "role": "Visual Effects Producer", "image": "leon.png"},
            {"name": "Denis", "role": "Senior Producer", "image": "denis.png"},
            {"name": "Erisk", "role": "Digital Producer", "image": "erisk.png"}
        ]

        # Load team member images
        self.team_images = {}
        for member in self.team_members:
            try:
                img = pygame.image.load(member["image"])
                img = pygame.transform.scale(img, (80, 80))
                self.team_images[member["name"]] = img
                print(f"Image for {member['name']} loaded successfully!")
            except Exception as e:
                # Create placeholder image
                placeholder = pygame.Surface((80, 80))
                placeholder.fill(pygame.Color('#333333'))
                letter_surface = self.credits_name_font.render(member["name"][0], True, pygame.Color('#FFFFFF'))
                letter_rect = letter_surface.get_rect(center=(40, 40))
                placeholder.blit(letter_surface, letter_rect)
                self.team_images[member["name"]] = placeholder
                print(f"Placeholder created for {member['name']}: {e}")

    def handle_event(self, event) -> Optional[str]:
        """
        Handle pygame events and return game state changes
        Returns: 'start_game', 'quit', or None
        """
        current_time = pygame.time.get_ticks()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if self.current_state == self.MENU:
                if self.start_button_rect.collidepoint(mouse_pos):
                    self._play_sound('menu_click')
                    self._play_sound('horror_start')
                    self.current_state = self.HORROR_EFFECT
                    self.start_effect_timer = current_time
                    pygame.mixer.music.stop()
                    print('Starting horror effect...')

                elif self.exit_button_rect.collidepoint(mouse_pos):
                    self._play_sound('menu_click')
                    return 'quit'

        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_hover(pygame.mouse.get_pos())

        return None

    def _handle_mouse_hover(self, mouse_pos: Tuple[int, int]):
        """Handle mouse hover effects with sound"""
        if self.current_state == self.MENU:
            new_start_hovered = self.start_button_rect.collidepoint(mouse_pos)
            new_exit_hovered = self.exit_button_rect.collidepoint(mouse_pos)

            current_hovered = None
            if new_start_hovered:
                current_hovered = "start"
            elif new_exit_hovered:
                current_hovered = "exit"

            if current_hovered != self.last_hovered_button and current_hovered is not None:
                self._play_sound('menu_hover')
                self.last_hovered_button = current_hovered
            elif current_hovered is None:
                self.last_hovered_button = None

            self.start_hovered = new_start_hovered
            self.exit_hovered = new_exit_hovered

    def _play_sound(self, sound_name: str):
        """Play a sound effect if available"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()

    def update(self) -> Optional[str]:
        """
        Update menu system state
        Returns: 'start_game' when ready to start gameplay, or None
        """
        current_time = pygame.time.get_ticks()

        if self.current_state == self.HORROR_EFFECT:
            elapsed_time = current_time - self.start_effect_timer

            if elapsed_time < self.start_effect_duration:
                progress = elapsed_time / self.start_effect_duration
                self.darkness_overlay = int(255 * progress)
            else:
                self.current_state = self.GAMEPLAY
                self.darkness_overlay = 0
                print("🎮 Horror effect complete - ready for gameplay!")
                return 'start_game'

        elif self.current_state == self.GAMEPLAY:
            # Handle basic movement for demo
            keys = pygame.key.get_pressed()
            moved = False

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.player_y -= self.player_speed
                moved = True
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.player_y += self.player_speed
                moved = True
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.player_x -= self.player_speed
                moved = True
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.player_x += self.player_speed
                moved = True

            if moved and (current_time - self.last_move_time) > self.move_sound_delay:
                self._play_sound('pacman_move')
                self.last_move_time = current_time

            # Keep player on screen
            self.player_x = max(0, min(self.screen_width - self.player_size, self.player_x))
            self.player_y = max(0, min(self.screen_height - self.player_size, self.player_y))

        return None

    def draw(self, surface):
        """Draw the current menu state"""
        # Draw background
        surface.blit(self.background_image, (0, 0))

        if self.current_state == self.MENU:
            self._draw_main_menu(surface)
        elif self.current_state == self.GAMEPLAY:
            self._draw_gameplay(surface)
        elif self.current_state == self.HORROR_EFFECT:
            self._draw_horror_effect(surface)

    def _draw_main_menu(self, surface):
        """Draw the main menu"""
        # Title
        title_rect = self.title_surface.get_rect(center=(self.screen_width // 2, 100))
        surface.blit(self.title_surface, title_rect)

        # Subtitle
        subtitle_rect = self.subtitle_surface.get_rect(center=(self.screen_width // 2, 140))
        surface.blit(self.subtitle_surface, subtitle_rect)

        # Buttons with hover effects
        self._draw_button(surface, "START", self.start_button_rect, self.start_hovered, '#FFFF00')
        self._draw_button(surface, "EXIT", self.exit_button_rect, self.exit_hovered, '#FF4444')

    def _draw_button(self, surface, text: str, rect: pygame.Rect, hovered: bool, hover_color: str):
        """Draw a button with hover effect"""
        color = pygame.Color(hover_color) if hovered else pygame.Color('#FFFFFF')
        text_surface = self.button_font.render(text, True, color)
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)

    def _draw_gameplay(self, surface):
        """Draw gameplay demo (yellow square)"""
        pygame.draw.rect(surface, pygame.Color('#FFFF00'),
                         (int(self.player_x), int(self.player_y), self.player_size, self.player_size))

    def _draw_horror_effect(self, surface):
        """Draw horror transition effect"""
        if self.darkness_overlay > 0:
            dark_surface = pygame.Surface((self.screen_width, self.screen_height))
            dark_surface.fill((0, 0, 0))
            dark_surface.set_alpha(self.darkness_overlay)
            surface.blit(dark_surface, (0, 0))

    def get_current_state(self) -> int:
        """Get the current menu state"""
        return self.current_state

    def is_in_game(self) -> bool:
        """Check if currently in gameplay mode"""
        return self.current_state == self.GAMEPLAY


def run_menu_system():
    """Standalone function to run the menu system"""
    pygame.init()
    pygame.mixer.init()

    pygame.display.set_caption('Pacman by the Ghostbusters')
    screen = pygame.display.set_mode((540, 720))

    menu = MenuSystem()
    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            else:
                result = menu.handle_event(event)
                if result == 'quit':
                    is_running = False
                elif result == 'start_game':
                    print("Game would start here!")

        result = menu.update()
        if result == 'start_game':
            print("Transitioning to main game!")

        menu.draw(screen)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    run_menu_system()