#version 330
layout (location = 0) out vec4 fragColor;
in vec2 uv_0;
uniform sampler2D u;
void main() 
{ 
    vec3 color = texture(u, uv_0*10).rgb;
    fragColor = vec4(color, 1.0);
}