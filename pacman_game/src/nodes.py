"""
Node System für erweiterte Pathfinding
Basiert auf dem ursprünglichen node.py Code
"""

from src.constants import GRID_SIZE

class Node:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.px = grid_x * GRID_SIZE + GRID_SIZE // 2  # Pixel-Koordinaten
        self.py = grid_y * GRID_SIZE + GRID_SIZE // 2
        self.neighbors = []

    def __repr__(self):
        return f"Node({self.grid_x}, {self.grid_y})"

def build_nodes_and_graph(maze):
    """Erstellt Knoten und Graphen aus dem Maze - aus ursprünglichem Code"""
    nodes = []
    node_map = {}
    
    # Erstelle Knoten für alle freien Felder
    for y in range(maze.height):
        for x in range(maze.width):
            if not maze.is_wall(x, y):
                n = Node(x, y)
                nodes.append(n)
                node_map[(x, y)] = n

    # Verbinde Nachbarn nur, wenn beide Weg sind
    for n in nodes:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = n.grid_x + dx, n.grid_y + dy
            if (nx, ny) in node_map:
                n.neighbors.append(node_map[(nx, ny)])
    
    return nodes, node_map
