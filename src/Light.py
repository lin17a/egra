import glm

class Light:
    def __init__(self, position=(5,5,0), color=(1,1,1)):
        self.position = glm.vec3(5,-5,5)
        self.color = glm.vec3(color)
        # intensities
        self.Ia = 0.2 * self.color # ambient
        self.Id = 0.8 * self.color # diffuse
        self.Is = 1.0 * self.color # specular