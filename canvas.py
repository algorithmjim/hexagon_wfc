import cv2
import numpy as np
from constants import *
from utility import distance
from events import Event


class CanvasObject:
    def __init__(self, img, x, y, layer_lvl, render):
        self.img = img
        self.x = x
        self.y = y
        self.layer_lvl = layer_lvl
        self.render = render
        self.selected = False
        self.at_camera = False
        self.no_display = False
        self.alpha = STARTING_ALPHA


class Canvas:
    def __init__(self):
        self.canvas = np.zeros([RESOLUTION[0], RESOLUTION[1], 3], dtype=np.uint8)
        self.shape = [RESOLUTION[0], RESOLUTION[1], 3]
        self.objects = []
        
        if not DISABLE_RENDER:
            if FULLSCREEN:
                cv2.namedWindow('Test', cv2.WINDOW_NORMAL)
                cv2.setWindowProperty('Test', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                cv2.namedWindow('Test', cv2.WINDOW_GUI_NORMAL)

            cv2.setMouseCallback('Test', self.click_callback)
        self.last_clicked_x = None
        self.last_clicked_y = None
        self.events = []

    def click_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            pass
            #cv2.setMouseCallback('Test', None)  # Disable mouse callback
        elif event == cv2.EVENT_LBUTTONDOWN:
            self.last_clicked_x = int(x / DISPLAY_RESOLUTION[1] * RESOLUTION[1]) - TILE_WIDTH / 2
            self.last_clicked_y = int(y / DISPLAY_RESOLUTION[0] * RESOLUTION[0]) - TILE_WIDTH / 2
            min_d = None
            min_idx = None
            for i, obj in enumerate(self.objects):
                obj_y = obj.y + TILE_HEIGHT / 2
                obj_x = obj.x + TILE_WIDTH / 2
                obj_x -= self.camera.pixel_x - int(RESOLUTION[1] / 2) + TILE_WIDTH
                obj_y -= self.camera.pixel_y - int(RESOLUTION[0] / 2) + TILE_WIDTH
                self.objects[i].selected = False
                if obj_x < 0 or obj_x > RESOLUTION[1] - TILE_WIDTH / 2:
                    continue
                if obj_y < 0 or obj_y > RESOLUTION[0] - TILE_HEIGHT / 2:
                    continue
                
                if not self.last_clicked_x is None and not self.last_clicked_y is None:
                    d = distance(obj_x, obj_y, self.last_clicked_x, self.last_clicked_y)
                    if min_d is None or d < min_d:
                        min_d = d
                        min_idx = i

            self.objects[min_idx].selected = True
            self.events = [Event(self.objects[min_idx], cv2.EVENT_LBUTTONDOWN)]
        # elif event == cv2.EVENT_LBUTTONDBLCLK:
        #     none_selected = True
        #     for i, obj in enumerate(self.objects):
        #         if obj.selected:
        #             self.events = [Event(obj, cv2.EVENT_RBUTTONDOWN)]
        #             none_selected = False
        #             break
        #     if none_selected:
        #         self.events = []

    def select_obj(self, obj_x, obj_y):
        for obj in self.objects:
            if obj.x == obj_x and obj.y == obj_y:
                obj.no_display = True


    def update_obj_visibility(self, layer_lvl, alpha):
        for obj in self.objects:
            if obj.layer_lvl == layer_lvl:
                obj.alpha = alpha


    def clear_selected(self):
        for obj in self.objects:
            obj.selected = False
            obj.render = True


    def render(self, camera, frame_idx, time_of_day):
        img = self.canvas.copy()
        self.camera = camera
        for obj in self.objects:
            if camera.pixel_x == obj.x and camera.pixel_y == obj.y:
                obj.at_camera = True
            else:
                obj.at_camera = False
                if not obj.selected:
                    obj.render = True

            if (obj.selected) and frame_idx % 15 == 0:
                obj.render = not obj.render
            
            if not obj.render or obj.no_display:
                continue

            obj_y = obj.y + int(TILE_HEIGHT / 2)
            obj_x = obj.x + int(TILE_WIDTH / 2)
            obj_x -= camera.pixel_x - int(RESOLUTION[1] / 2) + TILE_WIDTH
            obj_y -= camera.pixel_y - int(RESOLUTION[0] / 2) + TILE_WIDTH

            if obj_x < 0 or obj_x > RESOLUTION[1] - TILE_WIDTH:
                continue
            if obj_y < 0 or obj_y > RESOLUTION[0] - TILE_HEIGHT:
                continue
            
            broadcast_area = img[obj_y:obj_y+obj.img.shape[0], obj_x:obj_x+obj.img.shape[1]]
            if obj.selected and obj.render:
                new_img = cv2.addWeighted(obj.img[:broadcast_area.shape[0], :broadcast_area.shape[1]], 1, np.zeros_like(obj.img[:broadcast_area.shape[0], :broadcast_area.shape[1]]), 0, 0.0)
            else:
                new_img = cv2.addWeighted(obj.img[:broadcast_area.shape[0], :broadcast_area.shape[1]], obj.alpha, np.zeros_like(obj.img[:broadcast_area.shape[0], :broadcast_area.shape[1]]), 1-obj.alpha, 0.0)
            img[obj_y:obj_y+obj.img.shape[0], obj_x:obj_x+obj.img.shape[1]] = np.where(new_img != 0, new_img, img[obj_y:obj_y+obj.img.shape[0], obj_x:obj_x+obj.img.shape[1]])
            if obj.at_camera:
                img = camera.render(img, obj)
        
        img = time_of_day.render(img)
        #alpha = time_of_day.get_alpha_from_tod()
        #img = cv2.addWeighted(img, alpha, np.zeros_like(img), 1-alpha, 0.0)
        
        if not DISABLE_RENDER:
            upscaled = cv2.resize(img, (DISPLAY_RESOLUTION[1], DISPLAY_RESOLUTION[0]), interpolation = cv2.INTER_NEAREST)
            cv2.imshow('Test', upscaled)
        
        return self.events

    def draw_to_canvas(self, img, x, y, layer_lvl, render=True):
        self.objects.append(CanvasObject(img, x, y, layer_lvl, render))
        #self.objects.sort(key=lambda x: x.y, reverse=False)

    def clear_canvas(self):
        self.objects = []

    def clear_events(self):
        self.events = []