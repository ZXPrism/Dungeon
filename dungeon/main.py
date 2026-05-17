from rich.traceback import install

install(show_locals=True)

import random
import urllib.request
import io
import pygame
import numpy as np

from dungeon.ecs import *
from dungeon.ecs.builtin.component import Transform, Texture, Layer
from dungeon.ecs.builtin.resource import DeltaTime, Input, Camera
from dungeon.ecs.builtin.render_plugin import RenderPlugin
from dungeon.ecs.builtin.input_plugin import InputPlugin
from dungeon.ecs.builtin.time_plugin import TimePlugin
from dungeon.dungeon_gen import DungeonGen

HERO_SIZE = (64, 64)
HERO_URL = f"https://picsum.photos/{HERO_SIZE[0]}/{HERO_SIZE[1]}"


class Hero:
    pass


def fetch_image(url: str) -> pygame.Surface:
    with urllib.request.urlopen(url) as resp:
        data = resp.read()
    return pygame.image.load(io.BytesIO(data)).convert_alpha()


def setup(app: App):
    hero_entity = app.spawn(
        Hero(),
        Transform(np.array([0.0, 0.0]), np.array([1.0, 1.0])),
        Texture(np.array((0, 255, 0, 255)) / 255),
        Layer(id=1),
    )


def control(
    query: Query[Hero, Transform], res_input: Res[Input], res_camera: Res[Camera]
):
    for _, transform in query:
        pos = transform.position

        input_state = res_input.data
        if input_state.just_pressed(pygame.K_w):
            pos[1] += 1.0
        elif input_state.just_pressed(pygame.K_s):
            pos[1] -= 1.0
        elif input_state.just_pressed(pygame.K_a):
            pos[0] -= 1.0
        elif input_state.just_pressed(pygame.K_d):
            pos[0] += 1.0

        res_camera.data.position = pos


def show_dt(res_delta_time: Res[DeltaTime]):
    dt = res_delta_time.data.value
    fps = 1.0 / (dt + 1e-7)
    pygame.display.set_caption(f"Dungeon v0.1.0-b260517 [dt={dt:.3f} | fps={fps:.0f}]")


class GameCore(Plugin):
    def build(self, app: App):
        app.add_system(Schedule.StartUp, setup)
        app.add_system(Schedule.LogicalUpdate, control)
        app.add_system(Schedule.LogicalUpdate, show_dt)


def main():
    random.seed(42)

    app = App("Dungeon")
    app.add_plugin(TimePlugin())
    app.add_plugin(RenderPlugin(width=1280, height=720))
    app.add_plugin(InputPlugin())
    app.add_plugin(GameCore())
    app.add_plugin(DungeonGen())
    app.run()


if __name__ == "__main__":
    main()
