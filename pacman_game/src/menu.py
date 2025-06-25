#!/usr/bin/env python3
"""
Menu System for Pac-Man Game
Includes main menu, credits, and horror transition effects
"""

import pygame
import pygame_gui
import os
import random
from typing import Optional, Dict, List, Tuple


class Menu:
    """Menu wrapper for compatibility with game.py"""

    def __init__(self, screen_width=540, screen_height=720):
        """Initialize the menu system"""
        from .constants import SCREEN_WIDTH, SCREEN_HEIGHT
        self.menu_system = MenuSystem(SCREEN_WIDTH, SCREEN_HEIGHT)

    def draw(self, surface):
        """Draw the menu"""
        self.menu_system.draw(surface)

    def handle_event(self, event):
        """Handle events and pass to menu system"""
        return self.menu_system.handle_event(event)


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

        # Master volume control (30% max) - MUST be before _load_assets()
        self.master_volume = 0.15  # Start at 15% (50% of 30% max)
        self.max_master_volume = 0.30  # Maximum 30% system volume
        self.volume_step = 0.05  # 5% steps

        # Initialize components
        self._init_display()
        self._load_assets()
        self._init_ui_elements()

        # Game state
        self.start_effect_timer = 0
        self.start_effect_duration = 5000  # 5 seconds
        self.darkness_overlay = 0
        self.skip_horror_effect = False

        # Player demo
        self.player_x = screen_width // 2
        self.player_y = screen_height // 2
        self.player_size = 10
        self.player_speed = 5

        # Sound control
        self.last_move_time = 0
        self.move_sound_delay = 200
        self.last_hovered_button = None

        # Button states
        self.start_hovered = False
        self.exit_hovered = False

        # Info popup
        self.show_info_popup = False
        self.info_popup_alpha = 0
        self.info_fade_speed = 15

        # Start menu music
        self.start_menu_music()

    def _init_display(self):
        """Initialize display and UI manager"""
        self.manager = pygame_gui.UIManager((self.screen_width, self.screen_height))

    def _load_assets(self):
        """Load all assets"""
        self._load_background()
        self._load_sounds()
        self._load_fonts()

    def _load_background(self):
        """Load and prepare background image"""
        try:
            possible_paths = [
                'assets/images/ui/background.png',
                '../assets/images/ui/background.png',
                'pacman_game/assets/images/ui/background.png'
            ]

            original_image = None
            for path in possible_paths:
                try:
                    print(f"Trying to load background from: {path}")
                    original_image = pygame.image.load(path)
                    print(f"Background loaded from: {path}")
                    break
                except (pygame.error, FileNotFoundError) as e:
                    print(f"Could not load from {path}: {e}")
                    continue

            if original_image is None:
                raise FileNotFoundError("Background not found")

            img_width, img_height = original_image.get_size()
            target_ratio = self.screen_width / self.screen_height
            current_ratio = img_width / img_height

            if current_ratio > target_ratio:
                # Crop sides
                new_width = int(img_height * target_ratio)
                crop_x = (img_width - new_width) // 2
                cropped_image = original_image.subsurface((crop_x, 0, new_width, img_height))
            else:
                # Crop top/bottom
                new_height = int(img_width / target_ratio)
                crop_y = (img_height - new_height) // 2
                cropped_image = original_image.subsurface((0, crop_y, img_width, new_height))

            self.background_image = pygame.transform.scale(cropped_image, (self.screen_width, self.screen_height))
            self.has_background_image = True
            print("Background image loaded successfully!")
        except Exception as e:
            # Create fallback background
            self.background_image = pygame.Surface((self.screen_width, self.screen_height))

            # Gradient background
            for y in range(self.screen_height):
                color_value = max(0, int(40 - (y / self.screen_height * 40)))
                gradient_color = (0, color_value, color_value * 2)
                pygame.draw.line(self.background_image, gradient_color, (0, y), (self.screen_width, y))

            # Add stars
            for _ in range(100):
                star_x = random.randint(0, self.screen_width)
                star_y = random.randint(0, self.screen_height)
                star_size = random.randint(1, 3)
                brightness = random.randint(150, 255)
                pygame.draw.circle(self.background_image, (brightness, brightness, brightness),
                                   (star_x, star_y), star_size)

            self.has_background_image = False
            print(f"Using generated background: {e}")

    def start_menu_music(self):
        """Start menu background music"""
        try:
            menu_music_path = 'assets/sounds/effects/menu_music.mp3'
            if os.path.exists(menu_music_path):
                pygame.mixer.music.load(menu_music_path)
                pygame.mixer.music.set_volume(self.master_volume)
                pygame.mixer.music.play(-1)
                print(f"Menu music started at {self.master_volume * 100:.0f}% volume!")
            else:
                print(f"Menu music not found at: {menu_music_path}")
        except Exception as e:
            print(f"Could not load menu music: {e}")

    def stop_menu_music(self):
        """Stop menu music"""
        pygame.mixer.music.stop()

    def _load_sounds(self):
        """Load all sound effects"""
        self.sounds = {}
        self.base_sound_volumes = {}  # Store base volumes for later updates

        # Only load the sounds that actually exist
        sound_files = {
            'horror_start': ('assets/sounds/effects/horror_start.wav', 0.2),  # Increased volume
            'pacman_move': ('assets/sounds/effects/pacman_move.wav', 0.04)
        }

        for sound_name, (filename, base_volume) in sound_files.items():
            try:
                sound = pygame.mixer.Sound(filename)
                # Get sound info for debugging
                sound_length = sound.get_length()
                print(f"Loading {sound_name}: length = {sound_length:.2f} seconds")

                # Store base volume for later updates
                self.base_sound_volumes[sound_name] = base_volume
                # Apply master volume multiplier
                actual_volume = base_volume * (self.master_volume / 0.15)  # Scale based on master
                sound.set_volume(min(actual_volume, 1.0))
                self.sounds[sound_name] = sound
                print(f"{sound_name} sound loaded successfully at {actual_volume * 100:.0f}% volume!")
            except Exception as e:
                self.sounds[sound_name] = None
                print(f"ERROR loading {sound_name}: {e}")

    def _load_fonts(self):
        """Load fonts for UI elements"""
        try:
            self.title_font = pygame.font.Font(None, 80)
            self.subtitle_font = pygame.font.Font(None, 28)
            self.button_font = pygame.font.Font(None, 32)
            self.hardmode_font = pygame.font.Font(None, 36)
            self.info_font = pygame.font.Font(None, 24)
            self.info_title_font = pygame.font.Font(None, 36)
            self.info_instruction_font = pygame.font.Font(None, 20)
        except Exception:
            default_font = pygame.font.get_default_font()
            self.title_font = default_font
            self.subtitle_font = default_font
            self.button_font = default_font
            self.hardmode_font = default_font

    def _init_ui_elements(self):
        """Initialize UI elements and button positions"""
        self.title_surface = self.title_font.render("PACMAN", True, pygame.Color('#FF0000'))
        self.subtitle_surface = self.subtitle_font.render("The Return of the Blue Ghost", True, pygame.Color('#00FFFF'))
        self.hardmode_surface = self.hardmode_font.render("HARDMODE", True, pygame.Color('#FF0000'))
        self.info_instruction_surface = self.info_instruction_font.render("Press I for Info", True,
                                                                          pygame.Color('#FFFF00'))

        center_x = self.screen_width // 2
        self.start_button_rect = pygame.Rect(center_x - 50, 525, 100, 40)
        self.exit_button_rect = pygame.Rect(center_x - 50, 575, 100, 40)

    def handle_event(self, event) -> Optional[str]:
        """Handle pygame events"""
        current_time = pygame.time.get_ticks()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if self.current_state == self.MENU:
                if self.start_button_rect.collidepoint(mouse_pos):
                    # Don't play menu_click since it doesn't exist

                    # Stop menu music BEFORE playing horror sound
                    self.stop_menu_music()

                    # Small delay to ensure music is stopped
                    pygame.time.wait(100)

                    # Start horror effect sound
                    self._play_sound('horror_start')
                    self.current_state = self.HORROR_EFFECT
                    self.start_effect_timer = current_time
                    print('Starting horror effect with sound...')

                elif self.exit_button_rect.collidepoint(mouse_pos):
                    # Don't play menu_click since it doesn't exist
                    self.stop_menu_music()
                    return 'quit'

        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_hover(pygame.mouse.get_pos())

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                self.show_info_popup = not self.show_info_popup
            elif event.key == pygame.K_ESCAPE and self.show_info_popup:
                self.show_info_popup = False

        return None

    def _handle_mouse_hover(self, mouse_pos: Tuple[int, int]):
        """Handle mouse hover effects"""
        if self.current_state == self.MENU:
            new_start_hovered = self.start_button_rect.collidepoint(mouse_pos)
            new_exit_hovered = self.exit_button_rect.collidepoint(mouse_pos)

            # Don't play hover sounds since they don't exist
            self.start_hovered = new_start_hovered
            self.exit_hovered = new_exit_hovered

    def _play_sound(self, sound_name: str):
        """Play a sound effect"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            # Update volume based on current master volume before playing
            if sound_name in self.base_sound_volumes:
                base_vol = self.base_sound_volumes[sound_name]
                actual_vol = base_vol * (self.master_volume / 0.15)
                self.sounds[sound_name].set_volume(min(actual_vol, 1.0))
                print(f"Setting {sound_name} volume to {actual_vol * 100:.0f}%")

            # Play the sound and get the channel
            channel = self.sounds[sound_name].play()
            if channel:
                print(f"Playing {sound_name} sound on channel {channel}")
            else:
                print(f"Failed to play {sound_name} - no available channel")
        else:
            print(f"Sound {sound_name} not loaded or not found!")

    def update(self) -> Optional[str]:
        """Update menu system state"""
        current_time = pygame.time.get_ticks()

        if self.current_state == self.HORROR_EFFECT:
            elapsed_time = current_time - self.start_effect_timer

            if elapsed_time < self.start_effect_duration:
                # Fade to black
                progress = elapsed_time / self.start_effect_duration
                progress = progress * progress  # Quadratic curve
                self.darkness_overlay = int(255 * progress)
            else:
                # Start game
                self.current_state = self.GAMEPLAY
                self.darkness_overlay = 255
                print("Horror effect complete - starting game!")
                return 'start_game'

        elif self.current_state == self.GAMEPLAY:
            # Demo movement
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

        # Update info popup fade
        if self.show_info_popup and self.info_popup_alpha < 255:
            self.info_popup_alpha = min(255, self.info_popup_alpha + self.info_fade_speed)
        elif not self.show_info_popup and self.info_popup_alpha > 0:
            self.info_popup_alpha = max(0, self.info_popup_alpha - self.info_fade_speed)

        return None

    def draw(self, surface):
        """Draw the current menu state"""
        surface.blit(self.background_image, (0, 0))

        if self.current_state == self.MENU:
            self._draw_main_menu(surface)
            if self.info_popup_alpha > 0:
                self._draw_info_popup(surface)
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

        # HARDMODE indicator
        hardmode_rect = self.hardmode_surface.get_rect(topright=(self.screen_width - 10, 10))
        surface.blit(self.hardmode_surface, hardmode_rect)

        # Info instruction
        info_rect = self.info_instruction_surface.get_rect(topright=(self.screen_width - 10, 45))
        surface.blit(self.info_instruction_surface, info_rect)

        # Buttons
        self._draw_button(surface, "START", self.start_button_rect, self.start_hovered, '#FFFF00')
        self._draw_button(surface, "EXIT", self.exit_button_rect, self.exit_hovered, '#FF4444')

    def _draw_button(self, surface, text: str, rect: pygame.Rect, hovered: bool, hover_color: str):
        """Draw a button with hover effect"""
        button_bg = pygame.Surface((rect.width, rect.height))
        button_bg.set_alpha(150)
        button_bg.fill(pygame.Color('#333333'))
        surface.blit(button_bg, rect)

        pygame.draw.rect(surface, pygame.Color('#888888'), rect, 2)

        color = pygame.Color(hover_color) if hovered else pygame.Color('#FFFFFF')
        text_surface = self.button_font.render(text, True, color)
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)

    def _draw_gameplay(self, surface):
        """Draw gameplay demo"""
        pygame.draw.rect(surface, pygame.Color('#FFFF00'),
                         (int(self.player_x), int(self.player_y), self.player_size, self.player_size))

    def _draw_horror_effect(self, surface):
        """Draw horror transition effect"""
        self._draw_main_menu(surface)

        if self.darkness_overlay > 0:
            dark_surface = pygame.Surface((self.screen_width, self.screen_height))
            dark_surface.fill((0, 0, 0))
            dark_surface.set_alpha(self.darkness_overlay)
            surface.blit(dark_surface, (0, 0))

            # Flickering text
            if self.darkness_overlay > 128:
                if random.randint(0, 10) > 3:
                    horror_font = pygame.font.Font(None, 48)
                    horror_text = horror_font.render("BEWARE...", True, (200, 0, 0))
                    text_rect = horror_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                    text_rect.x += random.randint(-2, 2)
                    text_rect.y += random.randint(-2, 2)
                    surface.blit(horror_text, text_rect)

    def _draw_info_popup(self, surface):
        """Draw the Hardmode info popup"""
        # Dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(int(self.info_popup_alpha * 0.7))
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # Popup window
        popup_width = 500
        popup_height = 480
        popup_x = (self.screen_width - popup_width) // 2
        popup_y = (self.screen_height - popup_height) // 2

        # Popup background
        popup_surface = pygame.Surface((popup_width, popup_height))
        popup_surface.set_alpha(self.info_popup_alpha)
        popup_surface.fill((20, 20, 40))

        # Border
        pygame.draw.rect(popup_surface, (255, 0, 0), popup_surface.get_rect(), 3)

        # Title
        title_text = self.info_title_font.render("HARDMODE FEATURES", True, (255, 0, 0))
        title_rect = title_text.get_rect(centerx=popup_width // 2, y=20)
        popup_surface.blit(title_text, title_rect)

        # Info text
        info_lines = [
            "Welcome to HARDMODE - A true challenge!",
            "",
            "SPECIAL BUFFS:",
            "* The Powercherry & The Speedberry *",
            "• Power: Ghosts flee, slight speed boost — but they get angry!",
            "• Speed: Burst + short ghost stun. Pick: 2s run or hunt.",
            "",
            "PROGRESSIVE DIFFICULTY:",
            "• Ghosts get faster over time",
            "• Collect fruits to stack your own speed (up to 5 times)",
            "• After thirty seconds, CRANKY appears!",
            "",
            "CRANKY THE HUNTER:",
            "• Special purple ghost that never stops hunting",
            "• Tracks you across the entire maze",
            "• Can still be eaten when ghosts are frightened",
            "",
            "Speed and ghost difficulty persists through lives!",
            "",
            "Press I or ESC to close"
        ]

        y_offset = 70
        for line in info_lines:
            if line.startswith("•"):
                text_surface = self.info_font.render(line, True, (255, 255, 100))
            elif line == "" or line.startswith("Press"):
                text_surface = self.info_font.render(line, True, (200, 200, 200))
            else:
                text_surface = self.info_font.render(line, True, (100, 255, 255))

            text_rect = text_surface.get_rect(centerx=popup_width // 2, y=y_offset)
            popup_surface.blit(text_surface, text_rect)
            y_offset += 20

        surface.blit(popup_surface, (popup_x, popup_y))

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