import pygame

from dungeon.ecs.plugin import Plugin
from dungeon.ecs.schedule import Schedule
from dungeon.ecs.resource import Res
from dungeon.ecs.builtin.resource import Input
from dungeon.ecs.ecs import App


def resolve_input(app: App, res_input: Res[Input]):
    input_state = res_input.data
    input_state.reset()

    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                app.set_should_close()
            case pygame.KEYDOWN:
                input_state.set_just_pressed(event.key)


class InputPlugin(Plugin):
    def build(self, app: App):
        app.insert_resource(Input())
        app.add_system(Schedule.UpdateHighPriority, resolve_input)
