import networkx as nx
import pickle
import os

G = nx.DiGraph()

# 添加二维坐标作为节点，并设置节点属性
nodes = [
    (5, 0),
    (5, 1),
    (5, 2),
    (5, 3),
    (5, 4),
    (5, 5),
    (5, 6),
    (5, 7),
    (5, 8),
    (5, 9),
]
nodeAttributes = [
    {'node': (5, 0),'height': 1, 'start': True, 'exit': False, 'xy-location': (7, 2), 'row-col-coordinates': (5, 0)},
    {'node': (5, 1),'height': 2, 'start': False, 'exit': False, 'xy-location': (7, 3), 'row-col-coordinates': (5, 1)},
    {'node': (5, 2),'height': 3, 'start': False, 'exit': False, 'xy-location': (7, 4), 'row-col-coordinates': (5, 2)},
    {'node': (5, 3),'height': 4, 'start': False, 'exit': False, 'xy-location': (7, 5), 'row-col-coordinates': (5, 3)},
    {'node': (5, 4),'height': 5, 'start': False, 'exit': False, 'xy-location': (7, 6), 'row-col-coordinates': (5, 4)},
    {'node': (5, 5),'height': 5, 'start': False, 'exit': False, 'xy-location': (7, 7), 'row-col-coordinates': (5, 5)},
    {'node': (5, 6),'height': 4, 'start': False, 'exit': False, 'xy-location': (7, 8), 'row-col-coordinates': (5, 6)},
    {'node': (5, 7),'height': 3, 'start': False, 'exit': False, 'xy-location': (7, 9), 'row-col-coordinates': (5, 7)},
    {'node': (5, 8),'height': 2, 'start': False, 'exit': False, 'xy-location': (7, 10), 'row-col-coordinates': (5, 8)},
    {'node': (5, 9),'height': 1, 'start': False, 'exit': True, 'xy-location': (7, 11), 'row-col-coordinates': (5, 9)},
]

for i, attr in enumerate(nodeAttributes):
    G.add_node(nodes[i], **nodeAttributes[i])

# 添加边并为每条边设置 'prob' 属性为 1，使空间相邻的点形成单向图
edges = [(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)]

for edge in edges:
    G.add_edge(*edge, prob=1.0, tilt=-20)  # 设置概率属性为 1

# for i, node in enumerate(nodes):
    

# 输出节点和边的信息
print("Nodes:")
print(G.nodes(data=True))

print("\nEdges:")
print(G.edges(data=True))

# 确保保存目录存在
os.makedirs("structures", exist_ok=True)

# 将创建的DiGraph保存为pkl文件
with open("structures/zh_graph5LayerCurvedWall.pkl", "wb") as f:
    pickle.dump(G, f, protocol=pickle.HIGHEST_PROTOCOL)