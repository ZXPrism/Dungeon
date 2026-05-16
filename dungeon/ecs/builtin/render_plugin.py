import numpy as np
import pygame

from dungeon.ecs.query import Query
from dungeon.ecs.builtin.component import Transform, Texture
from dungeon.ecs.resource import Res
from dungeon.ecs.builtin.resource import Input
from dungeon.ecs.plugin import Plugin
from dungeon.ecs.schedule import Schedule
from dungeon.ecs.ecs import App

W = 800
H = 600


def render_setup():
    pygame.display.set_mode((W, H))


def render(query: Query[Transform, Texture], res_input: Res[Input]):
    camera_pos = np.array([0.0, 0.0])
    camera_width = 2.0
    camera_height = 2.0
    # [-camera_width / 2, camera_width / 2] x [-camera_height / 2, camera_height / 2]
    # to [-1, 1] x [-1, 1]
    ndc = np.array([[2 / camera_width, 0.0], [0.0, 2 / camera_height]])
    viewport = np.array([[W / 2, 0], [0, -H / 2]])
    viewport_translation = np.array([W / 2, H / 2])

    screen = pygame.display.get_surface()
    screen.fill((0, 0, 0))

    for transform, texture in query:
        rect_verts_world = (
            np.array([[-0.5, 0.5], [0.5, 0.5], [0.5, -0.5], [-0.5, -0.5]])
            + transform.position
        )
        rect_verts_camera = rect_verts_world - camera_pos
        rect_verts_ndc = rect_verts_camera @ ndc
        rect_verts_viewport = (rect_verts_ndc @ viewport) + viewport_translation
        rect = pygame.Rect(
            rect_verts_viewport[0][0],
            rect_verts_viewport[0][1],
            abs(rect_verts_viewport[1][0] - rect_verts_viewport[0][0]),
            abs(rect_verts_viewport[1][1] - rect_verts_viewport[2][1]),
        )

        surface = pygame.transform.scale(texture.data, (rect.w, rect.h))
        screen.blit(surface, rect)

    pygame.display.flip()


class RenderPlugin(Plugin):
    def build(self, app: App):
        app.add_system(Schedule.StartUp, render_setup)
        app.add_system(Schedule.Update, render)
