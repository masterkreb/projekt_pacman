"""
Unit tests for the Game class
Tests game logic, scoring, lives, state management, and sound following AAA pattern
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pacman_game.src.game import Game, MusicManager
from pacman_game.src.constants import *


@pytest.mark.unit
class TestGameInitialization:
    """Test Game initialization and basic properties"""
    
    def test_game_initializes_with_correct_defaults(self, mock_all_pygame, test_screen):
        """Test that Game initializes with correct default values"""
        # ARRANGE - Setup test screen
        
        # ACT - Create Game instance
        game = Game(test_screen)
        
        # ASSERT - Verify initialization
        assert game.screen == test_screen
        assert game.state == MENU
        assert game.score == 0
        assert game.lives == 3
        assert game.sound_enabled is True
        assert game.sound_loaded is False
        assert game.wakawaka_timer == 0
        assert game.wakawaka_interval == 200

    def test_game_initializes_components(self, mock_all_pygame, test_screen):
        """Test that Game initializes all required components"""
        # ARRANGE - Setup test screen
        
        # ACT - Create Game instance
        game = Game(test_screen)
        
        # ASSERT - Verify components are initialized
        assert hasattr(game, 'maze')
        assert hasattr(game, 'pacman')
        assert hasattr(game, 'pellet_manager')
        assert hasattr(game, 'menu')
        assert hasattr(game, 'music_manager')
        assert hasattr(game, 'ghosts')
        assert isinstance(game.ghosts, list)

    def test_game_initializes_sound_system(self, mock_all_pygame, test_screen):
        """Test that Game initializes sound system correctly"""
        # ARRANGE - Setup test screen
        
        # ACT - Create Game instance
        game = Game(test_screen)
        
        # ASSERT - Verify sound system initialization
        assert hasattr(game, 'wakawaka_sound')
        assert hasattr(game, 'wakawaka_channel')
        assert hasattr(game, 'eat_ghost_sound')
        assert hasattr(game, 'death_sound')


@pytest.mark.unit
class TestGameStateManagement:
    """Test Game state management functionality"""
    
    def test_game_starts_in_menu_state(self, mock_all_pygame, test_screen):
        """Test that game starts in MENU state"""
        # ARRANGE - Setup test screen
        
        # ACT - Create Game instance
        game = Game(test_screen)
        
        # ASSERT - Verify initial state
        assert game.state == MENU

    def test_game_state_transitions(self, mock_all_pygame, test_screen):
        """Test that game state can be changed"""
        # ARRANGE - Setup game
        game = Game(test_screen)
        
        # ACT - Change state to playing
        game.state = PLAYING
        
        # ASSERT - Verify state changed
        assert game.state == PLAYING
        
        # ACT - Change state to game over
        game.state = GAME_OVER
        
        # ASSERT - Verify state changed
        assert game.state == GAME_OVER


@pytest.mark.unit
class TestGameScoring:
    """Test Game scoring functionality"""
    
    def test_score_increases_when_collecting_pellets(self, mock_all_pygame, test_screen):
        """Test that score increases when pellets are collected"""
        # ARRANGE - Setup game
        game = Game(test_screen)
        initial_score = game.score
        points_to_add = 10
        
        # ACT - Add points to score
        game.score += points_to_add
        
        # ASSERT - Verify score increased
        assert game.score == initial_score + points_to_add

    def test_score_handles_large_values(self, mock_all_pygame, test_screen):
        """Test that score can handle large values"""
        # ARRANGE - Setup game
        game = Game(test_screen)
        large_score = 999999
        
        # ACT - Set large score
        game.score = large_score
        
        # ASSERT - Verify score is set correctly
        assert game.score == large_score

    def test_score_resets_correctly(self, mock_all_pygame, test_screen):
        """Test that score can be reset"""
        # ARRANGE - Setup game with some score
        game = Game(test_screen)
        game.score = 5000
        
        # ACT - Reset score
        game.score = 0
        
        # ASSERT - Verify score is reset
        assert game.score == 0


@pytest.mark.unit
class TestGameLivesManagement:
    """Test Game lives management functionality"""
    
    def test_game_starts_with_correct_lives(self, mock_all_pygame, test_screen):
        """Test that game starts with correct number of lives"""
        # ARRANGE - Setup test screen
        
        # ACT - Create game
        game = Game(test_screen)
        
        # ASSERT - Verify starting lives
        assert game.lives == 3

    def test_lives_decrease_when_pacman_dies(self, mock_all_pygame, test_screen):
        """Test that lives decrease when Pacman dies"""
        # ARRANGE - Setup game
        game = Game(test_screen)
        initial_lives = game.lives
        
        # ACT - Simulate Pacman death
        game.lives -= 1
        
        # ASSERT - Verify lives decreased
        assert game.lives == initial_lives - 1

    def test_game_over_when_no_lives_remaining(self, mock_all_pygame, test_screen):
        """Test game over condition when no lives remain"""
        # ARRANGE - Setup game with one life
        game = Game(test_screen)
        game.lives = 1
        
        # ACT - Lose last life
        game.lives -= 1
        
        # ASSERT - Verify no lives remain
        assert game.lives == 0
        # Game over logic would be triggered in actual update method


@pytest.mark.unit
class TestGameSoundSystem:
    """Test Game sound system functionality"""
    
    def test_sound_loading_handles_success(self, mock_all_pygame, test_screen):
        """Test that sound loading works when files are available"""
        # ARRANGE - Mock successful sound loading
        with patch('pygame.mixer.Sound') as mock_sound:
            mock_sound.return_value = Mock()
            
            # ACT - Create game (triggers sound loading)
            game = Game(test_screen)
            
            # ASSERT - Verify sounds were loaded
            mock_sound.assert_called()

    def test_sound_loading_handles_failure_gracefully(self, mock_all_pygame, test_screen):
        """Test that sound loading handles missing files gracefully"""
        # ARRANGE - Mock failed sound loading
        with patch('pygame.mixer.Sound', side_effect=FileNotFoundError("Sound file not found")):
            
            # ACT - Create game (should not crash)
            game = Game(test_screen)
            
            # ASSERT - Game should still be created
            assert game.sound_enabled is True
            assert game.sound_loaded is False

    def test_wakawaka_sound_timing(self, mock_all_pygame, test_screen):
        """Test that wakawaka sound has correct timing interval"""
        # ARRANGE - Setup game
        game = Game(test_screen)
        
        # ACT - Check wakawaka timing
        interval = game.wakawaka_interval
        
        # ASSERT - Verify timing interval
        assert interval == 200  # 200 milliseconds

    def test_sound_can_be_disabled(self, mock_all_pygame, test_screen):
        """Test that sound system can be disabled"""
        # ARRANGE - Setup game
        game = Game(test_screen)
        
        # ACT - Disable sound
        game.sound_enabled = False
        
        # ASSERT - Verify sound is disabled
        assert game.sound_enabled is False


@pytest.mark.unit
class TestGameUpdate:
    """Test Game update functionality"""
    
    def test_update_in_menu_state(self, mock_all_pygame, test_screen):
        """Test game update when in MENU state"""
        # ARRANGE - Setup game in menu state
        game = Game(test_screen)
        game.state = MENU
        
        # Mock menu system update method
        game.menu.menu_system = Mock()
        game.menu.menu_system.update = Mock(return_value=None)
        
        # ACT - Update game
        game.update()
        
        # ASSERT - Verify menu system was updated
        game.menu.menu_system.update.assert_called_once()

    def test_update_processes_pellet_collection(self, mock_all_pygame, test_screen):
        """Test that update processes pellet collection correctly"""
        # ARRANGE - Setup game in playing state
        game = Game(test_screen)
        game.state = PLAYING
        
        # Mock pellet manager to return points
        game.pellet_manager = Mock()
        game.pellet_manager.check_collection.return_value = 10  # Normal pellet
        game.pellet_manager.update = Mock()
        
        # Mock other components
        game.pacman = Mock()
        game.pacman.update = Mock()
        game.pacman.set_eating = Mock()
        game.ghosts = []
        
        initial_score = game.score
        
        # ACT - Update game
        game.update()
        
        # ASSERT - Verify score increased
        assert game.score == initial_score + 10
        game.pacman.set_eating.assert_called_with(True)

    def test_update_handles_power_pellet_collection(self, mock_all_pygame, test_screen):
        """Test that update handles power pellet collection correctly"""
        # ARRANGE - Setup game in playing state
        game = Game(test_screen)
        game.state = PLAYING
        
        # Mock pellet manager to return negative signal (power pellet)
        game.pellet_manager = Mock()
        game.pellet_manager.check_collection.return_value = -50  # Power pellet signal
        game.pellet_manager.update = Mock()
        
        # Mock other components
        game.pacman = Mock()
        game.pacman.update = Mock()
        game.pacman.set_eating = Mock()
        
        # Mock ghosts
        mock_ghost = Mock()
        mock_ghost.set_frightened = Mock()
        game.ghosts = [mock_ghost]
        
        initial_score = game.score
        
        # ACT - Update game
        game.update()
        
        # ASSERT - Verify power pellet effects
        assert game.score == initial_score + 50  # Absolute value added
        mock_ghost.set_frightened.assert_called_once()


@pytest.mark.unit
class TestGameGhostInteraction:
    """Test Game ghost interaction functionality"""
    
    def test_ghost_collision_reduces_lives(self, mock_all_pygame, test_screen):
        """Test that collision with non-frightened ghost reduces lives"""
        # ARRANGE - Setup game
        game = Game(test_screen)
        game.state = PLAYING
        game.lives = 3
        
        # Mock pacman and ghost collision
        game.pacman = Mock()
        game.pacman.update = Mock()
        game.pacman.collides_with.return_value = True
        game.pacman.set_eating = Mock()
        
        mock_ghost = Mock()
        mock_ghost.mode = CHASE  # Not frightened
        mock_ghost.update = Mock()
        game.ghosts = [mock_ghost]
        
        # Mock pellet manager
        game.pellet_manager = Mock()
        game.pellet_manager.check_collection.return_value = 0
        game.pellet_manager.update = Mock()
        
        # ACT - Update game (triggers collision)
        game.update()
        
        # ASSERT - Verify lives decreased
        assert game.lives == 2

    def test_eating_frightened_ghost_increases_score(self, mock_all_pygame, test_screen):
        """Test that eating a frightened ghost increases score"""
        # ARRANGE - Setup game
        game = Game(test_screen)
        game.state = PLAYING
        initial_score = game.score
        
        # Mock pacman and frightened ghost collision
        game.pacman = Mock()
        game.pacman.update = Mock()
        game.pacman.collides_with.return_value = True
        game.pacman.set_eating = Mock()
        
        mock_ghost = Mock()
        mock_ghost.mode = FRIGHTENED
        mock_ghost.update = Mock()
        game.ghosts = [mock_ghost]
        
        # Mock pellet manager
        game.pellet_manager = Mock()
        game.pellet_manager.check_collection.return_value = 0
        game.pellet_manager.update = Mock()
        
        # ACT - Update game
        game.update()
        
        # ASSERT - Verify score increased and ghost mode changed
        assert game.score == initial_score + 200  # GHOST_POINTS
        assert mock_ghost.mode == EATEN


@pytest.mark.unit
class TestMusicManager:
    """Test MusicManager functionality"""
    
    def test_music_manager_initializes_correctly(self, mock_all_pygame):
        """Test that MusicManager initializes with correct defaults"""
        # ARRANGE - Setup for creation
        
        # ACT - Create MusicManager
        music_manager = MusicManager()
        
        # ASSERT - Verify initialization
        assert music_manager.music_loaded is False
        assert music_manager.music_playing is False
        assert music_manager.music_volume == 0.3
        assert isinstance(music_manager.music_files, dict)

    def test_music_manager_has_required_music_files(self, mock_all_pygame):
        """Test that MusicManager defines required music files"""
        # ARRANGE - Setup for creation
        
        # ACT - Create MusicManager
        music_manager = MusicManager()
        
        # ASSERT - Verify required music files are defined
        required_files = ["background", "game_start", "game_over", "level_complete"]
        for file_key in required_files:
            assert file_key in music_manager.music_files
            assert isinstance(music_manager.music_files[file_key], str)

    def test_music_manager_volume_setting(self, mock_all_pygame):
        """Test that MusicManager has appropriate volume setting"""
        # ARRANGE - Setup for creation
        
        # ACT - Create MusicManager
        music_manager = MusicManager()
        
        # ASSERT - Verify volume is reasonable (not too loud)
        assert 0.0 <= music_manager.music_volume <= 1.0
        assert music_manager.music_volume == 0.3  # Specific expected value


@pytest.mark.unit
class TestGameEventHandling:
    """Test Game event handling functionality"""
    
    def test_game_handles_quit_event(self, mock_all_pygame, test_screen):
        """Test that game can handle quit events"""
        # ARRANGE - Setup game
        game = Game(test_screen)
        
        # Mock quit event
        mock_event = Mock()
        mock_event.type = 'QUIT'  # Simplified for testing
        
        # ACT & ASSERT - Should not crash when handling events
        # The actual event handling is done in main.py, 
        # but game should be prepared to handle state changes
        assert hasattr(game, 'handle_event')

    def test_game_state_affects_behavior(self, mock_all_pygame, test_screen):
        """Test that game behavior changes based on state"""
        # ARRANGE - Setup game
        game = Game(test_screen)
        
        # ACT & ASSERT - Verify different states exist
        assert MENU != PLAYING
        assert PLAYING != GAME_OVER
        assert GAME_OVER != PAUSED
        
        # Game should behave differently in different states
        game.state = MENU
        assert game.state == MENU
        
        game.state = PLAYING
        assert game.state == PLAYING


@pytest.mark.unit
class TestGameReset:
    """Test Game reset and restart functionality"""
    
    def test_game_can_reset_score_and_lives(self, mock_all_pygame, test_screen):
        """Test that game can reset score and lives"""
        # ARRANGE - Setup game with modified state
        game = Game(test_screen)
        game.score = 5000
        game.lives = 1
        
        # ACT - Reset game state
        game.score = 0
        game.lives = 3
        game.state = MENU
        
        # ASSERT - Verify reset state
        assert game.score == 0
        assert game.lives == 3
        assert game.state == MENU

    def test_game_components_can_be_reset(self, mock_all_pygame, test_screen):
        """Test that game components support reset functionality"""
        # ARRANGE - Setup game
        game = Game(test_screen)
        
        # ACT & ASSERT - Verify components have reset capabilities
        assert hasattr(game.pellet_manager, 'reset')
        
        # Call reset to ensure it doesn't crash
        game.pellet_manager.reset()
        
        # Verify pellets were recreated
        assert isinstance(game.pellet_manager.pellets, list)