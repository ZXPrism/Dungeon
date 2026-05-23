import moderngl

from dataclasses import dataclass


@dataclass
class RenderState:
    width: int
    height: int
    ctx: moderngl.Context
    quad_vao: moderngl.VertexArray
    quad_instance_vbo: moderngl.Buffer
    quad_program: moderngl.Program
