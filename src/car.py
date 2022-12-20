import glm
import numpy as np
import pywavefront
import math
from Physics import Physics


class Car:
    def __init__(self, app, player = None, color = "red"):
        self.player = player
        self.color = color
        self.app = app
        self.ctx = app.ctx
        self.vbo = self.get_vbo()
        self.shader_program = self.get_shader_program()
        self.vao = self.get_vao()
        self.rotation = self.get_start_rotation()
        self.position = self.get_start_position()
        self.m_model = self.get_model_matrix()
        self.increase = 0
        
        self.velocity = 0 #[x, y]
        self.friction = 1
        self.velmax = 30
        self.physics = Physics((self.position[0], self.position[2]), dt = 0.05, 
                               maxVel = self.velmax)

        self.velmin = 0

        self.completed_checkpoints = [False] * len(self.app.scene.checkpoints)
        self.crossed_finish = False

        self.on_init()

    @property
    def checkpoints_l(self):
        return self.completed_checkpoints

    def get_start_position(self):
        vertex = self.app.scene.all_vertex[self.app.scene.current_vertex - 20]
        next_vertex = self.app.scene.all_vertex[self.app.scene.current_vertex - 19]
        y_mid_point = (next_vertex[0].max() + vertex[0].min()) / 2
        x_mid_point = (next_vertex[2].max() + vertex[2].min()) / 2
        if self.player == None:
            return glm.vec3((y_mid_point, 0, x_mid_point))

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
        self.completed_checkpoints = [False] * len(self.app.scene.checkpoints)
        self.crossed_finish = False
        self.on_init()

    def on_init(self):
        self.shader_program['light.position'].write(self.app.light.position)
        # self.shader_program['light.Ia'].write(self.app.light.Ia)
        # self.shader_program['light.Id'].write(self.app.light.Id)
        if self.player == 1 or self.player == None:
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
        if self.player == 1 or self.player == None:
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
        if player == 1 or self.player == None:
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
                    if self.color == "red":
                        data.extend([0.5, 0, 0])
                        data.extend([0.5, 0, 0])
                    elif self.color == "blue":
                        data.extend([0, 0, 0.5])
                        data.extend([0, 0, 0.5])
                    elif self.color == "green":
                        data.extend([0, 0.5, 0])
                        data.extend([0, 0.5, 0])
                    elif self.color == "purple":
                        data.extend([0.5, 0, 0.5])
                        data.extend([0.5, 0, 0.5])
                    elif self.color == "turquoise":
                        data.extend([0, 0.5, 0.5])
                        data.extend([0, 0.5, 0.5])
                    elif self.color == "white":
                        data.extend([0.5, 0.5, 0.5])
                        data.extend([0.5, 0.5, 0.5])
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

        
        self.increase += 5
        
        self.velocity = self.physics.accelerate(self.increase, self.on_circuit())
        
        self.increase = 780 if self.increase > 780 else self.increase
        
        print(f"vel: {self.physics.Vel}")
        print(f"miu: {self.physics.miu}")
        
    
    def move_backward(self):
        #print(f"vel: {self.velocity}")
        self.increase -= 5
        self.increase = -30 if self.increase < -30 else self.increase
        self.velocity = self.physics.accelerate(self.increase, self.on_circuit())
        print(f"vel: {self.physics.Vel}")
        print(f"increase: {self.increase}")

        
    def up(self):
        
         
        if self.increase > 0:
            self.increase -= 2.5
        if self.increase == 0:
            self.physics.aant = [0, 0]
            self.physics.Fant = [0, 0]
            
        #self.increase = 0 if self.increase < 0 else self.increase
        
        self.velocity = self.physics.accelerate(self.increase, self.on_circuit())
        
        #self.velocity = 0 if self.velocity < 0 else self.velocity

        self.friction = self.get_friction()
        self.physics.update_miu(self.get_friction(), self.on_circuit())
        
        self.physics.Update(self.velocity, [1,0], self.physics.miu)
        
        
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

    def get_friction(self):
        if self.on_circuit():
            return 0
        else:
            return 10.5


    def on_circuit(self):
        points = self.app.scene.layout_points
        x, y = self.position[0], self.position[2]
        distances = np.sqrt((points[:, :, 0] - x)**2 + (points[:, :, 1] - y)**2)
        closest_point = np.unravel_index(distances.argmin(), distances.shape)
        layout = self.app.scene.layout_matrix
        return layout[closest_point]


    def direction_vector(self, rotation):
        # Hotfix: why do we need this formula
        rotation = 7 * np.pi / 2 - rotation - 2 * ((np.pi / 2 - rotation) % np.pi)  # TODO why is the direction initialised wrong
        direction_vector = glm.vec3(np.sin(rotation) / 5, 0, np.cos(rotation) / 5)  # TODO why do we need to divide by 5
        return direction_vector

    @staticmethod
    def area(p1, p2, p3):
        return abs((p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1])) / 2.0)

    # A function to check whether point P(x, y)
    # lies inside the triangle formed by
    # A(x1, y1), B(x2, y2) and C(x3, y3)
    def is_in_triangle(self, p1, p2, p3, p):
        # Calculate area of triangle ABC
        whole_area = self.area(p1, p2, p3)
        # Calculate area of triangle PBC
        area_1 = self.area(p, p2, p3)
        # Calculate area of triangle PAC
        area_2 = self.area(p1, p, p3)
        # Calculate area of triangle PAB
        area_3 = self.area(p1, p2, p)
        # Check if sum of A1, A2 and A3
        # is same as A
        if (abs(whole_area - (area_1 + area_2 + area_3)) < 1):
            return True
        else:
            return False

    def check_if_on_checkpoint(self):
        checkpoints = self.app.scene.checkpoints
        for i, checkpoint in enumerate(checkpoints):
            if (self.is_in_triangle(checkpoint[0][[2,0]], checkpoint[1][[2,0]], checkpoint[2][[2,0]], [self.position[2], self.position[0]]) or
                self.is_in_triangle(checkpoint[1][[2,0]], checkpoint[2][[2,0]], checkpoint[3][[2,0]], [self.position[2], self.position[0]])):
                self.completed_checkpoints[i] = True
                print("checkpoint ", i, " reached")
            #print(self.position)
            #print(checkpoint)

    def check_if_on_start_line(self):
        start_line = self.app.scene.start_line
        if (self.is_in_triangle(start_line[0][[2,0]], start_line[1][[2,0]], start_line[2][[2,0]], [self.position[2], self.position[0]]) or
            self.is_in_triangle(start_line[1][[2,0]], start_line[2][[2,0]], start_line[3][[2,0]], [self.position[2], self.position[0]])):
            if all(self.completed_checkpoints):
                self.crossed_finish = True

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


