import glm

class Camera:
    def __init__(self, app):
        self.app = app
        self.aspec_ratio = app.WIN_SIZE[0]/app.WIN_SIZE[1]
        self.position =glm.vec3(45,10,45)
        self.up = glm.vec3(1,0,0)
        self.lookat = glm.vec3(45,0,45)
        self.radians = 170
        # view_matrix
        self.m_view = self.get_view_matrix()
        # projection matrix
        self.m_proj = self.get_projection_matrix()
        
    def get_view_matrix(self):
        print(self.position, self.lookat, self.up)
        return glm.lookAt(self.position, self.lookat, self.up)
    
    def get_projection_matrix(self):
        return glm.perspective(glm.radians(self.radians), self.aspec_ratio, 0.1, 100)

    def zoom(self, scroll):
        if 180 > self.radians +  scroll> 0:
            self.radians = self.radians + scroll
            self.m_proj = self.get_projection_matrix()
    
    def move_right(self):
        self.lookat = self.lookat + glm.vec3((0, 0, 0.01*self.radians))
        self.position = self.position + glm.vec3((0, 0, 0.01*self.radians))
        self.m_view = self.get_view_matrix()

    def move_left(self):
        self.lookat = self.lookat + glm.vec3((0, 0, -0.01*self.radians))
        self.position = self.position + glm.vec3((0, 0, -0.01*self.radians))
        self.m_view = self.get_view_matrix()

    def move_up(self):
        self.lookat = self.lookat + glm.vec3((0.01*self.radians, 0, 0))
        self.position = self.position + glm.vec3((0.01*self.radians, 0, 0))
        self.m_view = self.get_view_matrix()
    
    def move_down(self):
        self.lookat = self.lookat + glm.vec3((-0.01*self.radians, 0, 0))
        self.position = self.position + glm.vec3((-0.01*self.radians, 0, 0))
        self.m_view = self.get_view_matrix()