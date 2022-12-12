#version 330
layout (location = 0) in vec3 in_position;
out vec3 texCubeCoords;
uniform mat4 m_proj;
uniform mat4 m_view;
//uniform mat4 m_model;
void main() 
{
    texCubeCoords = in_position;
    vec4 pos =  m_proj * m_view * vec4(in_position, 1.0);
    gl_Position = pos.xyww;
    gl_Position.z -= 0.0001;
    //gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}