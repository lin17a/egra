import networkx as nx
import matplotlib.pyplot as plt
import random


def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

# Return true if line segments AB and CD intersect
def intersect_one(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def intersect(G):
    pos = nx.get_node_attributes(G,'pos')
    for A,B in G.edges():
        for C,D in G.edges():
            if (A==C and B==D) or (A==D and B==C):
                continue
            if intersect_one(pos[A], pos[B], pos[C], pos[D]):
                return True
    return False

def get_next_node(n_origin, l_nodes, dis):
    if len(l_nodes)==0:
        return None
    n_node = l_nodes[0]
    for node in l_nodes:
        if dis[n_origin][node] < dis[n_origin][n_node]:
            n_node = node
    return n_node

def create_one():
    G=nx.Graph()
    for i in range(10):
        G.add_node(i,pos=(random.randint(0, 100), random.randint(0, 100)))
    pos=nx.get_node_attributes(G,'pos')

    dis = {}
    for node1, (x1, y1) in pos.items():
        dis[node1] = {}
        for node2, (x2, y2) in pos.items():
            dis[node1][node2] = ((x1-x2)**2+(y1-y2)**2)**(1/2)

    l_node = list(G.nodes())
    n_origin = 0
    n_act = n_origin
    l_node.remove(n_act)
    n_sig = get_next_node(n_act, l_node, dis)
    while len(l_node)!=0:
        G.add_edge(n_act, n_sig)
        n_act = n_sig
        l_node.remove(n_act)
        n_sig = get_next_node(n_act, l_node, dis)
    G.add_edge(n_act, n_origin)
    return G

def generation_track():
    G = create_one()
    while intersect(G):
        G = create_one()
    pos=nx.get_node_attributes(G,'pos')
    return list(pos.values()), list(G.edges())