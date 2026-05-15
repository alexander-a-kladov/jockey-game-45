#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Просмотрщик фрагментов изображения с ручным выравниванием.

Возможности:
- Загружает изображение
- Делит на N равных прямоугольников (по умолчанию 12)
- Порядок обхода:
    справа налево, сверху вниз
- Зацикленное переключение фрагментов
- Предыдущий фрагмент отображается бледно
- Отображение рамки границ изображения
- Переключение цвета фона:
    ↑ ↓

Управление:
    ← →      переключение фрагментов
    W A S D  смещение текущего фрагмента
    ↑ ↓      смена фона
    SPACE    печать массива смещений
    ESC      выход

Зависимости:
    pip install pillow pygame
"""

import math
import argparse

import pygame
from PIL import Image

# ---------------------------------------------------
# Аргументы
# ---------------------------------------------------

parser = argparse.ArgumentParser()

parser.add_argument("image", help="Путь к изображению")

parser.add_argument(
    "-n",
    "--parts",
    type=int,
    default=12,
    help="Количество частей (по умолчанию 12)",
)

args = parser.parse_args()

IMAGE_PATH = args.image
N = args.parts

# ---------------------------------------------------
# Загрузка изображения
# ---------------------------------------------------

img = Image.open(IMAGE_PATH).convert("RGBA")

img_w, img_h = img.size

# ---------------------------------------------------
# Разбиение на сетку
# ---------------------------------------------------

cols = math.ceil(math.sqrt(N))
rows = math.ceil(N / cols)

tile_w = img_w // cols
tile_h = img_h // rows

tiles = []

# порядок:
# справа налево, сверху вниз

for row in range(rows):

    row_tiles = []

    for col in range(cols):

        x0 = col * tile_w
        y0 = row * tile_h

        x1 = (col + 1) * tile_w if col < cols - 1 else img_w
        y1 = (row + 1) * tile_h if row < rows - 1 else img_h

        crop = img.crop((x0, y0, x1, y1))

        row_tiles.append(crop)

    row_tiles.reverse()

    tiles.extend(row_tiles)

tiles = tiles[:N]

# ---------------------------------------------------
# pygame
# ---------------------------------------------------

pygame.init()

SCREEN_W = max(t.width for t in tiles) + 400
SCREEN_H = max(t.height for t in tiles) + 400

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))

pygame.display.set_caption("Tile Align Viewer")

clock = pygame.time.Clock()

# ---------------------------------------------------
# PIL -> pygame
# ---------------------------------------------------

def pil_to_surface(pil_img):

    mode = pil_img.mode
    size = pil_img.size
    data = pil_img.tobytes()

    return pygame.image.fromstring(data, size, mode).convert_alpha()


surfaces = [pil_to_surface(t) for t in tiles]

# ---------------------------------------------------
# Смещения
# ---------------------------------------------------

offsets = [[0, 0] for _ in range(len(surfaces))]

current = 0

MOVE_STEP = 1

# ---------------------------------------------------
# Фоны
# ---------------------------------------------------

backgrounds = [
    (30, 30, 30),       # темный
    (180, 210, 255),    # светло-синий
    (255, 255, 255),    # белый
]

bg_index = 0

# ---------------------------------------------------
# Бледная версия
# ---------------------------------------------------

def make_faded(surface, alpha=90):

    s = surface.copy()
    s.set_alpha(alpha)

    return s

# ---------------------------------------------------
# Рисование
# ---------------------------------------------------

def draw():

    bg = backgrounds[bg_index]

    screen.fill(bg)

    center_x = SCREEN_W // 2
    center_y = SCREEN_H // 2

    # ------------------------------------------------
    # Рамка границ изображения
    # ------------------------------------------------

    frame_x = center_x - tile_w // 2
    frame_y = center_y - tile_h // 2

    pygame.draw.rect(
        screen,
        (255, 0, 0),
        (frame_x, frame_y, tile_w, tile_h),
        2,
    )

    # ------------------------------------------------
    # Предыдущий тайл
    # ------------------------------------------------

    prev_index = (current - 1) % len(surfaces)

    prev = surfaces[prev_index]

    px = center_x - prev.get_width() // 2
    py = center_y - prev.get_height() // 2

    faded = make_faded(prev)

    screen.blit(faded, (px, py))

    # ------------------------------------------------
    # Текущий тайл
    # ------------------------------------------------

    cur = surfaces[current]

    ox, oy = offsets[current]

    cx = center_x - cur.get_width() // 2 + ox
    cy = center_y - cur.get_height() // 2 + oy

    screen.blit(cur, (cx, cy))

    # ------------------------------------------------
    # Информация
    # ------------------------------------------------

    font = pygame.font.SysFont(None, 28)

    txt = font.render(
        f"{current+1}/{len(surfaces)}  offset=({ox},{oy})  bg={bg_index}",
        True,
        (255, 255, 255) if bg_index != 2 else (0, 0, 0),
    )

    screen.blit(txt, (20, 20))

    pygame.display.flip()

# ---------------------------------------------------
# Главный цикл
# ---------------------------------------------------

running = True

while running:

    clock.tick(60)

    draw()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            # ----------------------------------------
            # Следующий
            # ----------------------------------------

            if event.key == pygame.K_RIGHT:

                current = (current + 1) % len(surfaces)

            # ----------------------------------------
            # Предыдущий
            # ----------------------------------------

            elif event.key == pygame.K_LEFT:

                current = (current - 1) % len(surfaces)

            # ----------------------------------------
            # Смещения
            # ----------------------------------------

            elif event.key == pygame.K_w:

                offsets[current][1] -= MOVE_STEP

            elif event.key == pygame.K_s:

                offsets[current][1] += MOVE_STEP

            elif event.key == pygame.K_a:

                offsets[current][0] -= MOVE_STEP

            elif event.key == pygame.K_d:

                offsets[current][0] += MOVE_STEP

            # ----------------------------------------
            # Фон
            # ----------------------------------------

            elif event.key == pygame.K_UP:

                bg_index = (bg_index + 1) % len(backgrounds)

            elif event.key == pygame.K_DOWN:

                bg_index = (bg_index - 1) % len(backgrounds)

            # ----------------------------------------
            # Печать массива
            # ----------------------------------------

            elif event.key == pygame.K_SPACE:

                flat = []

                for x, y in offsets:

                    flat.append(x)
                    flat.append(y)

                print(flat)

            # ----------------------------------------
            # Выход
            # ----------------------------------------

            elif event.key == pygame.K_ESCAPE:

                running = False

pygame.quit()