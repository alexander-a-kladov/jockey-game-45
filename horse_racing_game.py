#!/usr/bin/python3

# =========================================================
# HORSE RACE
#
# pip install pygame moviepy imageio imageio-ffmpeg
#
# Для звука:
# ffmpeg -i videos/trumpet.mp4 videos/trumpet.mp3
# ffmpeg -i videos/congrats.mp4 videos/congrats.mp3
# =========================================================

import pygame
import sys
from moviepy import VideoFileClip

# =========================================================
# НАСТРОЙКИ
# =========================================================
WIDTH, HEIGHT = 1280, 720
FPS = 60

GROUND_Y = 580

HORSE_SCALE = 0.55

MAX_SPEED = 950
ACCELERATION = 520
FRICTION = 240
BRAKE_FORCE = 950

GRAVITY = 1700
JUMP_FORCE = -760

MIN_JUMP_SPEED = MAX_SPEED * 0.25

FINISH_DISTANCE = 500

# =========================================================
# ИНИЦИАЛИЗАЦИЯ
# =========================================================
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Horse Race")

clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 28)
big_font = pygame.font.SysFont("arial", 64, bold=True)

# =========================================================
# ЗАГРУЗКА СПРАЙТОВ
# =========================================================
sheet = pygame.image.load("horses.png").convert_alpha()

sheet_w, sheet_h = sheet.get_size()

COLS = 4
ROWS = 3

frame_w = sheet_w // COLS
frame_h = sheet_h // ROWS

frames = []

# справа налево, сверху вниз
for row in range(ROWS):

    for col in reversed(range(COLS)):

        rect = pygame.Rect(
            col * frame_w,
            row * frame_h,
            frame_w,
            frame_h
        )

        frame = sheet.subsurface(rect).copy()

        frame = pygame.transform.smoothscale(
            frame,
            (
                int(frame_w * HORSE_SCALE),
                int(frame_h * HORSE_SCALE)
            )
        )

        frames.append(frame)

# =========================================================
# ОФФСЕТЫ КОПЫТ
# =========================================================
ground_offsets = [
    20, 16, 10, 8,
    8, 12, 18, 22,
    16, 8, 0, 12
]

ground_offsets = [
    int(v * HORSE_SCALE)
    for v in ground_offsets
]

# =========================================================
# ВИДЕО
# =========================================================
start_clip = VideoFileClip("videos/trumpet.mp4")
finish_clip = VideoFileClip("videos/congrats.mp4")

# =========================================================
# ЗВУК
# =========================================================
start_sound = pygame.mixer.Sound("videos/trumpet.mp3")
finish_sound = pygame.mixer.Sound("videos/congrats.mp3")

# =========================================================
# СОСТОЯНИЯ
# =========================================================
STATE_START_VIDEO = 0
STATE_PLAYING = 1
STATE_FINISHED_WAIT = 2
STATE_FINISH_VIDEO = 3
STATE_RESTART_WAIT = 4

game_state = STATE_START_VIDEO

# =========================================================
# РЕКОРД
# =========================================================
best_time = None

# =========================================================
# ИГРОВЫЕ ПЕРЕМЕННЫЕ
# =========================================================
horse_x = 0
horse_y = 0

vertical_velocity = 0
is_jumping = False

speed = 0

distance_m = 0
elapsed_time = 0

frame_index = 10
animation_timer = 0

finish_timer = 0
video_timer = 0

# флаги воспроизведения звука
start_sound_played = False
finish_sound_played = False

# =========================================================
# ФУНКЦИИ
# =========================================================
def reset_game():

    global horse_x
    global horse_y
    global vertical_velocity
    global is_jumping
    global speed
    global distance_m
    global elapsed_time
    global frame_index
    global animation_timer
    global finish_timer
    global video_timer
    global game_state
    global start_sound_played
    global finish_sound_played

    horse_x = 0
    horse_y = 0

    vertical_velocity = 0
    is_jumping = False

    speed = 0

    distance_m = 0
    elapsed_time = 0

    frame_index = 10
    animation_timer = 0

    finish_timer = 0
    video_timer = 0

    start_sound_played = False
    finish_sound_played = False

    game_state = STATE_START_VIDEO


