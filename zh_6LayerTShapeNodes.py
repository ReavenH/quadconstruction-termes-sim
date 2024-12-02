import numpy as np
import networkx as nx
import os
import pickle

G = nx.DiGraph()

structureCSV = np.genfromtxt(f'structures/zh_6LayerTShape.csv', delimiter=',')

nodes = [
    (8, 15),
    (8, 14),
    (8, 13),
    (8, 12),
    (8, 11),
    (8, 10),
    (8, 9),
    (8, 8),
    (8, 7),
    (8, 6),
    (8, 5),
    (8, 4),
    (8, 3),
    (8, 2),
    (8, 1),

    (7, 1),
    (6, 1),
    (5, 1),
    (4, 1),
    (3, 1),
    (2, 1),
    (1, 1),

    (9, 1),
    (10, 1),
    (11, 1),
    (12, 1),
    (13, 1),
    (14, 1),
    (15, 1),
    (16, 1)
]

nodes = [(x + 3, y + 3) for x, y in nodes]

nodeAttributes = [
    {'node': node, 'height': structureCSV[node[1], node[0]], 'start': False, 'exit': False, 'xy-location': (node[0] + 2, node[1] + 2)} for node in nodes
]

nodeAttributes[0]['start'] = True
nodeAttributes[-9]['exit'] = True
nodeAttributes[-1]['exit'] = True

edges = []
for i, node in enumerate(nodes):
    if node not in [(8 + 3, 1 + 3), (1 + 3, 1 + 3), (16 + 3, 1 + 3)]:
        edges.append((node, nodes[i + 1]))
    elif node == (8 + 3, 1 + 3):
        edges.append((node, (7 + 3, 1 + 3)))
        edges.append((node, (9 + 3, 1 + 3)))

'''
edges = [
    (nodes[i], nodes[i + 1]) for i in range(14)
]

edges.append((nodes[14], nodes[15]))

edges.append(((nodes[i + 15], nodes[i + 16]) for i in range(6)))

edges.append((nodes[14], nodes[22]))

edges.append(((nodes[i + 22], nodes[i + 23]) for i in range(7)))
'''

print(f'edges {edges}')

for i, attr in enumerate(nodeAttributes):
    G.add_node(nodes[i], **nodeAttributes[i])

for edge in edges:
    if edge == ((8 + 3, 1 + 3), (7 + 3, 1 + 3)) or edge == ((8 + 3, 1 + 3), (9 + 3, 1 + 3)): 
        G.add_edge(*edge, prob=0.5)
    else:
        G.add_edge(*edge, prob=1.0)


print("Nodes:")
print(G.nodes(data=True))

print("\nEdges:")
print(G.edges(data=True))

os.makedirs("structures", exist_ok=True)
with open("structures/zh_graph6LayerTShape.pkl", "wb") as f:
    pickle.dump(G, f, protocol=pickle.HIGHEST_PROTOCOL)