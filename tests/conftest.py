"""
pytest configuration and fixtures for Pac-Man game tests
Provides common test setup, mocking, and reusable fixtures
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add the parent directory to the path so we can import the game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_pygame():
    """Mock pygame to prevent actual window creation and sound initialization"""
    # Create mock surface for image loading
    mock_surface = Mock()
    mock_surface.get_size.return_value = (64, 64)  # Mock sprite sheet size
    mock_surface.convert_alpha.return_value = mock_surface
    
    # Create mock font
    mock_font = Mock()
    mock_font.render.return_value = mock_surface
    
    with patch('pygame.init'), \
         patch('pygame.mixer.init'), \
         patch('pygame.display.set_mode'), \
         patch('pygame.image.load', return_value=mock_surface), \
         patch('pygame.transform.scale', return_value=mock_surface), \
         patch('pygame.font.Font', return_value=mock_font), \
         patch('pygame.mixer.Sound'), \
         patch('pygame.mixer.music'), \
         patch('pygame.time.Clock'), \
         patch('pygame.event.get', return_value=[]):
        yield


@pytest.fixture
def mock_pygame_gui():
    """Mock pygame_gui to prevent GUI initialization"""
    with patch('pygame_gui.UIManager'):
        yield


@pytest.fixture
def mock_all_pygame(mock_pygame, mock_pygame_gui):
    """Convenience fixture that mocks all pygame components"""
    yield


@pytest.fixture
def sample_maze_layout():
    """Provide a simple test maze layout"""
    return [
        "########",
        "#......#",
        "#.####.#",
        "#......#",
        "########"
    ]


@pytest.fixture
def test_screen():
    """Mock screen object for testing"""
    screen = Mock()
    screen.get_size.return_value = (560, 680)
    screen.blit = Mock()
    screen.fill = Mock()
    return screen


@pytest.fixture
def test_keys():
    """Mock keyboard state for testing"""
    keys = {
        'K_UP': False,
        'K_DOWN': False,
        'K_LEFT': False,
        'K_RIGHT': False,
        'K_SPACE': False
    }
    return keys


@pytest.fixture
def mock_sound_loading():
    """Mock sound file loading to prevent file system dependency"""
    with patch('pygame.mixer.Sound') as mock_sound:
        mock_sound.return_value = Mock()
        yield mock_sound