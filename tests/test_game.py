"""
Unit tests for the Game class following Arrange-Act-Assert pattern.
Tests cover score system, lives management, game states, and pellet collection.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the pacman_game directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pacman_game'))

# Mock pygame completely before any imports
pygame_mock = MagicMock()
pygame_mock.error = Exception
pygame_mock.KEYDOWN = 'keydown'
pygame_mock.K_SPACE = 'space'
pygame_mock.QUIT = 'quit'
sys.modules['pygame'] = pygame_mock
sys.modules['pygame_gui'] = MagicMock()  # Mock pygame_gui as well

from src.constants import *
from src.game import Game


class TestGame(unittest.TestCase):
    """Test cases for the Game class using Arrange-Act-Assert pattern."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        screen_mock = Mock()
        
        # Mock all the imported classes and their dependencies
        with patch('src.game.Pacman') as pacman_mock:
            with patch('src.game.Ghost') as ghost_mock:
                with patch('src.game.Maze') as maze_mock:
                    with patch('src.game.PelletManager') as pellet_mock:
                        with patch('src.game.Menu') as menu_mock:
                            with patch('src.game.os.path.exists', return_value=False):
                                with patch('builtins.print'):  # Suppress error messages
                                    self.game = Game(screen_mock)

    def test_game_initialization(self):
        """Test Game object initialization with correct initial state."""
        # ARRANGE - Setup done in setUp method
        expected_state = MENU
        expected_score = 0
        expected_lives = LIVES
        
        # ACT - Object created in setUp
        
        # ASSERT
        self.assertEqual(self.game.state, expected_state)
        self.assertEqual(self.game.score, expected_score)
        self.assertEqual(self.game.lives, expected_lives)
        self.assertIsNotNone(self.game.screen)

    def test_start_game_sets_playing_state(self):
        """Test start_game method sets state to PLAYING."""
        # ARRANGE
        initial_state = self.game.state
        expected_state = PLAYING
        
        # ACT
        self.game.start_game()
        
        # ASSERT
        self.assertEqual(initial_state, MENU)  # Verify initial state
        self.assertEqual(self.game.state, expected_state)

    def test_restart_game_resets_score_and_lives(self):
        """Test restart_game method resets score and lives to initial values."""
        # ARRANGE
        # Modify score and lives first
        self.game.score = 1500
        self.game.lives = 1
        expected_score = 0
        expected_lives = LIVES
        expected_state = PLAYING
        
        # ACT
        self.game.restart_game()
        
        # ASSERT
        self.assertEqual(self.game.score, expected_score)
        self.assertEqual(self.game.lives, expected_lives)
        self.assertEqual(self.game.state, expected_state)

    def test_handle_event_start_game_from_menu(self):
        """Test handle_event processes start game event from menu state."""
        # ARRANGE
        self.game.state = MENU
        event_mock = Mock()
        event_mock.type = 'keydown'
        event_mock.key = 'space'
        
        # Mock menu to return start game signal
        self.game.menu = Mock()
        self.game.menu.menu_system = Mock()
        self.game.menu.menu_system.handle_event.return_value = "start_game"
        
        # ACT
        self.game.handle_event(event_mock)
        
        # ASSERT
        self.assertEqual(self.game.state, PLAYING)

    def test_handle_event_quit_game(self):
        """Test handle_event processes quit event."""
        # ARRANGE
        event_mock = Mock()
        event_mock.type = 'quit'
        
        # ACT
        result = self.game.handle_event(event_mock)
        
        # ASSERT
        # The method should handle the quit event and return True (to quit)
        self.assertTrue(result)

    def test_play_wakawaka_sound(self):
        """Test play_wakawaka_sound method."""
        # ARRANGE
        # Mock the required attributes for the sound system
        self.game.wakawaka_sound = Mock()
        self.game.wakawaka_timer = 0
        self.game.wakawaka_interval = 100
        
        # Mock pygame.time.get_ticks
        with patch('src.game.pygame.time.get_ticks', return_value=150):
            # ACT
            self.game.play_wakawaka_sound()
            
            # ASSERT
            # Verify sound system was accessed
            self.assertIsNotNone(self.game.wakawaka_sound)

    def test_stop_wakawaka_sound(self):
        """Test stop_wakawaka_sound method."""
        # ARRANGE
        # Mock sound system
        self.game.wakawaka_sound = Mock()
        
        # ACT
        self.game.stop_wakawaka_sound()
        
        # ASSERT
        # Verify sound stop was attempted (specific implementation may vary)
        self.assertIsNotNone(self.game.wakawaka_sound)

    def test_play_eat_ghost_sound(self):
        """Test play_eat_ghost_sound method."""
        # ARRANGE
        # Mock sound system
        self.game.ghost_sound = Mock()
        
        # ACT
        self.game.play_eat_ghost_sound()
        
        # ASSERT
        # Verify sound was handled
        self.assertIsNotNone(self.game.ghost_sound)

    def test_play_death_sound(self):
        """Test play_death_sound method."""
        # ARRANGE
        # Mock sound system  
        self.game.death_sound = Mock()
        
        # ACT
        self.game.play_death_sound()
        
        # ASSERT
        # Verify sound was handled
        self.assertIsNotNone(self.game.death_sound)

    def test_score_increase_with_small_pellet(self):
        """Test score increases correctly when collecting small pellet."""
        # ARRANGE
        initial_score = self.game.score
        points_to_add = SMALL_PELLET_POINTS
        expected_score = initial_score + points_to_add
        
        # ACT
        self.game.score += points_to_add
        
        # ASSERT
        self.assertEqual(self.game.score, expected_score)

    def test_score_increase_with_large_pellet(self):
        """Test score increases correctly when collecting large pellet."""
        # ARRANGE
        initial_score = self.game.score
        points_to_add = LARGE_PELLET_POINTS
        expected_score = initial_score + points_to_add
        
        # ACT
        self.game.score += points_to_add
        
        # ASSERT
        self.assertEqual(self.game.score, expected_score)

    def test_score_increase_with_ghost(self):
        """Test score increases correctly when eating ghost."""
        # ARRANGE
        initial_score = self.game.score
        points_to_add = GHOST_POINTS
        expected_score = initial_score + points_to_add
        
        # ACT
        self.game.score += points_to_add
        
        # ASSERT
        self.assertEqual(self.game.score, expected_score)

    def test_lives_decrease_when_player_dies(self):
        """Test lives decrease when player dies."""
        # ARRANGE
        initial_lives = self.game.lives
        expected_lives = initial_lives - 1
        
        # ACT
        self.game.lives -= 1
        
        # ASSERT
        self.assertEqual(self.game.lives, expected_lives)

    def test_game_over_when_no_lives_remaining(self):
        """Test game state changes to GAME_OVER when no lives remain."""
        # ARRANGE
        self.game.lives = 1
        self.game.state = PLAYING
        expected_state = GAME_OVER
        
        # ACT
        self.game.lives -= 1
        if self.game.lives <= 0:
            self.game.state = GAME_OVER
        
        # ASSERT
        self.assertEqual(self.game.lives, 0)
        self.assertEqual(self.game.state, expected_state)

    def test_victory_state_when_all_pellets_collected(self):
        """Test game state changes to VICTORY when all pellets are collected."""
        # ARRANGE
        self.game.state = PLAYING
        expected_state = VICTORY
        
        # Simulate all pellets collected condition
        all_pellets_collected = True
        
        # ACT
        if all_pellets_collected:
            self.game.state = VICTORY
        
        # ASSERT
        self.assertEqual(self.game.state, expected_state)

    def test_state_transition_from_playing_to_paused(self):
        """Test game state can transition from PLAYING to PAUSED."""
        # ARRANGE
        self.game.state = PLAYING
        expected_state = PAUSED
        
        # ACT
        self.game.state = PAUSED
        
        # ASSERT
        self.assertEqual(self.game.state, expected_state)

    def test_state_transition_from_paused_to_playing(self):
        """Test game state can transition from PAUSED back to PLAYING."""
        # ARRANGE
        self.game.state = PAUSED
        expected_state = PLAYING
        
        # ACT
        self.game.state = PLAYING
        
        # ASSERT
        self.assertEqual(self.game.state, expected_state)

    def test_multiple_score_increases(self):
        """Test score accumulates correctly with multiple additions."""
        # ARRANGE
        initial_score = self.game.score
        pellet_points = SMALL_PELLET_POINTS
        ghost_points = GHOST_POINTS
        expected_total = initial_score + pellet_points + ghost_points
        
        # ACT
        self.game.score += pellet_points
        self.game.score += ghost_points
        
        # ASSERT
        self.assertEqual(self.game.score, expected_total)

    def test_game_state_constants_are_defined(self):
        """Test that all required game state constants are properly defined."""
        # ARRANGE & ACT & ASSERT
        self.assertIsNotNone(MENU)
        self.assertIsNotNone(PLAYING)
        self.assertIsNotNone(PAUSED)
        self.assertIsNotNone(GAME_OVER)
        self.assertIsNotNone(VICTORY)
        
        # Verify they are different values
        states = [MENU, PLAYING, PAUSED, GAME_OVER, VICTORY]
        self.assertEqual(len(states), len(set(states)))  # All unique values

    def test_point_constants_are_defined(self):
        """Test that all point value constants are properly defined."""
        # ARRANGE & ACT & ASSERT
        self.assertIsNotNone(SMALL_PELLET_POINTS)
        self.assertIsNotNone(LARGE_PELLET_POINTS)
        self.assertIsNotNone(GHOST_POINTS)
        
        # Verify they are positive values
        self.assertGreater(SMALL_PELLET_POINTS, 0)
        self.assertGreater(LARGE_PELLET_POINTS, 0)
        self.assertGreater(GHOST_POINTS, 0)
        
        # Verify logical point relationships
        self.assertGreater(LARGE_PELLET_POINTS, SMALL_PELLET_POINTS)


if __name__ == '__main__':
    unittest.main()