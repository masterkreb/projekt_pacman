class NodeGroup(object):
    """
    Verwaltet die Knoten im Pac-Man-Labyrinth.
    Diese Klasse ist verantwortlich für die Verwaltung der Wegpunkte und Pfade,
    die Pac-Man und die Geister im Spiel nutzen können.
    """

    def __init__(self, level):
        """
        Initialisiert eine neue NodeGroup.
        
        Args:
            level: Das Level-Layout, das die Knoten enthält
        """
        self.level = level
        self.nodesLUT = {}  # Look-Up-Table für schnellen Zugriff auf Knoten
        
        # Symbole für verschiedene Knotentypen
        self.nodeSymbols = [
            '+',  # Kreuzung
            'p',  # Pellet-Position
            'n'   # Normaler Wegpunkt
        ]
        
        # Symbole für verschiedene Pfadtypen
        self.pathSymbols = [
            '.',  # Normaler Pfad
            '|',  # Vertikaler Pfad
            'p'   # Pellet-Pfad
        ]

    def add_node(self, node):
        """
        Fügt einen neuen Knoten zur Gruppe hinzu.
        
        Args:
            node: Der hinzuzufügende Knoten
        """
        x = node.position.x
        y = node.position.y
        key = (x, y)
        self.nodesLUT[key] = node

    def get_node(self, x, y):
        """
        Holt einen Knoten an der angegebenen Position.
        
        Args:
            x: X-Koordinate
            y: Y-Koordinate
            
        Returns:
            Node: Der gefundene Knoten oder None
        """
        key = (x, y)
        return self.nodesLUT.get(key, None)

    def is_valid_position(self, position):
        """
        Überprüft, ob eine Position im Spielfeld gültig ist.
        
        Args:
            position: Tupel mit (x, y) Koordinaten
            
        Returns:
            bool: True wenn die Position gültig ist, sonst False
        """
        return position in self.nodesLUT