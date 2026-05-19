from rich.traceback import install

install(show_locals=True)

import copy
import random
import pygame
import numpy as np

from dungeon.ecs import *
from dungeon.ecs.builtin.component import (
    Entity,
    Layer,
    Transform,
    Texture,
    TweenPosition,
    AnimationEasing,
)
from dungeon.ecs.builtin.resource import DeltaTime, Input, Camera
from dungeon.ecs.builtin.render_plugin import RenderPlugin
from dungeon.ecs.builtin.input_plugin import InputPlugin
from dungeon.ecs.builtin.time_plugin import TimePlugin
from dungeon.ecs.builtin.animation_plugin import AnimationPlugin
from dungeon.dungeon_gen import DungeonGen

VERSION = "Dungeon v0.1.0-b260518"


class Hero:
    pass


def setup(app: App):
    hero_entity = app.spawn(
        Hero(),
        Transform(np.array([0.0, 0.0]), np.array([1.0, 1.0])),
        Texture(np.array((0, 255, 0, 255)) / 255),
        Layer(id=1),
    )


# TODO support WithOut[...] qualifier
def control(
    app: App,
    query: Query[Entity, Hero, Transform],
    res_input: Res[Input],
    res_camera: Res[Camera],
):
    for entity, _, transform in query:
        pos = transform.position
        res_camera.data.position = pos

        input_state = res_input.data
        if input_state.just_pressed(pygame.K_w):
            target_pos = copy.copy(pos)
            target_pos[1] += 1.0
            app.add_component(
                entity.id,
                TweenPosition(
                    duration=0.1,
                    elapsed=0.0,
                    start=pos,
                    end=target_pos,
                    easing=AnimationEasing.LINEAR,
                ),
            )
        elif input_state.just_pressed(pygame.K_s):
            target_pos = copy.copy(pos)
            target_pos[1] -= 1.0
            app.add_component(
                entity.id,
                TweenPosition(
                    duration=0.1,
                    elapsed=0.0,
                    start=pos,
                    end=target_pos,
                    easing=AnimationEasing.LINEAR,
                ),
            )
        elif input_state.just_pressed(pygame.K_a):
            target_pos = copy.copy(pos)
            target_pos[0] -= 1.0
            app.add_component(
                entity.id,
                TweenPosition(
                    duration=0.1,
                    elapsed=0.0,
                    start=pos,
                    end=target_pos,
                    easing=AnimationEasing.LINEAR,
                ),
            )
        elif input_state.just_pressed(pygame.K_d):
            target_pos = copy.copy(pos)
            target_pos[0] += 1.0
            app.add_component(
                entity.id,
                TweenPosition(
                    duration=0.1,
                    elapsed=0.0,
                    start=pos,
                    end=target_pos,
                    easing=AnimationEasing.LINEAR,
                ),
            )


def show_dt(res_delta_time: Res[DeltaTime]):
    dt = res_delta_time.data.value
    fps = 1.0 / (dt + 1e-7)
    pygame.display.set_caption(f"{VERSION} [dt={dt:.3f} | fps={fps:.0f}]")


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
    app.add_plugin(AnimationPlugin())
    app.add_plugin(GameCore())
    app.add_plugin(DungeonGen())
    app.run()


if __name__ == "__main__":
    main()
