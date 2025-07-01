"""
Node System für erweiterte Pathfinding
Basiert auf dem ursprünglichen node.py Code und spielfeld.py
"""

from .constants import GRID_SIZE


class Node:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.px = grid_x * GRID_SIZE + GRID_SIZE // 2  # Pixel-Koordinaten
        self.py = grid_y * GRID_SIZE + GRID_SIZE // 2
        self.neighbors = []

    def __repr__(self):
        return f"Node({self.grid_x}, {self.grid_y})"

    def get_neighbor_in_direction(self, direction):
        """Gibt den Nachbar-Node in der angegebenen Richtung zurück (falls vorhanden)"""
        # Konvertiere String-Richtung in dx, dy
        dir_vectors = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}

        if direction not in dir_vectors:
            return None

        dx, dy = dir_vectors[direction]

        # Suche nach einem Nachbarn in der angegebenen Richtung
        for neighbor in self.neighbors:
            # Prüfe, ob der Nachbar in der gewünschten Richtung liegt
            if (
                neighbor.grid_x - self.grid_x == dx
                and neighbor.grid_y - self.grid_y == dy
            ):
                return neighbor

        # Kein Nachbar in dieser Richtung gefunden
        return None


def build_nodes_and_graph(maze):
    """Erstellt Knoten und Graphen aus dem Maze - basierend auf ursprünglichem Code"""
    nodes = []
    node_map = {}

    # Erstelle Knoten für alle freien Felder
    for y in range(maze.height):
        for x in range(maze.width):
            if not maze.is_wall(x, y):
                n = Node(x, y)
                nodes.append(n)
                node_map[(x, y)] = n

    # Verbinde Nachbarn nur, wenn beide Weg sind und kein Hindernis dazwischen liegt
    for n in nodes:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = n.grid_x + dx, n.grid_y + dy

            # Prüfe auf Tunnel-Teleportation
            tunnel_exit = maze.get_tunnel_exit(n.grid_x, n.grid_y, dx, dy)
            if tunnel_exit:
                tx, ty = tunnel_exit
                if (tx, ty) in node_map:
                    n.neighbors.append(node_map[(tx, ty)])
            # Normale Nachbarverbindung - nur wenn direkt angrenzend und kein Hindernis
            elif (nx, ny) in node_map:
                # Prüfe, ob der Weg zwischen den Nodes frei ist
                # Direkte Nachbarn sind immer erreichbar, wenn beide keine Wände sind
                n.neighbors.append(node_map[(nx, ny)])

    # Entferne ungültige Verbindungen, die durch Wände führen würden
    for n in nodes:
        valid_neighbors = []
        for neighbor in n.neighbors:
            # Prüfe, ob direkt benachbart
            dx = neighbor.grid_x - n.grid_x
            dy = neighbor.grid_y - n.grid_y

            # Wenn nicht direkt benachbart (dx oder dy > 1), prüfe ob ein gültiger Pfad existiert
            if abs(dx) > 1 or abs(dy) > 1:
                # Prüfe für Tunnel-Verbindungen (die sind auch erlaubt)
                tunnel_exit = maze.get_tunnel_exit(n.grid_x, n.grid_y, dx, dy)
                if tunnel_exit and tunnel_exit == (neighbor.grid_x, neighbor.grid_y):
                    valid_neighbors.append(neighbor)
            else:
                valid_neighbors.append(neighbor)

        # Ersetze die Nachbarliste mit den gültigen Nachbarn
        n.neighbors = valid_neighbors

    return nodes, node_map


def find_nearest_node(node_map, grid_x, grid_y):
    """Findet den nächsten Node zu den angegebenen Grid-Koordinaten"""
    # Prüfe zuerst, ob exakt an diesen Koordinaten ein Node existiert
    if (grid_x, grid_y) in node_map:
        return node_map[(grid_x, grid_y)]

    # Wenn nicht, suche nach dem nächstgelegenen Node
    min_distance = float("inf")
    nearest_node = None

    for (nx, ny), node in node_map.items():
        # Berechne die Distanz (Euklidisch)
        distance = ((nx - grid_x) ** 2 + (ny - grid_y) ** 2) ** 0.5

        if distance < min_distance:
            min_distance = distance
            nearest_node = node

    return nearest_node


def find_node_by_grid(node_map, grid_x, grid_y):
    """Findet einen Node an den exakten Grid-Koordinaten oder gibt None zurück"""
    return node_map.get((grid_x, grid_y), None)
