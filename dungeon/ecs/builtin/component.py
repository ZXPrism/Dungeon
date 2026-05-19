import copy

from enum import IntEnum
from dataclasses import dataclass
from dungeon.type import vec2, vec4

# =======
#  basic
# =======


@dataclass
class Transform:
    position: vec2
    scale: vec2

    def __post_init__(self):
        self.position = copy.copy(self.position)
        self.scale = copy.copy(self.scale)


@dataclass
class Entity:
    id: int


# ===========
#  rendering
# ===========


@dataclass
class Texture:
    color: vec4  # HACK

    def __post_init__(self):
        self.color = copy.copy(self.color)


@dataclass
class Layer:
    id: int  # small -- foreground, large -- background


# ===========
#  animation
# ===========


class AnimationEasing(IntEnum):
    LINEAR = 0


@dataclass
class TweenPosition:
    duration: float
    elapsed: float
    start: vec2
    end: vec2
    easing: AnimationEasing

    def __post_init__(self):
        self.start = copy.copy(self.start)
        self.end = copy.copy(self.end)
        self.easing = copy.copy(self.easing)
