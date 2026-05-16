from rich.traceback import install

install()

import urllib.request
import io
import pygame
import numpy as np

from dungeon.ecs.ecs import App
from dungeon.ecs.plugin import Plugin
from dungeon.ecs.builtin.component import Transform, Texture
from dungeon.ecs.builtin.render_plugin import RenderPlugin
from dungeon.ecs.builtin.input_plugin import InputPlugin
from dungeon.ecs.builtin.time_plugin import TimePlugin
from dungeon.ecs.schedule import Schedule

HERO_SIZE = (64, 64)
HERO_URL = f"https://picsum.photos/{HERO_SIZE[0]}/{HERO_SIZE[1]}"


def fetch_image(url: str) -> pygame.Surface:
    with urllib.request.urlopen(url) as resp:
        data = resp.read()
    return pygame.image.load(io.BytesIO(data)).convert_alpha()


def setup(app: App):
    hero_texture = fetch_image(HERO_URL)
    hero_entity = app.spawn(
        Transform(np.array([0.0, 0.0]), np.array([1.0, 1.0])), Texture(hero_texture)
    )


class GamePlugin(Plugin):
    def build(self, app: App):
        app.add_system(Schedule.StartUp, setup)


def main():
    app = App("Dungeon")
    app.add_plugin(TimePlugin())
    app.add_plugin(RenderPlugin())
    app.add_plugin(InputPlugin())
    app.add_plugin(GamePlugin())
    app.run()


if __name__ == "__main__":
    main()
