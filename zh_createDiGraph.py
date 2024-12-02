import networkx as nx
import pickle
import os
import csv

# select nodes from py files.
# import zh_3layerLShapeNodes as n
import zh_5LayerTShapeNodes as n

# 创建一个有向图（DiGraph）
G = nx.DiGraph()

# 添加二维坐标作为节点，并设置节点属性
nodes = n.nodes
nodeAttributes = n.nodeAttributes

for i, attr in enumerate(nodeAttributes):
    G.add_node(nodes[i], **nodeAttributes[i])

# 添加边并为每条边设置 'prob' 属性为 1，使空间相邻的点形成单向图
edges = [(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)]

for edge in edges:
    G.add_edge(*edge, prob=1.0)  # 设置概率属性为 1

# for i, node in enumerate(nodes):
    

# 输出节点和边的信息
print("Nodes:")
print(G.nodes(data=True))

print("\nEdges:")
print(G.edges(data=True))

# 确保保存目录存在
os.makedirs("structures", exist_ok=True)

# 将创建的DiGraph保存为pkl文件
with open("structures/zh_graph5LayerTShape.pkl", "wb") as f:
    pickle.dump(G, f, protocol=pickle.HIGHEST_PROTOCOL)