class MinimapCar(Car):
    def __init__(self, app, player = None, color = "red"):
        self.scale = 5
        super().__init__(app, player, color)
        

    def on_init(self, player = 1):
        self.shader_program['light.position'].write(self.app.light.position)
        # self.shader_program['light.Ia'].write(self.app.light.Ia)
        # self.shader_program['light.Id'].write(self.app.light.Id)
        if self.player == 1 or self.player == None:
            self.shader_program['m_proj'].write(self.app.minimap.m_proj)
            self.shader_program['m_view'].write(self.app.minimap.m_view)
            self.shader_program['view_pos'].write(self.app.minimap.position)
        elif self.player == 2:
            self.shader_program['m_proj'].write(self.app.minimap_2.m_proj)
            self.shader_program['m_view'].write(self.app.minimap_2.m_view)
            self.shader_program['view_pos'].write(self.app.minimap_2.position)
        self.shader_program['m_model'].write(self.m_model)

    def update(self, player = 1):
        self.shader_program['light.position'].write(self.app.light.position)
        # self.shader_program['light.Ia'].write(self.app.light.Ia)
        # self.shader_program['light.Id'].write(self.app.light.Id)
        if self.player == 1 or self.player == None:
            self.shader_program['m_proj'].write(self.app.minimap.m_proj)
            self.shader_program['m_view'].write(self.app.minimap.m_view)
            self.shader_program['view_pos'].write(self.app.minimap.position)
        elif self.player == 2:
            self.shader_program['m_proj'].write(self.app.minimap_2.m_proj)
            self.shader_program['m_view'].write(self.app.minimap_2.m_view)
            self.shader_program['view_pos'].write(self.app.minimap_2.position)
        self.shader_program['m_model'].write(self.m_model)

    def render(self, player = 1):
        self.shader_program['light.position'].write(self.app.light.position)
        if player == 1 or self.player == None:
            self.shader_program['m_proj'].write(self.app.minimap.m_proj)
            self.shader_program['m_view'].write(self.app.minimap.m_view)
            self.shader_program['view_pos'].write(self.app.minimap.position)
        if player == 2:
            self.shader_program['m_proj'].write(self.app.minimap_2.m_proj)
            self.shader_program['m_view'].write(self.app.minimap_2.m_view)
            self.shader_program['view_pos'].write(self.app.minimap_2.position)

        self.shader_program['m_model'].write(self.m_model)
        #print(self.player, self.position)
        self.vao.render()
    
    def get_model_matrix(self):
        m_model = glm.mat4()
        m_model = glm.translate(m_model, self.position)
        m_model = glm.rotate(m_model, self.rotation, glm.vec3(0, 1, 0))
        m_model = glm.scale(m_model, glm.vec3(0.2, 0.2, 0.2)*self.scale)
        return m_model

    def up(self):
        if self.increase > 0:
            self.increase -= 2.5
        if self.increase == 0:
            self.physics.aant = [0, 0]
            self.physics.Fant = [0, 0]
        self.velocity = self.physics.accelerate(self.increase, self.on_circuit())
        self.friction = self.get_friction()
        self.physics.update_miu(self.get_friction(), self.on_circuit())
        self.physics.Update(self.velocity, [1,0], self.physics.miu)
        direction_vector = self.direction_vector(self.rotation)
        self.position = self.position + self.physics.Vel[0]/20 * direction_vector
        self.m_model = glm.translate(self.m_model, glm.vec3(self.physics.Vel[0]/(20*self.scale), 0, 0))
