import glm
import moderngl as mgl
from generation import generation_track
import numpy as np
from scipy.spatial.distance import cdist

import matplotlib.pyplot as plt

from numba import jit, njit
import numba


class Circuito:
    def __init__(self,app):
        self.app = app
        self.ctx = app.ctx
        self.edgy = 0.1
        self.rad = 0.1
        self.current_vertex = None
        self.all_vertex = np.empty(0,  dtype='f4')
        self.vbo, self.vboc = self.get_vbo()
        self.shader_program = self.get_shader_program()
        self.vao = self.get_vao()
        self.m_model = self.get_model_matrix()
        #self.curves = self.get_curvyness()
        self.layout_points, self.layout_matrix = self.get_layout_matrix()
        self.on_init()

    def get_model_matrix(self):
        m_model = glm.rotate(glm.mat4(), glm.radians(0), glm.vec3(0,1,0))
        return m_model
        
    def on_init(self):
        self.shader_program['m_proj'].write(self.app.camera.m_proj)
        self.shader_program['m_view'].write(self.app.camera.m_view)
        self.shader_program['m_model'].write(self.m_model)

    def render(self):
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
        self.current_vertex = idx_inicio

        return vertex_2d, color

    def new_road(self):
        self.vbo, self.vboc = self.get_vbo()
        self.vao = self.get_vao()
        self.render()
        self.layout_points, self.layout_matrix = self.get_layout_matrix()

    @staticmethod
    def get_data(vertices, indices): 
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')

    def get_vbo(self):
        vertex_data, color_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        vboc = self.ctx.buffer(color_data)
        return vbo, vboc
    
    def get_shader_program(self):
        program = self.ctx.program(    
            vertex_shader='''
                #version 330
                layout (location = 0) in vec3 in_position;
                layout (location = 1) in vec3 in_color;
                out vec3 color;
                out vec2 xy;
                uniform mat4 m_proj;
                uniform mat4 m_view;
                uniform mat4 m_model;

                float random2d(vec2 coord){
                    return fract(sin(dot(coord.xy, vec2(12.9898, 78.233))) * 43758.5453);
                }

                void main() {
                    color = in_color - random2d(floor(in_position.xy + 0.5)) * 0.06;
                    xy = in_position.xy;
                    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                layout (location = 0) out vec4 fragColor;
                in vec3 color;
                in vec2 xy;

                

                float round(float x){
                    return floor(x + 0.5);
                }

                void main() { 
                    //float x = round(100*xy.x) / 100;
                    //float y = xy.y;
                    //vec2 coord = vec2(xy.x, xy.y);
                    //float r = random2d(coord);
                    fragColor = vec4(color, 1.0);
                }
            ''',
        )
        return program


    def get_curvyness(self):
        vertices = self.all_vertex
        # number of nodes to take into account when calculating the curviness
        # (on each side of the node, so in total 2 * num_neighbours + 1 are taken into account)
        num_neighbours = 5
        # curviness at each vertexpair of the circuit
        curviness = np.zeros(int(len(vertices) / 2))
        # coordinates of the middle line
        middle_line = np.zeros((int(len(vertices) / 2), 3))

        for vert in range(0, len(vertices), 2):
            # define first and last node on each side that are considered for the current point on the circuit
            first_left = vert - 2 * num_neighbours
            last_left = (vert + 2 * num_neighbours) % len(vertices)
            first_right = vert - 2 * num_neighbours - 1
            last_right = (vert + 2 * num_neighbours - 1) % len(vertices)

            # get a list of nodes, that should be considered on each side
            if (first_left < 0 and last_left > 0) or first_left > (last_left % len(vertices)):
                idx_left_border = np.concatenate((np.arange((len(vertices) + first_left) % len(vertices), len(vertices), 2),
                                                  np.arange(0, last_left + 1 % len(vertices), 2)))
            else:
                idx_left_border = np.arange(first_left, last_left + 1, 2)

            if (first_right < 0 and last_right > 0) or first_right > (last_right % len(vertices)):
                idx_right_border = np.concatenate((np.arange((len(vertices) + first_right) % len(vertices), len(vertices), 2),
                                                   np.arange(1, last_right + 1 % len(vertices), 2)))
            else:
                idx_right_border = np.arange(first_right, last_right + 1, 2)

            # calculate the length of the circuit on both sides
            length_left = sum([sum(abs(vertices[i] - vertices[j])) for i, j in zip(idx_left_border[0:-1], idx_left_border[1:])])
            length_right = sum([sum(abs(vertices[i] - vertices[j])) for i, j in zip(idx_right_border[0:-1], idx_right_border[1:])])

            # curviness is the ratio of the two length
            curviness[int(vert / 2)] = length_left / length_right

            # calculate middle point of the circuit for plotting
            middle_line[int(vert / 2)] = (vertices[vert] + vertices[vert - 1]) / 2

        # take the logarithm to see the curves better
        curviness = np.sign(curviness) * np.log(abs(curviness))

        # plot the curviness
        curviness_colors = [[(vert - curviness.min()) / (curviness.max() - curviness.min()), 0, 0] for vert in curviness]
        plt.scatter(middle_line[:, 0], middle_line[:, 2], s=10, c=curviness_colors)
        plt.scatter(vertices[:, 0], vertices[:, 2], s=2)
        plt.show()

        return curviness

    @staticmethod
    @jit(nopython=True)
    def pointinpolygon(x, y, poly):
        n = len(poly)
        inside = False
        p2x = 0.0
        p2y = 0.0
        xints = 0.0
        p1x, p1y = poly[0]
        for i in numba.prange(n + 1):
            p2x, p2y = poly[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    #@njit(parallel=True)
    def parallelpointinpolygon(self, points, polygon):
        D = np.empty(len(points), dtype=np.bool)
        for i in numba.prange(0, len(D)):
            D[i] = self.pointinpolygon(points[i, 0], points[i, 1], polygon)
        return D


    def get_layout_matrix(self):

        vertices = self.all_vertex

        # get the bounds of the circuit
        x_max = vertices[:, 2].max()
        x_min = vertices[:, 2].min()
        y_max = vertices[:, 0].max()
        y_min = vertices[:, 0].min()

        # make regular grid
        M, N = 200, 200
        x = np.linspace(x_min - 2, x_max + 2, M + 1)
        y = np.linspace(y_min - 2, y_max + 2, N + 1)
        X, Y = np.meshgrid(x, y)
        test_points = np.vstack([Y.ravel(), X.ravel()])
        test_points = test_points.transpose()

        # test if points are in the inner bounds of the circuit
        in_out_inner = self.parallelpointinpolygon(test_points, vertices[::2, [0, 2]])
        # test if points are in the outer bounds of the circuit
        in_out_outer = self.parallelpointinpolygon(test_points, vertices[1::2, [0, 2]])

        in_list = []
        out_list = []

        # combine if point is on the circuit
        # in the outer border, but not inside the inner border
        on_track = np.logical_and(in_out_outer, np.logical_not(in_out_inner))

        # get points on track and not on track to plot
        for p, point in enumerate(on_track):
            if point:
                in_list.append(p)
            else:
                out_list.append(p)

        plt.plot(vertices[::2, 0], vertices[::2, 2])
        plt.plot(vertices[1::2, 0], vertices[1::2, 2])
        plt.scatter(test_points[in_list, 0], test_points[in_list, 1], s=2)
        plt.scatter(test_points[out_list, 0], test_points[out_list, 1], s=2)
        plt.show()

        return test_points.reshape(201, 201, 2), on_track.reshape(201, 201)

