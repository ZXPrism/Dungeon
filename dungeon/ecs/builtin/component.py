import pygame

from dataclasses import dataclass
from dungeon.type import vec2, vec4


@dataclass
class Transform:
    position: vec2
    scale: vec2


@dataclass
class Texture:
    color: vec4  # HACK


@dataclass
class Layer:
    id: int  # small -- foreground, large -- background
