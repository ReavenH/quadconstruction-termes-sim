import numpy as np
import networkx as nx
import os
import pickle

structureCSV = np.genfromtxt(f'structures/zh_6LayerCrossShape.csv', delimiter=',')

G = nx.DiGraph()

nodes = [
    (15, 27),  # 14 nodes.
    (15, 26),
    (15, 25),
    (15, 24),
    (15, 23),
    (15, 22),
    (15, 21),
    (15, 20),
    (15, 19),
    (15, 18),
    (15, 17),
    (15, 16),
    (15, 15),
    (15, 14),

    (15, 13),  # 10 nodes. front branch
    (15, 12),
    (15, 11),
    (15, 10),
    (15, 9),
    (15, 8),
    (15, 7),
    (15, 6),
    (15, 5),
    (15, 4),

    (14, 14),  # 12 nodes. left branch
    (13, 14),
    (12, 14),
    (11, 14),
    (10, 14),
    (9, 14),
    (8, 14),
    (7, 14),
    (6, 14),
    (5, 14),
    (4, 14),
    (3, 14),

    (16, 14),  # 14 nodes. right branch
    (17, 14),
    (18, 14),
    (19, 14),
    (20, 14),
    (21, 14),
    (22, 14),
    (23, 14),
    (24, 14),
    (25, 14),
    (26, 14),
    (27, 14),
    (28, 14),
    (29, 14)
]

nodeAttributes = [
    {'node': node, 'height': structureCSV[node[1], node[0]], 'start': False, 'exit': False, 'xy-location': (node[0] + 2, node[1] + 2)} for node in nodes
]

nodeAttributes[0]['start'] = True
nodeAttributes[-1]['exit'] = True
nodeAttributes[-15]['exit'] = True
nodeAttributes[-27]['exit'] = True

edges = []
for i, node in enumerate(nodes):
    if node not in [(15, 14), (15, 4), (3, 14), (29, 14)]:
        edges.append((node, nodes[i + 1]))
    elif node == (15, 14):
        edges.append((node, nodes[i + 1]))
        edges.append((node, nodes[i + 11]))
        edges.append((node, nodes[i + 23]))

print(f'edges {edges}')

for i, attr in enumerate(nodeAttributes):
    G.add_node(nodes[i], **nodeAttributes[i])

for i, edge in enumerate(edges):
    if edge not in [((15, 14), (15, 13)), ((15, 14), (14, 14)), ((15, 14), (16, 14))]:
        G.add_edge(*edge, prob = 1.0)
    else:
        G.add_edge(*edge, prob = 1/3)

print("Nodes:")
print(G.nodes(data=True))

print("\nEdges:")
print(G.edges(data=True))

os.makedirs("structures", exist_ok=True)
with open("structures/zh_graph6LayerCross.pkl", "wb") as f:
    pickle.dump(G, f, protocol=pickle.HIGHEST_PROTOCOL)