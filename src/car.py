import glm
import numpy as np
import pywavefront
import math

class Car:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.vbo = self.get_vbo()
        self.shader_program = self.get_shader_program()
        self.vao = self.get_vao()
        self.rotation = self.get_start_rotation()
        self.position = self.get_start_position()
        self.m_model = self.get_model_matrix()
        self.on_init()

    def get_start_position(self):
        vertex = self.app.scene.all_vertex[self.app.scene.current_vertex - 20]
        next_vertex = self.app.scene.all_vertex[self.app.scene.current_vertex - 19]
        y_mid_point = (next_vertex[0].max() + vertex[0].min()) / 2
        x_mid_point = (next_vertex[2].max() + vertex[2].min()) / 2
        return glm.vec3((y_mid_point, 0, x_mid_point))

    def get_start_rotation(self):
        vertex = self.app.scene.all_vertex[self.app.scene.current_vertex - 20] # coordinate order: y, z, x
        next_vertex = self.app.scene.all_vertex[self.app.scene.current_vertex - 19]
        dir_vec = next_vertex - vertex
        rot_rad = math.atan2(dir_vec[0], dir_vec[2]) # atan2(y, x)
        return rot_rad

    def get_model_matrix(self):
        m_model = glm.rotate(glm.mat4(), self.rotation, glm.vec3(0, 1, 0))
        m_model = glm.translate(m_model, glm.rotate(self.position, -self.rotation, glm.vec3(0, 1, 0)))
        m_model = glm.scale(m_model, glm.vec3(0.2, 0.2, 0.2))
        return m_model

    def move_to_start(self):
        self.position = self.get_start_position()
        self.rotation = self.get_start_rotation()
        self.m_model = self.get_model_matrix()
        self.on_init()

    def on_init(self):
        self.shader_program['light.position'].write(self.app.light.position)
        # self.shader_program['light.Ia'].write(self.app.light.Ia)
        # self.shader_program['light.Id'].write(self.app.light.Id)
        self.shader_program['m_proj'].write(self.app.camera.m_proj)
        self.shader_program['m_view'].write(self.app.camera.m_view)
        self.shader_program['view_pos'].write(self.app.camera.position)
        self.shader_program['m_model'].write(self.m_model)

    def update(self):
        self.shader_program['light.position'].write(self.app.light.position)
        # self.shader_program['light.Ia'].write(self.app.light.Ia)
        # self.shader_program['light.Id'].write(self.app.light.Id)
        self.shader_program['m_proj'].write(self.app.camera.m_proj)
        self.shader_program['m_view'].write(self.app.camera.m_view)
        self.shader_program['view_pos'].write(self.app.camera.position)
        self.shader_program['m_model'].write(self.m_model)


    def render(self):
        self.shader_program['view_pos'].write(self.app.camera.position)
        self.vao.render()

    def destroy(self):
        self.vbo.release()
        self.shader_program.release()
        self.vao.release()

    def get_vao(self):
        vao = self.ctx.vertex_array(self.shader_program, [(self.vbo, '3f 3f 3f 3f 3f', 'in_normal', 'in_position',
                                                           'in_diffuse', 'in_ambient', 'in_specular')])
        return vao

    def get_vertex_data(self):

        scene = pywavefront.Wavefront('models/car/F1.obj', collect_faces=True)

        vertex_data = self.get_data(scene)

        return vertex_data

    def get_data(self, scene):
        vertices = {}
        data = []

        for name, material in scene.materials.items():
            vertices[name] = material.vertices  # contains normals and vertices

            for i in range(0, len(vertices[name]), 6):
                data.extend(vertices[name][i:i + 6])
                data.extend(material.diffuse[0:3])
                data.extend(material.ambient[0:3])
                data.extend(material.specular[0:3])

        data_np = np.array(data, dtype='f4')
        return data_np

    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo

    def move_right(self):
        degree = -0.05
        self.rotation += degree
        m_model = glm.translate(self.m_model, -self.position)
        m_model = glm.rotate(m_model, degree, glm.vec3(0,1,0))
        self.m_model = glm.translate(m_model,  glm.rotate(self.position, -degree, glm.vec3(0,1,0)))


    def move_left(self):
        degree = 0.05
        self.rotation += degree
        old_position = self.position
        self.m_model = glm.translate(self.m_model, -self.position)
        self.m_model = glm.rotate(self.m_model, degree, glm.vec3(0,1,0))
        self.m_model = glm.translate(self.m_model, glm.rotate(old_position, -degree, glm.vec3(0,1,0)))


    def move_forward(self):
        x, y, z = self.position
        old_position = self.position
        self.position = glm.vec3(x+0.5, y, z)
        self.m_model = glm.translate(self.m_model, self.position - old_position)
    
    def move_backward(self):
        x, y, z = self.position
        old_position = self.position
        self.position = glm.vec3(x-0.5, y, z)
        print(self.position)
        self.m_model = glm.translate(self.m_model, self.position - old_position)

    def get_shader_program(self):
        program = self.ctx.program(
            vertex_shader='''
                #version 330
                layout (location = 0) in vec3 in_position;
                layout (location = 1) in vec3 in_normal;
                layout (location = 2) in vec3 in_diffuse;
                layout (location = 3) in vec3 in_ambient;
                layout (location = 4) in vec3 in_specular;
                out vec3 color;
                struct Light {
                    vec3 position;
                };
                uniform Light light;
                uniform mat4 m_proj;
                uniform mat4 m_view;
                uniform mat4 m_model;
                uniform vec3 view_pos;
                void main() {
                    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
                    vec3 frag_pos = vec3(m_model * vec4(in_position, 1.0));
                    vec3 norm = normalize(in_normal);
                    vec3 light_dir = normalize(light.position - frag_pos);  
                    mat3 inverse_m_model = mat3(transpose(inverse(m_model)));
                    vec3 normal = inverse_m_model * normalize(in_normal);
                    vec3 diffuse = in_diffuse * max(0, dot(normalize(normal), light_dir));
                    vec3 view_dir =  normalize(view_pos - frag_pos);
                    vec3 reflect_dir = reflect(-light_dir, normal);  
                    vec3 specular = in_specular *  pow(max(dot(view_dir, reflect_dir), 0.0), 256);
                    color = (in_ambient + diffuse + specular * 2) * vec3(1,1,1);
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