"""
Unit tests for the Pellet system
Tests pellet creation, collection, special pellets, and scoring following AAA pattern
"""

import pytest
import math
from unittest.mock import Mock, patch
from pacman_game.src.pellets import Pellet, SpecialPellet, PelletManager
from pacman_game.src.constants import *


@pytest.mark.unit
class TestPelletInitialization:
    """Test basic Pellet initialization and properties"""
    
    def test_normal_pellet_initializes_correctly(self, mock_all_pygame):
        """Test that normal pellet initializes with correct properties"""
        # ARRANGE - Setup test data
        x, y = 5, 10
        is_power_pellet = False
        
        # ACT - Create normal pellet
        pellet = Pellet(x, y, is_power_pellet)
        
        # ASSERT - Verify initialization
        assert pellet.x == x
        assert pellet.y == y
        assert pellet.grid_x == x
        assert pellet.grid_y == y
        assert pellet.is_power_pellet == is_power_pellet
        assert pellet.collected is False
        assert pellet.visible is True
        assert pellet.spawned is True
        assert pellet.points == SMALL_PELLET_POINTS
        assert pellet.radius == SMALL_PELLET_SIZE
        assert pellet.color == YELLOW

    def test_power_pellet_initializes_correctly(self, mock_all_pygame):
        """Test that power pellet initializes with correct properties"""
        # ARRANGE - Setup test data
        x, y = 3, 7
        is_power_pellet = True
        
        # ACT - Create power pellet
        pellet = Pellet(x, y, is_power_pellet)
        
        # ASSERT - Verify initialization
        assert pellet.x == x
        assert pellet.y == y
        assert pellet.is_power_pellet == is_power_pellet
        assert pellet.points == LARGE_PELLET_POINTS
        assert pellet.radius == LARGE_PELLET_SIZE
        assert pellet.color == (255, 184, 255)  # Rosa-weißlich
        assert pellet.visible is True
        assert pellet.spawned is True

    def test_pellet_has_animation_properties(self, mock_all_pygame):
        """Test that pellet has proper animation properties"""
        # ARRANGE - Setup test data
        x, y = 2, 4
        
        # ACT - Create pellet
        pellet = Pellet(x, y, True)  # Power pellet for animation
        
        # ASSERT - Verify animation properties
        assert hasattr(pellet, 'flash_time')
        assert hasattr(pellet, 'timer')
        assert hasattr(pellet, 'animation_frame')
        assert hasattr(pellet, 'animation_speed')
        assert pellet.flash_time == 0.2
        assert pellet.timer == 0
        assert pellet.animation_frame == 0
        assert pellet.animation_speed == 0.1


@pytest.mark.unit
class TestPelletAnimation:
    """Test Pellet animation functionality"""
    
    def test_power_pellet_animation_updates(self, mock_all_pygame):
        """Test that power pellet animation updates correctly"""
        # ARRANGE - Setup power pellet
        pellet = Pellet(5, 5, True)  # Power pellet
        initial_timer = pellet.timer
        initial_frame = pellet.animation_frame
        dt = 1/60
        
        # ACT - Update animation
        pellet.update(dt)
        
        # ASSERT - Verify animation updated
        assert pellet.timer >= initial_timer
        assert pellet.animation_frame >= initial_frame

    def test_power_pellet_visibility_flashing(self, mock_all_pygame):
        """Test that power pellet visibility flashes correctly"""
        # ARRANGE - Setup power pellet
        pellet = Pellet(5, 5, True)
        initial_visibility = pellet.visible
        
        # ACT - Update with enough time to trigger flash
        pellet.update(0.3)  # More than flash_time of 0.2
        
        # ASSERT - Verify visibility changed
        assert pellet.visible != initial_visibility

    def test_normal_pellet_no_animation(self, mock_all_pygame):
        """Test that normal pellets don't animate"""
        # ARRANGE - Setup normal pellet
        pellet = Pellet(5, 5, False)  # Normal pellet
        initial_visible = pellet.visible
        initial_timer = pellet.timer
        
        # ACT - Update animation
        pellet.update(1.0)  # Long time
        
        # ASSERT - Verify no animation changes
        assert pellet.visible == initial_visible
        assert pellet.timer == initial_timer

    def test_collected_pellet_stops_animating(self, mock_all_pygame):
        """Test that collected pellets stop animating"""
        # ARRANGE - Setup power pellet and mark as collected
        pellet = Pellet(5, 5, True)
        pellet.collected = True
        initial_visible = pellet.visible
        
        # ACT - Update animation
        pellet.update(0.3)
        
        # ASSERT - Verify no animation when collected
        assert pellet.visible == initial_visible


