import glm
import moderngl as mgl
from generation import generation_track
import numpy as np
from scipy.spatial.distance import cdist


class Circuito:
    def __init__(self,app):
        self.app = app
        self.ctx = app.ctx
        self.edgy = 0.1
        self.rad = 0.1
        self.current_vertex = None
        self.color_vertex = None
        self.all_vertex = np.empty(0,  dtype='f4')
        self.vbo, self.vboc = self.get_vbo()
        self.shader_program = self.get_shader_program('circuito')
        self.vao = self.get_vao()
        self.m_model = self.get_model_matrix()
        self.on_init()

    def get_model_matrix(self):
        m_model = glm.rotate(glm.mat4(), glm.radians(0), glm.vec3(0,1,0))
        return m_model
        
    def on_init(self):
        self.shader_program['m_model'].write(self.m_model)

    def render(self, player=1):
        if player == 1:
            self.shader_program['m_proj'].write(self.app.camera.m_proj)
            self.shader_program['m_view'].write(self.app.camera.m_view)
        elif player == 2:
            self.shader_program['m_proj'].write(self.app.camera_2.m_proj)
            self.shader_program['m_view'].write(self.app.camera_2.m_view)
        self.vao.render(mgl.TRIANGLE_STRIP)
        
        
    def destroy (self):
        self.vbo.release()
        self.vboc.release()
        self.shader_program.release()
        self.vao.release()
    
    def get_vao(self):
        vao = self.ctx.vertex_array(self.shader_program, [(self.vbo, '3f', 'in_position'), (self.vboc, '3f', 'in_color')])
        return vao

    def get_vertex_data(self):
        # Generacion de la forma del circuito
        xs, ys, punto_inicio = generation_track(10, self.rad, self.edgy)
        vertex_data = np.array([np.array([x, 0, y]) for x, y in zip(xs, ys)], dtype='f4')
        vertex_2d = []
        weight = 3
        # Genera los bordes de la carretera a partir de la forma
        for i in range(len(vertex_data)-1):
            vec = vertex_data[i]-vertex_data[i+1]
            vec1 = np.array([-vec[2], 0, vec[0]])
            vec2 = np.array((vec[2], 0, -vec[0]))
            module = sum(vec1**2)**(1/2)+sum(vec2**2)**(1/2)
            if module == 0:
                continue
            vertex_2d.append(vertex_data[i]+vec1/module*weight)
            vertex_2d.append(vertex_data[i]+vec2/module*weight)

        # Añadimos los primeros vertices al final para cerrar el circuito
        vertex_2d = vertex_2d + vertex_2d[:2]
        vertex_2d = np.array(vertex_2d, dtype='f4')
        # Se centra el circuito
        x_mid_point = (np.array(vertex_2d)[:, 0].max() - np.array(vertex_2d)[:, 0].min()) / 2
        y_mid_point = (np.array(vertex_2d)[:, 2].max() - np.array(vertex_2d)[:, 2].min()) / 2
        vertex_2d[:, 0] = vertex_2d[:, 0] - x_mid_point
        vertex_2d[:, 2] = vertex_2d[:, 2] - y_mid_point

        self.all_vertex = vertex_2d

        start_vertex = np.array([[punto_inicio[0],0,punto_inicio[1]]], dtype='f4')
        d = cdist(start_vertex, vertex_data)
        idx_inicio = np.argmin(d)*2
        color = np.array([(0.2,0.2,0.2) for _ in range(vertex_2d.shape[0])], dtype='f4')
        color[idx_inicio-2:idx_inicio+2] = (1,1,1)

        self.color_vertex = color
        self.current_vertex = idx_inicio

        return vertex_2d, color

    def new_road(self):
        self.vbo, self.vboc = self.get_vbo()
        self.vao = self.get_vao()
        self.render()

    @staticmethod
    def get_data(vertices, indices): 
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')

    def get_vbo(self):
        vertex_data, color_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        vboc = self.ctx.buffer(color_data)
        return vbo, vboc
    
    def get_shader_program(self, shader_program_name):
        with open(f'shaders/{shader_program_name}.vert') as file:
                    vertex_shader = file.read()

        with open(f'shaders/{shader_program_name}.frag') as file:
            fragment_shader = file.read()

        program = self.ctx.program(vertex_shader=vertex_shader, 
                                fragment_shader=fragment_shader)
        return program


class MinimapCircuito(Circuito):
    def __init__(self, app, all_vertex, color_vertex):
        self.app = app
        self.ctx = app.ctx
        self.edgy = 0.1
        self.rad = 0.1
        self.current_vertex = None
        self.color_vertex = color_vertex
        self.all_vertex = all_vertex
        self.vbo, self.vboc = self.get_vbo(all_vertex, color_vertex)
        self.shader_program = self.get_shader_program('circuito')
        self.vao = self.get_vao()
        self.m_model = self.get_model_matrix()
        self.on_init()

    def new_road(self, all_vertex, color_vertex):
        self.vbo, self.vboc = self.get_vbo(all_vertex, color_vertex)
        self.vao = self.get_vao()
        self.render()

    def get_vbo(self, all_vertex, color_vertex):
        vbo = self.ctx.buffer(all_vertex)
        vboc = self.ctx.buffer(color_vertex)
        return vbo, vboc

    def render(self, player=1):
        if player == 1:
            self.shader_program['m_proj'].write(self.app.minimap.m_proj)
            self.shader_program['m_view'].write(self.app.minimap.m_view)
        elif player == 2:
            self.shader_program['m_proj'].write(self.app.minimap_2.m_proj)
            self.shader_program['m_view'].write(self.app.minimap_2.m_view)
        self.vao.render(mgl.TRIANGLE_STRIP)

