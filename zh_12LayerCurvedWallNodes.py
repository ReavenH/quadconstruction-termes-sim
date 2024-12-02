import networkx as nx
import pickle
import os

G = nx.DiGraph()

# 添加二维坐标作为节点，并设置节点属性
nodes = [
    (11, 0),
    (11, 1),
    (11, 2),
    (11, 3),
    (11, 4),
    (11, 5),
    (11, 6),
    (11, 7),
    (11, 8),
    (11, 9),
    (11, 10),
    (11, 11),
    (11, 12),
    (11, 13),
    (11, 14),
    (11, 15),
    (11, 16),
    (11, 17),
    (11, 18),
    (11, 19),
    (11, 20),
    (11, 21),
    (11, 22),
    (11, 23)
]
nodeAttributes = [
    {'node': (11, 0),'height': 1, 'start': True, 'exit': False, 'xy-location': (13, 2), 'row-col-coordinates': (11, 0)},
    {'node': (11, 1),'height': 2, 'start': False, 'exit': False, 'xy-location': (13, 3), 'row-col-coordinates': (11, 1)},
    {'node': (11, 2),'height': 3, 'start': False, 'exit': False, 'xy-location': (13, 4), 'row-col-coordinates': (11, 2)},
    {'node': (11, 3),'height': 4, 'start': False, 'exit': False, 'xy-location': (13, 5), 'row-col-coordinates': (11, 3)},
    {'node': (11, 4),'height': 5, 'start': False, 'exit': False, 'xy-location': (13, 6), 'row-col-coordinates': (11, 4)},
    {'node': (11, 5),'height': 6, 'start': False, 'exit': False, 'xy-location': (13, 7), 'row-col-coordinates': (11, 5)},
    {'node': (11, 6),'height': 7, 'start': False, 'exit': False, 'xy-location': (13, 8), 'row-col-coordinates': (11, 6)},
    {'node': (11, 7),'height': 8, 'start': False, 'exit': False, 'xy-location': (13, 9), 'row-col-coordinates': (11, 7)},
    {'node': (11, 8),'height': 9, 'start': False, 'exit': False, 'xy-location': (13, 10), 'row-col-coordinates': (11, 8)},
    {'node': (11, 9),'height': 10, 'start': False, 'exit': False, 'xy-location': (13, 11), 'row-col-coordinates': (11, 9)},
    {'node': (11, 10),'height': 11, 'start': False, 'exit': False, 'xy-location': (13, 12), 'row-col-coordinates': (11, 10)},
    {'node': (11, 11),'height': 12, 'start': False, 'exit': False, 'xy-location': (13, 13), 'row-col-coordinates': (11, 11)},
    {'node': (11, 12),'height': 12, 'start': False, 'exit': False, 'xy-location': (13, 14), 'row-col-coordinates': (11, 12)},
    {'node': (11, 13),'height': 11, 'start': False, 'exit': False, 'xy-location': (13, 15), 'row-col-coordinates': (11, 13)},
    {'node': (11, 14),'height': 10, 'start': False, 'exit': False, 'xy-location': (13, 16), 'row-col-coordinates': (11, 14)},
    {'node': (11, 15),'height': 9, 'start': False, 'exit': False, 'xy-location': (13, 17), 'row-col-coordinates': (11, 15)},
    {'node': (11, 16),'height': 8, 'start': False, 'exit': False, 'xy-location': (13, 18), 'row-col-coordinates': (11, 16)},
    {'node': (11, 17),'height': 7, 'start': False, 'exit': False, 'xy-location': (13, 19), 'row-col-coordinates': (11, 17)},
    {'node': (11, 18),'height': 6, 'start': False, 'exit': False, 'xy-location': (13, 20), 'row-col-coordinates': (11, 18)},
    {'node': (11, 19),'height': 5, 'start': False, 'exit': False, 'xy-location': (13, 21), 'row-col-coordinates': (11, 19)},
    {'node': (11, 20),'height': 4, 'start': False, 'exit': False, 'xy-location': (13, 22), 'row-col-coordinates': (11, 20)},
    {'node': (11, 21),'height': 3, 'start': False, 'exit': False, 'xy-location': (13, 23), 'row-col-coordinates': (11, 21)},
    {'node': (11, 22),'height': 2, 'start': False, 'exit': False, 'xy-location': (13, 24), 'row-col-coordinates': (11, 22)},
    {'node': (11, 23),'height': 1, 'start': False, 'exit': True, 'xy-location': (13, 25), 'row-col-coordinates': (11, 23)}
]

for i, attr in enumerate(nodeAttributes):
    G.add_node(nodes[i], **nodeAttributes[i])

# 添加边并为每条边设置 'prob' 属性为 1，使空间相邻的点形成单向图
edges = [(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)]

# for edge in edges:
for edge in edges[:4]:
    G.add_edge(*edge, prob=1.0, tilt=0)  # 设置概率属性为 1
for edge in edges[4:10]:
    G.add_edge(*edge, prob=1.0, tilt=-25)  # 设置概率属性为 1
for edge in edges[10:]:
    G.add_edge(*edge, prob=1.0, tilt=25)  # 设置概率属性为 1


# 输出节点和边的信息
print("Nodes:")
print(G.nodes(data=True))

print("\nEdges:")
print(G.edges(data=True))

# 确保保存目录存在
os.makedirs("structures", exist_ok=True)

# 将创建的DiGraph保存为pkl文件
with open("structures/zh_graph12LayerCurvedWall2.pkl", "wb") as f:
    pickle.dump(G, f, protocol=pickle.HIGHEST_PROTOCOL)