import glm

class Light:
    def __init__(self, m, position=(0,30,0)):
        self.position = glm.vec3(position)

        light_colos = {"sunset" : glm.vec3((251, 144, 98)),
                        "desert" : glm.vec3((250, 213, 165)),
                        "field" : glm.vec3((1,1,1))}
                        
        self.color = light_colos[m]
        # intensities
        self.Ia = 0.2 * self.color # ambient
        self.Id = 0.8 * self.color # diffuse
        self.Is = 1.0 * self.color # specular