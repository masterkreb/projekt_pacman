"""
Unit tests for the Pacman Player class
Tests movement, collision detection, speed boost, and animation following AAA pattern
"""

import pytest
import math
from unittest.mock import Mock, patch, MagicMock
from pacman_game.src.player import Pacman
from pacman_game.src.constants import *


@pytest.mark.unit
class TestPacmanInitialization:
    """Test Pacman initialization and basic properties"""
    
    def test_pacman_initializes_with_correct_starting_values(self, mock_all_pygame):
        """Test that Pacman initializes with correct starting position and properties"""
        # ARRANGE - Setup test data
        start_x = 10
        start_y = 15
        
        # ACT - Create Pacman instance
        pacman = Pacman(start_x, start_y)
        
        # ASSERT - Verify initialization values
        assert pacman.start_x == start_x
        assert pacman.start_y == start_y
        assert pacman.x == start_x * GRID_SIZE
        assert pacman.y == start_y * GRID_SIZE
        assert pacman.grid_x == start_x
        assert pacman.grid_y == start_y
        assert pacman.speed == PACMAN_SPEED
        assert pacman.base_speed == PACMAN_SPEED
        assert pacman.current_direction is None
        assert pacman.next_direction is None
        assert pacman.velocity_x == 0
        assert pacman.velocity_y == 0

    def test_pacman_initializes_with_correct_size(self, mock_all_pygame):
        """Test that Pacman has the correct size"""
        # ARRANGE - Setup test data
        start_x, start_y = 5, 5
        
        # ACT - Create Pacman instance
        pacman = Pacman(start_x, start_y)
        
        # ASSERT - Verify size
        assert pacman.size == PACMAN_SIZE


@pytest.mark.unit
class TestPacmanMovement:
    """Test Pacman movement and direction handling"""
    
    def test_set_direction_updates_next_direction(self, mock_all_pygame):
        """Test that setting direction updates the next_direction property"""
        # ARRANGE - Setup Pacman
        pacman = Pacman(10, 10)
        test_direction = UP  # Use the actual constant from constants.py
        
        # ACT - Set direction
        pacman.set_direction(test_direction)
        
        # ASSERT - Verify direction was set
        assert pacman.next_direction == "up"

    def test_activate_speed_boost_increases_speed(self, mock_all_pygame):
        """Test that speed boost activation doubles the speed"""
        # ARRANGE - Setup Pacman
        pacman = Pacman(10, 10)
        original_speed = pacman.speed
        
        # ACT - Activate speed boost
        pacman.activate_speed_boost()
        
        # ASSERT - Verify speed is doubled
        assert pacman.speed == PACMAN_SPEED_BOOST
        assert pacman.speed == original_speed * 2
        assert pacman.speed_boost_active is True

    def test_reached_target_returns_false_when_no_target(self, mock_all_pygame):
        """Test that reached_target returns False when no target is set"""
        # ARRANGE - Setup Pacman with no target
        pacman = Pacman(10, 10)
        pacman.target = None
        
        # ACT - Check if target is reached
        result = pacman.reached_target()
        
        # ASSERT - Verify result
        assert result is False

    def test_reached_target_returns_true_when_close_to_target(self, mock_all_pygame):
        """Test that reached_target returns True when Pacman is close to target"""
        # ARRANGE - Setup Pacman and mock target
        pacman = Pacman(10, 10)
        
        # Create mock target node very close to Pacman
        mock_target = Mock()
        mock_target.px = pacman.x + pacman.size / 2  # Same as Pacman center
        mock_target.py = pacman.y + pacman.size / 2
        pacman.target = mock_target
        
        # ACT - Check if target is reached
        result = pacman.reached_target()
        
        # ASSERT - Verify target is reached
        assert result is True

    def test_reached_target_returns_false_when_far_from_target(self, mock_all_pygame):
        """Test that reached_target returns False when Pacman is far from target"""
        # ARRANGE - Setup Pacman and mock target far away
        pacman = Pacman(10, 10)
        
        # Create mock target node far from Pacman
        mock_target = Mock()
        mock_target.px = pacman.x + 100  # 100 pixels away
        mock_target.py = pacman.y + 100
        pacman.target = mock_target
        
        # ACT - Check if target is reached
        result = pacman.reached_target()
        
        # ASSERT - Verify target is not reached
        assert result is False


