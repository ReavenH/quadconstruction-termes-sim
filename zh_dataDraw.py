import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# 1. 加载五个 CSV 文件
file_paths = [
    "exp/processed/0_A.csv",
    "exp/processed/5_A.csv",
    "exp/processed/10_A.csv",
    "exp/processed/15_A.csv",
    "exp/processed/20_A.csv"
]

data_frames = []
for file in file_paths:
    df = pd.read_csv(file)
    df['source'] = os.path.basename(file)  # 添加文件来源列，仅保留文件名
    data_frames.append(df)

# 2. 合并所有数据
combined_data = pd.concat(data_frames)

# 3. 获取所有 Layers 和源文件
layers = np.sort(combined_data["Layer"].unique())[1:2]  # 正序排列 Layer
sources = combined_data["source"].unique()

# 4. 创建 12x1 的子图布局
fig, axes = plt.subplots(nrows=len(layers), ncols=1, figsize=(10, 3*len(layers)), sharex=True)

# 5. 遍历每个子图，从最下面的 Layer 开始画起
for i, layer in enumerate(layers):
    if len(layers) == 1:
        ax = axes
    else:
        ax = axes[i]  # 使用从下到上的顺序
    layer_data = combined_data[combined_data["Layer"] == layer]
    
    # 在该子图中为每个 CSV 文件画一条线
    for source in sources:
        source_data = layer_data[layer_data["source"] == source]
        
        # 提取序号和 TPin 数据
        indices = np.arange(len(source_data)) * 2 + i  # 从 Layer 1 开始，逐层交错横坐标
        means = source_data["mean_TPinSecurity"].values
        stds = source_data["std_TPinSecurity"].values
        
        # 绘制带误差棒的线
        ax.errorbar(
            x=indices, 
            y=means, 
            yerr=0 if len(layers) == 1 else stds, 
            fmt='-o', 
            alpha=0.7,  # 设置不透明度
            label=source.split('_')[0],
            capsize=0 if len(layers) == 1 else 5,
            linewidth = 2
        )
    ax.axhline(y=2, color='gray', linestyle='--', linewidth=1.75)
    # 子图设置
    ax.set_title(f"Layer {layer}")
    ax.grid(True, alpha=0.5)
    ax.set_xticks(np.arange(0, 21, 1))
    ax.set_ylim(1.75, 4.25)

# 6. 设置共享的 X 轴并设置字号
fig.text(0.5, 0.04, "Position of Block in Each Layer in Plan Graph", ha="center", fontsize=14)

# 7. 添加全局图例，确保显示
if len(layers) > 1:
    handles, labels = axes[0].get_legend_handles_labels()
else:
    handles, labels = axes.get_legend_handles_labels()
fig.legend(handles, labels, title="Incline Angle (Degree)", loc="upper right")
fig.suptitle("Number of T-pins Secured v.s. Expansion of Layer\n(Selected Layers)", fontsize = 16)
# 调整布局以确保图例显示
# plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()