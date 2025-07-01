# Unit Tests für das Pac-Man Projekt

Dieses Verzeichnis enthält umfassende Unit-Tests für das Pac-Man Spiel, implementiert nach dem bewährten **Arrange-Act-Assert** Muster.

## 📁 Teststruktur

```
tests/
├── __init__.py              # Test package
├── test_player.py           # Tests für Pacman Klasse (14 Tests)
├── test_maze.py             # Tests für Maze Klasse (18 Tests)
├── test_ghost.py            # Tests für Ghost Klasse (16 Tests)
└── test_game.py             # Tests für Game Klasse (20 Tests)
```

## 🎯 Getestete Komponenten

### Pacman Klasse (`test_player.py`)
- ✅ **Initialisierung**: Korrekte Startposition und Attribute
- ✅ **Bewegung**: Richtungssteuerung und Geschwindigkeitssystem
- ✅ **Speed Boost**: Aktivierung und Timer-Management
- ✅ **Kollisionserkennung**: Mit verschiedenen Objekttypen
- ✅ **Input-Handling**: Tasteneingabe-Verarbeitung

### Maze Klasse (`test_maze.py`)
- ✅ **Layout-Parsing**: Korrekte Wand- und Freiraum-Erkennung
- ✅ **Kollisionsprüfung**: Wand-Erkennung und Bounds-Checking
- ✅ **Tunnel-Funktionalität**: Links-rechts Teleportation
- ✅ **Pathfinding**: Einfache Wegfindung für AI
- ✅ **Nachbarschaftsberechnung**: Gültige angrenzende Positionen

### Ghost Klasse (`test_ghost.py`)
- ✅ **Initialisierung**: Verschiedene Geister-Typen (Blinky, Pinky)
- ✅ **AI-Verhalten**: Chase/Scatter/Frightened Modi
- ✅ **Bewegungslogik**: Richtungswahl an Kreuzungen
- ✅ **Zustandswechsel**: Mode-Transitions und Timer
- ✅ **Geisterhaus-Logik**: Ein-/Ausgang-Mechanismen

### Game Klasse (`test_game.py`)
- ✅ **Score-System**: Punkte für Pellets und Geister
- ✅ **Leben-Management**: Leben-Verlust und Game Over
- ✅ **Spielzustände**: Menu/Playing/Paused/Victory/Game Over
- ✅ **Event-Handling**: Benutzer-Eingaben und Quit-Events
- ✅ **Sound-System**: Waka-Waka und andere Effekte

## 🧪 Arrange-Act-Assert Muster

Alle Tests folgen dem bewährten AAA-Muster:

```python
def test_example(self):
    """Test description following AAA pattern."""
    # ARRANGE - Setup der Testdaten
    initial_value = 10
    expected_result = 20
    
    # ACT - Ausführung der zu testenden Aktion
    actual_result = function_to_test(initial_value)
    
    # ASSERT - Überprüfung des Ergebnisses
    self.assertEqual(actual_result, expected_result)
```

## 🚀 Tests ausführen

### Alle Tests
```bash
# Mit unittest
python3 -m unittest discover tests -v

# Mit dem Test-Runner
python3 run_tests.py
```

### Einzelne Test-Dateien
```bash
python3 -m unittest tests.test_player -v
python3 -m unittest tests.test_maze -v
python3 -m unittest tests.test_ghost -v
python3 -m unittest tests.test_game -v
```

### Einzelne Tests
```bash
python3 -m unittest tests.test_player.TestPacman.test_activate_speed_boost -v
```

## 📊 Test-Coverage

- **Gesamt**: 68 Tests
- **Success Rate**: 100%
- **Framework**: Python unittest (built-in)
- **Mocking**: unittest.mock für pygame Dependencies

### Test-Verteilung:
- **Pacman**: 14 Tests (20.6%)
- **Maze**: 18 Tests (26.5%)
- **Ghost**: 16 Tests (23.5%)
- **Game**: 20 Tests (29.4%)

## 🔧 Technische Details

### Dependencies
- Python 3.x
- pygame (wird für Tests gemockt)
- unittest (Python built-in)

### Mocking-Strategie
```python
# Pygame wird vollständig gemockt
pygame_mock = MagicMock()
pygame_mock.error = Exception
sys.modules['pygame'] = pygame_mock
```

### Besondere Testfälle
- **Kollisionserkennung**: Mit/ohne get_center() Methode
- **Tunnel-Tests**: Links-rechts Teleportation
- **AI-Verhalten**: Zufällige vs. zielgerichtete Bewegung
- **Edge Cases**: Out-of-bounds, leere Eingaben

## 📈 Benefits für das Team

1. **Qualitätssicherung**: Frühe Erkennung von Bugs
2. **Refactoring-Sicherheit**: Änderungen ohne Angst vor Regressionen
3. **Dokumentation**: Tests als lebende Dokumentation des Codes
4. **CI/CD Ready**: Automatisierte Tests für GitHub Actions
5. **Team-Lernen**: Besseres Verständnis der Codebasis

## 🎮 Game-spezifische Tests

### Pacman Movement Tests
- Grid-basierte Bewegung
- Node-System Kompatibilität
- Speed Boost Mechanik

### Ghost AI Tests
- Verschiedene Modi (Scatter, Chase, Frightened)
- Keine 180°-Wendungen (außer in Sackgassen)
- Prioritäts-System bei Richtungswahl

### Maze Logic Tests
- 28x31 Grid Layout
- Tunnel-Mechanik auf Row 14
- Wand-Kollisionserkennung

### Game State Tests
- Score-Berechnungen
- Leben-System
- State-Transitions

---
*Entwickelt im Rahmen des Agilen Arbeiten mit Scrum Projekts*