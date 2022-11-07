
#version 330
layout (location = 0) out vec4 fragColor;
in vec3 color;
in vec2 xy;



float round(float x){
    return floor(x + 0.5);
}

void main() { 
    //float x = round(100*xy.x) / 100;
    //float y = xy.y;
    //vec2 coord = vec2(xy.x, xy.y);
    //float r = random2d(coord);
    fragColor = vec4(color, 1.0);
}
