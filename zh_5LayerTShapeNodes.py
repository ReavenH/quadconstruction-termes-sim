import numpy as np

structureCSV = np.genfromtxt(f'structures/zh_5LayerTShape.csv', delimiter=',')

nodes = [(0, 3), 
         (1, 3), 
         (2, 3), 
         (3, 3), 
         (4, 3), 
         (5, 3), 
         (5, 4), 
         (5, 5), 
         (5, 6), 
         (5, 7), 
         (5, 8), 
         (5, 9), 
         (6, 9), 
         (6, 8), 
         (6, 7), 
         (6, 6), 
         (6, 5), 
         (6, 4),
         (6, 3),
         (7, 3), 
         (8, 3), 
         (9, 3), 
         (10, 3), 
         (11, 3)]

nodeAttributes = [
    {'node': node, 'height': structureCSV[node[1], node[0]], 'start': False, 'exit': False, 'xy-location': (node[0] + 2, node[1] + 2)} for node in nodes
]

nodeAttributes[0]['start'] = True
nodeAttributes[-1]['exit'] = True

# print(nodeAttributes)

