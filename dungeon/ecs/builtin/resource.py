import json
import moderngl
import pygame
import numpy as np

from dungeon.type import vec2
from dungeon.ecs.builtin.render_state import RenderState


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


class ResourceLoader:
    def __init__(self):
        self.texture_array_data: dict[str, moderngl.TextureArray] = {}
        self.texture_array_layer_map: dict[str, dict[str, int]] = {}

    def load_resources(self, meta_path: str, render_state: RenderState):
        ctx = render_state.ctx

        with open(meta_path, "r") as fp:
            meta = json.load(fp)

        # TODO add types for meta file, to facilitate parsing and resource manager tool in the future
        texture_meta = meta["textures"]
        for entry in texture_meta:
            name = entry["name"]
            ty = entry["type"]
            data = entry["data"]

            if ty != "array":
                raise RuntimeError(
                    f"Only support texture arrays currently, but found {ty}"
                )

            if name in self.texture_array_data:
                raise RuntimeError(f"Found duplicate texture array name {name}!")

            self.texture_array_layer_map[name] = {}

            layer_data_list = []
            width = None
            height = None
            for idx, layer in enumerate(data):
                subname = layer["subname"]
                path = layer["path"]

                self.texture_array_layer_map[name][subname] = idx

                surface = pygame.image.load(path).convert_alpha()
                surface_width = surface.get_width()
                surface_height = surface.get_height()
                if width is None:
                    width = surface_width
                    height = surface_height
                elif width != surface_width or height != surface_height:
                    raise RuntimeError(
                        "Textures in the same texture array must have identical resolution!\n"
                        f"However, texture from {path} has a resolution of {surface_width}x{surface_height},\n"
                        f"which mismatch with the reference resolution {width}x{height}"
                    )

                raw_bytes = pygame.image.tostring(surface, "RGBA")
                layer_data_list.append(raw_bytes)

            all_bytes = b"".join(layer_data_list)
            texture_array = ctx.texture_array(
                (width, height, len(layer_data_list)),
                4,
                all_bytes,
            )
            texture_array.filter = (moderngl.NEAREST, moderngl.NEAREST)

            self.texture_array_data[name] = texture_array

    def get_texture_array(self, name: str) -> moderngl.TextureArray:
        return self.texture_array_data[name]

    def get_texture_array_layer_index(self, name: str, subname: str) -> int:
        return self.texture_array_layer_map[name][subname]
