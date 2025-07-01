"""
Unit tests for the Maze class
Tests maze layout, wall detection, tunnels, and nodes following AAA pattern
"""

import pytest
from unittest.mock import Mock, patch
from pacman_game.src.maze import Maze
from pacman_game.src.constants import *


@pytest.mark.unit
class TestMazeInitialization:
    """Test Maze initialization and basic properties"""
    
    def test_maze_initializes_with_correct_dimensions(self, mock_all_pygame):
        """Test that Maze initializes with correct width and height"""
        # ARRANGE - Setup for maze creation
        
        # ACT - Create Maze instance
        maze = Maze()
        
        # ASSERT - Verify dimensions
        assert maze.width == 28  # Based on layout string length
        assert maze.height == 31  # Based on number of layout strings
        assert len(maze.layout) == maze.height
        assert len(maze.layout[0]) == maze.width

    def test_maze_layout_parsing_creates_correct_walls(self, mock_all_pygame):
        """Test that layout string parsing creates correct wall/path structure"""
        # ARRANGE - Setup for maze creation
        
        # ACT - Create Maze instance
        maze = Maze()
        
        # ASSERT - Verify layout parsing
        # First row should be all walls (################...)
        for x in range(maze.width):
            assert maze.layout[0][x] == 1  # Wall
            
        # Check a known path position (second row, x=1 should be path)
        assert maze.layout[1][1] == 0  # Path (from "#......#" pattern)

    def test_maze_tunnel_parameters_set_correctly(self, mock_all_pygame):
        """Test that tunnel parameters are set correctly"""
        # ARRANGE - Setup for maze creation
        
        # ACT - Create Maze instance
        maze = Maze()
        
        # ASSERT - Verify tunnel parameters
        assert maze.TUNNEL_ROW == 14
        assert maze.LEFT_TUNNEL_X == 0
        assert maze.RIGHT_TUNNEL_X == maze.width - 1

    def test_maze_creates_node_map(self, mock_all_pygame):
        """Test that maze creates nodes and node map"""
        # ARRANGE - Setup for maze creation
        
        # ACT - Create Maze instance
        maze = Maze()
        
        # ASSERT - Verify nodes and node map exist
        assert hasattr(maze, 'nodes')
        assert hasattr(maze, 'node_map')
        assert isinstance(maze.nodes, list)
        assert isinstance(maze.node_map, dict)


@pytest.mark.unit
class TestMazeWallDetection:
    """Test Maze wall detection functionality"""
    
    def test_is_wall_returns_true_for_wall_positions(self, mock_all_pygame):
        """Test that is_wall returns True for wall positions"""
        # ARRANGE - Setup maze
        maze = Maze()
        
        # ACT & ASSERT - Check wall positions
        # Top-left corner should be a wall
        assert maze.is_wall(0, 0) is True
        
        # Top-right corner should be a wall
        assert maze.is_wall(maze.width - 1, 0) is True

    def test_is_wall_returns_false_for_path_positions(self, mock_all_pygame):
        """Test that is_wall returns False for path positions"""
        # ARRANGE - Setup maze
        maze = Maze()
        
        # ACT & ASSERT - Check path positions
        # Position (1,1) should be a path based on layout
        assert maze.is_wall(1, 1) is False

    def test_is_wall_handles_out_of_bounds_coordinates(self, mock_all_pygame):
        """Test that is_wall handles out-of-bounds coordinates correctly"""
        # ARRANGE - Setup maze
        maze = Maze()
        
        # ACT & ASSERT - Check out-of-bounds positions
        assert maze.is_wall(-1, 0) is True  # Should return True for out-of-bounds
        assert maze.is_wall(0, -1) is True
        assert maze.is_wall(maze.width, 0) is True
        assert maze.is_wall(0, maze.height) is True


@pytest.mark.unit
class TestMazeTunnelFunctionality:
    """Test Maze tunnel functionality"""
    
    def test_get_tunnel_exit_returns_none_for_non_tunnel_positions(self, mock_all_pygame):
        """Test that get_tunnel_exit returns None for non-tunnel positions"""
        # ARRANGE - Setup maze
        maze = Maze()
        
        # ACT - Check non-tunnel position
        tunnel_exit = maze.get_tunnel_exit(5, 5, -1, 0)  # Middle of maze
        
        # ASSERT - Should return None
        assert tunnel_exit is None

    def test_get_tunnel_exit_returns_correct_exit_for_left_tunnel(self, mock_all_pygame):
        """Test that get_tunnel_exit returns correct exit for left tunnel"""
        # ARRANGE - Setup maze
        maze = Maze()
        
        # ACT - Check left tunnel exit
        tunnel_exit = maze.get_tunnel_exit(0, maze.TUNNEL_ROW, -1, 0)
        
        # ASSERT - Should return right tunnel position
        expected_exit = (maze.RIGHT_TUNNEL_X, maze.TUNNEL_ROW)
        assert tunnel_exit == expected_exit

    def test_get_tunnel_exit_returns_correct_exit_for_right_tunnel(self, mock_all_pygame):
        """Test that get_tunnel_exit returns correct exit for right tunnel"""
        # ARRANGE - Setup maze
        maze = Maze()
        
        # ACT - Check right tunnel exit
        tunnel_exit = maze.get_tunnel_exit(maze.width - 1, maze.TUNNEL_ROW, 1, 0)
        
        # ASSERT - Should return left tunnel position
        expected_exit = (maze.LEFT_TUNNEL_X, maze.TUNNEL_ROW)
        assert tunnel_exit == expected_exit

    def test_get_tunnel_exit_returns_none_for_wrong_direction(self, mock_all_pygame):
        """Test that get_tunnel_exit returns None for wrong direction at tunnel"""
        # ARRANGE - Setup maze
        maze = Maze()
        
        # ACT - Check tunnel position with wrong direction
        tunnel_exit = maze.get_tunnel_exit(0, maze.TUNNEL_ROW, 1, 0)  # Moving right at left tunnel
        
        # ASSERT - Should return None
        assert tunnel_exit is None


