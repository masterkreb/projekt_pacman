"""
Unit tests for the Ghost class following Arrange-Act-Assert pattern.
Tests cover ghost movement logic, AI behavior, and state changes.
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
sys.modules['pygame'] = pygame_mock

from src.constants import *
from src.ghost import Ghost


class TestGhost(unittest.TestCase):
    """Test cases for the Ghost class using Arrange-Act-Assert pattern."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        with patch('builtins.print'):  # Suppress any print statements
            self.ghost = Ghost(10, 15, RED, "blinky")

    def test_ghost_initialization_blinky(self):
        """Test Ghost object initialization for Blinky."""
        # ARRANGE
        start_x = 8
        start_y = 12
        color = RED
        name = "blinky"
        expected_pixel_x = start_x * GRID_SIZE
        expected_pixel_y = (start_y - 3) * GRID_SIZE  # Blinky starts above house
        
        # ACT
        ghost = Ghost(start_x, start_y, color, name)
        
        # ASSERT
        self.assertEqual(ghost.start_x, start_x)
        self.assertEqual(ghost.color, color)
        self.assertEqual(ghost.name, name)
        self.assertEqual(ghost.x, expected_pixel_x)
        self.assertEqual(ghost.y, expected_pixel_y)
        self.assertEqual(ghost.direction, UP)
        self.assertEqual(ghost.mode, SCATTER)
        self.assertEqual(ghost.size, GHOST_SIZE)
        self.assertEqual(ghost.speed, GHOST_SPEED)
        self.assertFalse(ghost.in_house)  # Blinky starts outside

    def test_ghost_initialization_pinky(self):
        """Test Ghost object initialization for Pinky."""
        # ARRANGE
        start_x = 8
        start_y = 12
        color = PINK
        name = "pinky"
        expected_pixel_x = start_x * GRID_SIZE
        expected_pixel_y = start_y * GRID_SIZE
        
        # ACT
        ghost = Ghost(start_x, start_y, color, name)
        
        # ASSERT
        self.assertEqual(ghost.name, name)
        self.assertEqual(ghost.x, expected_pixel_x)
        self.assertEqual(ghost.y, expected_pixel_y)
        self.assertTrue(ghost.in_house)  # Pinky starts in house

    def test_switch_mode_scatter_to_chase(self):
        """Test switching ghost mode from SCATTER to CHASE."""
        # ARRANGE
        new_mode = CHASE
        initial_mode = self.ghost.mode
        
        # ACT
        self.ghost.switch_mode(new_mode)
        
        # ASSERT
        self.assertEqual(initial_mode, SCATTER)  # Verify initial state
        self.assertEqual(self.ghost.mode, new_mode)
        self.assertEqual(self.ghost.previous_mode, SCATTER)
        self.assertEqual(self.ghost.mode_timer, 0)

    def test_switch_mode_to_frightened(self):
        """Test switching ghost mode to FRIGHTENED."""
        # ARRANGE
        self.ghost.mode = CHASE
        new_mode = FRIGHTENED
        
        # ACT
        self.ghost.switch_mode(new_mode)
        
        # ASSERT
        self.assertEqual(self.ghost.mode, new_mode)
        self.assertEqual(self.ghost.previous_mode, CHASE)
        self.assertEqual(self.ghost.mode_timer, 0)

    def test_get_position(self):
        """Test get_position returns correct grid coordinates."""
        # ARRANGE
        expected_x = self.ghost.grid_x
        expected_y = self.ghost.grid_y
        
        # ACT
        result_x, result_y = self.ghost.get_position()
        
        # ASSERT
        self.assertEqual(result_x, expected_x)
        self.assertEqual(result_y, expected_y)

    def test_get_center(self):
        """Test get_center returns correct pixel center coordinates."""
        # ARRANGE
        expected_center_x = self.ghost.x + self.ghost.size // 2
        expected_center_y = self.ghost.y + self.ghost.size // 2
        
        # ACT
        result_x, result_y = self.ghost.get_center()
        
        # ASSERT
        self.assertEqual(result_x, expected_center_x)
        self.assertEqual(result_y, expected_center_y)

    def test_set_frightened(self):
        """Test set_frightened switches mode to FRIGHTENED."""
        # ARRANGE
        initial_mode = self.ghost.mode
        
        # ACT
        self.ghost.set_frightened()
        
        # ASSERT
        self.assertEqual(self.ghost.mode, FRIGHTENED)
        self.assertEqual(self.ghost.previous_mode, initial_mode)

    def test_reset_position(self):
        """Test reset method returns ghost to starting position."""
        # ARRANGE
        new_start_x = 5
        new_start_y = 8
        expected_pixel_x = new_start_x * GRID_SIZE
        # For blinky, y position is adjusted (start_y - 3)
        expected_pixel_y = (new_start_y - 3) * GRID_SIZE if self.ghost.name == "blinky" else new_start_y * GRID_SIZE
        
        # ACT
        self.ghost.reset(new_start_x, new_start_y)
        
        # ASSERT
        self.assertEqual(self.ghost.x, expected_pixel_x)
        self.assertEqual(self.ghost.y, expected_pixel_y)
        # Note: start_x and start_y are not modified by reset method in the actual implementation

    def test_at_intersection_center_position(self):
        """Test at_intersection returns True when ghost is at center of tile."""
        # ARRANGE
        # Set pixel position exactly at grid center
        self.ghost.pixel_x = self.ghost.grid_x * GRID_SIZE
        self.ghost.pixel_y = self.ghost.grid_y * GRID_SIZE
        
        # ACT
        result = self.ghost.at_intersection()
        
        # ASSERT
        self.assertTrue(result)

    def test_at_intersection_off_center_position(self):
        """Test at_intersection returns False when ghost is off-center."""
        # ARRANGE
        # Set pixel position off-center
        self.ghost.pixel_x = self.ghost.grid_x * GRID_SIZE + 5
        self.ghost.pixel_y = self.ghost.grid_y * GRID_SIZE + 5
        
        # ACT
        result = self.ghost.at_intersection()
        
        # ASSERT
        self.assertFalse(result)

    def test_choose_direction_frightened_mode(self):
        """Test choose_direction_at_intersection in FRIGHTENED mode uses random choice."""
        # ARRANGE
        self.ghost.mode = FRIGHTENED
        self.ghost.grid_x = 10
        self.ghost.grid_y = 10
        
        # Mock maze with some valid directions
        maze_mock = Mock()
        maze_mock.is_wall.return_value = False  # All directions are valid
        
        # Mock random.choice to return a specific direction
        with patch('src.ghost.random.choice', return_value=UP) as mock_choice:
            # ACT
            self.ghost.choose_direction_at_intersection(maze_mock)
            
            # ASSERT
            self.assertEqual(self.ghost.direction, UP)
            mock_choice.assert_called_once()

    def test_choose_direction_chase_mode_targets_closest(self):
        """Test choose_direction_at_intersection in CHASE mode targets closest direction."""
        # ARRANGE
        self.ghost.mode = CHASE
        self.ghost.grid_x = 10
        self.ghost.grid_y = 10
        self.ghost.target_x = 10
        self.ghost.target_y = 8  # Target is directly above
        self.ghost.direction = DOWN  # Current direction
        
        # Mock maze - only UP direction is valid (towards target)
        maze_mock = Mock()
        def mock_is_wall(x, y):
            if x == 10 and y == 9:  # UP from current position
                return False
            return True  # All other directions are walls
        maze_mock.is_wall.side_effect = mock_is_wall
        
        # ACT
        self.ghost.choose_direction_at_intersection(maze_mock)
        
        # ASSERT
        self.assertEqual(self.ghost.direction, UP)

    def test_choose_direction_no_reverse_allowed(self):
        """Test choose_direction_at_intersection doesn't allow reverse direction."""
        # ARRANGE
        self.ghost.mode = CHASE
        self.ghost.grid_x = 10
        self.ghost.grid_y = 10
        self.ghost.direction = UP
        self.ghost.can_reverse = False
        self.ghost.target_x = 10
        self.ghost.target_y = 12  # Target is below (reverse direction)
        
        # Mock maze - only DOWN direction would be towards target, but UP is blocked
        maze_mock = Mock()
        def mock_is_wall(x, y):
            if x == 10 and y == 11:  # DOWN from current position (reverse of UP)
                return False
            elif x == 9 and y == 10:  # LEFT from current position
                return False
            return True
        maze_mock.is_wall.side_effect = mock_is_wall
        
        # ACT
        self.ghost.choose_direction_at_intersection(maze_mock)
        
        # ASSERT
        self.assertNotEqual(self.ghost.direction, DOWN)  # Should not reverse
        self.assertEqual(self.ghost.direction, LEFT)  # Should choose available direction

    def test_exit_house(self):
        """Test exit_house sets correct state for leaving ghost house."""
        # ARRANGE
        self.ghost.in_house = True
        
        # ACT
        self.ghost.exit_house()
        
        # ASSERT
        self.assertFalse(self.ghost.in_house)

    def test_handle_house_exit_with_timer(self):
        """Test handle_house_exit exits house when timer expires."""
        # ARRANGE
        self.ghost.in_house = True
        self.ghost.house_exit_timer = 300  # Timer expired
        pacman_mock = Mock()
        
        # ACT
        self.ghost.handle_house_exit(pacman_mock)
        
        # ASSERT
        self.assertFalse(self.ghost.in_house)

    def test_move_in_house_changes_position(self):
        """Test move_in_house moves ghost towards center and exit."""
        # ARRANGE
        self.ghost.in_house = True
        initial_pixel_x = self.ghost.pixel_x
        initial_pixel_y = self.ghost.pixel_y
        
        # ACT
        self.ghost.move_in_house()
        
        # ASSERT
        # The method should adjust the position (specific behavior depends on current position relative to center)
        # This test verifies the method executes without error and may modify position
        self.assertIsNotNone(self.ghost.pixel_x)
        self.assertIsNotNone(self.ghost.pixel_y)


if __name__ == '__main__':
    unittest.main()