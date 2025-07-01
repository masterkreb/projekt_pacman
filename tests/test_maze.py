"""
Unit tests for the Maze class following Arrange-Act-Assert pattern.
Tests cover layout parsing, collision checking with walls, and tunnel functionality.
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
from src.maze import Maze


class TestMaze(unittest.TestCase):
    """Test cases for the Maze class using Arrange-Act-Assert pattern."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock the nodes module to avoid dependencies
        with patch('src.maze.build_nodes_and_graph', return_value=([], {})):
            with patch('builtins.print'):  # Suppress any print statements
                self.maze = Maze()

    def test_maze_initialization(self):
        """Test Maze object initialization with correct dimensions."""
        # ARRANGE - Setup done in setUp method
        expected_height = 31  # Length of layout_strings
        expected_width = 28   # Length of first layout string
        
        # ACT - Object created in setUp
        
        # ASSERT
        self.assertEqual(self.maze.height, expected_height)
        self.assertEqual(self.maze.width, expected_width)
        self.assertIsNotNone(self.maze.layout)
        self.assertEqual(len(self.maze.layout), expected_height)
        self.assertEqual(len(self.maze.layout[0]), expected_width)

    def test_is_wall_with_wall_position(self):
        """Test is_wall returns True for wall positions."""
        # ARRANGE
        # Top-left corner should be a wall (# in layout)
        x, y = 0, 0
        expected_result = True
        
        # ACT
        result = self.maze.is_wall(x, y)
        
        # ASSERT
        self.assertEqual(result, expected_result)

    def test_is_wall_with_empty_position(self):
        """Test is_wall returns False for empty positions."""
        # ARRANGE
        # Find a position that should be empty (. in layout)
        x, y = 1, 1  # This should be empty based on the layout
        expected_result = False
        
        # ACT
        result = self.maze.is_wall(x, y)
        
        # ASSERT
        self.assertEqual(result, expected_result)

    def test_is_wall_out_of_bounds(self):
        """Test is_wall returns True for out of bounds positions."""
        # ARRANGE
        x, y = -1, -1  # Out of bounds
        expected_result = True
        
        # ACT
        result = self.maze.is_wall(x, y)
        
        # ASSERT
        self.assertEqual(result, expected_result)

    def test_is_wall_out_of_bounds_positive(self):
        """Test is_wall returns True for positive out of bounds positions."""
        # ARRANGE
        x, y = 100, 100  # Out of bounds
        expected_result = True
        
        # ACT
        result = self.maze.is_wall(x, y)
        
        # ASSERT
        self.assertEqual(result, expected_result)

    def test_is_empty_with_empty_position(self):
        """Test is_empty returns True for empty positions."""
        # ARRANGE
        x, y = 1, 1  # Should be empty
        expected_result = True
        
        # ACT
        result = self.maze.is_empty(x, y)
        
        # ASSERT
        self.assertEqual(result, expected_result)

    def test_is_empty_with_wall_position(self):
        """Test is_empty returns False for wall positions."""
        # ARRANGE
        x, y = 0, 0  # Should be a wall
        expected_result = False
        
        # ACT
        result = self.maze.is_empty(x, y)
        
        # ASSERT
        self.assertEqual(result, expected_result)

    def test_get_valid_positions_returns_list(self):
        """Test get_valid_positions returns a list of valid positions."""
        # ARRANGE
        # No specific arrangement needed
        
        # ACT
        result = self.maze.get_valid_positions()
        
        # ASSERT
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)  # Should have some valid positions
        
        # Check that all returned positions are actually valid
        for x, y in result:
            self.assertTrue(self.maze.is_empty(x, y))

    def test_get_neighbors_center_position(self):
        """Test get_neighbors returns correct neighbors for a center position."""
        # ARRANGE
        x, y = 10, 10  # Position in the center
        
        # ACT
        result = self.maze.get_neighbors(x, y)
        
        # ASSERT
        self.assertIsInstance(result, list)
        # Each neighbor should be exactly one step away and not a wall
        for neighbor_x, neighbor_y in result:
            distance = abs(neighbor_x - x) + abs(neighbor_y - y)
            self.assertEqual(distance, 1)  # Should be exactly one step away
            self.assertFalse(self.maze.is_wall(neighbor_x, neighbor_y))

    def test_get_neighbors_boundary_position(self):
        """Test get_neighbors handles boundary positions correctly."""
        # ARRANGE
        x, y = 0, 0  # Corner position
        
        # ACT
        result = self.maze.get_neighbors(x, y)
        
        # ASSERT
        self.assertIsInstance(result, list)
        # All neighbors should be within bounds and not walls
        for neighbor_x, neighbor_y in result:
            self.assertTrue(0 <= neighbor_x < self.maze.width)
            self.assertTrue(0 <= neighbor_y < self.maze.height)
            self.assertFalse(self.maze.is_wall(neighbor_x, neighbor_y))

    def test_get_center_position(self):
        """Test get_center_position returns maze center coordinates."""
        # ARRANGE
        expected_x = self.maze.width // 2
        expected_y = self.maze.height // 2
        
        # ACT
        result_x, result_y = self.maze.get_center_position()
        
        # ASSERT
        self.assertEqual(result_x, expected_x)
        self.assertEqual(result_y, expected_y)

    def test_get_tunnel_exit_left_tunnel(self):
        """Test get_tunnel_exit for left tunnel entrance."""
        # ARRANGE
        x, y = self.maze.LEFT_TUNNEL_X, self.maze.TUNNEL_ROW
        dx, dy = -1, 0  # Moving left
        expected_exit = (self.maze.RIGHT_TUNNEL_X, self.maze.TUNNEL_ROW)
        
        # ACT
        result = self.maze.get_tunnel_exit(x, y, dx, dy)
        
        # ASSERT
        self.assertEqual(result, expected_exit)

    def test_get_tunnel_exit_right_tunnel(self):
        """Test get_tunnel_exit for right tunnel entrance."""
        # ARRANGE
        x, y = self.maze.RIGHT_TUNNEL_X, self.maze.TUNNEL_ROW
        dx, dy = 1, 0  # Moving right
        expected_exit = (self.maze.LEFT_TUNNEL_X, self.maze.TUNNEL_ROW)
        
        # ACT
        result = self.maze.get_tunnel_exit(x, y, dx, dy)
        
        # ASSERT
        self.assertEqual(result, expected_exit)

    def test_get_tunnel_exit_wrong_direction(self):
        """Test get_tunnel_exit returns None for wrong direction at tunnel."""
        # ARRANGE
        x, y = self.maze.LEFT_TUNNEL_X, self.maze.TUNNEL_ROW
        dx, dy = 1, 0  # Moving right at left tunnel (wrong direction)
        
        # ACT
        result = self.maze.get_tunnel_exit(x, y, dx, dy)
        
        # ASSERT
        self.assertIsNone(result)

    def test_get_tunnel_exit_not_tunnel_row(self):
        """Test get_tunnel_exit returns None for non-tunnel positions."""
        # ARRANGE
        x, y = 5, 5  # Not on tunnel row
        dx, dy = -1, 0
        
        # ACT
        result = self.maze.get_tunnel_exit(x, y, dx, dy)
        
        # ASSERT
        self.assertIsNone(result)

    def test_get_tunnel_positions(self):
        """Test get_tunnel_positions returns correct tunnel entrance positions."""
        # ARRANGE
        # No specific arrangement needed
        
        # ACT
        left_tunnel, right_tunnel = self.maze.get_tunnel_positions()
        
        # ASSERT
        # Check that tunnel positions are at the edges and not walls
        if left_tunnel:
            self.assertEqual(left_tunnel[0], 0)  # Should be at left edge
            self.assertFalse(self.maze.is_wall(*left_tunnel))
        
        if right_tunnel:
            self.assertEqual(right_tunnel[0], self.maze.width - 1)  # Should be at right edge
            self.assertFalse(self.maze.is_wall(*right_tunnel))

    def test_find_path_same_position(self):
        """Test find_path returns path with single element for same start and end position."""
        # ARRANGE
        start = (5, 5)
        end = (5, 5)
        
        # ACT
        result = self.maze.find_path(start, end)
        
        # ASSERT
        self.assertIsInstance(result, list)
        # When start == end, the method returns the path which includes the start position
        self.assertEqual(result, [start])

    def test_find_path_unreachable_position(self):
        """Test find_path returns empty list for unreachable positions."""
        # ARRANGE
        start = (1, 1)  # Valid position
        end = (0, 0)    # Wall position (unreachable)
        
        # ACT
        result = self.maze.find_path(start, end)
        
        # ASSERT
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()