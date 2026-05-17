def get_vertex_shader():
    return """
#version 450 core
layout(location = 0) in vec2 in_quad;
layout(location = 1) in vec2 in_inst_pos;
layout(location = 2) in vec2 in_inst_scale;
layout(location = 3) in vec4 in_inst_color;

uniform mat4 view;
uniform mat4 projection;

out vec4 quad_color;

void main() {
    vec2 world = (in_quad * in_inst_scale) + in_inst_pos;
    gl_Position = projection * view * vec4(world, 0.0, 1.0);
    quad_color = in_inst_color;
}

"""


def get_fragment_shader():
    return """
#version 450 core
layout(location = 0) out vec4 frag_color;

in vec4 quad_color;

void main() {
    frag_color = quad_color;
}

"""
