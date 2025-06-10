import pygame
import pygame_gui
import os

pygame.init()
pygame.mixer.init()

pygame.display.set_caption('Pacman by the Ghostbusters')
window_surface = pygame.display.set_mode((540, 720))

# Hintergrundbild laden (falls vorhanden)
try:
    # Du kannst hier den Pfad zu deinem Hintergrundbild einfügen
    original_image = pygame.image.load('background.png')  # oder .jpg

    # Option 1: Bild zentriert zuschneiden (empfohlen für quadratische Bilder)
    # Schneide das Bild so zu, dass es das richtige Seitenverhältnis hat
    img_width, img_height = original_image.get_size()
    target_ratio = 540 / 720  # 0.75
    current_ratio = img_width / img_height

    if current_ratio > target_ratio:
        # Bild ist zu breit - an den Seiten beschneiden
        new_width = int(img_height * target_ratio)
        crop_x = (img_width - new_width) // 2
        cropped_image = original_image.subsurface((crop_x, 0, new_width, img_height))
    else:
        # Bild ist zu hoch - oben und unten beschneiden
        new_height = int(img_width / target_ratio)
        crop_y = (img_height - new_height) // 2
        cropped_image = original_image.subsurface((0, crop_y, img_width, new_height))

    background_image = pygame.transform.scale(cropped_image, (540, 720))
    has_background_image = True
except:
    # Fallback: schwarzer Hintergrund
    background_image = pygame.Surface((540, 720))
    background_image.fill(pygame.Color('#1a0d2e'))  # Dunkelviolett für gruseligere Atmosphäre
    has_background_image = False

# Hintergrundmusik laden und abspielen
try:
    pygame.mixer.music.load('menu_music.mp3')  # oder .wav, .ogg
    pygame.mixer.music.set_volume(0.3)  # Lautstärke 30%
    pygame.mixer.music.play(-1)  # Endlosschleife
    print("Hintergrundmusik geladen!")
except:
    print("Keine Hintergrundmusik gefunden - stelle sicher, dass 'menu_music.mp3' im Projektordner ist")

# Soundeffekte laden
try:
    start_sound = pygame.mixer.Sound('horror_start.wav')  # oder .mp3, .ogg
    start_sound.set_volume(0.5)
    print("Horror-Soundeffekt geladen!")
except:
    print("Kein Horror-Soundeffekt gefunden - stelle sicher, dass 'horror_start.wav' im Projektordner ist")
    start_sound = None

# Menu-Soundeffekte laden
try:
    menu_hover_sound = pygame.mixer.Sound('menu_hover.wav')  # Sound beim Drüberfahren
    menu_hover_sound.set_volume(0.3)
    print("Menu-Hover-Sound geladen!")
except:
    print("Kein Menu-Hover-Sound gefunden - erstelle 'menu_hover.wav' für Hover-Effekte")
    menu_hover_sound = None

try:
    menu_click_sound = pygame.mixer.Sound('menu_click.wav')  # Sound beim Klicken
    menu_click_sound.set_volume(0.4)
    print("Menu-Click-Sound geladen!")
except:
    print("Kein Menu-Click-Sound gefunden - erstelle 'menu_click.wav' für Klick-Effekte")
    menu_click_sound = None

# Bewegungs-Soundeffekte laden
try:
    move_sound = pygame.mixer.Sound('pacman_move.wav')  # Sound beim Bewegen
    move_sound.set_volume(0.2)
    print("Bewegungs-Sound geladen!")
except:
    print("Kein Bewegungs-Sound gefunden - erstelle 'pacman_move.wav' für Bewegungen")
    move_sound = None

manager = pygame_gui.UIManager((540, 720))

# Schriftarten für Titel laden (Horror-Style)
try:
    # Versuche zuerst eine Horror-passende Schrift zu laden
    title_font = pygame.font.Font(None, 80)  # Noch größer für mehr Impact
    subtitle_font = pygame.font.Font(None, 28)  # Etwas kleiner für bessere Lesbarkeit
    button_font = pygame.font.Font(None, 32)  # Schrift für Buttons
except:
    title_font = pygame.font.get_default_font()
    subtitle_font = pygame.font.get_default_font()
    button_font = pygame.font.get_default_font()

# Titel-Texte erstellen
title_surface = title_font.render("PACMAN", True, pygame.Color('#FF0000'))  # Rot für Horror-Feeling
subtitle_surface = subtitle_font.render("The Return of the Blue Ghost", True, pygame.Color('#00FFFF'))  # Cyan

# Button-Texte erstellen
start_text = button_font.render("► START", True, pygame.Color('#FFFFFF'))
exit_text = button_font.render("✕ EXIT", True, pygame.Color('#FFFFFF'))

# Button-Positionen (Resident Evil Style - untereinander, zentriert, WEITER UNTEN)
start_button_rect = pygame.Rect(220, 550, 100, 40)  # Noch weiter unten (war 450)
exit_button_rect = pygame.Rect(220, 600, 100, 40)  # Entsprechend weiter unten (war 500)

# Hover-Effekte für Buttons
start_hovered = False
exit_hovered = False
last_hovered_button = None  # Für Hover-Sound-Kontrolle

# Bewegungs-Sound-Kontrolle
last_move_time = 0
move_sound_delay = 200  # Millisekunden zwischen Bewegungs-Sounds

# Keine pygame_gui Buttons mehr - wir zeichnen sie selbst!

player_x = 270  # starts in middle
player_y = 360
player_size = 10
player_speed = 5

game_started = False
start_effect_playing = False
start_effect_timer = 0
start_effect_duration = 5000  # 5 Sekunden
darkness_overlay = 0  # 0 = hell, 255 = komplett dunkel

