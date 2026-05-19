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
        self.view = np.array([])
        self.projection = np.array([])
        self.position = position
        self.resolution = (width, height)

    def update(self):
        self.view = np.eye(4, dtype="f4")
        self.view[:2, 3] = -self.position
        self.view = self.view.T

        self.projection = np.eye(4, dtype="f4")
        self.projection[0, 0] = 2.0 / self.resolution[0]
        self.projection[1, 1] = 2.0 / self.resolution[1]
        self.projection = self.projection.T


class DeltaTime:
    def __init__(self):
        self._last_timepoint = None
        self.value = 0.0
