#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Просмотрщик фрагментов изображения с ручным выравниванием.

Особенности:
- Деление изображения на N частей
- Порядок:
    справа налево, сверху вниз
- Зацикленное переключение
- Предыдущий фрагмент отображается бледно
- Смещение применяется КО ВСЕМ ПОСЛЕДУЮЩИМ изображениям
- Рамка области изображения
- Переключение фона

Управление:
    ← →      переключение
    W A S D  смещение текущего и всех следующих
    ↑ ↓      смена фона
    SPACE    печать массива смещений
    ESC      выход
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
    help="Количество частей",
)

args = parser.parse_args()

IMAGE_PATH = args.image
N = args.parts

# ---------------------------------------------------
# Загрузка
# ---------------------------------------------------

img = Image.open(IMAGE_PATH).convert("RGBA")

img_w, img_h = img.size

# ---------------------------------------------------
# Сетка
# ---------------------------------------------------

cols = math.ceil(math.sqrt(N))
rows = math.ceil(N / cols)

tile_w = img_w // cols
tile_h = img_h // rows

tiles = []

for row in range(rows):

    row_tiles = []

    for col in range(cols):

        x0 = col * tile_w
        y0 = row * tile_h

        x1 = (col + 1) * tile_w if col < cols - 1 else img_w
        y1 = (row + 1) * tile_h if row < rows - 1 else img_h

        crop = img.crop((x0, y0, x1, y1))

        row_tiles.append(crop)

    # справа налево
    row_tiles.reverse()

    tiles.extend(row_tiles)

tiles = tiles[:N]

# ---------------------------------------------------
# pygame
# ---------------------------------------------------

pygame.init()

pygame.key.set_repeat(200, 25)

SCREEN_W = max(t.width for t in tiles) + 400
SCREEN_H = max(t.height for t in tiles) + 400

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))

pygame.display.set_caption("Tile Align Viewer")

clock = pygame.time.Clock()

# ---------------------------------------------------
# PIL -> pygame
# ---------------------------------------------------

def pil_to_surface(pil_img):

    return pygame.image.fromstring(
        pil_img.tobytes(),
        pil_img.size,
        pil_img.mode,
    ).convert_alpha()


surfaces = [pil_to_surface(t) for t in tiles]

# ---------------------------------------------------
# Смещения
# ---------------------------------------------------
# offsets[i] =
# итоговое накопленное смещение
# для i-го изображения
# ---------------------------------------------------

offsets = [[0, 0] for _ in range(len(surfaces))]

current = 0

MOVE_STEP = 1

# ---------------------------------------------------
# Фоны
# ---------------------------------------------------

backgrounds = [
    (30, 30, 30),
    (180, 210, 255),
    (255, 255, 255),
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
# Добавление смещения
# ---------------------------------------------------
# Смещение действует
# на текущий и все следующие
# ---------------------------------------------------

def add_offset(dx, dy):

    for i in range(current, len(offsets)):

        offsets[i][0] += dx
        offsets[i][1] += dy

# ---------------------------------------------------
# Рисование
# ---------------------------------------------------

def draw():

    bg = backgrounds[bg_index]

    screen.fill(bg)

    center_x = SCREEN_W // 2
    center_y = SCREEN_H // 2

    # ------------------------------------------------
    # Рамка
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
    # Предыдущий
    # ------------------------------------------------

    prev_index = (current - 1) % len(surfaces)

    prev = surfaces[prev_index]

    # используем смещение предыдущего изображения
    pox, poy = offsets[prev_index]

    px = center_x - prev.get_width() // 2 + pox
    py = center_y - prev.get_height() // 2 + poy

    faded = make_faded(prev)

    screen.blit(faded, (px, py))

    # ------------------------------------------------
    # Текущий
    # ------------------------------------------------

    cur = surfaces[current]

    ox, oy = offsets[current]

    cx = center_x - cur.get_width() // 2 + ox
    cy = center_y - cur.get_height() // 2 + oy

    screen.blit(cur, (cx, cy))

    # ------------------------------------------------
    # Текст
    # ------------------------------------------------

    font = pygame.font.SysFont(None, 28)

    color = (0, 0, 0) if bg_index == 2 else (255, 255, 255)

    txt = font.render(
        f"{current+1}/{len(surfaces)}  "
        f"offset=({ox},{oy})  "
        f"bg={bg_index}",
        True,
        color,
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
            # Переключение
            # ----------------------------------------

            if event.key == pygame.K_RIGHT:

                current = (current + 1) % len(surfaces)

            elif event.key == pygame.K_LEFT:

                current = (current - 1) % len(surfaces)

            # ----------------------------------------
            # Смещения
            # ----------------------------------------

            elif event.key == pygame.K_w:

                add_offset(0, -MOVE_STEP)

            elif event.key == pygame.K_s:

                add_offset(0, MOVE_STEP)

            elif event.key == pygame.K_a:

                add_offset(-MOVE_STEP, 0)

            elif event.key == pygame.K_d:

                add_offset(MOVE_STEP, 0)

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