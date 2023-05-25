import os
import cv2
import json
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from constants import *

def load_tileset():
    num_columns = 8
    num_rows = 6
    tiles = []
    base_img = cv2.imread(os.path.join("assets", "tileset", "fantasyhextiles_v3.png"))
    img_shape = np.array(base_img).shape
    tile_width = int(img_shape[1] / num_columns)
    tile_height = int(img_shape[0] / num_rows)

    row_index = 0
    column_index = 0
    for i in range((num_columns * (num_rows - 1))):
        tiles.append(base_img[row_index * tile_height:(row_index + 1) * tile_height, column_index * tile_width: (column_index + 1) * tile_width])
        if row_index == 0:
            tiles[-1] = tiles[-1][1:, :]

        if column_index >= (num_columns - 1):
            column_index = 0
            row_index += 1
        else:
            column_index += 1
    return tiles


def load_tileset_rules():
    with open(os.path.join("assets", "tileset", "ruleset.json"), "r") as jf:
        ruleset = json.load(jf)
    return ruleset


def add_random_tiles(my_canvas, tiles, num_tiles, num_layers):
    for i in range(num_tiles):
        new_layer = np.random.randint(0, num_layers)
        new_tile_idx = np.random.randint(0, len(tiles) - 1)
        new_x = np.random.randint(0, my_canvas.shape[1] - tiles[new_tile_idx].shape[1])
        new_y = np.random.randint(0, my_canvas.shape[0] - tiles[new_tile_idx].shape[0])
        my_canvas.draw_to_canvas(tiles[new_tile_idx], new_x, new_y, new_layer)
    return my_canvas


def add_random_tiles_one_each(my_canvas, tiles, num_layers):
    for new_tile_idx, tile in enumerate(tiles):
        new_layer = np.random.randint(0, num_layers)
        new_x = np.random.randint(0, my_canvas.shape[1] - tiles[new_tile_idx].shape[1])
        new_y = np.random.randint(0, my_canvas.shape[0] - tiles[new_tile_idx].shape[0])
        my_canvas.draw_to_canvas(tiles[new_tile_idx], new_x, new_y, new_layer)
    return my_canvas


def distance(x1, y1, x2, y2):
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def get_time_difference(t1, t2):
    return t1.year - t2.year, t1.month - t2.month, t1.day - t2.day, t1.hour - t2.hour, t1.minute - t2.minute


def load_character_assets():
    num_columns = 5
    num_rows = 1
    tiles = []
    base_img = cv2.imread(os.path.join("assets", "living_npcs", "sprite sheets", "medieval", "adventurer_01.png"))
    img_shape = np.array(base_img).shape
    tile_width = int(img_shape[1] / num_columns)
    tile_height = int(img_shape[0] / num_rows)

    row_index = 0
    column_index = 0
    for i in range(num_columns * num_rows):
        tiles.append(base_img[row_index * tile_height:(row_index + 1) * tile_height, column_index * tile_width: (column_index + 1) * tile_width])
        if column_index >= (num_columns - 1):
            column_index = 0
            row_index += 1
        else:
            column_index += 1
    return tiles


def get_neighbor_transform(y):
    if y % 2 == 0:
        neighbor_transform = [[0, -1],
                            [0, 1],
                            [0, -2],
                            [0, 2],
                            [1, 1],
                            [1, -1]]
    else:
        neighbor_transform = [[0, -1],
                            [0, 1],
                            [0, -2],
                            [0, 2],
                            [-1, 1],
                            [-1, -1]]
    return neighbor_transform


# Position is (x, y)
def write_text_to_image(image, text, position):
    font = ImageFont.truetype("assets/DungeonFont.ttf", FONT_SIZE)
    image_pil = Image.fromarray(image)
    draw = ImageDraw.Draw(image_pil)
    # split text into words, count the number of characters in each word, and add a newline to a word once text needs to be wrapped
    #new_text = wrap_text(text)
    draw.text(position, text, font = font, fill = (255, 255, 255))
    image = np.array(image_pil)
    return image