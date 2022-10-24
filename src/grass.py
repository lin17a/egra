from msilib.schema import Component
import glm
import moderngl as mgl
import numpy as np
import pygame as pg

class Grass:
    def __init__(self,app):
        self.app = app
        self.ctx = app.ctx
        self.vbo = self.get_vbo()
        self.shader_program = self.get_shader_program()
        self.vao = self.get_vao()
        self.m_model = self.get_model_matrix()
        self.texture = self.get_texture_cube(dir_path='./textures/sky/')
        self.on_init()
        
    def get_model_matrix(self):
        m_model = glm.scale(glm.mat4(1), glm.vec3(0,1,0))
        #m_model = glm.rotate(glm.mat4(),glm.radians(0),glm.vec3(0,1,0))
        return m_model
        
    def get_texture_cube(self, dir_path):
        faces = ['right', 'left', 'top', 'bottom', 'front', 'back']
        textures = [pg.image.load(dir_path + f"{face}.png").convert() for face in faces]
        size = textures[0].get_size()
        texture_cube = self.ctx.texture_cube(size=size, components=3, data=None)

        for i in range(6):
            texture_data = pg.image.tostring(textures[i], 'RGB')
            texture_cube.write(face=i, data=texture_data)

        return texture_cube

    def get_texture(self, path):
        texture = pg.image.load(path).convert()
        texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
        texture = self.ctx.texture(size=texture.get_size(), components=3, 
                                    data=pg.image.tostring(texture, 'RGB'))
        return texture


    def on_init(self):
        self.shader_program['u_texture_skybox'] = 0
        self.texture.use(location=0)
        self.shader_program['m_proj'].write(self.app.camera.m_proj)
        self.shader_program['m_view'].write(glm.mat4(glm.mat3(self.app.camera.m_view)))
        #self.shader_program['m_model'].write(self.m_model)
        #self.shader_program["skybox"] = self.get_texture_cube(dir_path='./textures/sky/')

    def o(self, x):
        self.obj = x
        return self.obj

    def ax(self, x):
        self.ax = x
        return self.ax

    def render(self):
        if self.o:
            self.vao.render()
        #if self.ax:
            #self.vaoa.render(mgl.LINE_LOOP)
        #self.vaop.render(mgl.POINTS)
        
    def destroy (self):
        self.vbo.release()
        self.shader_program.release()
        self.vao.release()
    
    def get_vertex_data(self):
        vertices = [(-1, -1, 1), ( 1, -1,  1), (1,  1,  1), (-1, 1,  1),
                    (-1, 1, -1), (-1, -1, -1), (1, -1, -1), ( 1, 1, -1)]

        indices = [(0, 2, 3), (0, 1, 2),
                   (1, 7, 2), (1, 6, 7),
                   (6, 5, 4), (4, 7, 6),
                   (3, 4, 5), (3, 5, 0),
                   (3, 7, 4), (3, 2, 7),
                   (0, 6, 1), (0, 5, 6)]

        vertex_data = self.get_data(vertices, indices)
        vertex_data = np.flip(vertex_data, 1).copy(order='C')

        '''
                vertices = [
                    (-0.5, 0, -0.5), # (0,0)
                    (0.5, 0, -0.5), # (1,0)
                    (0.5, 0, 0.5), # (1,1)
                    (-0.5, 0, 0.5), # (0,1)
                    ]
        indices = [
                (0,2,3),(0,1,2)
        ]
        tex_coord = [(0,0), (1,0), (0,1), (1,1)]
        tex_coord_indices = [(0, 3, 1), (0, 2, 3)]
        
        tex_coord_data = self.get_data(tex_coord, tex_coord_indices)

        data = np.hstack([tex_coord_data, vertex_data])
        '''

        return vertex_data

    def get_vao(self):
        vao = self.ctx.vertex_array(self.shader_program, [(self.vbo, '3f', 'in_position')])
        return vao                      
    
    @staticmethod
    def get_data(vertices, indices): 
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')

    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo
    
    def get_shader_program(self):
        program = self.ctx.program(    
            vertex_shader='''
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
            ''',
            fragment_shader='''
                #version 330
                layout (location = 0) out vec4 fragColor;
                in vec3 texCubeCoords;
                uniform samplerCube u_texture_skybox;
                void main() 
                { 
                    fragColor = texture(u_texture_skybox, texCubeCoords);
                }
            ''',
        )
        return program