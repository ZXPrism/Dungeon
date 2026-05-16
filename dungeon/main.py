from rich.traceback import install

install(show_locals=True)

import urllib.request
import io
import pygame
import numpy as np

from dungeon.ecs.ecs import App
from dungeon.ecs.plugin import Plugin
from dungeon.ecs.builtin.component import Transform, Texture
from dungeon.ecs.query import Query
from dungeon.ecs.resource import Res
from dungeon.ecs.builtin.resource import Input, Camera
from dungeon.ecs.builtin.render_plugin import RenderPlugin
from dungeon.ecs.builtin.input_plugin import InputPlugin
from dungeon.ecs.builtin.time_plugin import TimePlugin
from dungeon.ecs.schedule import Schedule

HERO_SIZE = (64, 64)
HERO_URL = f"https://picsum.photos/{HERO_SIZE[0]}/{HERO_SIZE[1]}"


class Hero:
    pass


def fetch_image(url: str) -> pygame.Surface:
    with urllib.request.urlopen(url) as resp:
        data = resp.read()
    return pygame.image.load(io.BytesIO(data)).convert_alpha()


def setup(app: App):
    hero_texture = fetch_image(HERO_URL)
    hero_entity = app.spawn(
        Hero(),
        Transform(np.array([0.0, 0.0]), np.array([1.0, 1.0])),
        Texture(hero_texture),
    )


def control(query: Query[Hero, Transform], res_input: Res[Input]):
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


class GameCore(Plugin):
    def build(self, app: App):
        app.add_system(Schedule.StartUp, setup)
        app.add_system(Schedule.Update, control)


def main():
    app = App("Dungeon")
    app.add_plugin(TimePlugin())
    app.add_plugin(RenderPlugin())
    app.add_plugin(InputPlugin())
    app.add_plugin(GameCore())
    app.run()


if __name__ == "__main__":
    main()
