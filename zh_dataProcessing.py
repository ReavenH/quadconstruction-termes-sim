import pandas as pd
import glob
import os

# 定义文件夹路径和文件名模式
folder_path = "exp/"
file_pattern = "15_A_*.csv"
file_list = glob.glob(os.path.join(folder_path, file_pattern))
savePath = f"exp/processed/15_A.csv"

# 存储所有文件的数据
data_frames = []

# 遍历文件列表并读取每个文件
for file in file_list:
    df = pd.read_csv(file)
    # 按照 'Layer' 列排序，不改变组内顺序
    df_sorted = df.sort_values(by=["Layer"], kind="stable")
    # 添加到列表
    data_frames.append(df_sorted)

# 将所有文件的 `TPinSecurity` 和 `overlapAreaPercentage` 按对应位置分别合并
tpinsecurity_data = pd.concat([df["TPinSecurity"] for df in data_frames], axis=1)
overlap_area_data = pd.concat([df["overlapAreaPercentage"] for df in data_frames], axis=1)

# 计算均值和标准差
mean_tpinsecurity = tpinsecurity_data.mean(axis=1)
std_tpinsecurity = tpinsecurity_data.std(axis=1)
mean_overlap_area = overlap_area_data.mean(axis=1)
std_overlap_area = overlap_area_data.std(axis=1)

# 将结果存入一个新的 DataFrame
result_df = data_frames[0][["Layer"]].copy()
result_df["mean_TPinSecurity"] = mean_tpinsecurity
result_df["std_TPinSecurity"] = std_tpinsecurity
result_df["mean_overlapAreaPercentage"] = mean_overlap_area
result_df["std_overlapAreaPercentage"] = std_overlap_area

# 保存结果为 CSV 文件
result_df.to_csv(savePath, index=False)
print("Summary results saved to {}".format(savePath))
