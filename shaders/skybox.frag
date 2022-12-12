#version 330
layout (location = 0) out vec4 fragColor;
in vec3 texCubeCoords;
uniform samplerCube u_texture_skybox;
void main() 
{ 
    fragColor = texture(u_texture_skybox, texCubeCoords);
}