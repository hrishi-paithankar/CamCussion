from led_point.point import Point
from enum import Enum

class Direction(Enum):
    UP = 'up'
    DOWN = 'down'
    RIGHT = 'right'
    LEFT = 'left'

class Trajectory():
    def __init__(self, window_size: Point, speed, padding=0):
        self.window_size = window_size
        self.speed = speed
        self.current_direction = Direction.RIGHT
        self.padding = padding
        self.current_position = Point(padding, padding)

    def get_current_position(self):
        return self.current_position

    def move_point(self):
        if self.current_direction == Direction.RIGHT:
            self.current_position.x += self.speed
            if self.current_position.x >= (self.window_size.x - self.padding):
                self.current_direction = Direction.DOWN
                self.current_position.x = (self.window_size.x - self.padding)
        elif self.current_direction == Direction.DOWN:
            self.current_position.y += self.speed
            if self.current_position.y >= (self.window_size.y - self.padding):
                self.current_direction = Direction.LEFT
                self.current_position.y = (self.window_size.y - self.padding)
        elif self.current_direction == Direction.LEFT:
            self.current_position.x -= self.speed
            if self.current_position.x <= self.padding:
                self.current_direction = Direction.UP
                self.current_position.x = self.padding
        elif self.current_direction == Direction.UP:
            self.current_position.y -= self.speed
            if self.current_position.y <= self.padding:
                self.current_direction = Direction.RIGHT
                self.current_position.y = self.padding