@pytest.mark.unit
class TestPacmanCollision:
    """Test Pacman collision detection"""
    
    def test_collides_with_object_with_get_center_method(self, mock_all_pygame):
        """Test collision with object that has get_center method"""
        # ARRANGE - Setup Pacman and mock object at same position
        pacman = Pacman(10, 10)
        
        mock_object = Mock()
        mock_object.get_center.return_value = (pacman.x + pacman.size / 2, pacman.y + pacman.size / 2)
        mock_object.size = 16
        
        # ACT - Check collision
        result = pacman.collides_with(mock_object)
        
        # ASSERT - Verify collision detected
        assert result is True

    def test_collides_with_object_without_get_center_method(self, mock_all_pygame):
        """Test collision with object using fallback position calculation"""
        # ARRANGE - Setup Pacman and mock object
        pacman = Pacman(10, 10)
        
        mock_object = Mock()
        # Remove get_center method to trigger fallback
        del mock_object.get_center
        mock_object.x = pacman.x
        mock_object.y = pacman.y
        mock_object.size = 16
        
        # ACT - Check collision
        result = pacman.collides_with(mock_object)
        
        # ASSERT - Verify collision detected
        assert result is True

    def test_no_collision_when_objects_far_apart(self, mock_all_pygame):
        """Test no collision when objects are far apart"""
        # ARRANGE - Setup Pacman and distant object
        pacman = Pacman(10, 10)
        
        mock_object = Mock()
        mock_object.get_center.return_value = (pacman.x + 100, pacman.y + 100)  # Far away
        mock_object.size = 16
        
        # ACT - Check collision
        result = pacman.collides_with(mock_object)
        
        # ASSERT - Verify no collision
        assert result is False

    def test_collision_distance_calculation_uses_80_percent(self, mock_all_pygame):
        """Test that collision detection uses 80% of combined radii for better gameplay"""
        # ARRANGE - Setup Pacman and object at exact combined radius distance
        pacman = Pacman(10, 10)
        
        mock_object = Mock()
        object_size = 16
        mock_object.size = object_size
        
        # Calculate exact 80% collision distance
        collision_distance = (pacman.size + object_size) / 2 * 0.8
        
        # Position object at exactly this distance
        pacman_center_x = pacman.x + pacman.size / 2
        pacman_center_y = pacman.y + pacman.size / 2
        object_center_x = pacman_center_x + collision_distance - 1  # Slightly less than threshold
        object_center_y = pacman_center_y
        
        mock_object.get_center.return_value = (object_center_x, object_center_y)
        
        # ACT - Check collision
        result = pacman.collides_with(mock_object)
        
        # ASSERT - Verify collision detected (just under threshold)
        assert result is True


@pytest.mark.unit
class TestPacmanAnimation:
    """Test Pacman animation functionality"""
    
    def test_update_animation_increments_frame(self, mock_all_pygame):
        """Test that animation frame updates correctly"""
        # ARRANGE - Setup Pacman
        pacman = Pacman(10, 10)
        initial_frame = pacman.animation_frame
        pacman.is_moving = True  # Set moving to enable animation
        
        # ACT - Update animation
        pacman.update_animation()
        
        # ASSERT - Verify frame incremented
        assert pacman.animation_frame != initial_frame

    def test_set_eating_updates_eating_status(self, mock_all_pygame):
        """Test that eating status can be set correctly"""
        # ARRANGE - Setup Pacman
        pacman = Pacman(10, 10)
        
        # ACT - Set eating status
        pacman.set_eating(True)
        
        # ASSERT - Verify eating status set
        assert pacman.is_eating is True
        
        # ACT - Set eating status to False
        pacman.set_eating(False)
        
        # ASSERT - Verify eating status updated
        assert pacman.is_eating is False


@pytest.mark.unit
class TestPacmanPositionMethods:
    """Test Pacman position-related methods"""
    
    def test_get_pixel_position_returns_center_coordinates(self, mock_all_pygame):
        """Test that get_pixel_position returns the center of Pacman"""
        # ARRANGE - Setup Pacman at known position
        pacman = Pacman(10, 10)
        expected_x = pacman.x + pacman.size / 2
        expected_y = pacman.y + pacman.size / 2
        
        # ACT - Get pixel position
        pixel_x, pixel_y = pacman.get_pixel_position()
        
        # ASSERT - Verify center coordinates
        assert pixel_x == expected_x
        assert pixel_y == expected_y


@pytest.mark.unit
class TestPacmanSpeedBoost:
    """Test Pacman speed boost functionality"""
    
    def test_speed_boost_timer_initialization(self, mock_all_pygame):
        """Test that speed boost timer is properly initialized"""
        # ARRANGE - Setup Pacman
        pacman = Pacman(10, 10)
        
        # ACT - Activate speed boost
        pacman.activate_speed_boost()
        
        # ASSERT - Verify timer is set
        assert hasattr(pacman, 'speed_boost_timer')
        assert pacman.speed_boost_timer > 0

    def test_speed_boost_deactivates_when_timer_expires(self, mock_all_pygame):
        """Test that speed boost deactivates when timer reaches zero"""
        # ARRANGE - Setup Pacman with expired timer
        pacman = Pacman(10, 10)
        pacman.activate_speed_boost()
        pacman.speed_boost_timer = 0  # Expire timer
        
        # Create a proper mock maze with node_map
        mock_maze = Mock()
        mock_maze.node_map = {}  # Empty dict to avoid iteration error
        
        # ACT - Update Pacman (should check timer)
        pacman.update(mock_maze)
        
        # ASSERT - Verify speed boost deactivated
        assert pacman.speed == PACMAN_SPEED  # Back to normal speed
        assert pacman.speed_boost_active is False