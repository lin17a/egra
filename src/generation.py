from turtle import distance
import numpy as np
from scipy.special import binom
from scipy.interpolate import interp1d

np.random.seed(13)


def bernstein(n, k, t):
    return binom(n,k) * t**k * (1.-t)**(n-k)


def bezier(points, num=200):
    n = len(points)
    t = np.linspace(0, 1, num=num)
    curve = np.zeros((num, 2))
    for i in range(n):
        curve += np.outer(bernstein(n - 1, i, t), points[i])
    return curve


class Segment:
    def __init__(self, p1, p2, angle1, angle2, **kw):
        self.p1 = p1; self.p2 = p2
        self.angle1 = angle1; self.angle2 = angle2
        self.numpoints = kw.get("numpoints", 100)
        r = kw.get("r", 0.3)
        d = np.sqrt(np.sum((self.p2-self.p1)**2))
        self.r = r*d
        self.p = np.zeros((4,2))
        self.p[0,:] = self.p1[:]
        self.p[3,:] = self.p2[:]
        self.curve = None
        self.calc_intermediate_points()

    def calc_intermediate_points(self):
        self.p[1,:] = self.p1 + np.array([self.r*np.cos(self.angle1), self.r*np.sin(self.angle1)])
        self.p[2,:] = self.p2 + np.array([self.r*np.cos(self.angle2+np.pi), self.r*np.sin(self.angle2+np.pi)])
        self.curve = bezier(self.p, self.numpoints)


def get_curve(points, **kw):
    segments = []
    for i in range(len(points)-1):
        seg = Segment(points[i,:2], points[i+1,:2], points[i,2],points[i+1,2],**kw)
        segments.append(seg)
    curve = np.concatenate([s.curve for s in segments])
    return segments, curve


def ccw_sort(p):
    d = p-np.mean(p, axis=0)
    s = np.arctan2(d[:,0], d[:,1])
    p = p[np.argsort(s),:]
    return p


def get_bezier_curve(a, rad=0.2, edgy=0):
    """ given an array of points *a*, create a curve through
    those points. 
    *rad* is a number between 0 and 1 to steer the distance of
        control points.
    *edgy* is a parameter which controls how "edgy" the curve is,
        edgy=0 is smoothest."""
    p = np.arctan(edgy)/np.pi+.5
    a = np.append(a, np.atleast_2d(a[0,:]), axis=0)
    d = np.diff(a, axis=0)
    ang = np.arctan2(d[:,1],d[:,0])
    f = lambda ang: (ang>=0)*ang + (ang<0)*(ang+2*np.pi)
    ang = f(ang)
    ang1 = ang
    ang2 = np.roll(ang,1)
    ang = p*ang1 + (1-p)*ang2 + (np.abs(ang2-ang1) > np.pi )*np.pi
    ang = np.append(ang, [ang[0]])
    a = np.append(a, np.atleast_2d(ang).T, axis=1)
    s, c = get_curve(a, r=rad, method="var")
    x,y = c.T
    return x,y,a


def get_random_points(n=5, scale=0.8, mindst=None, rec=0):
    """ create n random points in the unit square, which are *mindst*
    apart, then scale them."""
    mindst = mindst or .7/n
    a = np.random.rand(n,2)
    d = np.sqrt(np.sum(np.diff(ccw_sort(a), axis=0), axis=1)**2)
    if np.all(d >= mindst) or rec>=200:
        return a*scale
    else:
        return get_random_points(n=n, scale=scale, mindst=mindst, rec=rec+1)

def homogenizar(xs, ys):
    dist_homogenia = 0.1
    coor = np.array([np.array([x, y]) for x, y in zip(xs, ys)], dtype='f4')
    dist = []
    dist_total = 0
    for i in range(coor.shape[0]):
        d = np.linalg.norm(abs(coor[i-1] - coor[i]))
        dist_total += d
        dist.append(dist_total)
    dist = np.array(dist, dtype='f4')
    
    seen = set()
    dupes = [x for x in range(len(dist)) if dist[x] in seen or seen.add(dist[x])] 
    mask = np.ones(len(dist), dtype=bool)
    mask[dupes] = False
    coor = coor[mask,:]
    dist = dist[mask]
    
    f = interp1d(dist, coor.transpose(), kind="cubic")
    x = []
    y = []
    for i in range(0, int((dist_total+dist_homogenia)/dist_homogenia)):
        i = i*dist_homogenia
        vertice = f(i)
        x.append(vertice[0])
        y.append(vertice[1])
    return x, y

def calcular_inicio(a):
    dis_max = 0
    for i in range(len(a)):
        dis = ((a[i-1][0]-a[i][0])**2+(a[i-1][1]-a[i][1])**2)**(1/2)
        if dis > dis_max:
            dis_max = dis
            punto_max = i
    x = a[punto_max][0]+(a[punto_max-1][0]-a[punto_max][0])/2
    y = a[punto_max][1]+(a[punto_max-1][1]-a[punto_max][1])/2
    return (x, y)

def generation_track(points, rad, edgy):
    a = get_random_points(n=points, scale=100)
    a = ccw_sort(a)
    punto_inicio = calcular_inicio(a)
    x,y, _ = get_bezier_curve(a,rad=rad, edgy=edgy)
    x,y = homogenizar(x, y)
    
    return x, y, punto_inicio