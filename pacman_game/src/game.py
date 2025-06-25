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
from .ghost import Ghost, CrankyGhost
from .maze import Maze
from .pellets import PelletManager
from .menu import Menu
from .highscore import HighscoreManager

class MusicManager:
    """Manages background music for the game"""

    def __init__(self):
        self.music_loaded = False
        self.music_playing = False
        self.music_volume = 0.5  # Internal volume (0-1)
        self.master_volume = 0.15  # Master volume cap at 15% (half of 30% max)
        self.max_master_volume = 0.30  # Maximum 30% of system volume
        self.music_files = {
            'background': 'assets/sounds//effects/Castor.mp3',
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
                actual_volume = self.music_volume * self.master_volume
                pygame.mixer.music.set_volume(actual_volume)
                self.music_loaded = True
                print(f"HARDMODE music loaded: {music_file} ({actual_volume * 100:.0f}% volume)")
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
                print("HARDMODE music started")
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
        """Set music volume (0.0 to 1.0) - applies master volume cap"""
        self.music_volume = max(0.0, min(1.0, volume))
        actual_volume = self.music_volume * self.master_volume
        pygame.mixer.music.set_volume(actual_volume)
        print(f"Music volume set to: {actual_volume * 100:.0f}% (internal: {self.music_volume * 100:.0f}%)")

    def increase_master_volume(self):
        """Increase master volume by 5%"""
        self.master_volume = min(self.master_volume + 0.05, self.max_master_volume)
        self.update_volume()
        return self.master_volume

    def decrease_master_volume(self):
        """Decrease master volume by 5%"""
        self.master_volume = max(self.master_volume - 0.05, 0.0)
        self.update_volume()
        return self.master_volume

    def update_volume(self):
        """Update the actual volume based on current settings"""
        actual_volume = self.music_volume * self.master_volume
        pygame.mixer.music.set_volume(actual_volume)

    def toggle_music(self):
        """Toggle music on/off"""
        if self.music_playing:
            self.pause_background_music()
            self.music_playing = False
        else:
            if self.music_loaded:
                self.unpause_background_music()
                self.music_playing = True
            else:
                self.load_background_music()
                if self.music_loaded:
                    self.play_background_music()

    def is_playing(self):
        """Check if music is currently playing"""
        return pygame.mixer.music.get_busy()

class Game:
    """Main game class that manages the entire game state"""

    def __init__(self, screen):
        self.screen = screen
        self.state = MENU
        self.score = 0
        self.lives = 3

        # Sound system
        self.sound_enabled = True
        self.sound_loaded = False
        self.wakawaka_sound = None
        self.wakawaka_channel = None
        self.eat_ghost_sound = None
        self.death_sound = None
        self.eat_fruit_sound = None
        self.eat_ghost_new_sound = None

        # Master volume for sound effects
        self.sound_master_volume = 0.15  # 15% max
        self.max_sound_volume = 0.30  # 30% max

        # Waka-waka timer
        self.wakawaka_timer = 0
        self.wakawaka_interval = 200

        # Initialize music manager
        self.music_manager = MusicManager()

        # Load sound effects
        self.load_sounds()

        # Initialize game components
        self.maze = Maze()
        self.pacman = Pacman(11, 15)
        self.pellet_manager = PelletManager(self.maze)
        self.menu = Menu()

        # Initialize ghosts
        ghost_start_x = self.maze.width // 2
        ghost_start_y = self.maze.height // 2
        self.ghosts = [
            Ghost(ghost_start_x, ghost_start_y, RED, "blinky"),
            Ghost(ghost_start_x, ghost_start_y, PINK, "pinky"),
            Ghost(ghost_start_x, ghost_start_y, CYAN, "inky"),
            Ghost(ghost_start_x, ghost_start_y, ORANGE, "clyde")
        ]

        # HARDMODE: Cranky ghost timer - Changed from 3600 (60s) to 1800 (30s)
        self.cranky_spawn_timer = 0
        self.cranky_spawn_time = 1800  # 30 seconds at 60 FPS
        self.cranky_spawned = False

        # Font for UI
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Initialize highscore manager
        self.highscore_manager = HighscoreManager()
        self.new_highscore_position = 0

    def load_sounds(self):
        """Load all game sound effects"""
        try:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(8)

            sound_path = "assets/sounds/effects/"

            # Base volumes for different sounds
            sound_configs = {
                "wakawaka.wav": 0.05,
                "eat_ghost.wav": 0.08,
                "death.wav": 0.1,
                "pacman_eatfruit.wav": 0.06,
                "pacman_eatghost.wav": 0.08
            }

            try:
                self.wakawaka_sound = pygame.mixer.Sound(sound_path + "wakawaka.wav")
                actual_vol = sound_configs["wakawaka.wav"] * (self.sound_master_volume / 0.15)
                self.wakawaka_sound.set_volume(actual_vol)
                print(f"Waka-waka sound loaded at {actual_vol * 100:.0f}%!")
            except:
                print("Could not load wakawaka.wav")

            try:
                self.eat_ghost_sound = pygame.mixer.Sound(sound_path + "eat_ghost.wav")
                actual_vol = sound_configs["eat_ghost.wav"] * (self.sound_master_volume / 0.15)
                self.eat_ghost_sound.set_volume(actual_vol)
                print(f"Eat ghost sound loaded at {actual_vol * 100:.0f}%!")
            except:
                print("Could not load eat_ghost.wav")

            try:
                self.death_sound = pygame.mixer.Sound(sound_path + "death.wav")
                actual_vol = sound_configs["death.wav"] * (self.sound_master_volume / 0.15)
                self.death_sound.set_volume(actual_vol)
                print(f"Death sound loaded at {actual_vol * 100:.0f}%!")
                self.sound_loaded = True
            except:
                print("Could not load death.wav")

            try:
                self.eat_fruit_sound = pygame.mixer.Sound(sound_path + "pacman_eatfruit.wav")
                actual_vol = sound_configs["pacman_eatfruit.wav"] * (self.sound_master_volume / 0.15)
                self.eat_fruit_sound.set_volume(actual_vol)
                print(f"Eat fruit sound loaded at {actual_vol * 100:.0f}%!")
            except:
                print("Could not load pacman_eatfruit.wav")

            try:
                self.eat_ghost_new_sound = pygame.mixer.Sound(sound_path + "pacman_eatghost.wav")
                actual_vol = sound_configs["pacman_eatghost.wav"] * (self.sound_master_volume / 0.15)
                self.eat_ghost_new_sound.set_volume(actual_vol)
                print(f"New eat ghost sound loaded at {actual_vol * 100:.0f}%!")
            except:
                print("Could not load pacman_eatghost.wav")

        except Exception as e:
            print(f"Sound system error: {e}")
            self.sound_loaded = False

    def update_sound_volumes(self):
        """Update all sound effect volumes based on master volume"""
        sound_configs = {
            self.wakawaka_sound: 0.05,
            self.eat_ghost_sound: 0.08,
            self.death_sound: 0.1,
            self.eat_fruit_sound: 0.06,
            self.eat_ghost_new_sound: 0.08
        }

        for sound, base_vol in sound_configs.items():
            if sound:
                actual_vol = base_vol * (self.sound_master_volume / 0.15)
                sound.set_volume(min(actual_vol, 1.0))

    def increase_volume(self):
        """Increase both music and sound volumes"""
        # Increase music volume
        new_music_vol = self.music_manager.increase_master_volume()

        # Increase sound volume
        self.sound_master_volume = min(self.sound_master_volume + 0.05, self.max_sound_volume)
        self.update_sound_volumes()

        print(f"Volume increased - Music: {new_music_vol * 100:.0f}%, Sounds: {self.sound_master_volume * 100:.0f}%")

    def decrease_volume(self):
        """Decrease both music and sound volumes"""
        # Decrease music volume
        new_music_vol = self.music_manager.decrease_master_volume()

        # Decrease sound volume
        self.sound_master_volume = max(self.sound_master_volume - 0.05, 0.0)
        self.update_sound_volumes()

        print(f"Volume decreased - Music: {new_music_vol * 100:.0f}%, Sounds: {self.sound_master_volume * 100:.0f}%")

    def setup_music(self):
        """Initialize and start background music"""
        self.music_manager.load_background_music()
        self.music_manager.play_background_music()

    def play_wakawaka_sound(self):
        """Play waka-waka sound when eating pellets"""
        if self.sound_enabled and self.sound_loaded and self.wakawaka_sound:
            current_time = pygame.time.get_ticks()
            if current_time - self.wakawaka_timer > self.wakawaka_interval:
                self.wakawaka_sound.play()
                self.wakawaka_timer = current_time

    def stop_wakawaka_sound(self):
        """Stop waka-waka sound playback"""
        if self.wakawaka_channel and self.wakawaka_channel.get_busy():
            self.wakawaka_channel.stop()

    def play_eat_ghost_sound(self):
        """Play sound effect when eating a ghost"""
        if self.sound_enabled and self.sound_loaded and self.eat_ghost_new_sound:
            self.eat_ghost_new_sound.play()
        elif self.sound_enabled and self.sound_loaded and self.eat_ghost_sound:
            self.eat_ghost_sound.play()

    def play_eat_fruit_sound(self):
        """Play sound effect when eating a pellet"""
        if self.sound_enabled and self.sound_loaded and self.eat_fruit_sound:
            self.eat_fruit_sound.play()

    def play_death_sound(self):
        """Play death sound effect when Pac-Man dies"""
        if self.sound_enabled and self.sound_loaded and self.death_sound:
            self.death_sound.play()

    def handle_event(self, event):
        """Handle all input events based on current game state"""
        if self.state == MENU:
            menu_result = self.menu.handle_event(event)
            if menu_result == 'start_game':
                self.start_game()
                return True
            elif menu_result == 'quit':
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.start_game()
                elif event.key == pygame.K_q:
                    return False

        elif self.state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = PAUSED
                    self.music_manager.pause_background_music()
                elif event.key == pygame.K_m:
                    self.music_manager.toggle_music()
                # Volume controls - Multiple keys
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS or event.key == pygame.K_COMMA:
                    self.decrease_volume()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS or event.key == pygame.K_PERIOD:
                    self.increase_volume()
                # Movement controls
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
                    self.music_manager.unpause_background_music()
                elif event.key == pygame.K_q:
                    self.state = MENU
                    self.music_manager.stop_background_music()
                    self.menu.menu_system.current_state = self.menu.menu_system.MENU
                    self.menu.menu_system.darkness_overlay = 0
                    self.menu.menu_system.start_menu_music()

        elif self.state == GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_q:
                    self.state = MENU
                    self.music_manager.stop_background_music()
                    self.menu.menu_system.current_state = self.menu.menu_system.MENU
                    self.menu.menu_system.darkness_overlay = 0
                    self.menu.menu_system.start_menu_music()

        elif self.state == VICTORY:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.restart_game()
                elif event.key == pygame.K_q:
                    self.state = MENU
                    self.music_manager.stop_background_music()
                    self.menu.menu_system.current_state = self.menu.menu_system.MENU
                    self.menu.menu_system.darkness_overlay = 0
                    self.menu.menu_system.start_menu_music()

        return True

    def start_game(self):
        """Initialize a new game with fresh state"""
        self.state = PLAYING
        self.score = 0
        self.lives = 3

        self.pacman.full_reset(1, 1)
        self.pacman.initialize_nodes(self.maze.node_map)
        self.pellet_manager.reset()

        # Remove Cranky if present
        self.ghosts = [ghost for ghost in self.ghosts if ghost.name != "cranky"]

        # Reset ghosts
        ghost_start_x = self.maze.width // 2
        ghost_start_y = self.maze.height // 2

        if len(self.ghosts) != 4:
            self.ghosts = [
                Ghost(ghost_start_x, ghost_start_y, RED, "blinky"),
                Ghost(ghost_start_x, ghost_start_y, PINK, "pinky"),
                Ghost(ghost_start_x, ghost_start_y, CYAN, "inky"),
                Ghost(ghost_start_x, ghost_start_y, ORANGE, "clyde")
            ]

        for ghost in self.ghosts:
            if hasattr(ghost, 'full_reset'):
                ghost.full_reset(ghost_start_x, ghost_start_y)
            else:
                ghost.reset(ghost_start_x, ghost_start_y)

        # Reset Cranky spawn timer
        self.cranky_spawn_timer = 0
        self.cranky_spawned = False

        # Reset highscore position
        self.new_highscore_position = 0

        # Start music
        self.setup_music()

    def restart_game(self):
        """Restart the game with fresh state"""
        self.start_game()

    def update(self):
        """Main game logic update"""
        if self.state == MENU:
            menu_result = self.menu.menu_system.update()
            if menu_result == 'start_game':
                self.start_game()

        if self.state == PLAYING:
            self.pacman.update(self.maze)

            # HARDMODE: Check for Cranky spawn (after 30 seconds)
            if not self.cranky_spawned:
                self.cranky_spawn_timer += 1
                # Debug output every 5 seconds
                if self.cranky_spawn_timer % 300 == 0:
                    print(f"Cranky spawn timer: {self.cranky_spawn_timer // 60} seconds")

                if self.cranky_spawn_timer >= self.cranky_spawn_time:
                    ghost_start_x = self.maze.width // 2
                    ghost_start_y = self.maze.height // 2
                    cranky = CrankyGhost(ghost_start_x, ghost_start_y)
                    self.ghosts.append(cranky)
                    self.cranky_spawned = True
                    print(f"CRANKY HAS ENTERED THE GAME! (after {self.cranky_spawn_timer // 60} seconds)")

            # Update ghosts
            for ghost in self.ghosts:
                ghost.update(self.maze, self.pacman, self.ghosts)

            # Update pellets
            self.pellet_manager.update()

            # Check pellet collection
            collected_points = self.pellet_manager.check_collection(self.pacman)
            if collected_points != 0:
                if collected_points < 0:
                    if collected_points < -1000:
                        # Speed pellet eaten
                        actual_points = abs(collected_points + 1000)
                        self.score += actual_points
                        self.pacman.activate_speed_boost()
                        self.pacman.add_speed_stack()
                        self.play_eat_fruit_sound()
                        # Speed Pellet: 2 second frightened without speed buff
                        for ghost in self.ghosts:
                            if hasattr(ghost, 'set_frightened_short'):
                                ghost.set_frightened_short()
                            else:
                                ghost.set_frightened(trigger_speed_buff=False)
                                if ghost.mode == FRIGHTENED:
                                    ghost.mode_timer = 240
                    else:
                        # Power pellet eaten
                        self.score += abs(collected_points)
                        self.pacman.add_speed_stack()
                        self.play_eat_fruit_sound()
                        # Make ghosts frightened with speed buff
                        for ghost in self.ghosts:
                            ghost.set_frightened(trigger_speed_buff=True)
                        self.pacman.activate_power_speed_boost()
                else:
                    # Normal pellet eaten
                    self.score += collected_points

                self.play_wakawaka_sound()
                self.pacman.set_eating(True)
            else:
                self.pacman.set_eating(False)

            # Check ghost collisions
            for ghost in self.ghosts:
                if self.pacman.collides_with(ghost):
                    if ghost.mode == FRIGHTENED:
                        ghost.mode = EATEN
                        self.score += 200
                        self.play_eat_ghost_sound()
                    elif ghost.mode != EATEN:
                        self.lives -= 1
                        self.play_death_sound()
                        pygame.time.wait(1500)

                        if self.lives <= 0:
                            self.state = GAME_OVER
                            self.music_manager.stop_background_music()
                            # Check for new highscore
                            self.new_highscore_position = self.highscore_manager.add_score(self.score)
                        else:
                            self.reset_after_death()

            # Check victory
            if self.pellet_manager.all_collected():
                self.state = VICTORY
                self.music_manager.stop_background_music()
                # Check for new highscore
                self.new_highscore_position = self.highscore_manager.add_score(self.score)

    def draw(self):
        """Main rendering function"""
        self.screen.fill(BLACK)

        if self.state == MENU:
            self.menu.draw(self.screen)

        elif self.state in [PLAYING, PAUSED]:
            self.maze.draw(self.screen)
            self.maze.draw_nodes(self.screen, show_nodes=False)
            self.pellet_manager.draw(self.screen)
            self.pacman.draw(self.screen)

            for ghost in self.ghosts:
                ghost.draw(self.screen)

            self.draw_ui()

            if self.state == PAUSED:
                self.draw_pause_screen()

        elif self.state == GAME_OVER:
            self.draw_game_over()

        elif self.state == VICTORY:
            self.draw_victory()

    def draw_ui(self):
        """Draw the user interface elements"""
        # UI area starts after the game field
        ui_y_start = GAME_AREA_HEIGHT + 5

        # Background for UI area
        ui_rect = pygame.Rect(0, GAME_AREA_HEIGHT, SCREEN_WIDTH, 60)
        pygame.draw.rect(self.screen, (10, 10, 30), ui_rect)
        pygame.draw.rect(self.screen, (50, 50, 100), ui_rect, 3)

        # Score - Centered at top (slightly smaller)
        score_font = pygame.font.Font(None, 28)  # Reduced from 32
        score_text = score_font.render(f"SCORE: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(centerx=SCREEN_WIDTH//2, y=ui_y_start + 7)
        self.screen.blit(score_text, score_rect)

        # Lives - Top right as hearts
        lives_x_start = SCREEN_WIDTH - 100
        lives_y = ui_y_start + 15

        for i in range(self.lives):
            heart_x = lives_x_start + (i * 25)
            # Simple heart shape
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

        # Power pellet legend - use ghostcherry.png (bigger size)
        try:
            power_icon = pygame.image.load('assets/images/pacman/ghostcherry.png').convert_alpha()
            power_icon = pygame.transform.scale(power_icon, (24, 24))  # Increased from 16x16
            self.screen.blit(power_icon, (8, legend_y - 7))
        except:
            # Fallback if image not found
            pygame.draw.circle(self.screen, (255, 184, 255), (20, legend_y + 5), 8)
            pygame.draw.circle(self.screen, (255, 220, 255), (20, legend_y + 5), 9, 1)
        power_text = legend_font.render("= Power Up", True, WHITE)
        self.screen.blit(power_text, (36, legend_y))

        # Speed pellet legend - use speedberry.png (bigger size)
        try:
            speed_icon = pygame.image.load('assets/images/pacman/speedberry.png').convert_alpha()
            speed_icon = pygame.transform.scale(speed_icon, (24, 24))  # Increased from 16x16
            self.screen.blit(speed_icon, (138, legend_y - 7))
        except:
            # Fallback if image not found
            pygame.draw.circle(self.screen, CYAN, (150, legend_y + 5), 8)
            pygame.draw.circle(self.screen, (150, 255, 255), (150, legend_y + 5), 10, 1)
        speed_text = legend_font.render("= Speed Boost", True, WHITE)
        self.screen.blit(speed_text, (166, legend_y))

        # Music/Volume controls - Better formatted
        control_font = pygame.font.Font(None, 18)  # Larger font
        music_status = "ON" if self.music_manager.music_playing else "OFF"

        # Draw controls with button-style formatting
        controls_y = SCREEN_HEIGHT - 22

        # Draw "Music:" text
        music_label = control_font.render("Music:", True, WHITE)
        self.screen.blit(music_label, (SCREEN_WIDTH - 280, controls_y))

        # Draw M button
        m_button_rect = pygame.Rect(SCREEN_WIDTH - 230, controls_y - 2, 25, 20)
        button_color = GREEN if self.music_manager.music_playing else RED
        pygame.draw.rect(self.screen, button_color, m_button_rect, 2)
        m_text = control_font.render("M", True, button_color)
        m_text_rect = m_text.get_rect(center=m_button_rect.center)
        self.screen.blit(m_text, m_text_rect)

        # Draw = Mute text
        mute_text = control_font.render(f"= Mute", True, WHITE)
        self.screen.blit(mute_text, (SCREEN_WIDTH - 200, controls_y))

        # Draw separator
        sep_text = control_font.render("|", True, (100, 100, 100))
        self.screen.blit(sep_text, (SCREEN_WIDTH - 150, controls_y))

        # Draw Volume controls
        vol_text = control_font.render("Volume:", True, WHITE)
        self.screen.blit(vol_text, (SCREEN_WIDTH - 140, controls_y))

        # Draw - button
        minus_button_rect = pygame.Rect(SCREEN_WIDTH - 85, controls_y - 2, 20, 20)
        pygame.draw.rect(self.screen, WHITE, minus_button_rect, 2)
        minus_text = control_font.render("-", True, WHITE)
        minus_text_rect = minus_text.get_rect(center=minus_button_rect.center)
        self.screen.blit(minus_text, minus_text_rect)

        # Draw current volume
        current_vol = int(self.music_manager.master_volume * 100)
        vol_color = GREEN if current_vol > 0 else RED
        vol_percent_text = control_font.render(f"{current_vol}", True, vol_color)
        vol_percent_rect = vol_percent_text.get_rect(centerx=SCREEN_WIDTH - 45, y=controls_y)
        self.screen.blit(vol_percent_text, vol_percent_rect)

        # Draw + button
        plus_button_rect = pygame.Rect(SCREEN_WIDTH - 25, controls_y - 2, 20, 20)
        pygame.draw.rect(self.screen, WHITE, plus_button_rect, 2)
        plus_text = control_font.render("+", True, WHITE)
        plus_text_rect = plus_text.get_rect(center=plus_button_rect.center)
        self.screen.blit(plus_text, plus_text_rect)

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
        """Draw game over screen with highscores"""
        self.menu.draw(self.screen)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        game_over_text = self.font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(game_over_text, text_rect)

        # Final Score
        score_text = self.font.render(f"Final Score: {self.score:,}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(score_text, score_rect)

        # New highscore notification
        if self.new_highscore_position > 0:
            congrats_text = self.font.render(f"NEW HIGHSCORE! Rank #{self.new_highscore_position}", True, YELLOW)
            congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH//2, 240))
            self.screen.blit(congrats_text, congrats_rect)

        # Highscore list
        highscore_title = self.font.render("HIGHSCORES", True, CYAN)
        title_rect = highscore_title.get_rect(center=(SCREEN_WIDTH//2, 300))
        self.screen.blit(highscore_title, title_rect)

        # Draw highscore entries
        formatted_scores = self.highscore_manager.get_formatted_scores()
        y_offset = 340
        for i, score_line in enumerate(formatted_scores):
            # Highlight new highscore
            if i + 1 == self.new_highscore_position:
                color = YELLOW
                # Add glow effect
                glow_text = self.small_font.render(score_line, True, YELLOW)
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        glow_rect = glow_text.get_rect(center=(SCREEN_WIDTH//2 + dx, y_offset + dy))
                        glow_surface = pygame.Surface(glow_rect.size)
                        glow_surface.set_alpha(50)
                        glow_surface.fill(YELLOW)
                        self.screen.blit(glow_surface, glow_rect)
            else:
                color = WHITE

            score_surface = self.small_font.render(score_line, True, color)
            score_rect = score_surface.get_rect(center=(SCREEN_WIDTH//2, y_offset))
            self.screen.blit(score_surface, score_rect)
            y_offset += 30

        # Instructions
        restart_text = self.small_font.render("Press SPACE or Q for menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, 550))
        self.screen.blit(restart_text, restart_rect)

    def draw_victory(self):
        """Draw victory screen with highscores"""
        self.menu.draw(self.screen)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Victory text
        victory_text = self.font.render("VICTORY!", True, GREEN)
        text_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(victory_text, text_rect)

        # Final Score
        score_text = self.font.render(f"Final Score: {self.score:,}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(score_text, score_rect)

        # New highscore notification
        if self.new_highscore_position > 0:
            congrats_text = self.font.render(f"NEW HIGHSCORE! Rank #{self.new_highscore_position}", True, YELLOW)
            congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH//2, 240))
            self.screen.blit(congrats_text, congrats_rect)

        # Highscore list
        highscore_title = self.font.render("HIGHSCORES", True, CYAN)
        title_rect = highscore_title.get_rect(center=(SCREEN_WIDTH//2, 300))
        self.screen.blit(highscore_title, title_rect)

        # Draw highscore entries
        formatted_scores = self.highscore_manager.get_formatted_scores()
        y_offset = 340
        for i, score_line in enumerate(formatted_scores):
            # Highlight new highscore
            if i + 1 == self.new_highscore_position:
                color = YELLOW
                # Add glow effect
                glow_text = self.small_font.render(score_line, True, YELLOW)
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        glow_rect = glow_text.get_rect(center=(SCREEN_WIDTH//2 + dx, y_offset + dy))
                        glow_surface = pygame.Surface(glow_rect.size)
                        glow_surface.set_alpha(50)
                        glow_surface.fill(YELLOW)
                        self.screen.blit(glow_surface, glow_rect)
            else:
                color = WHITE

            score_surface = self.small_font.render(score_line, True, color)
            score_rect = score_surface.get_rect(center=(SCREEN_WIDTH//2, y_offset))
            self.screen.blit(score_surface, score_rect)
            y_offset += 30

        # Instructions
        restart_text = self.small_font.render("Press SPACE to play again or Q for menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, 550))
        self.screen.blit(restart_text, restart_rect)

    def reset_after_death(self):
        """Reset positions after Pac-Man dies (pellets remain eaten)"""
        self.pacman.reset(1, 1)
        self.pacman.initialize_nodes(self.maze.node_map)

        ghost_start_x = self.maze.width // 2
        ghost_start_y = self.maze.height // 2

        # Keep track of Cranky before resetting
        has_cranky = any(ghost.name == "cranky" for ghost in self.ghosts)

        for ghost in self.ghosts:
            # All ghosts including Cranky reset to house
            ghost.reset(ghost_start_x, ghost_start_y)
            if ghost.name != "cranky":
                ghost.mode = SCATTER
                ghost.mode_timer = 0
                ghost.scatter_timer = 0

    def cleanup(self):
        """Clean up resources when closing the game"""
        self.music_manager.stop_background_music()