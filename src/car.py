import glm
import numpy as np
import pywavefront
import math
from Physics import Physics


class Car:
    def __init__(self, app, player = 1):
        self.player = player
        self.app = app
        self.ctx = app.ctx
        self.vbo = self.get_vbo()
        self.shader_program = self.get_shader_program()
        self.vao = self.get_vao()
        self.rotation = self.get_start_rotation()
        self.position = self.get_start_position()
        self.m_model = self.get_model_matrix()
        
        self.velocity = 0 #[x, y]
        self.physics = Physics((self.position[0], self.position[2]), dt = 0.05)
        self.velmax = 30
        self.velmin = 0
        
        self.on_init()

    def get_start_position(self):
        vertex = self.app.scene.all_vertex[self.app.scene.current_vertex - 20]
        next_vertex = self.app.scene.all_vertex[self.app.scene.current_vertex - 19]
        y_mid_point = (next_vertex[0].max() + vertex[0].min()) / 2
        x_mid_point = (next_vertex[2].max() + vertex[2].min()) / 2
        dir_vec = next_vertex - vertex
        Movement = 0.2
        if self.player == 1:
            return glm.vec3((y_mid_point, 0, x_mid_point)) - dir_vec * glm.vec3((Movement, 0, Movement))
        elif self.player == 2:
            return glm.vec3((y_mid_point, 0, x_mid_point)) + dir_vec * glm.vec3((Movement, 0, Movement))

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
        if self.player == 1:
            self.shader_program['m_proj'].write(self.app.camera.m_proj)
            self.shader_program['m_view'].write(self.app.camera.m_view)
            self.shader_program['view_pos'].write(self.app.camera.position)
        elif self.player == 2:
            self.shader_program['m_proj'].write(self.app.camera_2.m_proj)
            self.shader_program['m_view'].write(self.app.camera_2.m_view)
            self.shader_program['view_pos'].write(self.app.camera_2.position)
        self.shader_program['m_model'].write(self.m_model)

    def update(self):
        self.shader_program['light.position'].write(self.app.light.position)
        # self.shader_program['light.Ia'].write(self.app.light.Ia)
        # self.shader_program['light.Id'].write(self.app.light.Id)
        if self.player == 1:
            self.shader_program['m_proj'].write(self.app.camera.m_proj)
            self.shader_program['m_view'].write(self.app.camera.m_view)
            self.shader_program['view_pos'].write(self.app.camera.position)
        elif self.player == 2:
            self.shader_program['m_proj'].write(self.app.camera_2.m_proj)
            self.shader_program['m_view'].write(self.app.camera_2.m_view)
            self.shader_program['view_pos'].write(self.app.camera_2.position)
        self.shader_program['m_model'].write(self.m_model)

    def render(self, player):
        self.shader_program['light.position'].write(self.app.light.position)
        if player == 1:
            self.shader_program['m_proj'].write(self.app.camera.m_proj)
            self.shader_program['m_view'].write(self.app.camera.m_view)
            self.shader_program['view_pos'].write(self.app.camera.position)
        if player == 2:
            self.shader_program['m_proj'].write(self.app.camera_2.m_proj)
            self.shader_program['m_view'].write(self.app.camera_2.m_view)
            self.shader_program['view_pos'].write(self.app.camera_2.position)

        self.shader_program['m_model'].write(self.m_model)
        #print(self.player, self.position)
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
                if name == "default7":
                    if self.player == 1:
                        data.extend(material.diffuse[0:3])
                        data.extend(material.ambient[0:3])
                    elif self.player == 2:
                        #Color del coche 2
                        data.extend([0, 0, 0.5])
                        data.extend([0, 0, 0.5])
                else:
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
        degree = -0.05 * self.velocity / 30
        self.rotation = (self.rotation + degree) % (2 * np.pi)
        self.m_model = glm.translate(self.m_model, -self.position)
        self.m_model = glm.rotate(self.m_model, degree, glm.vec3(0,1,0))
        self.m_model = glm.translate(self.m_model,  glm.rotate(self.position, -degree, glm.vec3(0,1,0)))

    def move_left(self):
        degree = 0.05 * self.velocity / 30
        self.rotation = (self.rotation + degree) % (2 * np.pi)
        self.m_model = glm.translate(self.m_model, -self.position)
        self.m_model = glm.rotate(self.m_model, degree, glm.vec3(0,1,0))
        self.m_model = glm.translate(self.m_model, glm.rotate(self.position, -degree, glm.vec3(0,1,0)))

    def move_forward(self):
        self.velocity += 0.5
        self.velocity = self.velmax if self.velocity > self.velmax else self.velocity
        """
        direction_vector = self.direction_vector(self.rotation)
        self.position = self.position + 0.5 * direction_vector
        self.m_model = glm.translate(self.m_model, glm.vec3(0.5, 0, 0))
        """
    
    def move_backward(self):
        #print(f"vel: {self.velocity}")
        self.velocity -= 0.5
        self.velocity = self.velmin if self.velocity < self.velmin else self.velocity

        
    def up(self):
        if self.velocity > 0:
            self.velocity -= 0.1
        #self.velocity = 0 if self.velocity < 0 else self.velocity
        self.physics.Update(self.velocity, [1,0], 1)
        
        
        
        direction_vector = self.direction_vector(self.rotation)
        
        old_position = self.position
        
        self.position = self.position + self.physics.Vel[0]/20 * direction_vector
        
        self.m_model = glm.translate(self.m_model, glm.vec3(self.physics.Vel[0]/20, 0, 0))#self.position - old_position)
        
        
        #print(f"velocidad de la física: {self.physics.Vel}")
        #print(f"velocidad que se le da: {self.velocity}")
        #print(f"miu: {self.physics.miu}")
        #print(f"position {self.physics.Pos[0]}")
        
        #x, y, z = self.position
        #old_position = self.position
        #self.position = glm.vec3(x+0.5, y, z)
        #self.position = glm.vec3(self.physics.Pos[0], y, z)
        #self.position = glm.vec3(x+0.5, y, z)
        #self.m_model = glm.translate(self.m_model, self.position - old_position)
        

    def direction_vector(self, rotation):
        # Hotfix: why do we need this formula
        rotation = 7 * np.pi / 2 - rotation - 2 * ((np.pi / 2 - rotation) % np.pi)  # TODO why is the direction initialised wrong
        direction_vector = glm.vec3(np.sin(rotation) / 5, 0, np.cos(rotation) / 5)  # TODO why do we need to divide by 5
        return direction_vector

    def get_shader_program(self):
        program = self.ctx.program(    
            vertex_shader='''
                #version 330
                #extension GL_ARB_separate_shader_objects: enable

                layout (location = 0) in vec3 in_position;
                layout (location = 1) in vec3 in_normal;
                layout (location = 2) in vec3 in_diffuse;
                layout (location = 3) in vec3 in_ambient;
                layout (location = 4) in vec3 in_specular;
                out vec3 normal;
                out vec3 fragPos;
                
                out vec3 Id;
                out vec3 Ia;
                out vec3 Is;

                uniform mat4 m_proj;
                uniform mat4 m_view;
                uniform mat4 m_model;

                void main() {
                    Id = in_diffuse;
                    Ia = in_ambient;
                    Is = in_specular;
                    fragPos = vec3(m_model * vec4(in_position, 1.0));
                    normal = mat3(transpose(inverse(m_model))) * normalize(in_normal);
                    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                layout (location = 0) out vec4 fragColor;
                
                in vec3 normal;
                in vec3 fragPos;
                
                in vec3 Id;
                in vec3 Ia;
                in vec3 Is;
                
                struct Light {
                    vec3 position;
                };
                uniform Light light;
                uniform vec3 view_pos;
                
                void main() { 
                    vec3 Normal = normalize(normal);
                    vec3 ambient = Ia;
                    vec3 lightDir = normalize(light.position - fragPos);
                    vec3 diffuse = max(0, dot(lightDir, Normal)) * Id;
                    vec3 viewDir = normalize(view_pos - fragPos);
                    vec3 reflectDir = reflect(-lightDir, Normal);
                    float spec = pow(max(dot(viewDir, reflectDir), 0), 32);
                    vec3 specular = spec*Is;
                    vec3 Color = vec3(1,1,1) * (ambient + diffuse + specular);
                    fragColor = vec4(Color,1.0);
                }
            ''',
            )
        return program