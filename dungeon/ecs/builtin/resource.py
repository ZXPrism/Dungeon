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
    pass


class Time:
    pass