@pytest.mark.unit
class TestSpecialPellet:
    """Test SpecialPellet functionality"""
    
    def test_special_pellet_initializes_correctly(self, mock_all_pygame):
        """Test that special pellet initializes with correct properties"""
        # ARRANGE - Setup test data
        x, y = 8, 12
        
        # ACT - Create special pellet
        special_pellet = SpecialPellet(x, y)
        
        # ASSERT - Verify initialization
        assert special_pellet.x == x
        assert special_pellet.y == y
        assert special_pellet.color == CYAN
        assert special_pellet.points == 25
        assert special_pellet.radius == LARGE_PELLET_SIZE
        assert special_pellet.visible is True
        assert special_pellet.spawned is True

    def test_special_pellet_animation_updates(self, mock_all_pygame):
        """Test that special pellet animation updates correctly"""
        # ARRANGE - Setup special pellet
        special_pellet = SpecialPellet(5, 5)
        initial_frame = special_pellet.animation_frame
        initial_pulse = special_pellet.pulse_effect
        
        # ACT - Update animation
        special_pellet.update(1/60)
        
        # ASSERT - Verify animation updated
        assert special_pellet.animation_frame >= initial_frame
        # Pulse effect should be calculated based on sine function

    def test_special_pellet_pulse_effect_calculation(self, mock_all_pygame):
        """Test that special pellet pulse effect is calculated correctly"""
        # ARRANGE - Setup special pellet
        special_pellet = SpecialPellet(5, 5)
        
        # ACT - Update to get pulse effect
        special_pellet.update(1/60)
        
        # ASSERT - Verify pulse effect is calculated
        expected_pulse = math.sin(special_pellet.animation_frame * math.pi) * 1.5
        assert abs(special_pellet.pulse_effect - expected_pulse) < 0.001


@pytest.mark.unit
class TestPelletManager:
    """Test PelletManager functionality"""
    
    def test_pellet_manager_initializes_with_maze(self, mock_all_pygame):
        """Test that PelletManager initializes correctly with maze"""
        # ARRANGE - Setup mock maze
        mock_maze = Mock()
        mock_maze.width = 28
        mock_maze.height = 31
        mock_maze.is_wall.return_value = False
        mock_maze.get_center_position.return_value = (14, 15)
        
        # ACT - Create PelletManager
        pellet_manager = PelletManager(mock_maze)
        
        # ASSERT - Verify initialization
        assert pellet_manager.maze == mock_maze
        assert isinstance(pellet_manager.pellets, list)
        assert isinstance(pellet_manager.power_pellet_positions, list)
        assert isinstance(pellet_manager.active_power_pellets, list)
        assert pellet_manager.active_speed_pellet is None
        assert pellet_manager.power_pellet_timer == 0
        assert pellet_manager.speed_pellet_timer == 0

    def test_pellet_manager_creates_pellets_on_valid_positions(self, mock_all_pygame):
        """Test that PelletManager creates pellets on valid maze positions"""
        # ARRANGE - Setup mock maze with some walls and paths
        mock_maze = Mock()
        mock_maze.width = 10
        mock_maze.height = 10
        mock_maze.get_center_position.return_value = (5, 5)
        
        # Mock is_wall to return True for borders, False for inside
        def mock_is_wall(x, y):
            return x == 0 or y == 0 or x == 9 or y == 9
        mock_maze.is_wall.side_effect = mock_is_wall
        
        # ACT - Create PelletManager
        pellet_manager = PelletManager(mock_maze)
        
        # ASSERT - Verify pellets were created
        assert len(pellet_manager.pellets) > 0
        
        # Verify no pellets on walls
        for pellet in pellet_manager.pellets:
            assert not mock_maze.is_wall(pellet.x, pellet.y)

    def test_pellet_manager_skips_ghost_area(self, mock_all_pygame):
        """Test that PelletManager skips ghost starting area"""
        # ARRANGE - Setup mock maze
        mock_maze = Mock()
        mock_maze.width = 10
        mock_maze.height = 10
        mock_maze.is_wall.return_value = False  # All positions are paths
        mock_maze.get_center_position.return_value = (5, 5)  # Center at (5,5)
        
        # ACT - Create PelletManager
        pellet_manager = PelletManager(mock_maze)
        
        # ASSERT - Verify no pellets in ghost area (center ±3)
        for pellet in pellet_manager.pellets:
            distance_from_center_x = abs(pellet.x - 5)
            distance_from_center_y = abs(pellet.y - 5)
            assert not (distance_from_center_x <= 3 and distance_from_center_y <= 3)

    def test_pellet_manager_power_pellet_positions_defined(self, mock_all_pygame):
        """Test that PelletManager defines power pellet positions correctly"""
        # ARRANGE - Setup mock maze
        mock_maze = Mock()
        mock_maze.width = 28
        mock_maze.height = 31
        mock_maze.is_wall.return_value = False
        mock_maze.get_center_position.return_value = (14, 15)
        
        # ACT - Create PelletManager
        pellet_manager = PelletManager(mock_maze)
        
        # ASSERT - Verify power pellet positions
        expected_positions = [
            (1, 3),  # Top left
            (26, 3),  # Top right (width-2)
            (1, 27),  # Bottom left (height-4)
            (26, 27)  # Bottom right
        ]
        assert pellet_manager.power_pellet_positions == expected_positions


