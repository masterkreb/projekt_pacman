"""
Unit tests for the Pacman player class following Arrange-Act-Assert pattern.
Tests cover movement, positioning, collision detection, and speed boost system.
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
pygame_mock.K_w = 'w'
pygame_mock.K_UP = 'up'
pygame_mock.K_s = 's'
pygame_mock.K_DOWN = 'down'
pygame_mock.K_a = 'a'
pygame_mock.K_LEFT = 'left'
pygame_mock.K_d = 'd'
pygame_mock.K_RIGHT = 'right'

# Mock sprite loading
sprite_mock = MagicMock()
sprite_mock.get_size.return_value = (64, 64)
sprite_mock.convert_alpha.return_value = sprite_mock
pygame_mock.image.load.return_value = sprite_mock

sys.modules['pygame'] = pygame_mock

from src.constants import *
from src.player import Pacman


class TestPacman(unittest.TestCase):
    """Test cases for the Pacman class using Arrange-Act-Assert pattern."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        with patch('builtins.print'):  # Suppress any print statements
            self.pacman = Pacman(10, 15)

    def test_pacman_initialization(self):
        """Test Pacman object initialization with correct starting position."""
        # ARRANGE
        start_x = 5
        start_y = 8
        expected_pixel_x = start_x * GRID_SIZE
        expected_pixel_y = start_y * GRID_SIZE
        
        # ACT
        with patch('builtins.print'):
            pacman = Pacman(start_x, start_y)
        
        # ASSERT
        self.assertEqual(pacman.start_x, start_x)
        self.assertEqual(pacman.start_y, start_y)
        self.assertEqual(pacman.x, expected_pixel_x)
        self.assertEqual(pacman.y, expected_pixel_y)
        self.assertEqual(pacman.grid_x, start_x)
        self.assertEqual(pacman.grid_y, start_y)
        self.assertEqual(pacman.size, PACMAN_SIZE)
        self.assertFalse(pacman.speed_boost_active)
        self.assertEqual(pacman.speed, PACMAN_SPEED)

    def test_activate_speed_boost(self):
        """Test speed boost activation sets correct state and timer."""
        # ARRANGE
        initial_speed_boost_active = self.pacman.speed_boost_active
        expected_speed = PACMAN_SPEED_BOOST
        expected_duration = 360  # 6 seconds at 60 FPS
        
        # ACT
        with patch('builtins.print'):  # Suppress the "Speed boost activated!" message
            self.pacman.activate_speed_boost()
        
        # ASSERT
        self.assertFalse(initial_speed_boost_active)  # Verify initial state
        self.assertTrue(self.pacman.speed_boost_active)
        self.assertEqual(self.pacman.speed, expected_speed)
        self.assertEqual(self.pacman.speed_boost_timer, expected_duration)
        self.assertEqual(self.pacman.speed_boost_duration, expected_duration)

    def test_set_direction_up(self):
        """Test setting direction to UP updates next_direction correctly."""
        # ARRANGE
        direction = UP
        expected_next_direction = "up"
        
        # ACT
        self.pacman.set_direction(direction)
        
        # ASSERT
        self.assertEqual(self.pacman.next_direction, expected_next_direction)

    def test_set_direction_down(self):
        """Test setting direction to DOWN updates next_direction correctly."""
        # ARRANGE
        direction = DOWN
        expected_next_direction = "down"
        
        # ACT
        self.pacman.set_direction(direction)
        
        # ASSERT
        self.assertEqual(self.pacman.next_direction, expected_next_direction)

    def test_set_direction_left(self):
        """Test setting direction to LEFT updates next_direction correctly."""
        # ARRANGE
        direction = LEFT
        expected_next_direction = "left"
        
        # ACT
        self.pacman.set_direction(direction)
        
        # ASSERT
        self.assertEqual(self.pacman.next_direction, expected_next_direction)

    def test_set_direction_right(self):
        """Test setting direction to RIGHT updates next_direction correctly."""
        # ARRANGE
        direction = RIGHT
        expected_next_direction = "right"
        
        # ACT
        self.pacman.set_direction(direction)
        
        # ASSERT
        self.assertEqual(self.pacman.next_direction, expected_next_direction)

    def test_set_direction_stop(self):
        """Test setting direction to STOP clears next_direction."""
        # ARRANGE
        direction = STOP
        # First set a direction, then stop
        self.pacman.set_direction(UP)
        
        # ACT
        self.pacman.set_direction(direction)
        
        # ASSERT
        self.assertIsNone(self.pacman.next_direction)

    def test_set_velocity_from_direction_up(self):
        """Test setting velocity for upward movement."""
        # ARRANGE
        direction = "up"
        expected_velocity_x = 0
        expected_velocity_y = -self.pacman.speed
        expected_current_direction = "up"
        
        # ACT
        self.pacman.set_velocity_from_direction(direction)
        
        # ASSERT
        self.assertEqual(self.pacman.velocity_x, expected_velocity_x)
        self.assertEqual(self.pacman.velocity_y, expected_velocity_y)
        self.assertEqual(self.pacman.current_direction, expected_current_direction)

    def test_set_velocity_from_direction_right(self):
        """Test setting velocity for rightward movement."""
        # ARRANGE
        direction = "right"
        expected_velocity_x = self.pacman.speed
        expected_velocity_y = 0
        expected_current_direction = "right"
        
        # ACT
        self.pacman.set_velocity_from_direction(direction)
        
        # ASSERT
        self.assertEqual(self.pacman.velocity_x, expected_velocity_x)
        self.assertEqual(self.pacman.velocity_y, expected_velocity_y)
        self.assertEqual(self.pacman.current_direction, expected_current_direction)

    def test_collides_with_object_with_get_center(self):
        """Test collision detection with object that has get_center method."""
        # ARRANGE
        other_object = Mock()
        other_object.get_center.return_value = (self.pacman.x + 8, self.pacman.y + 8)
        other_object.size = 16
        
        # Mock get_pixel_position method
        self.pacman.get_pixel_position = Mock(return_value=(self.pacman.x + 8, self.pacman.y + 8))
        
        # ACT
        result = self.pacman.collides_with(other_object)
        
        # ASSERT
        self.assertTrue(result)

    def test_collides_with_object_without_get_center(self):
        """Test collision detection with object without get_center method."""
        # ARRANGE
        other_object = Mock()
        other_object.x = self.pacman.x + 5
        other_object.y = self.pacman.y + 5
        other_object.size = 16
        # Remove get_center method
        del other_object.get_center
        
        # Mock get_pixel_position method
        self.pacman.get_pixel_position = Mock(return_value=(self.pacman.x + 8, self.pacman.y + 8))
        
        # ACT
        result = self.pacman.collides_with(other_object)
        
        # ASSERT
        self.assertTrue(result)

    def test_no_collision_when_objects_far_apart(self):
        """Test no collision when objects are far apart."""
        # ARRANGE
        other_object = Mock()
        other_object.get_center.return_value = (self.pacman.x + 100, self.pacman.y + 100)
        other_object.size = 16
        
        # Mock get_pixel_position method  
        self.pacman.get_pixel_position = Mock(return_value=(self.pacman.x + 8, self.pacman.y + 8))
        
        # ACT
        result = self.pacman.collides_with(other_object)
        
        # ASSERT
        self.assertFalse(result)

    def test_get_pressed_direction_with_up_key(self):
        """Test getting direction from pressed keys - UP key."""
        # ARRANGE
        # Create a mock pacman with a simpler move_keys structure for testing
        simple_pacman = Mock()
        simple_pacman.move_keys = {
            "up": ['up_key'],
            "down": ['down_key'], 
            "left": ['left_key'],
            "right": ['right_key']
        }
        
        keys = {'up_key': True, 'down_key': False, 'left_key': False, 'right_key': False}
        expected_direction = "up"
        
        # Use the actual method but with our mock object
        from src.player import Pacman
        
        # ACT
        result = Pacman.get_pressed_direction(simple_pacman, keys)
        
        # ASSERT
        self.assertEqual(result, expected_direction)

    def test_get_pressed_direction_no_keys_pressed(self):
        """Test getting direction when no keys are pressed."""
        # ARRANGE
        simple_pacman = Mock()
        simple_pacman.move_keys = {
            "up": ['up_key'],
            "down": ['down_key'], 
            "left": ['left_key'],
            "right": ['right_key']
        }
        
        keys = {'up_key': False, 'down_key': False, 'left_key': False, 'right_key': False}
        
        # ACT
        from src.player import Pacman
        result = Pacman.get_pressed_direction(simple_pacman, keys)
        
        # ASSERT
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()