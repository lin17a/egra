import numpy as np
import glm
import pywavefront

class Car3D:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        # init car positions
        self.x = 0
        self.y = 0
        self.z = 0
        self.degree = 0
        self.translate = glm.translate(glm.mat4(), glm.vec3(self.x, self.y, self.z))
        self.rotation = glm.rotate(glm.mat4(), glm.radians(self.degree), glm.vec3(0, 1, 0))
        self.vbo = self.get_vbo()
        self.shader_program = self.get_shader_program()
        self.vao = self.get_vao()
        self.m_model = self.get_model_matrix()
        self.on_init()

    def get_model_matrix(self):
        # m_model = glm.mat4()
        """
        Aquí debemos establecer el movimiento del coche con
        una transformación respecto al eje de las Y con desplazamiento
        hacia los ejes X y Z
        """
        m_model = self.rotation * self.translate
        return m_model

    def on_init(self):
        self.shader_program['m_proj'].write(self.app.camera.m_proj)
        self.shader_program['m_view'].write(self.app.camera.m_view)
        self.shader_program['m_model'].write(self.m_model)

    def render(self):
        self.vao.render()

    def destroy(self):
        self.vbo.release()
        self.shader_program.release()
        self.vao.release()

    def get_vao(self):
        vao = self.ctx.vertex_array(self.shader_program, [(self.vbo, '2f 3f 3f', 'in_texcoord_0', 'in_normal', 'in_position')])
        return vao

    def move_right(self):
        self.degree -= 0.5
        self.rotation = glm.rotate(glm.mat4(), glm.radians(self.degree), glm.vec3(0, 1, 0))
        self.shader_program['m_model'].write(self.get_model_matrix())

    def move_left(self):
        self.degree += 0.5
        self.rotation = glm.rotate(glm.mat4(), glm.radians(self.degree), glm.vec3(0, 1, 0))
        self.shader_program['m_model'].write(self.get_model_matrix())

    def move_forward(self):
        self.z -= 0.05
        self.translate = glm.translate(glm.mat4(), glm.vec3(self.x, self.y, self.z))
        self.shader_program['m_model'].write(self.get_model_matrix())

    def get_vertex_data(self):
        objs = pywavefront.Wavefront('Car-Model/Car.obj', cache=True, parse=True)
        obj = objs.materials.popitem()[1]
        vertex_data = obj.vertices
        vertex_data = np.array(vertex_data, dtype='f4')

        return vertex_data

    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo

    def get_shader_program(self):
        program = self.ctx.program(
            vertex_shader='''
                #version 330
                layout (location = 0) in vec3 in_position;
                layout (location = 1) in vec3 in_colors;
                out vec3 color;
                uniform mat4 m_proj;
                uniform mat4 m_view;
                uniform mat4 m_model;
                void main() {
                    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
                    color = in_colors;
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