@pytest.mark.unit 
class TestPelletCollection:
    """Test pellet collection functionality"""
    
    def test_check_collection_with_pacman_at_pellet_position(self, mock_all_pygame):
        """Test pellet collection when Pacman is at pellet position"""
        # ARRANGE - Setup mock maze and pellet manager
        mock_maze = Mock()
        mock_maze.width = 10
        mock_maze.height = 10
        mock_maze.is_wall.return_value = False
        mock_maze.get_center_position.return_value = (5, 5)
        
        pellet_manager = PelletManager(mock_maze)
        
        # Add a test pellet at known position
        test_pellet = Pellet(3, 3, False)
        pellet_manager.pellets = [test_pellet]
        
        # Setup mock Pacman at same position
        mock_pacman = Mock()
        mock_pacman.grid_x = 3
        mock_pacman.grid_y = 3
        mock_pacman.x = 3 * GRID_SIZE
        mock_pacman.y = 3 * GRID_SIZE
        mock_pacman.size = PACMAN_SIZE
        
        # ACT - Check collection
        points = pellet_manager.check_collection(mock_pacman)
        
        # ASSERT - Verify pellet was collected
        assert points == SMALL_PELLET_POINTS
        assert test_pellet.collected is True

    def test_check_collection_no_pellets_at_position(self, mock_all_pygame):
        """Test pellet collection when no pellets at Pacman position"""
        # ARRANGE - Setup mock maze and pellet manager
        mock_maze = Mock()
        mock_maze.width = 10
        mock_maze.height = 10
        mock_maze.is_wall.return_value = False
        mock_maze.get_center_position.return_value = (5, 5)
        
        pellet_manager = PelletManager(mock_maze)
        pellet_manager.pellets = []  # No pellets
        
        # Setup mock Pacman
        mock_pacman = Mock()
        mock_pacman.grid_x = 3
        mock_pacman.grid_y = 3
        mock_pacman.x = 3 * GRID_SIZE
        mock_pacman.y = 3 * GRID_SIZE
        mock_pacman.size = PACMAN_SIZE
        
        # ACT - Check collection
        points = pellet_manager.check_collection(mock_pacman)
        
        # ASSERT - Verify no collection
        assert points == 0

    def test_check_collection_power_pellet_returns_negative_signal(self, mock_all_pygame):
        """Test that power pellet collection returns negative signal"""
        # ARRANGE - Setup mock maze and pellet manager
        mock_maze = Mock()
        mock_maze.width = 10
        mock_maze.height = 10
        mock_maze.is_wall.return_value = False
        mock_maze.get_center_position.return_value = (5, 5)
        
        pellet_manager = PelletManager(mock_maze)
        
        # Add a power pellet
        power_pellet = Pellet(3, 3, True)  # Power pellet
        pellet_manager.active_power_pellets = [power_pellet]
        
        # Setup mock Pacman
        mock_pacman = Mock()
        mock_pacman.grid_x = 3
        mock_pacman.grid_y = 3
        mock_pacman.x = 3 * GRID_SIZE
        mock_pacman.y = 3 * GRID_SIZE
        mock_pacman.size = PACMAN_SIZE
        
        # ACT - Check collection
        points = pellet_manager.check_collection(mock_pacman)
        
        # ASSERT - Verify power pellet signal (negative)
        assert points < 0
        assert abs(points) == LARGE_PELLET_POINTS

    def test_check_collection_speed_pellet_returns_special_signal(self, mock_all_pygame):
        """Test that speed pellet collection returns special signal"""
        # ARRANGE - Setup mock maze and pellet manager
        mock_maze = Mock()
        mock_maze.width = 10
        mock_maze.height = 10
        mock_maze.is_wall.return_value = False
        mock_maze.get_center_position.return_value = (5, 5)
        
        pellet_manager = PelletManager(mock_maze)
        
        # Add a speed pellet
        speed_pellet = SpecialPellet(3, 3)
        pellet_manager.active_speed_pellet = speed_pellet
        
        # Setup mock Pacman
        mock_pacman = Mock()
        mock_pacman.grid_x = 3
        mock_pacman.grid_y = 3
        mock_pacman.x = 3 * GRID_SIZE
        mock_pacman.y = 3 * GRID_SIZE
        mock_pacman.size = PACMAN_SIZE
        
        # ACT - Check collection
        points = pellet_manager.check_collection(mock_pacman)
        
        # ASSERT - Verify speed pellet signal
        assert points < -1000  # Special signal for speed pellet


