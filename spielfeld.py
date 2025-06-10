# spielfeld.py

TILE = 24  # Passt exakt zu deinem PNG (672x744)

layout = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.#####.##.#####.######",
    "######.#####.##.#####.######",
    "######.##..........##.######",
    "######.##.########.##.######",
    "######.##.########.##.######",
    "..........########..........",
    "######.##.########.##.######",
    "######.##.########.##.######",
    "######.##..........##.######",
    "######.##.########.##.######",
    "######.##.########.##.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#...##................##...#",
    "###.##.##.########.##.##.###",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################",
]

ROWS = len(layout)
COLS = len(layout[0])

class Node:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.px = grid_x * TILE + TILE // 2
        self.py = grid_y * TILE + TILE // 2
        self.neighbors = []

    def __repr__(self):
        return f"Node({self.grid_x}, {self.grid_y})"

def build_nodes_and_graph():
    nodes = []
    node_map = {}
    for y in range(ROWS):
        for x in range(COLS):
            if layout[y][x] != "#":
                n = Node(x, y)
                nodes.append(n)
                node_map[(x, y)] = n

    # Verbinde Nachbarn nur, wenn beide Weg sind
    for n in nodes:
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = n.grid_x + dx, n.grid_y + dy
            if (nx, ny) in node_map:
                n.neighbors.append(node_map[(nx, ny)])
    return nodes, TILE

def get_tunnel_exit(x, y, dx, dy):
    TUNNEL_ROW = 14
    LEFT_TUNNEL_X = 0
    RIGHT_TUNNEL_X = 27
    if y == TUNNEL_ROW:
        if x == LEFT_TUNNEL_X and dx == -1:
            return (RIGHT_TUNNEL_X, TUNNEL_ROW)
        if x == RIGHT_TUNNEL_X and dx == 1:
            return (LEFT_TUNNEL_X, TUNNEL_ROW)
    return None
