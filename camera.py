import numpy as np
from utility import load_character_assets
from constants import *


class Camera:
    def __init__(self, middle_x, middle_y):
        self.x = middle_x
        self.y = middle_y
        self.pixel_x = None
        self.pixel_y = None
        self.time_last_moved = None
        self.char_tiles = load_character_assets()
        self.animation_idx = 0
        self.animation_interval = 10
        self.animation_counter = 0

    def update(self):
        if self.animation_counter == self.animation_interval:
            self.animation_idx += 1
            self.animation_counter = 0
        if self.animation_idx >= len(self.char_tiles):
            self.animation_idx = 0
        self.animation_counter += 1

    def render(self, img, obj):
        self.update()

        obj_y = obj.y + int(TILE_HEIGHT / 2)
        obj_x = obj.x + int(TILE_WIDTH / 2)
        obj_x -= self.pixel_x - int(RESOLUTION[1] / 2) + TILE_WIDTH
        obj_y -= self.pixel_y - int(RESOLUTION[0] / 2) + TILE_WIDTH

        #print(obj_x, obj_y)
        #print(len(self.char_tiles))
        broadcast_area = img[obj_y:obj_y+self.char_tiles[self.animation_idx].shape[0], obj_x:obj_x+self.char_tiles[self.animation_idx].shape[1]]
        img[obj_y:obj_y+self.char_tiles[self.animation_idx].shape[0], obj_x:obj_x+self.char_tiles[self.animation_idx].shape[1]] = np.where(self.char_tiles[self.animation_idx][:broadcast_area.shape[0], :broadcast_area.shape[1]] != 0, self.char_tiles[self.animation_idx][:broadcast_area.shape[0], :broadcast_area.shape[1]], img[obj_y:obj_y+self.char_tiles[self.animation_idx].shape[0], obj_x:obj_x+self.char_tiles[self.animation_idx].shape[1]])
        return img