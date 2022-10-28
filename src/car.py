import glm
import numpy as np
import pywavefront

class Car:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.vbo = self.get_vbo()
        self.shader_program = self.get_shader_program()
        self.vao = self.get_vao()
        self.degree = 0
        self.position = glm.vec3(0, 0, 0)
        self.translate = glm.translate(glm.mat4(), glm.vec3(0, 0, 0))
        self.rotation = glm.rotate(glm.mat4(), glm.radians(self.degree), glm.vec3(0, 1, 0))
        self.m_model = self.get_model_matrix()
        self.on_init()

    def get_model_matrix(self):
        m_model = glm.mat4()
        #m_model = glm.rotate(glm.mat4(), glm.radians(0), glm.vec3(0, 1, 0))
        #m_model = self.rotation * self.translate

        return m_model

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
        self.degree += degree
        m_model = glm.translate(self.m_model, -self.position)
        m_model = glm.rotate(m_model, degree, glm.vec3(0,1,0))
        self.m_model = glm.translate(m_model,  glm.rotate(self.position, -degree, glm.vec3(0,1,0)))


    def move_left(self):
        degree = 0.05
        self.degree += degree
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