@pytest.mark.unit
class TestMazeUtilityMethods:
    """Test Maze utility methods"""
    
    def test_get_center_position_returns_correct_coordinates(self, mock_all_pygame):
        """Test that get_center_position returns correct center coordinates"""
        # ARRANGE - Setup maze
        maze = Maze()
        
        # ACT - Get center position
        center_x, center_y = maze.get_center_position()
        
        # ASSERT - Verify center coordinates
        expected_x = maze.width // 2
        expected_y = maze.height // 2
        assert center_x == expected_x
        assert center_y == expected_y

    def test_maze_has_valid_layout_strings(self, mock_all_pygame):
        """Test that maze layout strings are valid"""
        # ARRANGE - Setup maze
        maze = Maze()
        
        # ACT & ASSERT - Verify layout strings
        assert len(maze.layout_strings) > 0
        
        # All layout strings should have same length
        first_length = len(maze.layout_strings[0])
        for layout_string in maze.layout_strings:
            assert len(layout_string) == first_length
            
        # Layout strings should only contain valid characters
        valid_chars = {'#', '.'}
        for layout_string in maze.layout_strings:
            for char in layout_string:
                assert char in valid_chars


@pytest.mark.unit
class TestMazeNodeSystem:
    """Test Maze node system for pathfinding"""
    
    def test_nodes_created_for_all_non_wall_positions(self, mock_all_pygame):
        """Test that nodes are created for all non-wall positions"""
        # ARRANGE - Setup maze
        maze = Maze()
        
        # ACT - Count nodes and non-wall positions
        node_count = len(maze.nodes)
        
        # Count expected non-wall positions
        expected_node_count = 0
        for y in range(maze.height):
            for x in range(maze.width):
                if not maze.is_wall(x, y):
                    expected_node_count += 1
        
        # ASSERT - Node count should match non-wall positions
        assert node_count == expected_node_count

    def test_node_map_contains_all_nodes(self, mock_all_pygame):
        """Test that node_map contains entries for all nodes"""
        # ARRANGE - Setup maze
        maze = Maze()
        
        # ACT & ASSERT - Verify node_map
        assert len(maze.node_map) == len(maze.nodes)
        
        # Each node should be in the node_map
        for node in maze.nodes:
            assert (node.grid_x, node.grid_y) in maze.node_map
            assert maze.node_map[(node.grid_x, node.grid_y)] == node

    def test_nodes_have_correct_pixel_positions(self, mock_all_pygame):
        """Test that nodes have correct pixel positions"""
        # ARRANGE - Setup maze
        maze = Maze()
        
        # ACT & ASSERT - Check a few nodes
        for node in maze.nodes[:5]:  # Check first 5 nodes
            expected_px = node.grid_x * GRID_SIZE + GRID_SIZE // 2
            expected_py = node.grid_y * GRID_SIZE + GRID_SIZE // 2
            assert node.px == expected_px
            assert node.py == expected_py


@pytest.mark.unit
class TestMazeImageLoading:
    """Test Maze image loading functionality"""
    
    def test_maze_handles_missing_image_gracefully(self, mock_all_pygame):
        """Test that maze handles missing background image gracefully"""
        # ARRANGE - Mock image loading to fail
        with patch('pygame.image.load', side_effect=FileNotFoundError("File not found")):
            
            # ACT - Create maze (should not crash)
            maze = Maze()
            
            # ASSERT - Maze should still be created successfully
            assert maze.width > 0
            assert maze.height > 0
            assert hasattr(maze, 'background_image')

    def test_maze_loads_image_successfully_when_available(self, mock_all_pygame):
        """Test that maze loads background image when available"""
        # ARRANGE - Mock successful image loading
        mock_surface = Mock()
        mock_surface.get_size.return_value = (560, 620)
        mock_surface.convert_alpha.return_value = mock_surface
        
        with patch('pygame.image.load', return_value=mock_surface), \
             patch('pygame.transform.scale', return_value=mock_surface):
            
            # ACT - Create maze
            maze = Maze()
            
            # ASSERT - Image should be loaded
            assert hasattr(maze, 'background_image')


@pytest.mark.unit
class TestMazeCollisionDetection:
    """Test Maze collision detection for game objects"""
    
    def test_collision_detection_with_walls(self, mock_all_pygame):
        """Test collision detection between objects and walls"""
        # ARRANGE - Setup maze
        maze = Maze()
        
        # Create mock object at wall position
        mock_object = Mock()
        mock_object.grid_x = 0  # Wall position
        mock_object.grid_y = 0  # Wall position
        
        # ACT - Check collision
        is_collision = maze.is_wall(mock_object.grid_x, mock_object.grid_y)
        
        # ASSERT - Should detect collision with wall
        assert is_collision is True

    def test_no_collision_with_paths(self, mock_all_pygame):
        """Test no collision detection for objects on paths"""
        # ARRANGE - Setup maze
        maze = Maze()
        
        # Create mock object at path position
        mock_object = Mock()
        mock_object.grid_x = 1  # Path position
        mock_object.grid_y = 1  # Path position
        
        # ACT - Check collision
        is_collision = maze.is_wall(mock_object.grid_x, mock_object.grid_y)
        
        # ASSERT - Should not detect collision with path
        assert is_collision is False