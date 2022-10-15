# basado en: https://www.youtube.com/watch?v=eJDIsFJN4OQ
import pygame as pg
import moderngl as mgl
import glm
import sys
import pywavefront


import numpy as np

class Camera:
    def __init__(self, app):
        self.app = app
        self.aspec_ratio = app.WIN_SIZE[0]/app.WIN_SIZE[1]
        self.position =glm.vec3(-4,3,8)
        self.up = glm.vec3(0,1,0)
        # view_matrix
        self.m_view = self.get_view_matrix()
        # projection matrix
        self.m_proj = self.get_projection_matrix()
        
    def get_view_matrix(self):
        return glm.lookAt(self.position, glm.vec3(0), self.up)
    
    def get_projection_matrix(self):
        return glm.perspective(glm.radians(45), self.aspec_ratio, 0.1, 100)
    

class Light:
    def __init__(self, position=(5,5,0), color=(1,1,1)):
        self.position = glm.vec3(5,-5,5)
        self.color = glm.vec3(color)
        # intensities
        self.Ia = 0.2 * self.color # ambient
        self.Id = 0.8 * self.color # diffuse
        self.Is = 1.0 * self.color # specular


class Object:
    def __init__(self,app):
        self.app = app
        self.ctx = app.ctx
        self.vbo = self.get_vbo()
        self.shader_program = self.get_shader_program()
        self.vao = self.get_vao()
        self.m_model = self.get_model_matrix()
        self.on_init()
        
    def get_model_matrix(self):
        #m_model = glm.mat4()
        m_model = glm.rotate(glm.mat4(),glm.radians(45),glm.vec3(0,1,0))
        return m_model
        
    def on_init(self):
        self.shader_program['light.position'].write(self.app.light.position)
        # self.shader_program['light.Ia'].write(self.app.light.Ia)
        # self.shader_program['light.Id'].write(self.app.light.Id)
        self.shader_program['m_proj'].write(self.app.camera.m_proj)
        self.shader_program['m_view'].write(self.app.camera.m_view)
        self.shader_program['m_model'].write(self.m_model)

    def render(self):
        self.vao.render()
        
    def destroy (self):
        self.vbo.release()
        self.shader_program.release()
        self.vao.release()
    
    def get_vao(self):
        vao = self.ctx.vertex_array(self.shader_program, [(self.vbo, '3f 3f 3f 3f', 'in_normal', 'in_position',
                                                           'in_diffuse', 'in_ambient')])
        return vao
    
    def get_vertex_data(self):
        # vertices = [(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)]
        # indices = [(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,4),(1,4,5),
        #           (7,2,3),(2,7,6),(1,2,6),(6,5,1),(0,4,7),(0,7,3)]

        scene = pywavefront.Wavefront('models/car/Car.obj', collect_faces=True)

        # scene_box = (scene.vertices[0], scene.vertices[0])
        # for vertex in scene.vertices:
        #     min_v = [min(scene_box[0][i], vertex[i]) for i in range(3)]
        #     max_v = [max(scene_box[1][i], vertex[i]) for i in range(3)]
        #     scene_box = (min_v, max_v)

        # scene_size     = [scene_box[1][i]-scene_box[0][i] for i in range(3)]
        # max_scene_size = max(scene_size)
        # scaled_size    = 5
        # scene_scale    = [scaled_size/max_scene_size for i in range(3)]
        # scene_trans    = [-(scene_box[1][i]+scene_box[0][i])/2 for i in range(3)]

        vertex_data = self.get_data(scene)

        return vertex_data

    def get_data(self, scene):
        vertices = {}
        data = []

        for name, material in scene.materials.items():
            vertices[name] = material.vertices # contains normals and vertices
            # Material properties
            #material.illumination_model]

            for i in range(0, len(vertices[name]), 6):
                data.extend(vertices[name][i:i+6])
                data.extend(material.diffuse[0:3])
                data.extend(material.ambient[0:3])

        data_np = np.array(data, dtype='f4')
        return data_np

    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo
    
    def get_shader_program(self):
        program = self.ctx.program(    
            vertex_shader='''
                #version 330
                layout (location = 0) in vec3 in_position;
                layout (location = 1) in vec3 in_normal;
                layout (location = 2) in vec3 in_diffuse;
                layout (location = 3) in vec3 in_ambient;

                out vec3 color;
                struct Light {
                    vec3 position;
                };
                
                uniform Light light;
                uniform mat4 m_proj;
                uniform mat4 m_view;
                uniform mat4 m_model;
                void main() {
                    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
                    vec3 frag_pos = vec3(m_model * vec4(in_position, 1.0));
                    vec3 norm = normalize(-in_normal);
                    vec3 light_dir = normalize(light.position - frag_pos);  
                    vec3 diffuse1 = in_diffuse * max(dot(norm, light_dir), 0.0);
                    vec3 light_dir2 = normalize(vec3(0,5,-5));
                    vec3 light_dir3 = normalize(vec3(5,5,0));
                    vec3 diffuse2 = in_diffuse * max(dot(norm, light_dir2), 0.0);
                    vec3 diffuse3 = in_diffuse * max(dot(norm, light_dir3), 0.0);
                    color = in_ambient / 2 + (diffuse1 + diffuse2 + diffuse3) / 2;
                }
            ''',
            fragment_shader='''
                #version 330
                #extension GL_ARB_separate_shader_objects : require
                layout (location = 0) out vec4 fragColor;
                in vec3 color;
                void main() {
                    fragColor = vec4(color, 1.0);
                }
            ''',
        )
        return program


class GraphicsEngine:
    def __init__(self, win_size=(900,900)):
        # init pygame modules
        pg.init()
        # window size
        self.WIN_SIZE = win_size
        # set opengl attr
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION,3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION,3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        # create opengl context
        pg.display.set_mode(self.WIN_SIZE, flags=pg.OPENGL | pg.DOUBLEBUF)
        # detect and use exixting opengl context
        self.ctx = mgl.create_context()
        # camera
        self.camera = Camera(self)
        # light
        self.light = Light(self)
        # scene
        self.scene = Object(self)
        
        
    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.scene.destroy()
                pg.quit()
                sys.exit()
                
    def render(self):
        # clear framebuffer
        self.ctx.clear(color=(0,0,0))
        # render scene
        self.scene.render()
        # swap buffers
        pg.display.flip()
        
    def run(self):
         while True:
             self.check_events()
             self.render()
             
        
if __name__ == '__main__':
    app = GraphicsEngine()
    app.run()
