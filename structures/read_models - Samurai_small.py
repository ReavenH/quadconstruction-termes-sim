# -*- coding: utf-8 -*-
"""
Created on Wed May 31 06:56:25 2023

@author: nen38
"""
import cv2
import numpy as np
import csv
from matplotlib import pyplot as plt
from bfd import exitsExpending, history_nodes, history_deque, make_graph_plan
import pickle


FNAME_BASE='bfd_output'

#CSV_NAME='Height_map-Compiles.csv'
CSV_NAME='Height_map.csv'

cap_csv=[]
with open(CSV_NAME,'r') as fh:
    reader = csv.reader(fh)
    for row in reader:
        cap_csv.append(list(int(i) for i in row))
plt.close() 
plt.imshow(cap_csv)
plt.gca().invert_yaxis()
 
exits=((10,2),(2,6),); #compiles
starts=((28,0),);

for e in exits:
    plt.plot((e[1],),(e[0],),'ro')
    
for e in starts:
    plt.plot((e[1],),(e[0],),'rx')
    
ep = exitsExpending(cap_csv, starts, exits) 
ep.use_spanning_tree = True
res = ep.expending()

plan_graph=make_graph_plan(res)

for n in plan_graph.nodes:
    if n in starts:
        plan_graph.nodes[n]['start']=True
    if n in exits:
        plan_graph.nodes[n]['exit']=True
        
with open(FNAME_BASE + '_graph.pkl', 'wb') as fh:
    pickle.dump(plan_graph,fh)
    
with open(FNAME_BASE + '_struct.pkl', 'wb') as fh:
    pickle.dump(cap_csv,fh)


def write_res(res,fname='file.csv'):
    with open(fname,'w',newline='') as fh:
        writer = csv.writer(fh)
        for row in res:
            writer.writerow(row)
            
def read_res(fname='Samurai_small.csv'):
    res=[]  
    with open(fname,'r') as fh:
        reader = csv.reader(fh)
        for row in reader:
            print(f'reading row {row}')
            x,y,z,up,dp,lp,rp = row
            res.append((int(x),int(y),int(z),float(up),float(dp),float(lp),float(rp)))
    return res  