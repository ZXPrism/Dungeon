import pygame

from dataclasses import dataclass
from dungeon.type import vec2


@dataclass
class Transform:
    position: vec2
    scale: vec2


@dataclass
class Texture:
    data: pygame.Surface
