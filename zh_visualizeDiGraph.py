import networkx as nx
import plotly.graph_objects as go
import pickle

# 从文件中读取有向图
# with open('structures/bfd_output_graph_Castle_opt_10_100.pkl', 'rb') as fh: 
# with open('structures/zh_graph5LayerWall.pkl', 'rb') as fh: 
# with open('structures/zh_graph3LayerLShape.pkl', 'rb') as fh:
# with open('structures/bfd_plan_graph_25.pkl', 'rb') as fh: 
with open('structures\zh_graph12LayerCurvedWall.pkl', 'rb') as fh:
    G = pickle.load(fh)

# 直接使用节点的 (x, y) 作为实际坐标
pos = {}  # 存储节点的坐标
for i, loc in G.nodes(data=True):
    # 假设每个节点的数据中包含 'x' 和 'y' 坐标
    print('i: {} | LOC: {}'.format(i, loc))
    pos[i] = i  # 将节点的 (x, y) 坐标添加到 pos 中

# 提取边的坐标，绘制边线
edge_x = []  # 用于存储边的 x 坐标
edge_y = []  # 用于存储边的 y 坐标
arrow_annotations = []  # 用于存储箭头的 annotations
prob_annotations = []  # 用于存储边的 'prob' 值标注

for edge in G.edges():
    x0, y0 = pos[edge[0]]  # 获取边的起点坐标
    x1, y1 = pos[edge[1]]  # 获取边的终点坐标
    edge_x.append(x0)  # 添加起点的 x 坐标
    edge_x.append(x1)  # 添加终点的 x 坐标
    edge_x.append(None)  # 添加 None 以在绘制时断开连续边
    edge_y.append(y0)  # 添加起点的 y 坐标
    edge_y.append(y1)  # 添加终点的 y 坐标
    edge_y.append(None)  # 同样添加 None 以断开边
    
    # 创建箭头：通过 annotation 的方式为每条边添加箭头
    arrow_annotations.append(
        dict(
            ax=x0, ay=y0,  # 箭头的起点坐标
            x=x1, y=y1,    # 箭头的终点坐标
            xref='x', yref='y',
            axref='x', ayref='y',
            showarrow=True,
            arrowhead=3,  # 设置箭头样式
            arrowsize=3,  # 设置箭头大小
            arrowwidth=1,  # 设置箭头线宽度
            arrowcolor='gray'  # 设置箭头颜色为灰色
        )
    )

     # 提取并标注边的 'prob' 概率值
    # prob_value = edge[2].get('prob', 0)  # 获取边的 'prob' 值，默认值为 0
    prob_value = G.edges[edge]['prob']
    tilt_value = G.edges[edge]['tilt']
    print("Edge: {} | Prob Value: {} | Tilt: {}".format(edge, prob_value, tilt_value))
    prob_x = (x0 + x1) / 2  # 计算边的中间位置的 x 坐标
    prob_y = (y0 + y1) / 2  # 计算边的中间位置的 y 坐标
    
    # 为每条边的 'prob' 添加标注
    prob_annotations.append(
        dict(
            x=prob_x, y=prob_y,  # 概率值显示的位置
            xref='x', yref='y',
            # text=f'{prob_value:.2f}',  # 显示概率值，保留两位小数
            text=f'{tilt_value:.2f}',
            showarrow=False,  # 不显示箭头
            font=dict(size=10, color='black'),  # 设置字体大小和颜色
            bgcolor='rgba(255, 255, 255, 0.7)',  # 背景颜色，带透明度
            bordercolor='black',  # 边框颜色
            borderwidth=1,  # 边框宽度
            borderpad=2  # 边框与文字的间距
        )
    )

# 绘制边的 trace（用于绘制线条）
edge_trace = go.Scatter(
    x=edge_x,  # x 坐标列表
    y=edge_y,  # y 坐标列表
    line=dict(width=1, color='gray'),  # 线条宽度和颜色
    hoverinfo='none',  # 关闭悬停显示的信息
    mode='lines'  # 绘制线条模式
)

# 提取节点的位置和标签，准备绘制节点
node_x = []  # 用于存储节点的 x 坐标
node_y = []  # 用于存储节点的 y 坐标
node_text = []  # 用于存储节点的标签

for node in G.nodes():
    x, y = pos[node]  # 获取每个节点的 x 和 y 坐标
    node_x.append(x)  # 添加到 x 坐标列表中
    node_y.append(y)  # 添加到 y 坐标列表中
    node_text.append(str(node))  # 将节点名称作为标签存储

# 绘制节点的 trace（用于绘制散点图）
node_trace = go.Scatter(
    x=node_x,  # 节点的 x 坐标
    y=node_y,  # 节点的 y 坐标
    mode='markers+text',  # 绘制节点和文本
    text=node_text,  # 节点的标签
    textposition="bottom center",  # 标签位置：节点下方
    marker=dict(size=20, color='lightblue'),  # 节点大小和颜色
)

# 创建图形对象并加入箭头注释
fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    showlegend=False,  # 不显示图例
                    hovermode='closest',  # 悬停时显示最近的点
                    margin=dict(b=0, l=0, r=0, t=0),  # 边距
                    xaxis=dict(showgrid=False, zeroline=False),  # 隐藏 x 轴网格线和零线
                    yaxis=dict(showgrid=False, zeroline=False),  # 隐藏 y 轴网格线和零线
                    annotations=arrow_annotations + prob_annotations  # 添加箭头和概率值标注
                ))

# 显示图形
fig.show()
