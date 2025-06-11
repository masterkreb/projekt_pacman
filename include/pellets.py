import pygame
import numpy as np
from pygame.math import Vector2

# Konstanten definieren
TILEWIDTH = 30
TILEHEIGHT = 30
WHITE = (255, 255, 255)
PELLET = "pellet"
POWERPELLET = "powerpellet"

class Pellet(object):
    """
    Basisklasse für normale Pellets im Spiel.
    Diese sind die kleinen Punkte, die Pac-Man einsammeln kann
    """
    def __init__(self, row, column):
        # Grundlegende Eigenschaften des Pellets
        self.name = PELLET
        self.position = Vector2(column * TILEWIDTH, row * TILEHEIGHT)  # Position auf dem Spielfeld
        self.color = WHITE
        self.radius = int(4 * TILEWIDTH / 16)  # Größe des Pellets
        self.collideRadius = int(4 * TILEWIDTH / 16)  # Kollisionsradius
        self.points = 10  # Punktewert beim Einsammeln
        self.visible = True  # Sichtbarkeitsstatus

    def render(self, screen):
        """
        Zeichnet das Pellet auf dem Bildschirm, wenn es sichtbar ist.
        Args:
            screen: Pygame-Oberflächenobjekt zum Zeichnen
        """
        if self.visible:
            pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)

class PowerPellet(Pellet):
    """
    Spezielle Pellet-Klasse für Power-Pellets.
    Diese sind größer und verleihen Pac-Man spezielle Fähigkeiten.
    """
    def __init__(self, row, column):
        super().__init__(row, column)  # Initialisierung der Basisklasse
        self.name = POWERPELLET
        self.radius = int(8 * TILEWIDTH / 16)  # Größerer Radius als normale Pellets
        self.points = 50  # Mehr Punkte als normale Pellets
        self.flashTime = 0.2  # Zeit zwischen Blinken
        self.timer = 0  # Timer für Blinkeffekt

    def update(self, dt):
        """
        Aktualisiert den Blinkeffekt des Power-Pellets.
        Args:
            dt: Vergangene Zeit seit dem letzten Update
        """
        self.timer += dt
        if self.timer > self.flashTime:
            self.visible = not self.visible  # Umschalten der Sichtbarkeit
            self.timer = 0

class PelletGroup(object):
    """
    Verwaltet alle Pellets im Spiel als Gruppe.
    Lädt das Pellet-Layout aus einer Datei und handhabt Updates und Rendering.
    """
    def __init__(self, pelletfile):
        self.pelletList = []  # Liste aller Pellets
        self.powerpellets = []  # Separate Liste für Power-Pellets
        self.createPelletlist(pelletfile)
        self.numEaten = 0  # Zähler für eingesammelte Pellets

    def update(self, dt):
        """
        Aktualisiert alle Power-Pellets in der Gruppe.
        Args:
            dt: Vergangene Zeit seit dem letzten Update
        """
        for powerpellet in self.powerpellets:
            powerpellet.update(dt)

    def createPelletlist(self, pelletfile):
        """
        Erstellt die Pellet-Liste aus einer Textdatei.
        Args:
            pelletfile: Pfad zur Textdatei mit dem Pellet-Layout
        """
        data = self.readPelletfile(pelletfile)
        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                if data[row][col] in ['.', '+']:
                    self.pelletList.append(Pellet(row, col))
                elif data[row][col] in ['P', 'p']:
                    pp = PowerPellet(row, col)
                    self.pelletList.append(pp)
                    self.powerpellets.append(pp)

    def readPelletfile(self, textfile):
        """
        Liest die Pellet-Karte aus einer Textdatei.
        Args:
            textfile: Pfad zur Textdatei
        Returns:
            numpy.ndarray: Matrix mit dem Pellet-Layout
        """
        return np.loadtxt(textfile, dtype='<U1')

    def isEmpty(self):
        """
        Prüft, ob alle Pellets eingesammelt wurden.
        Returns:
            bool: True wenn keine Pellets mehr übrig sind
        """
        return len(self.pelletList) == 0

    def render(self, screen):
        """
        Zeichnet alle sichtbaren Pellets.
        Args:
            screen: Pygame-Oberflächenobjekt zum Zeichnen
        """
        for pellet in self.pelletList:
            pellet.render(screen)