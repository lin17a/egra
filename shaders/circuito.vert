
#version 330
layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_color;
out vec3 color;
out vec2 xy;
uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

float random2d(vec2 coord){
    return fract(sin(dot(coord.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
    color = in_color - random2d(floor(in_position.xy + 0.5)) * 0.06;
    xy = in_position.xy;
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}
