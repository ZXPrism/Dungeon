import random
import pygame
import numpy as np

from enum import IntEnum
from dataclasses import dataclass
from dungeon.ecs import *
from dungeon.ecs.builtin.component import Transform, Texture


@dataclass
class DungeonConfig:
    dungeon_width: int
    dungeon_height: int
    num_room_tries: int
    room_extra_size: int


class TileType(IntEnum):
    EMPTY = 0
    WALL = 1
    FLOOR = 2


# mainly a port of https://github.com/munificent/hauberk/blob/db360d9efa714efb6d937c31953ef849c7394a39/lib/src/content/dungeon.dart
def dungeon_gen(app: App, query: Res[DungeonConfig]):
    config = query.data

    if config.dungeon_width < 5 or config.dungeon_height < 5:
        raise RuntimeError("The dungeon is too small!")

    if config.dungeon_width % 2 == 0 or config.dungeon_height % 2 == 0:
        raise RuntimeError("The dungeon must be odd-sized!")

    regions = [[-1] * config.dungeon_width for _ in range(config.dungeon_height)]
    dungeon = [
        [TileType.EMPTY] * config.dungeon_width for _ in range(config.dungeon_height)
    ]
    rooms = []
    current_region = -1  # the index of current region being carved

    # 1. Generate rooms
    for i in range(config.num_room_tries):
        size = random.randint(1, 2 + config.room_extra_size) * 2 + 1
        rectangularity = random.randint(0, size // 2) * 2
        width = size
        height = size
        if random.random() < 0.5:
            width += rectangularity
        else:
            height += rectangularity

        x = random.randint(0, (config.dungeon_width - width) // 2 - 1) * 2 + 1
        y = random.randint(0, (config.dungeon_height - height) // 2 - 1) * 2 + 1

        room = pygame.Rect(x, y, width, height)

        overlap = False
        for other_room in rooms:
            other_room: pygame.Rect
            other_room_inflated = other_room.inflate(2, 2)
            if room.colliderect(other_room_inflated):
                overlap = True
                break

        if overlap:
            continue

        rooms.append(room)

        current_region += 1
        for y in range(room.top, room.bottom):
            for x in range(room.left, room.right):
                dungeon[y][x] = TileType.FLOOR
                regions[y][x] = current_region

    # 2. Generate mazes

    # 3. Connect

    # 4. Remove dead ends

    # Generate debug color for each region
    floor_colors = []
    for _ in range(current_region + 1):
        floor_color = np.ones((4,)) * 255.0
        floor_color[:3] = np.random.randint(0, 255, (3,)) / 255
        floor_colors.append(floor_color)
    empty_color = np.array((50, 50, 50, 255)) / 255

    for y in range(config.dungeon_height):
        for x in range(config.dungeon_width):
            if dungeon[y][x] == TileType.FLOOR:
                app.spawn(
                    Transform(np.array([x, y]), np.array([1.0, 1.0])),
                    Texture(floor_colors[regions[y][x]]),
                )
            elif dungeon[y][x] == TileType.EMPTY:
                app.spawn(
                    Transform(np.array([x, y]), np.array([1.0, 1.0])),
                    Texture(empty_color),
                )


class DungeonGen(Plugin):
    def build(self, app: App):
        app.add_system(Schedule.StartUp, dungeon_gen)
        app.insert_resource(
            DungeonConfig(
                dungeon_width=101,
                dungeon_height=101,
                num_room_tries=100,
                room_extra_size=0,
            )
        )
