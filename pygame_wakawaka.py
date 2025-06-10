import pygame
import pygame_gui
from pellets import PelletGroup

pygame.init()

pygame.display.set_caption('Pacman by the Ghostbusters')
window_surface = pygame.display.set_mode((540, 720))

background = pygame.Surface((540, 720))
background.fill(pygame.Color('#000000'))

manager = pygame_gui.UIManager((540, 720))

start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((170, 275), (200, 50)),
                                            text='Start',
                                            manager=manager)

end_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((450, 10), (80, 30)),
                                          text='End game',
                                          manager=manager)

player_x = 270  # starts in middle
player_y = 360
player_size = 10
player_speed = 5

game_started = False

clock = pygame.time.Clock()
is_running = True

while is_running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == start_button:
                print('Waka Waka Waka...')
                game_started = True
                start_button.hide()  # bye bye button
            elif event.ui_element == end_button:
                is_running = False

        manager.process_events(event)

    # movement stuff
    if game_started:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            player_y -= player_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            player_y += player_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player_x += player_speed

        # dont let it go off screen lol
        player_x = max(0, min(540 - player_size, player_x))
        player_y = max(0, min(720 - player_size, player_y))

    manager.update(time_delta)

    # draw everything
    window_surface.blit(background, (0, 0))

    # yellow square time
    if game_started:
        pygame.draw.rect(window_surface, pygame.Color('#FFFF00'),
                         (int(player_x), int(player_y), player_size, player_size))

    manager.draw_ui(window_surface)
    pygame.display.update()
