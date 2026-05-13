#!/usr/bin/python3

import pygame
import sys

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

# Прыжок
GRAVITY = 1700
JUMP_FORCE = -600

MIN_JUMP_SPEED = MAX_SPEED * 0.25

# Финиш
FINISH_DISTANCE = 500  # метры

# =========================================================
# ИНИЦИАЛИЗАЦИЯ
# =========================================================
pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Horse Race")

clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 28)
big_font = pygame.font.SysFont("arial", 60, bold=True)

# =========================================================
# ЗАГРУЗКА PNG СПРАЙТОВ
# =========================================================
sheet = pygame.image.load("horses.png").convert_alpha()

sheet_w, sheet_h = sheet.get_size()

COLS = 4
ROWS = 3

frame_w = sheet_w // COLS
frame_h = sheet_h // ROWS

frames = []

# ---------------------------------------------------------
# ПОРЯДОК:
# справа налево
# сверху вниз
# ---------------------------------------------------------
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
# Подгонка ног к поверхности
# 11 фаза — стоячая
ground_offsets = [
    20, 16, 10, 8,
    8, 12, 18, 22,
    16, 8, 10, 12
]

ground_offsets = [
    int(v * HORSE_SCALE)
    for v in ground_offsets
]

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

frame_index = 10  # стоячая поза
animation_timer = 0

finished = False

# =========================================================
# ФУНКЦИИ
# =========================================================
def get_ground_y(frame_id, stop=False):
    frame = frames[frame_id]

    return (
        GROUND_Y
        - frame.get_height()
        + ground_offsets[frame_id] + (30 if stop else 5)
    )

# =========================================================
# ГЛАВНЫЙ ЦИКЛ
# =========================================================
running = True

while running:

    dt = clock.tick(FPS) / 1000.0

    if not finished:
        elapsed_time += dt

    # =====================================================
    # СОБЫТИЯ
    # =====================================================
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Прыжок
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:

                if (
                    not is_jumping
                    and speed >= MIN_JUMP_SPEED
                ):
                    is_jumping = True
                    vertical_velocity = JUMP_FORCE

    keys = pygame.key.get_pressed()

    # =====================================================
    # ФИЗИКА
    # =====================================================
    if not finished:

        accelerating = False

        # Ускорение
        if keys[pygame.K_RIGHT]:
            speed += ACCELERATION * dt
            accelerating = True

        # Тормоз
        if keys[pygame.K_LEFT]:
            speed -= BRAKE_FORCE * dt

        # Трение
        if not accelerating:
            if speed > 0:
                speed -= FRICTION * dt

        # Ограничения
        speed = max(0, min(speed, MAX_SPEED))

        # =================================================
        # ДВИЖЕНИЕ
        # =================================================
        horse_x += speed * dt

        # пиксели -> метры
        distance_m += speed * dt / 100

        # =================================================
        # ПРЫЖОК
        # =================================================
        if is_jumping:

            vertical_velocity += GRAVITY * dt
            horse_y += vertical_velocity * dt

            # Приземление
            if horse_y >= 0:
                horse_y = 0
                vertical_velocity = 0
                is_jumping = False

                # Приземление во 2 фазу
                frame_index = 1

        # =================================================
        # АНИМАЦИЯ
        # =================================================
        stop = False
        if is_jumping:

            # В воздухе анимация сильно замедлена
            animation_speed = 0.22

            animation_timer += dt

            if animation_timer >= animation_speed:
                animation_timer = 0

                frame_index += 1

                # цикл только беговых фаз
                if frame_index > 11:
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

                    if frame_index > 11:
                        frame_index = 0

            else:
                # Стоячая поза
                frame_index = 10
                stop = True

        # =================================================
        # ФИНИШ
        # =================================================
        if distance_m >= FINISH_DISTANCE:
            finished = True
            speed = 0

    # =====================================================
    # КАМЕРА
    # =====================================================
    camera_x = horse_x - 240

    # =====================================================
    # РЕНДЕР
    # =====================================================
    screen.fill((170, 220, 255))

    # -----------------------------------------------------
    # Земля
    # -----------------------------------------------------
    pygame.draw.rect(
        screen,
        (60, 160, 60),
        (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y)
    )

    # -----------------------------------------------------
    # Полосы движения
    # -----------------------------------------------------
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
    # ФИНИШНЫЙ ФЛАГ
    # =====================================================
    finish_world_x = FINISH_DISTANCE * 100

    finish_screen_x = finish_world_x - camera_x

    if -100 < finish_screen_x < WIDTH + 100:

        pole_top = GROUND_Y - 260

        # Столб
        pygame.draw.rect(
            screen,
            (80, 80, 80),
            (finish_screen_x, pole_top, 10, 260)
        )

        # Клетчатый флаг
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
        get_ground_y(frame_index, stop)
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

    # =====================================================
    # ФИНИШ
    # =====================================================
    if finished:

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        text = big_font.render(
            "FINISH!",
            True,
            (255, 255, 255)
        )

        text2 = font.render(
            f"Final time: {elapsed_time:.1f} s",
            True,
            (255, 255, 255)
        )

        screen.blit(
            text,
            (
                WIDTH // 2 - text.get_width() // 2,
                HEIGHT // 2 - 80
            )
        )

        screen.blit(
            text2,
            (
                WIDTH // 2 - text2.get_width() // 2,
                HEIGHT // 2 + 10
            )
        )

    pygame.display.flip()

pygame.quit()
sys.exit()
