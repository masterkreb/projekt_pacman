import pygame
import pygame_gui

pygame.init()
pygame.mixer.init()

pygame.display.set_caption('Pacman by the Ghostbusters')
window_surface = pygame.display.set_mode((540, 720))

# Window Icon setzen
try:
    icon = pygame.image.load("feature/images/icon.png")
    pygame.display.set_icon(icon)
    print("Game icon loaded successfully!")
except (pygame.error, FileNotFoundError) as e:
    print(f"Could not load game icon: {e}")

background = pygame.Surface((540, 720))
background.fill(pygame.Color('#000000'))

manager = pygame_gui.UIManager((540, 720))

# =========================
# UI BUTTONS SETUP
# =========================
start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((170, 275), (200, 50)),
                                            text='Start',
                                            manager=manager)

# Einfache Text-Buttons - Unicode funktioniert nicht zuverlässig
end_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((450, 10), (80, 30)),
                                          text='EXIT',
                                          manager=manager)

mute_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 10), (90, 30)),
                                           text='SOUND: ON',
                                           manager=manager)

# =========================
# PLAYER VARIABLEN
# =========================
player_x = 270
player_y = 360
player_size = 20  # größer als das winzige Original
player_speed = 3  # nicht zu schnell sonst wird's stressig

# Movement System - wie im echten Pacman (bewegt sich ständig)
current_direction = None
next_direction = None
velocity_x = 0
velocity_y = 0

move_keys = {
    'up': [pygame.K_w, pygame.K_UP],
    'down': [pygame.K_s, pygame.K_DOWN],
    'left': [pygame.K_a, pygame.K_LEFT],
    'right': [pygame.K_d, pygame.K_RIGHT]
}

# =========================
# SOUND SYSTEM
# =========================
try:
    wakawaka_sound = pygame.mixer.Sound("feature/sounds/wakawaka.wav")
    wakawaka_sound.set_volume(0.2)  # 20% - endlich nicht mehr ohrenbetäubend
    wakawaka_channel = None
    sound_loaded = True
    print("WakaWaka sound loaded successfully at 20% volume!")
except (pygame.error, FileNotFoundError) as e:
    print(f"Could not load wakawaka.wav: {e}")
    print("Make sure the file exists at 'feature/sounds/wakawaka.wav'")
    wakawaka_sound = None
    sound_loaded = False

sound_enabled = True
game_started = False
is_moving = False
last_moving_state = False

clock = pygame.time.Clock()
is_running = True


# =========================
# ALLE FUNKTIONEN HIER - RICHTIGE REIHENFOLGE!
# =========================
def get_pressed_direction(keys):
    """Checkt welche Richtungstaste gedrückt wird"""
    for direction, key_list in move_keys.items():
        for key in key_list:
            if keys[key]:
                return direction
    return None


def set_velocity_from_direction(direction):
    """Setzt die Geschwindigkeit basierend auf Richtung - originales Pacman Movement"""
    global velocity_x, velocity_y
    if direction == 'up':
        velocity_x, velocity_y = 0, -player_speed
    elif direction == 'down':
        velocity_x, velocity_y = 0, player_speed
    elif direction == 'left':
        velocity_x, velocity_y = -player_speed, 0
    elif direction == 'right':
        velocity_x, velocity_y = player_speed, 0
    else:
        velocity_x, velocity_y = 0, 0


def start_wakawaka_sound():
    """Startet den WakaWaka Sound aber nur wenn Sound aktiviert ist"""
    global wakawaka_channel
    if sound_loaded and wakawaka_sound and sound_enabled:
        if wakawaka_channel is None or not wakawaka_channel.get_busy():
            wakawaka_channel = wakawaka_sound.play(-1)


def stop_wakawaka_sound():
    """Stoppt den WakaWaka Sound"""
    global wakawaka_channel
    if wakawaka_channel and wakawaka_channel.get_busy():
        wakawaka_channel.stop()
        wakawaka_channel = None


def update_mute_button():
    """Updated das Mute Button Text basierend auf sound_enabled"""
    if sound_enabled:
        mute_button.set_text('SOUND: ON')
    else:
        mute_button.set_text('SOUND: OFF')


def toggle_sound():
    """Schaltet Sound an/aus und updated das Icon"""
    global sound_enabled
    sound_enabled = not sound_enabled

    if not sound_enabled:
        stop_wakawaka_sound()  # Stoppe Sound wenn ausgeschaltet
    else:
        # Wenn Sound wieder an und Pacman sich bewegt, starte Sound
        if game_started and is_moving:
            start_wakawaka_sound()

    update_mute_button()


# =========================
# MAIN GAME LOOP
# =========================
while is_running:
    time_delta = clock.tick(60) / 1000.0

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == start_button:
                print('Waka Waka Waka...')
                game_started = True
                start_button.hide()
            elif event.ui_element == end_button:
                is_running = False
            elif event.ui_element == mute_button:
                toggle_sound()

        manager.process_events(event)

    # =========================
    # PACMAN MOVEMENT LOGIC
    # =========================
    if game_started:
        keys = pygame.key.get_pressed()

        # Input handling - wie im Original Pacman
        pressed_direction = get_pressed_direction(keys)
        if pressed_direction:
            next_direction = pressed_direction

        # Movement State Machine
        if next_direction and current_direction is None:
            # Starte Bewegung
            current_direction = next_direction
            set_velocity_from_direction(current_direction)
            next_direction = None
        elif next_direction and next_direction != current_direction:
            # Richtung ändern
            current_direction = next_direction
            set_velocity_from_direction(current_direction)
            next_direction = None

        # Physik Update - Pacman bewegt sich kontinuierlich
        old_x, old_y = player_x, player_y
        new_x = player_x + velocity_x
        new_y = player_y + velocity_y

        # Boundary Collision
        new_x = max(0, min(540 - player_size, new_x))
        new_y = max(0, min(720 - player_size, new_y))

        # Wand getroffen? Dann stoppen
        if new_x != player_x + velocity_x or new_y != player_y + velocity_y:
            velocity_x, velocity_y = 0, 0
            current_direction = None

        player_x, player_y = new_x, new_y

        # Sound Management
        is_moving = (velocity_x != 0 or velocity_y != 0)

        if is_moving and not last_moving_state:
            start_wakawaka_sound()
        elif not is_moving and last_moving_state:
            stop_wakawaka_sound()

        last_moving_state = is_moving

    # =========================
    # RENDERING
    # =========================
    manager.update(time_delta)
    window_surface.blit(background, (0, 0))

    # Der gelbe Pacman - endlich in anständiger Größe
    if game_started:
        pygame.draw.rect(window_surface, pygame.Color('#FFFF00'),
                         (int(player_x), int(player_y), player_size, player_size))

    manager.draw_ui(window_surface)
    pygame.display.update()

# Cleanup beim Beenden
if sound_loaded:
    stop_wakawaka_sound()
pygame.quit()