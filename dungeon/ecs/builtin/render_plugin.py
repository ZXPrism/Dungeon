import numpy as np
import pygame

from dataclasses import dataclass
from dungeon.ecs.query import Query
from dungeon.ecs.builtin.component import Transform, Texture
from dungeon.ecs.resource import Res
from dungeon.ecs.builtin.resource import Camera
from dungeon.ecs.plugin import Plugin
from dungeon.ecs.schedule import Schedule
from dungeon.ecs.ecs import App


@dataclass
class ScreenSize:
    width: int
    height: int


def render_setup():
    pass


def render(
    query: Query[Transform, Texture],
    res_camera: Res[Camera],
    res_screen_size: Res[ScreenSize],
):
    screen_size = res_screen_size.data

    viewport = np.array([[screen_size.width / 2, 0], [0, -screen_size.height / 2]])
    viewport_translation = np.array([screen_size.width / 2, screen_size.height / 2])

    screen = pygame.display.get_surface()
    screen.fill((0, 0, 0))

    camera = res_camera.data

    for transform, texture in query:
        rect_verts_world = (
            np.array([[-0.5, 0.5], [0.5, 0.5], [0.5, -0.5], [-0.5, -0.5]])
            + transform.position
        )
        rect_verts_camera = rect_verts_world - camera.position
        rect_verts_ndc = rect_verts_camera @ camera.ndc_matrix
        rect_verts_viewport = (rect_verts_ndc @ viewport) + viewport_translation
        rect = pygame.Rect(
            rect_verts_viewport[0][0],
            rect_verts_viewport[0][1],
            rect_verts_viewport[1][0] - rect_verts_viewport[0][0],
            rect_verts_viewport[2][1] - rect_verts_viewport[1][1],
        )

        surface = pygame.transform.scale(texture.data, (rect.w, rect.h))
        screen.blit(surface, rect)

    pygame.display.flip()


class RenderPlugin(Plugin):
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        pygame.display.set_mode((width, height))

    def build(self, app: App):
        camera_height = 16.0
        aspect_ratio = self.width / self.height
        app.insert_resource(
            Camera(np.zeros((2,)), camera_height * aspect_ratio, camera_height)
        )
        app.insert_resource(ScreenSize(width=self.width, height=self.height))
        app.add_system(Schedule.StartUp, render_setup)
        app.add_system(Schedule.Update, render)
