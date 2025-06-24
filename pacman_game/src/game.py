"""
Main Game Class
Handles game logic, state management, and coordination between components
"""

import pygame
import os
from .constants import *
from .player import Pacman
from .ghost import Ghost
from .maze import Maze
from .pellets import PelletManager
from .menu import Menu

class MusicManager:
    """Verwaltet die Hintergrundmusik für das Pacman-Spiel"""

    def __init__(self):
        self.music_loaded = False
        self.music_playing = False
        self.music_volume = 0.5
        self.music_files = {
            'background': 'assets/sounds//effects/background_music.mp3',
            'game_start': 'assets/audio/game_start.ogg',
            'game_over': 'assets/audio/game_over.ogg',
            'level_complete': 'assets/audio/level_complete.ogg'
        }

    def load_background_music(self, music_file=None):
        """Lädt die Hintergrundmusik"""
        try:
            if music_file is None:
                music_file = self.music_files['background']

            if os.path.exists(music_file):
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self.music_volume)
                self.music_loaded = True
                print(f"Hintergrundmusik geladen: {music_file}")
            else:
                print(f"Musikdatei nicht gefunden: {music_file}")
                self.music_loaded = False

        except pygame.error as e:
            print(f"Fehler beim Laden der Musik: {e}")
            self.music_loaded = False

    def play_background_music(self, loops=-1):
        """Startet die Hintergrundmusik"""
        if self.music_loaded and not self.music_playing:
            try:
                pygame.mixer.music.play(loops)
                self.music_playing = True
                print("Hintergrundmusik gestartet")
            except pygame.error as e:
                print(f"Fehler beim Abspielen der Musik: {e}")

    def stop_background_music(self):
        """Stoppt die Hintergrundmusik"""
        pygame.mixer.music.stop()
        self.music_playing = False
        print("Hintergrundmusik gestoppt")

    def pause_background_music(self):
        """Pausiert die Hintergrundmusik"""
        if self.music_playing:
            pygame.mixer.music.pause()
            print("Hintergrundmusik pausiert")

    def unpause_background_music(self):
        """Setzt die Hintergrundmusik fort"""
        pygame.mixer.music.unpause()
        print("Hintergrundmusik fortgesetzt")

    def set_volume(self, volume):
        """Setzt die Lautstärke der Musik"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        print(f"Musiklautstärke gesetzt auf: {self.music_volume}")

    def toggle_music(self):
        """Schaltet die Musik ein/aus"""
        if self.music_playing:
            self.pause_background_music()
        else:
            self.unpause_background_music()

    def is_playing(self):
        """Prüft ob Musik gerade abgespielt wird"""
        return pygame.mixer.music.get_busy()

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.state = MENU
        self.score = 0
        self.lives = 3

        # Sound-System
        self.sound_enabled = True
        self.sound_loaded = False
        self.wakawaka_sound = None
        self.wakawaka_channel = None
        self.eat_ghost_sound = None
        self.death_sound = None

        # Waka-Waka Timer für bessere Kontrolle
        self.wakawaka_timer = 0
        self.wakawaka_interval = 200  # Millisekunden zwischen Sounds

        # Musikmanager initialisieren
        self.music_manager = MusicManager()

        # Lade Sounds
        self.load_sounds()

        # Initialize game components
        self.maze = Maze()
        self.pacman = Pacman(11, 15)  # Bessere Startposition im Labyrinth
        self.pellet_manager = PelletManager(self.maze)
        self.menu = Menu()

        # Initialize ghosts - Geister-Startbereich mit klassischen Namen
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
        """Lade Sound-Dateien"""
        try:
            pygame.mixer.init()

            # Hauptpfad für Sounds
            sound_path = "assets/sounds/effects/"

            try:
                # Waka-Waka Sound
                self.wakawaka_sound = pygame.mixer.Sound(sound_path + "wakawaka.wav")
                self.wakawaka_sound.set_volume(0.3)
                print("Waka-waka sound loaded!")
            except:
                print("Could not load wakawaka.wav")

            try:
                # Ghost eat sound
                self.eat_ghost_sound = pygame.mixer.Sound(sound_path + "eat_ghost.wav")
                self.eat_ghost_sound.set_volume(0.4)
                print("Eat ghost sound loaded!")
            except:
                print("Could not load eat_ghost.wav")

            try:
                # Death sound
                self.death_sound = pygame.mixer.Sound(sound_path + "death.wav")
                self.death_sound.set_volume(0.5)
                print("Death sound loaded!")
                self.sound_loaded = True
            except:
                print("Could not load death.wav")

        except Exception as e:
            print(f"Sound system error: {e}")
            self.sound_loaded = False

    def setup_music(self):
        """Lädt und startet die Hintergrundmusik"""
        self.music_manager.load_background_music()
        self.music_manager.play_background_music()

    def play_wakawaka_sound(self):
        """Spiele WakaWaka Sound nur beim Essen"""
        if self.sound_enabled and self.sound_loaded and self.wakawaka_sound:
            current_time = pygame.time.get_ticks()
            # Spiele Sound nur wenn genug Zeit vergangen ist
            if current_time - self.wakawaka_timer > self.wakawaka_interval:
                self.wakawaka_sound.play()
                self.wakawaka_timer = current_time

    def stop_wakawaka_sound(self):
        """Stoppe WakaWaka Sound"""
        if self.wakawaka_channel and self.wakawaka_channel.get_busy():
            self.wakawaka_channel.stop()

    def play_eat_ghost_sound(self):
        """Spiele Sound beim Geister essen"""
        if self.sound_enabled and self.sound_loaded and self.eat_ghost_sound:
            self.eat_ghost_sound.play()

    def play_death_sound(self):
        """Spiele Sound beim Tod"""
        if self.sound_enabled and self.sound_loaded and self.death_sound:
            self.death_sound.play()

    def handle_event(self, event):
        """Handle input events"""
        if self.state == MENU:
            # Ereignisse an das Menüsystem weiterleiten
            menu_result = self.menu.handle_event(event)
            if menu_result == 'start_game':
                self.start_game()
                return True
            elif menu_result == 'quit':
                return False

            # Für Tastatureingaben (als Fallback)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.start_game()
                elif event.key == pygame.K_q:
                    return False

        elif self.state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = PAUSED
                    # Musik pausieren wenn das Spiel pausiert wird
                    self.music_manager.pause_background_music()
                # Musik-Steuerung
                elif event.key == pygame.K_m:
                    self.music_manager.toggle_music()
                elif event.key == pygame.K_MINUS:
                    # Lautstärke verringern
                    current_vol = self.music_manager.music_volume
                    self.music_manager.set_volume(current_vol - 0.1)
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    # Lautstärke erhöhen
                    current_vol = self.music_manager.music_volume
                    self.music_manager.set_volume(current_vol + 0.1)
                # Node-basierte Steuerung mit WASD oder Pfeiltasten
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
                    # Musik fortsetzen wenn das Spiel fortgesetzt wird
                    self.music_manager.unpause_background_music()
                elif event.key == pygame.K_q:
                    self.state = MENU
                    # Musik stoppen wenn zum Menü gewechselt wird
                    self.music_manager.stop_background_music()
                    # Starte Menü-Musik wieder
                    self.menu.menu_system.start_menu_music()

        elif self.state == GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.restart_game()
                elif event.key == pygame.K_q:
                    self.state = MENU
                    self.music_manager.stop_background_music()
                    # Starte Menü-Musik wieder
                    self.menu.menu_system.start_menu_music()

        elif self.state == VICTORY:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.restart_game()
                elif event.key == pygame.K_q:
                    self.state = MENU
                    self.music_manager.stop_background_music()
                    # Starte Menü-Musik wieder
                    self.menu.menu_system.start_menu_music()

    def start_game(self):
        """Start a new game"""
        self.state = PLAYING
        self.score = 0
        self.lives = 3
        # Pacman oben links positionieren (x=1, y=1 ist der erste freie Platz in der Ecke)
        self.pacman.reset(1, 1)

        # Initialisiere Pacman mit den Nodes für die Bewegung
        self.pacman.initialize_nodes(self.maze.node_map)

        self.pellet_manager.reset()

        # Reset ghosts mit ihren Startpositionen
        ghost_start_x = self.maze.width // 2
        ghost_start_y = self.maze.height // 2
        for ghost in self.ghosts:
            ghost.reset(ghost_start_x, ghost_start_y)

        # Hintergrundmusik starten
        self.setup_music()

    def restart_game(self):
        """Restart the current game"""
        self.start_game()

    def update(self):
        """Update game logic"""
        # Prüfe auf Statusänderungen im Menüsystem, wenn wir im Menü sind
        if self.state == MENU:
            menu_result = self.menu.menu_system.update()
            if menu_result == 'start_game':
                self.start_game()

        if self.state == PLAYING:
            # Update Pac-Man
            self.pacman.update(self.maze)

            # Update ghosts
            for ghost in self.ghosts:
                ghost.update(self.maze, self.pacman, self.ghosts)

            # Update pellets
            self.pellet_manager.update()

            # Check pellet collection
            collected_points = self.pellet_manager.check_collection(self.pacman)
            if collected_points != 0:
                if collected_points < 0:
                    # Power Pellet gegessen (negativ als Signal)
                    self.score += abs(collected_points)
                    # Mache alle Geister ängstlich
                    for ghost in self.ghosts:
                        ghost.set_frightened()
                else:
                    # Normale Pellet
                    self.score += collected_points

                # Pac-Man isst gerade - spiele Waka-Waka Sound
                self.play_wakawaka_sound()
                self.pacman.set_eating(True)
            else:
                # Pac-Man isst nicht
                self.pacman.set_eating(False)

            # Check ghost collisions
            for ghost in self.ghosts:
                if self.pacman.collides_with(ghost):
                    if ghost.mode == FRIGHTENED:
                        ghost.mode = EATEN
                        self.score += 200
                        self.play_eat_ghost_sound()
                    elif ghost.mode != EATEN:  # Geister im EATEN mode können nicht töten
                        # Pac-Man stirbt
                        self.lives -= 1

                        # Spiele Tod-Sound
                        self.play_death_sound()

                        # Pause für Tod-Animation
                        pygame.time.wait(1500)  # 1.5 Sekunden Pause

                        if self.lives <= 0:
                            self.state = GAME_OVER
                            self.music_manager.stop_background_music()
                        else:
                            # Reset Level - Pac-Man und Geister zurück zu Start
                            # aber Punkte bleiben weg!
                            self.reset_after_death()

            # Check victory condition
            if self.pellet_manager.all_collected():
                self.state = VICTORY
                self.music_manager.stop_background_music()

    def draw(self):
        """Draw everything to the screen"""
        self.screen.fill(BLACK)

        if self.state == MENU:
            self.menu.draw(self.screen)

        elif self.state in [PLAYING, PAUSED]:
            # Draw maze
            self.maze.draw(self.screen)

            # Debug: Nodes anzeigen (auf False setzen für normales Spiel)
            self.maze.draw_nodes(self.screen, show_nodes=False)

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

        # Musik-Steuerung Hinweise
        music_hint = self.font.render("M: Music On/Off  +/-: Volume", True, WHITE)
        music_hint = pygame.transform.scale(music_hint, (music_hint.get_width()//2, music_hint.get_height()//2))
        self.screen.blit(music_hint, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 25))

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

    def reset_after_death(self):
        """Reset nach Pac-Man Tod - Positionen zurücksetzen aber Punkte bleiben weg"""
        # Reset Pac-Man zur Startposition
        self.pacman.reset(1, 1)
        self.pacman.initialize_nodes(self.maze.node_map)

        # Reset alle Geister zu ihren Startpositionen
        ghost_start_x = self.maze.width // 2
        ghost_start_y = self.maze.height // 2
        for ghost in self.ghosts:
            ghost.reset(ghost_start_x, ghost_start_y)
            # Reset auch ihre Modi
            ghost.mode = SCATTER
            ghost.mode_timer = 0
            ghost.scatter_timer = 0

        # WICHTIG: Pellets bleiben gefressen!
        # Keine pellet_manager.reset() hier!

    def cleanup(self):
        """Aufräumen beim Beenden des Spiels"""
        self.music_manager.stop_background_music()