def get_ground_y(frame_id):

    frame = frames[frame_id]

    return (
        GROUND_Y
        - frame.get_height()
        + ground_offsets[frame_id]
    )


def draw_world():

    global horse_x

    screen.fill((170, 220, 255))

    # земля
    pygame.draw.rect(
        screen,
        (60, 160, 60),
        (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y)
    )

    # линии движения
    camera_x = horse_x - 240

    for i in range(-2, 25):

        x = (i * 140) - (camera_x % 140)

        pygame.draw.line(
            screen,
            (80, 130, 80),
            (x, GROUND_Y),
            (x + 40, GROUND_Y + 40),
            3
        )

    # =====================================================
    # ФИНИШ
    # =====================================================
    finish_world_x = FINISH_DISTANCE * 100

    finish_screen_x = finish_world_x - camera_x

    if -200 < finish_screen_x < WIDTH + 200:

        pole_top = GROUND_Y - 260

        pygame.draw.rect(
            screen,
            (80, 80, 80),
            (finish_screen_x, pole_top, 10, 260)
        )

        FLAG_SIZE = 24

        for y in range(6):
            for x in range(8):

                color = (
                    (255, 255, 255)
                    if (x + y) % 2 == 0
                    else (0, 0, 0)
                )

                pygame.draw.rect(
                    screen,
                    color,
                    (
                        finish_screen_x + 10 + x * FLAG_SIZE,
                        pole_top + y * FLAG_SIZE,
                        FLAG_SIZE,
                        FLAG_SIZE
                    )
                )

    # =====================================================
    # ЛОШАДЬ
    # =====================================================
    current_frame = frames[frame_index]

    draw_x = 240

    draw_y = (
        get_ground_y(frame_index)
        + horse_y
    )

    screen.blit(current_frame, (draw_x, draw_y))

    # =====================================================
    # UI
    # =====================================================
    speed_kmh = speed * 0.12

    ui_lines = [
        f"Speed: {speed_kmh:.1f} km/h",
        f"Distance: {distance_m:.2f} / 500 m",
        f"Time: {elapsed_time:.1f} s"
    ]

    if best_time is not None:
        ui_lines.append(f"Best time: {best_time:.1f} s")

    y = 20

    for line in ui_lines:

        txt = font.render(line, True, (20, 20, 20))

        screen.blit(txt, (20, y))

        y += 40

    controls = font.render(
        "RIGHT = accelerate   LEFT = brake   SPACE = jump",
        True,
        (20, 20, 20)
    )

    screen.blit(controls, (20, HEIGHT - 50))


def play_video_frame(clip, timer, size):

    frame = clip.get_frame(timer)

    frame_surface = pygame.surfarray.make_surface(
        frame.swapaxes(0, 1)
    )

    frame_surface = pygame.transform.smoothscale(
        frame_surface,
        size
    )

    x = WIDTH // 2 - size[0] // 2
    y = HEIGHT // 2 - size[1] // 2

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(120)
    overlay.fill((0, 0, 0))

    screen.blit(overlay, (0, 0))
    screen.blit(frame_surface, (x, y))


# =========================================================
# СТАРТ
# =========================================================
reset_game()

running = True

