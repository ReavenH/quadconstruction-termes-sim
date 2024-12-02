import numpy as np
import networkx as nx
import os
import pickle

G = nx.DiGraph()

structureCSV = np.genfromtxt(f'structures/zh_3LayerTShape.csv', delimiter=',')

nodes = [
    (0, 3),
    (1, 3),
    (2, 3),
    (3, 3),
    (4, 3),
    (5, 3),
    (6, 3),
    (6, 2),
    (6, 1),
    (6, 0),
    (6, 4),
    (6, 5),
    (6, 6),
    (6, 7),
]

nodeAttributes = [
    {'node': node, 'height': structureCSV[node[1], node[0]], 'start': False, 'exit': False, 'xy-location': (node[0] + 2, node[1] + 2)} for node in nodes
]

nodeAttributes[0]['start'] = True
nodeAttributes[-5]['exit'] = True
nodeAttributes[-1]['exit'] = True

edges = [
    ((0, 3), (1, 3)),
    ((1, 3), (2, 3)),
    ((2, 3), (3, 3)),
    ((3, 3), (4, 3)),
    ((4, 3), (5, 3)),
    ((5, 3), (6, 3)),
    ((6, 3), (6, 2)),
    ((6, 2), (6, 1)),
    ((6, 1), (6, 0)),
    ((6, 3), (6, 4)),
    ((6, 4), (6, 5)),
    ((6, 5), (6, 6)),
    ((6, 6), (6, 7))
]

for i, attr in enumerate(nodeAttributes):
    G.add_node(nodes[i], **nodeAttributes[i])

for edge in edges[:6]:
    G.add_edge(*edge, prob=1.0)

G.add_edge(*edges[6], prob=0.5)

for edge in edges[7:9]:
    G.add_edge(*edge, prob=1.0)

G.add_edge(*edges[9], prob=0.5)

for edge in edges[10:]:
    G.add_edge(*edge, prob=1.0)

print("Nodes:")
print(G.nodes(data=True))

print("\nEdges:")
print(G.edges(data=True))

os.makedirs("structures", exist_ok=True)
with open("structures/zh_graph3LayerTShape.pkl", "wb") as f:
    pickle.dump(G, f, protocol=pickle.HIGHEST_PROTOCOL)