import pygame
from spielfeld import build_nodes_and_graph, get_tunnel_exit

BILDDATEI = "bilder/Teil_017_Spielfeld.png"

class Player:
    def __init__(self, node, all_nodes, color=(255,255,0)):
        self.pos = node
        self.target = None
        self.color = color
        self.all_nodes = all_nodes

    def move(self, direction):
        dir_map = {'L':(-1,0),'R':(1,0),'U':(0,-1),'D':(0,1)}
        dx, dy = dir_map[direction]
        next_x = self.pos.grid_x + dx
        next_y = self.pos.grid_y + dy

        # >>> Tunnel-Abfrage beim Spielfeld <<<
        tunnel_exit = get_tunnel_exit(self.pos.grid_x, self.pos.grid_y, dx, dy)
        if tunnel_exit:
            self.target = self.find_node_by_grid(*tunnel_exit)
            return

        for nb in self.pos.neighbors:
            if nb.grid_x == next_x and nb.grid_y == next_y:
                self.target = nb
                return

    def update(self):
        if self.target:
            self.pos = self.target
            self.target = None

    def draw(self, screen, radius):
        pygame.draw.circle(screen, self.color, (self.pos.px, self.pos.py), radius)

    def find_node_by_grid(self, x, y):
        for n in self.all_nodes:
            if n.grid_x == x and n.grid_y == y:
                return n
        return None

def main():
    pygame.init()
    bg_img_raw = pygame.image.load(BILDDATEI)
    w, h = bg_img_raw.get_width(), bg_img_raw.get_height()
    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption("Pac-Man Layout-Array mit Tunnel (zentral)")
    clock = pygame.time.Clock()
    bg_img = bg_img_raw.convert()

    nodes, TILE = build_nodes_and_graph()
    start = min(nodes, key=lambda n: n.grid_x + n.grid_y)
    player = Player(start, nodes)

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                keys = {pygame.K_LEFT:'L', pygame.K_RIGHT:'R', pygame.K_UP:'U', pygame.K_DOWN:'D'}
                if e.key in keys:
                    player.move(keys[e.key])

        player.update()
        screen.blit(bg_img, (0,0))

        # Debug-Draws sind auskommentiert!
        # for n in nodes:
        #     for nb in n.neighbors:
        #         pygame.draw.line(screen, (0,255,255), (n.px, n.py), (nb.px, nb.py), 2)
        # for n in nodes:
        #     pygame.draw.circle(screen, (0,255,0), (n.px, n.py), 4)

        player.draw(screen, TILE//2)
        pygame.display.flip()
        clock.tick(15)
    pygame.quit()

if __name__ == "__main__":
    main()
