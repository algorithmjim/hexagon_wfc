import cv2
import numpy as np
from copy import deepcopy
from enum import Enum

from constants import *
from camera import Camera
from canvas import Canvas
from utility import get_time_difference, write_text_to_image
from time_of_day import TimeOfDay
from map import MapGenerater, MapNavigator


class GameStateEnum(Enum):
    MAIN_MENU = 0
    GAME = 1
    QUIT = 2


class GameState:
    def __init__(self):
        self.my_canvas = Canvas()

    def update(self):
        pass


class GameStateMainMenu(GameState):
    def __init__(self):
        super().__init__()
    
    def update(self):
        pass


class GameStateMainGameMode(GameState):
    def __init__(self):
        super().__init__()
        self.last_event = None
        self.move_path = []
        self.frame_idx = 0
        self.time_manager = TimeOfDay()
        self.generate_map()
        

    def generate_map(self):
        self.my_canvas.clear_canvas()
        # say loading map on canvas
        self.my_map = MapGenerater()
        self.my_camera = Camera(int(self.my_map.tile_map_width / 2) - 1,
                                int(self.my_map.tile_map_height / 2) + 2)
        
        if self.my_camera.y % 2 == 0:
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
        # Parallax Right
        for y in range(self.my_map.tile_map_height):
            for x in range(self.my_map.tile_map_width):
                self.my_canvas.draw_to_canvas(self.my_map.tile_map[y][x].tile_img,
                                        self.my_map.tile_map[y][x].x + int(self.my_map.tile_map_width * TILE_WIDTH * 1.5),
                                        self.my_map.tile_map[y][x].y,
                                        self.my_map.tile_map[y][x].layer_lvl)

        # Parallax Bottom-Right
        for y in range(self.my_map.tile_map_height):
            for x in range(self.my_map.tile_map_width):
                self.my_canvas.draw_to_canvas(self.my_map.tile_map[y][x].tile_img,
                                        self.my_map.tile_map[y][x].x + int(self.my_map.tile_map_width * TILE_WIDTH * 1.5),
                                        self.my_map.tile_map[y][x].y + int(self.my_map.tile_map_height * TILE_WIDTH * 0.47),
                                        self.my_map.tile_map[y][x].layer_lvl)

        # Parallax Top-Right
        for y in range(self.my_map.tile_map_height):
            for x in range(self.my_map.tile_map_width):
                self.my_canvas.draw_to_canvas(self.my_map.tile_map[y][x].tile_img,
                                        self.my_map.tile_map[y][x].x + int(self.my_map.tile_map_width * TILE_WIDTH * 1.5),
                                        self.my_map.tile_map[y][x].y - int(self.my_map.tile_map_height * TILE_WIDTH * 0.47),
                                        self.my_map.tile_map[y][x].layer_lvl)

        # Parallax Left
        for y in range(self.my_map.tile_map_height):
            for x in range(self.my_map.tile_map_width):
                self.my_canvas.draw_to_canvas(self.my_map.tile_map[y][x].tile_img,
                                        self.my_map.tile_map[y][x].x - int(self.my_map.tile_map_width * TILE_WIDTH * 1.5),
                                        self.my_map.tile_map[y][x].y,
                                        self.my_map.tile_map[y][x].layer_lvl)

        # Parallax Bottom-Left
        for y in range(self.my_map.tile_map_height):
            for x in range(self.my_map.tile_map_width):
                self.my_canvas.draw_to_canvas(self.my_map.tile_map[y][x].tile_img,
                                        self.my_map.tile_map[y][x].x - int(self.my_map.tile_map_width * TILE_WIDTH * 1.5),
                                        self.my_map.tile_map[y][x].y + int(self.my_map.tile_map_height * TILE_WIDTH * 0.47),
                                        self.my_map.tile_map[y][x].layer_lvl)

        # Parallax Top-Left
        for y in range(self.my_map.tile_map_height):
            for x in range(self.my_map.tile_map_width):
                self.my_canvas.draw_to_canvas(self.my_map.tile_map[y][x].tile_img,
                                        self.my_map.tile_map[y][x].x - int(self.my_map.tile_map_width * TILE_WIDTH * 1.5),
                                        self.my_map.tile_map[y][x].y - int(self.my_map.tile_map_height * TILE_WIDTH * 0.47),
                                        self.my_map.tile_map[y][x].layer_lvl)

        # Parallax Down
        for y in range(self.my_map.tile_map_height):
            for x in range(self.my_map.tile_map_width):
                self.my_canvas.draw_to_canvas(self.my_map.tile_map[y][x].tile_img,
                                        self.my_map.tile_map[y][x].x,
                                        self.my_map.tile_map[y][x].y + int(self.my_map.tile_map_height * TILE_WIDTH * 0.47),
                                        self.my_map.tile_map[y][x].layer_lvl)

        # Parallax Down
        for y in range(self.my_map.tile_map_height):
            for x in range(self.my_map.tile_map_width):
                self.my_canvas.draw_to_canvas(self.my_map.tile_map[y][x].tile_img,
                                        self.my_map.tile_map[y][x].x,
                                        self.my_map.tile_map[y][x].y - int(self.my_map.tile_map_height * TILE_WIDTH * 0.47),
                                        self.my_map.tile_map[y][x].layer_lvl)
        
        # main map
        for y in range(self.my_map.tile_map_height):
            for x in range(self.my_map.tile_map_width):
                _display = False
                if self.my_camera.x == x and self.my_camera.y == y:
                    _display = True
                else:
                    for tf in neighbor_transform:
                        if self.my_camera.x + tf[0] == x and self.my_camera.y + tf[1] == y:
                            _display = True
                            break
                self.my_canvas.draw_to_canvas(self.my_map.tile_map[y][x].tile_img,
                                        self.my_map.tile_map[y][x].x,
                                        self.my_map.tile_map[y][x].y,
                                        self.my_map.tile_map[y][x].layer_lvl)
                if _display:
                    self.my_canvas.update_obj_visibility(self.my_map.tile_map[y][x].layer_lvl, 1)
                else:
                    self.my_canvas.update_obj_visibility(self.my_map.tile_map[y][x].layer_lvl, STARTING_ALPHA)

        self.my_camera.pixel_x, self.my_camera.pixel_y, _ = self.my_map.get_camera_pixel_pos(self.my_camera)


    def update(self):
        self.my_camera.pixel_x, self.my_camera.pixel_y, camera_tile = self.my_map.get_camera_pixel_pos(self.my_camera)
        #if frame_idx % 2 == 0:
        self.time_manager.update()
        events = self.my_canvas.render(self.my_camera, self.frame_idx, self.time_manager)
        key = cv2.waitKey(1)
        if key == 27: #ESC
            return GameStateEnum.QUIT
        elif key == 32 and not self.last_event is None: #SPACE
            self.my_canvas.clear_selected()
            self.my_camera, camera_tile_new = self.my_map.move_camera_to_selected(self.my_camera, self.last_event.object)
            self.move_path = MapNavigator(self.my_map.tile_map, self.my_map.tile_map_width, self.my_map.tile_map_height, self.my_camera, (self.my_camera.x, self.my_camera.y), (camera_tile_new.idx_x,camera_tile_new.idx_y)).get_path()
            self.my_camera.time_last_moved = deepcopy(self.time_manager)
            #print(self.my_camera.time_last_moved)
        elif key == 100: # D
            self.my_camera.x += 1
        elif key == 97: # A
            self.my_camera.x -= 1
        elif key == 119: # W
            self.my_camera.y -= 1
        elif key == 115: # S
            self.my_camera.y += 1
        elif key != -1:
            print(f"Unmapped Key: {key}")
        if len(events) > 0 and cv2.EVENT_LBUTTONDOWN == events[0].event_type:
            self.last_event = events[0]

        if not self.my_camera.time_last_moved is None and len(self.move_path) > 0:
            #print(self.my_camera.time_last_moved)
            #print(self.time_manager)
            _, month, day, hour, _ = get_time_difference(self.time_manager, self.my_camera.time_last_moved)
            #print(month, day, hour)
            go_to = self.move_path[0]
            #print(self.move_path)
            if go_to[0] == self.my_camera.x and go_to[1] == self.my_camera.y:
                self.move_path = self.move_path[1:]
            else:
                cost = self.my_map.tile_map[go_to[1]][go_to[0]].terrian_cost * HOURS_PER_MOVE_COST + self.my_map.tile_map[self.my_camera.y][self.my_camera.x].terrian_cost * HOURS_PER_MOVE_COST
                #print(month * 30 * 24 + day * 24 + hour)
                if (month * 30 * 24) + (day * 24) + hour > cost:
                    self.move_path = self.move_path[1:]
                    self.my_map.update_visibility(self.my_camera, self.my_map.tile_map[go_to[1]][go_to[0]].idx_x, self.my_map.tile_map[go_to[1]][go_to[0]].idx_y, self.my_canvas)
                    self.my_camera.x = self.my_map.tile_map[go_to[1]][go_to[0]].idx_x
                    self.my_camera.y = self.my_map.tile_map[go_to[1]][go_to[0]].idx_y
                    self.my_camera.time_last_moved = deepcopy(self.time_manager)

        # More Parallax Stuff
        if self.my_camera.x < 0:
            self.my_camera.x = self.my_map.tile_map_width - 1
        if self.my_camera.x >= self.my_map.tile_map_width:
            self.my_camera.x = 0
        if self.my_camera.y < 0:
            self.my_camera.y = self.my_map.tile_map_height - 1
        if self.my_camera.y >= self.my_map.tile_map_height:
            self.my_camera.y = 0
        self.frame_idx += 1

        return GameStateEnum.GAME