# =========================================================
# ГЛАВНЫЙ ЦИКЛ
# =========================================================
while running:

    dt = clock.tick(FPS) / 1000.0

    # =====================================================
    # СОБЫТИЯ
    # =====================================================
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # прыжок
        if (
            game_state == STATE_PLAYING
            and event.type == pygame.KEYDOWN
            and event.key == pygame.K_SPACE
        ):

            if (
                not is_jumping
                and speed >= MIN_JUMP_SPEED
            ):
                is_jumping = True
                vertical_velocity = JUMP_FORCE

        # рестарт
        if (
            game_state == STATE_RESTART_WAIT
            and event.type == pygame.KEYDOWN
            and event.key == pygame.K_SPACE
        ):

            reset_game()

    keys = pygame.key.get_pressed()

    # =====================================================
    # СТАРТОВОЕ ВИДЕО
    # =====================================================
    if game_state == STATE_START_VIDEO:

        if not start_sound_played:
            start_sound.play()
            start_sound_played = True

        video_timer += dt

        draw_world()

        play_video_frame(
            start_clip,
            min(video_timer, start_clip.duration - 0.01),
            (250, 250)
        )

        title = big_font.render(
            "GET READY!",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            (
                WIDTH // 2 - title.get_width() // 2,
                120
            )
        )

        if video_timer >= start_clip.duration:

            video_timer = 0
            game_state = STATE_PLAYING

    # =====================================================
    # ИГРА
    # =====================================================
    elif game_state == STATE_PLAYING:

        elapsed_time += dt

        accelerating = False

        if keys[pygame.K_RIGHT]:
            speed += ACCELERATION * dt
            accelerating = True

        if keys[pygame.K_LEFT]:
            speed -= BRAKE_FORCE * dt

        if not accelerating:
            if speed > 0:
                speed -= FRICTION * dt

        speed = max(0, min(speed, MAX_SPEED))

        # движение
        horse_x += speed * dt

        distance_m += speed * dt / 100

        # прыжок
        if is_jumping:

            vertical_velocity += GRAVITY * dt
            horse_y += vertical_velocity * dt

            if horse_y >= 0:

                horse_y = 0
                vertical_velocity = 0
                is_jumping = False

                frame_index = 1

        # анимация
        if is_jumping:

            animation_speed = 0.22

            animation_timer += dt

            if animation_timer >= animation_speed:

                animation_timer = 0

                frame_index += 1

                if frame_index >= 10:
                    frame_index = 0

        else:

            if speed > 1:

                animation_speed = (
                    0.09
                    - (speed / MAX_SPEED) * 0.05
                )

                animation_timer += dt

                if animation_timer >= animation_speed:

                    animation_timer = 0

                    frame_index += 1

                    if frame_index >= 10:
                        frame_index = 0

            else:
                frame_index = 10

        # финиш
        if distance_m >= FINISH_DISTANCE:

            game_state = STATE_FINISHED_WAIT

            finish_timer = 0

            speed = 0

            if (
                best_time is None
                or elapsed_time < best_time
            ):
                best_time = elapsed_time

        draw_world()

    # =====================================================
    # ОЖИДАНИЕ ПЕРЕД ФИНАЛОМ
    # =====================================================
    elif game_state == STATE_FINISHED_WAIT:

        finish_timer += dt

        draw_world()

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))

        screen.blit(overlay, (0, 0))

        txt = big_font.render(
            "FINISH!",
            True,
            (255, 255, 255)
        )

        screen.blit(
            txt,
            (
                WIDTH // 2 - txt.get_width() // 2,
                HEIGHT // 2 - 50
            )
        )

        if finish_timer >= 3:

            game_state = STATE_FINISH_VIDEO
            video_timer = 0

    # =====================================================
    # ФИНАЛЬНОЕ ВИДЕО
    # =====================================================
    elif game_state == STATE_FINISH_VIDEO:

        if not finish_sound_played:
            finish_sound.play()
            finish_sound_played = True

        video_timer += dt

        draw_world()

        play_video_frame(
            finish_clip,
            min(video_timer, finish_clip.duration - 0.01),
            (400, 400)
        )

        if video_timer >= finish_clip.duration:

            game_state = STATE_RESTART_WAIT

    # =====================================================
    # ОЖИДАНИЕ RESTART
    # =====================================================
    elif game_state == STATE_RESTART_WAIT:

        draw_world()

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))

        screen.blit(overlay, (0, 0))

        txt1 = big_font.render(
            "PRESS SPACE",
            True,
            (255, 255, 255)
        )

        txt2 = font.render(
            "to restart race",
            True,
            (255, 255, 255)
        )

        screen.blit(
            txt1,
            (
                WIDTH // 2 - txt1.get_width() // 2,
                HEIGHT // 2 - 40
            )
        )

        screen.blit(
            txt2,
            (
                WIDTH // 2 - txt2.get_width() // 2,
                HEIGHT // 2 + 40
            )
        )

    pygame.display.flip()

pygame.quit()
sys.exit()
