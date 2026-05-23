import numpy as np
import pygame
import moderngl
import dungeon.shader.quad as quad_shader

from dungeon.ecs.builtin.render_state import RenderState
from dungeon.ecs.query import Query
from dungeon.ecs.builtin.component import Transform, TextureArray, Layer
from dungeon.ecs.resource import Res
from dungeon.ecs.builtin.resource import Camera, ResourceLoader
from dungeon.ecs.plugin import Plugin
from dungeon.ecs.schedule import Schedule
from dungeon.ecs.ecs import App

INSTANCE_DTYPE = np.dtype(
    [
        ("pos", "f4", 2),
        ("scale", "f4", 2),
        ("texture_id", "u4", 1),
    ]
)
INITIAL_CAPACITY_INSTANCE_VBO = 4096


def render(
    query: Query[Transform, TextureArray, Layer],
    res_camera: Res[Camera],
    res_render_state: Res[RenderState],
    res_resource_loader: Res[ResourceLoader],
):
    camera = res_camera.data
    camera.update()

    resource_loader = res_resource_loader.data

    render_state = res_render_state.data
    ctx = render_state.ctx
    ctx.screen.use()
    ctx.clear(0.1, 0.1, 0.13, 1.0)

    quad_instance_vbo = render_state.quad_instance_vbo

    n_instance = len(query)
    old_capacity = quad_instance_vbo.size / INSTANCE_DTYPE.itemsize
    if len(query) > old_capacity:
        new_capacity = max(n_instance * 2, old_capacity * 2)
        quad_instance_vbo.orphan(new_capacity * INSTANCE_DTYPE.itemsize)

    instance_data = np.empty(n_instance, dtype=INSTANCE_DTYPE)

    # Index sort on layer id
    indices = [i for i in range(n_instance)]
    indices.sort(key=lambda x: query[x][2].id, reverse=True)

    texture_array_slot: dict[str, int] = {}

    for i in range(n_instance):
        entry = query[indices[i]]
        transform = entry[0]
        texture_array = entry[1]

        name = texture_array.name
        if name not in texture_array_slot:
            slot = len(texture_array_slot)
            texture_array_slot[name] = slot

            texture_array_handle = resource_loader.get_texture_array(name)
            texture_array_handle.use(slot)
            render_state.quad_program[f"texture_array_sampler_{slot}"] = slot

        subname = texture_array.subname
        layer_index = resource_loader.get_texture_array_layer_index(name, subname)

        instance_data[i]["pos"] = transform.position
        instance_data[i]["scale"] = transform.scale
        instance_data[i]["texture_id"] = texture_array_slot[name] + (layer_index << 4)

    quad_instance_vbo.write(instance_data.tobytes())
    render_state.quad_program["view"].write(camera.view.tobytes())
    render_state.quad_program["projection"].write(camera.projection.tobytes())
    render_state.quad_vao.render(instances=n_instance)

    pygame.display.flip()


class RenderPlugin(Plugin):
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def build(self, app: App):
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 4)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 5)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE
        )
        pygame.display.set_mode(
            (self.width, self.height),
            pygame.OPENGL | pygame.DOUBLEBUF,
        )

        ctx = moderngl.create_context(require=450)
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        camera_height = 24.0
        aspect_ratio = self.width / self.height
        app.insert_resource(
            Camera(np.zeros((2,)), camera_height * aspect_ratio, camera_height)
        )

        quad_program = ctx.program(
            vertex_shader=quad_shader.get_vertex_shader(),
            fragment_shader=quad_shader.get_fragment_shader(),
        )
        quad_vertices = np.concat(
            [
                [-0.5, -0.5, 0.0, 1.0],
                [0.5, -0.5, 1.0, 1.0],
                [0.5, 0.5, 1.0, 0.0],
                [-0.5, 0.5, 0.0, 0.0],
            ],
            dtype="f4",
        )
        quad_indices = np.array([0, 1, 2, 0, 2, 3], dtype="u4")

        quad_vbo = ctx.buffer(quad_vertices.tobytes())
        quad_ebo = ctx.buffer(quad_indices.tobytes())
        quad_instance_vbo = ctx.buffer(
            reserve=INITIAL_CAPACITY_INSTANCE_VBO * INSTANCE_DTYPE.itemsize,
            dynamic=True,
        )
        quad_vao = ctx.vertex_array(
            quad_program,
            [
                (quad_vbo, "4f", "in_quad"),
                (
                    quad_instance_vbo,
                    "2f 2f 1u /i",
                    "in_inst_pos",
                    "in_inst_scale",
                    "in_inst_texture_id",
                ),
            ],
            index_buffer=quad_ebo,
            index_element_size=4,
        )

        app.insert_resource(
            RenderState(
                width=self.width,
                height=self.height,
                ctx=ctx,
                quad_vao=quad_vao,
                quad_instance_vbo=quad_instance_vbo,
                quad_program=quad_program,
            )
        )
        app.add_system(Schedule.RenderUpdate, render)