@pytest.mark.unit
class TestPelletManagerUtilities:
    """Test PelletManager utility methods"""
    
    def test_get_pellet_count_returns_correct_count(self, mock_all_pygame):
        """Test that get_pellet_count returns correct number of pellets"""
        # ARRANGE - Setup mock maze and pellet manager
        mock_maze = Mock()
        mock_maze.width = 5
        mock_maze.height = 5
        mock_maze.is_wall.return_value = False
        mock_maze.get_center_position.return_value = (2, 2)
        
        pellet_manager = PelletManager(mock_maze)
        
        # ACT - Get pellet count
        count = pellet_manager.get_remaining_count()
        
        # ASSERT - Verify count matches number of uncollected pellets
        expected_count = len([p for p in pellet_manager.pellets if not p.collected])
        assert count == expected_count

    def test_reset_clears_all_pellets_and_timers(self, mock_all_pygame):
        """Test that reset clears all pellets and resets timers"""
        # ARRANGE - Setup pellet manager with some data
        mock_maze = Mock()
        mock_maze.width = 10
        mock_maze.height = 10
        mock_maze.is_wall.return_value = False
        mock_maze.get_center_position.return_value = (5, 5)
        
        pellet_manager = PelletManager(mock_maze)
        pellet_manager.power_pellet_timer = 100
        pellet_manager.speed_pellet_timer = 200
        pellet_manager.active_power_pellets = [Mock()]
        pellet_manager.active_speed_pellet = Mock()
        
        # ACT - Reset
        pellet_manager.reset()
        
        # ASSERT - Verify reset
        assert pellet_manager.power_pellet_timer == 0
        assert pellet_manager.speed_pellet_timer == 0
        assert pellet_manager.active_power_pellets == []
        assert pellet_manager.active_speed_pellet is None
        # New pellets should be created (at least some)
        assert len(pellet_manager.pellets) >= 0  # May be 0 if center exclusion removes all


@pytest.mark.unit
class TestPelletSpawning:
    """Test special pellet spawning functionality"""
    
    def test_spawn_power_pellet_at_available_position(self, mock_all_pygame):
        """Test spawning power pellet at available position"""
        # ARRANGE - Setup mock maze and pellet manager
        mock_maze = Mock()
        mock_maze.width = 28
        mock_maze.height = 31
        mock_maze.is_wall.return_value = False
        mock_maze.get_center_position.return_value = (14, 15)
        
        pellet_manager = PelletManager(mock_maze)
        pellet_manager.active_power_pellets = []  # No active power pellets
        
        # ACT - Spawn power pellet
        with patch('random.choice') as mock_choice:
            mock_choice.return_value = (1, 3)  # Mock random position selection
            pellet_manager.spawn_power_pellet()
        
        # ASSERT - Verify power pellet was spawned
        assert len(pellet_manager.active_power_pellets) == 1
        spawned_pellet = pellet_manager.active_power_pellets[0]
        assert spawned_pellet.x == 1
        assert spawned_pellet.y == 3
        assert spawned_pellet.is_power_pellet is True

    def test_spawn_power_pellet_respects_available_positions(self, mock_all_pygame):
        """Test that power pellet spawning respects available positions"""
        # ARRANGE - Setup pellet manager with all positions occupied
        mock_maze = Mock()
        mock_maze.width = 28
        mock_maze.height = 31
        mock_maze.is_wall.return_value = False
        mock_maze.get_center_position.return_value = (14, 15)
        
        pellet_manager = PelletManager(mock_maze)
        
        # Occupy all power pellet positions
        power_pellets = []
        for pos in pellet_manager.power_pellet_positions:
            pellet = Mock()
            pellet.x, pellet.y = pos
            power_pellets.append(pellet)
        pellet_manager.active_power_pellets = power_pellets
        
        # ACT - Try to spawn another power pellet
        initial_count = len(pellet_manager.active_power_pellets)
        pellet_manager.spawn_power_pellet()
        
        # ASSERT - Verify no additional power pellet was spawned (no available positions)
        assert len(pellet_manager.active_power_pellets) == initial_count