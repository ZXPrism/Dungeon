import random
import pygame
import numpy as np

from enum import IntEnum
from dataclasses import dataclass
from dungeon.ecs import *
from dungeon.ecs.builtin.component import Transform, Texture, Layer


@dataclass
class DungeonConfig:
    dungeon_width: int
    dungeon_height: int
    num_room_tries: int
    room_extra_size: int
    winding_percent: int
    extra_connector_chance: float


class TileType(IntEnum):
    EMPTY = 0
    WALL = 1
    ROOM = 2
    DOOR = 3
    FLOOR = 4


# TODO
# optimize meshes using greedy meshing etc.


# mainly a port of https://github.com/munificent/hauberk/blob/db360d9efa714efb6d937c31953ef849c7394a39/lib/src/content/dungeon.dart
def dungeon_gen(app: App, query: Res[DungeonConfig]):
    config = query.data

    if config.dungeon_width < 5 or config.dungeon_height < 5:
        raise RuntimeError("The dungeon is too small!")

    if config.dungeon_width % 2 == 0 or config.dungeon_height % 2 == 0:
        raise RuntimeError("The dungeon must be odd-sized!")

    region_idx = [[-1] * config.dungeon_width for _ in range(config.dungeon_height)]
    dungeon = [
        [TileType.WALL] * config.dungeon_width for _ in range(config.dungeon_height)
    ]
    rooms = []
    current_region = -1  # the index of current region being carved

    def carve(x: int, y: int, t: TileType):
        dungeon[y][x] = t
        region_idx[y][x] = current_region

    # 1. Generate rooms
    for _ in range(config.num_room_tries):
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
                carve(x, y, TileType.ROOM)

    # 2. Generate mazes
    def is_cell_valid(cell) -> bool:
        return (
            0 <= cell[0] < config.dungeon_width and 0 <= cell[1] < config.dungeon_height
        )

    cells = []
    last_dir_idx = None
    dirs = np.array([(-1, 0), (1, 0), (0, -1), (0, 1)])

    for y in range(1, config.dungeon_height, 2):
        for x in range(1, config.dungeon_width, 2):
            if dungeon[y][x] != TileType.WALL:
                continue
            current_region += 1
            carve(x, y, TileType.FLOOR)
            cells.append(np.array([x, y]))

            while len(cells) != 0:
                cell = cells[-1]

                unmade_cell_dirs = []

                for dir_idx, dir in enumerate(dirs):
                    cell_1 = cell + (dir * 3)
                    cell_2 = cell + (dir * 2)
                    if (
                        is_cell_valid(cell_1)
                        and dungeon[cell_2[1]][cell_2[0]] == TileType.WALL
                    ):
                        unmade_cell_dirs.append(dir_idx)

                if len(unmade_cell_dirs) != 0:
                    dir_idx = None
                    if (
                        last_dir_idx in unmade_cell_dirs
                        and random.randint(0, 99) > config.winding_percent
                    ):
                        dir_idx = last_dir_idx
                    else:
                        dir_idx = unmade_cell_dirs[
                            random.randint(0, len(unmade_cell_dirs) - 1)
                        ]

                    carve(*(cell + dirs[dir_idx]), TileType.FLOOR)
                    carve(*(cell + (dirs[dir_idx] * 2)), TileType.FLOOR)

                    cells.append(cell + (dirs[dir_idx] * 2))
                    last_dir_idx = dir_idx
                else:
                    cells.pop()
                    last_dir_idx = None

    # 3. Connect regions
    connector_regions = {}
    for y in range(1, config.dungeon_height - 1):
        for x in range(1, config.dungeon_width - 1):
            if dungeon[y][x] != TileType.WALL:
                continue

            regions = set()
            for dir in dirs:
                adj_pos_x = x + dir[0]
                adj_pos_y = y + dir[1]
                region = region_idx[adj_pos_y][adj_pos_x]
                if region != -1:
                    regions.add(region)

            if len(regions) < 2:
                continue

            connector_regions[(x, y)] = regions

    connectors = list(connector_regions.keys())

    merged = []
    open_regions = set()
    for i in range(current_region + 1):
        merged.append(i)
        open_regions.add(i)

    while len(open_regions) > 1:
        connector = connectors[random.randint(0, len(connectors) - 1)]

        dungeon[connector[1]][connector[0]] = TileType.DOOR

        regions = list(map(lambda region: merged[region], connector_regions[connector]))
        dest = regions[0]
        sources = regions[1:]

        for i in range(current_region + 1):
            if merged[i] in sources:
                merged[i] = dest

        for src in sources:
            open_regions.remove(src)

        new_connectors = []
        for pos in connectors:
            is_adjacent = False
            for dir in dirs:
                if connector[0] + dir[0] == pos[0] and connector[1] + dir[1] == pos[1]:
                    is_adjacent = True
                    break
            if is_adjacent:
                continue

            regions = set(map(lambda region: merged[region], connector_regions[pos]))

            if len(regions) > 1:
                new_connectors.append(pos)
                continue

            if random.random() < config.extra_connector_chance:
                dungeon[pos[1]][pos[0]] = TileType.DOOR

        connectors = new_connectors

    # 4. Remove dead ends
    done = False
    while not done:
        done = True
        for y in range(1, config.dungeon_height - 1):
            for x in range(1, config.dungeon_width - 1):
                if dungeon[y][x] == TileType.WALL:
                    continue

                exits = 0
                for dir in dirs:
                    if dungeon[y + dir[1]][x + dir[0]] != TileType.WALL:
                        exits += 1

                if exits != 1:
                    continue

                done = False
                dungeon[y][x] = TileType.WALL

    # Generate debug color for each region
    floor_colors = []
    for _ in range(current_region + 1):
        floor_color = np.ones((4,)) * 255.0
        floor_color[:3] = np.random.randint(0, 255, (3,)) / 255
        floor_colors.append(floor_color)
    wall_color = np.array((50, 50, 50, 255)) / 255
    floor_color = np.array((255, 255, 255, 255)) / 255
    door_color = np.array((222, 184, 135, 255)) / 255

    for y in range(config.dungeon_height):
        for x in range(config.dungeon_width):
            match dungeon[y][x]:
                case TileType.ROOM:
                    app.spawn(
                        Transform(np.array([x, y]), np.array([1.0, 1.0])),
                        Texture(floor_colors[region_idx[y][x]]),
                        Layer(id=2),
                    )
                case TileType.WALL:
                    app.spawn(
                        Transform(np.array([x, y]), np.array([1.0, 1.0])),
                        Texture(wall_color),
                        Layer(id=2),
                    )
                case TileType.FLOOR:
                    app.spawn(
                        Transform(np.array([x, y]), np.array([1.0, 1.0])),
                        Texture(floor_color),
                        Layer(id=2),
                    )
                case TileType.DOOR:
                    app.spawn(
                        Transform(np.array([x, y]), np.array([1.0, 1.0])),
                        Texture(door_color),
                        Layer(id=2),
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
                winding_percent=0,
                extra_connector_chance=0.05,
            )
        )
