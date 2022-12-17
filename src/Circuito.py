import glm
import moderngl as mgl
from generation import generation_track
import numpy as np
from scipy.spatial.distance import cdist

from numba import jit, njit
import numba

class Circuito:
    def __init__(self,app):
        self.app = app
        self.ctx = app.ctx
        self.edgy = 0.1
        self.rad = 0.1
        self.current_vertex = None
        self.color_vertex = None
        self.all_vertex = np.empty(0,  dtype='f4')
        self.curves = []
        self.checkpoints = []
        self.vbo, self.vboc = self.get_vbo()
        self.shader_program = self.get_shader_program('circuito')
        self.vao = self.get_vao()
        self.m_model = self.get_model_matrix()
        self.layout_points, self.layout_matrix = self.get_layout_matrix()
        self.curve_matrix = self.get_curve_matrix()
        self.curviness = []
        self.middle_line = []
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
        self.curves = self.get_curvyness()
        checkpoint_thickness = 32
        for curve_idx in self.curves:
            idx_start = curve_idx - checkpoint_thickness
            if idx_start > 0:
                idx_end = curve_idx + checkpoint_thickness % len(color)
                color[idx_start:idx_end] = (0.4, 0.4, 0.4)
                self.checkpoints.append(vertex_2d[idx_start:idx_end])
        color[idx_inicio-2:idx_inicio+2] = (1,1,1)
        self.color_vertex = color
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
    
    def get_shader_program(self, shader_program_name):
        with open(f'shaders/{shader_program_name}.vert') as file:
                    vertex_shader = file.read()

        with open(f'shaders/{shader_program_name}.frag') as file:
            fragment_shader = file.read()

        program = self.ctx.program(vertex_shader=vertex_shader,
                                   fragment_shader=fragment_shader)
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
                idx_left_border = np.concatenate(
                    (np.arange((len(vertices) + first_left) % len(vertices), len(vertices), 2),
                     np.arange(0, last_left + 1 % len(vertices), 2)))
            else:
                idx_left_border = np.arange(first_left, last_left + 1, 2)

            if (first_right < 0 and last_right > 0) or first_right > (last_right % len(vertices)):
                idx_right_border = np.concatenate(
                    (np.arange((len(vertices) + first_right) % len(vertices), len(vertices), 2),
                     np.arange(1, last_right + 1 % len(vertices), 2)))
            else:
                idx_right_border = np.arange(first_right, last_right + 1, 2)

            # calculate the length of the circuit on both sides
            length_left = sum(
                [sum(abs(vertices[i] - vertices[j])) for i, j in zip(idx_left_border[0:-1], idx_left_border[1:])])
            length_right = sum(
                [sum(abs(vertices[i] - vertices[j])) for i, j in zip(idx_right_border[0:-1], idx_right_border[1:])])

            # curviness is the ratio of the two length
            curviness[int(vert / 2)] = length_left / length_right

            # calculate middle point of the circuit for plotting
            middle_line[int(vert / 2)] = (vertices[vert] + vertices[vert - 1]) / 2

        # take the logarithm to see the curves better
        curviness = np.sign(curviness) * np.log(abs(curviness))

        self.curviness = curviness
        self.middle_line = middle_line

        curves = [True if (point > 0.9 or point < -0.9) else False for point in curviness]
        curves_mids = [False] * len(curviness)  # [[0, 0, 0, 0]] * len(curviness)
        i = 0
        end = False
        while not end:
            if curves[i]:
                j = i
                last_curve = i
                num_curves = 0
                while curves[j] or j - last_curve < 18:
                    if curves[j]:
                        last_curve = j
                        num_curves = num_curves + 1
                    if j + 1 >= len(curviness):
                        end = True
                    j = (j + 1) % len(curviness)
                if num_curves > 3:
                    curve_middle = int(i + (last_curve - i) / 2)
                    curves_mids[curve_middle] = True  # [0, 1, 0, 1]
                i = j
            else:
                if i + 1 >= len(curviness):
                    end = True
                i = i + 1

        curve_idx = []
        for i, curve in enumerate(curves_mids):
            if curve:
                curve_idx.append(2 * i)
        return curve_idx

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

        # combine if point is on the circuit
        # in the outer border, but not inside the inner border
        on_track = np.logical_and(in_out_outer, np.logical_not(in_out_inner))

        return test_points.reshape(201, 201, 2), on_track.reshape(201, 201)


    def get_curve_matrix(self):
        #curve_matrix = np.array(np.logical_not(self.layout_matrix), dtype=float)
        curve_matrix = np.where(self.layout_matrix, 0, np.nan)
        middle_point_idxs = []
        for i, middle_point in enumerate(self.middle_line):
            x, y = middle_point[0], middle_point[2]
            distances = np.sqrt((self.layout_points[:, :, 0] - x) ** 2 + (self.layout_points[:, :, 1] - y) ** 2)
            middle_point_idxs.append(np.unravel_index(distances.argmin(), distances.shape))
            curve_matrix[middle_point_idxs[-1]] = self.curviness[(i + 40) % len(self.curviness)]
        while not curve_matrix.all() or not middle_point_idxs:
            new_middle_points = []
            for (x, y) in middle_point_idxs:
                for neighbour_idx in [[x + 1, y], [x - 1, y], [x, y + 1], [x, y - 1]]:
                    if not curve_matrix[neighbour_idx[0], neighbour_idx[1]]:
                        curve_matrix[neighbour_idx[0], neighbour_idx[1]] = curve_matrix[x, y]
                        new_middle_points.append(neighbour_idx)
            middle_point_idxs = new_middle_points
        return curve_matrix


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
