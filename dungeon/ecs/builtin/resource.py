import numpy as np

from dungeon.type import vec2


class Input:
    def __init__(self):
        self.key_just_pressed = -1

    def reset(self):
        self.key_just_pressed = -1

    def set_just_pressed(self, key: int):
        self.key_just_pressed = key

    def just_pressed(self, key: int) -> bool:
        return self.key_just_pressed == key


class Camera:
    def __init__(self, position: vec2, width: float, height: float):
        self.position = position
        self.ndc_matrix = np.array([[2 / width, 0.0], [0.0, 2 / height]])


class Time:
    pass
