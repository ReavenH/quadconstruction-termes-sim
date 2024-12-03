import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

filePath = f'hp_agentsSteps.csv'
data = pd.read_csv(filePath)
dataIWall = data['custom(average)'][0:20].to_numpy().reshape(-1, 2)
dataTWall = data['custom4'][0:20]
dataTWall = np.array([np.mean(np.array(row.split(",")).astype('int')) if isinstance(row, str) else row for row in dataTWall]).reshape(-1, 2)
dataXWall = data['custom6'][0:20]
dataXWall = np.array([np.mean(np.array(row.split(",")).astype('int')) if isinstance(row, str) else row for row in dataXWall]).reshape(-1, 2)
dataCWall = data['custom10(average)'][0:20].to_numpy().reshape(-1, 2)

dataCWall[:, 0] = dataCWall[:, 0] / dataCWall[0, 0]
dataIWall[:, 0] = dataIWall[:, 0] / dataIWall[0, 0]
dataTWall[:, 0] = dataTWall[:, 0] / dataTWall[0, 0]
dataXWall[:, 0] = dataXWall[:, 0] / dataXWall[0, 0]

fig1, ax1 = plt.subplots(figsize = (10, 6))
ax1.plot(dataCWall[:, 0], label='C Wall', alpha = 0.7, linewidth = 2)
ax1.plot(dataIWall[:, 0], label='I Wall', alpha = 0.7, linewidth = 2)
ax1.plot(dataTWall[:, 0], label='T Wall', alpha = 0.7, linewidth = 2)
ax1.plot(dataXWall[:, 0], label='X Wall', alpha = 0.7, linewidth = 2)
ax1.set_title('Normalized Average Time Step to Complete v.s. Number of Agents', fontsize = 15)
ax1.legend(fontsize = 15)
ax1.set_xlabel('Number of Agents', fontsize = 15)
ax1.set_ylabel('Normalized Average Time Step', fontsize = 15)
ax1.set_xticks(np.arange(0, len(dataCWall), 1))
ax1.set_xticklabels(np.arange(1, len(dataCWall) + 1, 1))
ax1.tick_params(axis='y', labelsize=12)
ax1.tick_params(axis='x', labelsize=12)
ax1.grid(True)

fig2, ax2 = plt.subplots(figsize = (10, 6))
ax2.plot(dataCWall[:, 1], label='C Wall', alpha = 0.7, linewidth = 2)
ax2.plot(dataIWall[:, 1], label='I Wall', alpha = 0.7, linewidth = 2)
ax2.plot(dataTWall[:, 1], label='T Wall', alpha = 0.7, linewidth = 2)
ax2.plot(dataXWall[:, 1], label='X Wall', alpha = 0.7, linewidth = 2)
ax2.set_title('Average Waiting Steps to Complete v.s. Number of Agents', fontsize = 15)
ax2.legend(fontsize = 15)
ax2.set_xlabel('Number of Agents', fontsize = 15)
ax2.set_ylabel('Average Waiting Steps', fontsize = 15)
ax2.set_xticks(np.arange(0, len(dataCWall), 1))
ax2.set_xticklabels(np.arange(1, len(dataCWall) + 1, 1))
ax2.tick_params(axis='y', labelsize=12)
ax2.tick_params(axis='x', labelsize=12)
ax2.grid(True)

plt.show()