from constants import *
from utility import write_text_to_image
class TimeOfDay:
    def __init__(self):
        self.year = 0
        self.month = 7
        self.day = 23
        self.hour = 12
        self.minute = 0
    
    def update(self):
        self.minute += 10
        if self.minute >= 60:
            self.hour += 1
            self.minute = 0
        if self.hour >= 24:
            self.hour = 0
            self.day += 1
        if self.day >= 31:
            self.month += 1
            self.day = 1
        if self.month >= 13:
            self.month = 1
            self.year += 1

    def get_alpha_from_tod(self):
        if self.hour > 12:
            time_val = self.hour + self.minute / 60
            time_val = (12 - (time_val - 12)) / 12
        else:
            time_val = self.hour + self.minute / 60
            time_val = time_val / 12
        
        time_val += 0.3

        if time_val < MIN_ALPHA:
            time_val = MIN_ALPHA
        if time_val > MAX_ALPHA:
            time_val = MAX_ALPHA
        return time_val

    def __repr__(self) -> str:
        return f"{self.month}/{self.day}/{self.year} {self.hour}:{self.minute}"

    def render(self, image):
        image = write_text_to_image(image, str(self), (10, 10))
        return image