# Game States
MENU = 0
HORROR_EFFECT = 1
GAMEPLAY = 2
current_state = MENU

clock = pygame.time.Clock()
is_running = True

while is_running:
    time_delta = clock.tick(60) / 1000.0
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        # Maus-Events für unsere eigenen Buttons
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Start-Button geklickt?
            if start_button_rect.collidepoint(mouse_pos) and current_state == MENU:
                print('Waka Waka Waka...')

                # Menu-Click-Sound abspielen
                if menu_click_sound:
                    menu_click_sound.play()

                # Horror-Soundeffekt abspielen
                if start_sound:
                    start_sound.play()

                # Zum Horror-Effekt wechseln
                current_state = HORROR_EFFECT
                start_effect_timer = current_time

                # Hintergrundmusik stoppen
                pygame.mixer.music.stop()

            # Exit-Button geklickt?
            elif exit_button_rect.collidepoint(mouse_pos):
                # Menu-Click-Sound abspielen
                if menu_click_sound:
                    menu_click_sound.play()
                is_running = False

        # Maus-Hover-Effekte mit Sound
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            new_start_hovered = start_button_rect.collidepoint(mouse_pos) and current_state == MENU
            new_exit_hovered = exit_button_rect.collidepoint(mouse_pos) and current_state == MENU

            # Hover-Sound abspielen wenn ein neuer Button gehovered wird
            current_hovered = None
            if new_start_hovered:
                current_hovered = "start"
            elif new_exit_hovered:
                current_hovered = "exit"

            if current_hovered != last_hovered_button and current_hovered is not None:
                if menu_hover_sound:
                    menu_hover_sound.play()
                last_hovered_button = current_hovered
            elif current_hovered is None:
                last_hovered_button = None

            start_hovered = new_start_hovered
            exit_hovered = new_exit_hovered

    # State Management
    if current_state == HORROR_EFFECT:
        elapsed_time = current_time - start_effect_timer

        if elapsed_time < start_effect_duration:
            # Langsam verdunkeln über die Dauer des Effekts
            progress = elapsed_time / start_effect_duration
            darkness_overlay = int(255 * progress)
        else:
            # Horror-Effekt beendet - zum Gameplay wechseln
            current_state = GAMEPLAY
            darkness_overlay = 0
            print("🎮 Gameplay gestartet! Hier kommt euer Team-Feature!")

    # movement stuff (nur im Gameplay-Modus)
    if current_state == GAMEPLAY:
        keys = pygame.key.get_pressed()
        moved = False

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            player_y -= player_speed
            moved = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            player_y += player_speed
            moved = True
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player_x -= player_speed
            moved = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player_x += player_speed
            moved = True

        # Bewegungs-Sound abspielen (aber nicht zu oft)
        if moved and move_sound and (current_time - last_move_time) > move_sound_delay:
            move_sound.play()
            last_move_time = current_time

        # dont let it go off screen lol
        player_x = max(0, min(540 - player_size, player_x))
        player_y = max(0, min(720 - player_size, player_y))

    # Verdunkelungseffekt verwalten
    if start_effect_playing:
        elapsed_time = current_time - start_effect_timer

        if elapsed_time < start_effect_duration:
            # Langsam verdunkeln über die Dauer des Effekts
            progress = elapsed_time / start_effect_duration
            darkness_overlay = int(255 * progress)
        else:
            # Effekt beendet
            start_effect_playing = False
            darkness_overlay = 0

    # movement stuff
    if game_started and not start_effect_playing:  # Bewegung nur wenn Effekt vorbei ist
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
    window_surface.blit(background_image, (0, 0))

    # Titel zeichnen (nur im Menü) - HÖHER positioniert
    if not game_started:
        # Haupttitel "PACMAN"
        title_rect = title_surface.get_rect(center=(270, 100))  # Viel höher (war 150)
        window_surface.blit(title_surface, title_rect)

        # Untertitel "The Return of the Blue Ghost"
        subtitle_rect = subtitle_surface.get_rect(center=(270, 140))  # Entsprechend höher (war 200)
        window_surface.blit(subtitle_surface, subtitle_rect)

        # Custom Buttons zeichnen (Resident Evil Style)
        # Start Button
        start_color = pygame.Color('#FFFF00') if start_hovered else pygame.Color('#FFFFFF')  # Gelb bei Hover
        start_text_colored = button_font.render("► START", True, start_color)
        start_text_rect = start_text_colored.get_rect(center=start_button_rect.center)
        window_surface.blit(start_text_colored, start_text_rect)

        # Exit Button
        exit_color = pygame.Color('#FF4444') if exit_hovered else pygame.Color('#FFFFFF')  # Rot bei Hover
        exit_text_colored = button_font.render("✕ EXIT", True, exit_color)
        exit_text_rect = exit_text_colored.get_rect(center=exit_button_rect.center)
        window_surface.blit(exit_text_colored, exit_text_rect)

    # yellow square time
    if game_started and not start_effect_playing:
        pygame.draw.rect(window_surface, pygame.Color('#FFFF00'),
                         (int(player_x), int(player_y), player_size, player_size))

    # Verdunkelungsoverlay zeichnen (nur während Horror-Effekt)
    if current_state == HORROR_EFFECT and darkness_overlay > 0:
        dark_surface = pygame.Surface((540, 720))
        dark_surface.fill((0, 0, 0))
        dark_surface.set_alpha(darkness_overlay)
        window_surface.blit(dark_surface, (0, 0))

    pygame.display.update()

pygame.quit()
