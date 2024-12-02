# -*- coding: utf-8 -*-
"""
Created on Sat Nov 24 18:39:29 2018
@author: nnapp

Classes for TERMES simulation

Simulation of Termes moving in a partailly built structure 
and running a SLAM like algorithm to place a brick
"""



import pickle
import csv
#Relative import from base so types match the ones from external programs
from termes.pose import Pose, heading
from termes.agent import ACTIONS,Agent
from random import randint
import numpy as np
import os


#   ^
#   |             N 
# Y |           W  E
#   ----->        S 
#     X


# Assume robot is facing norht so forward is +1 in the y dir
            
class Structure:
    
    def __init__(self):
        self.padding=0
        self.worldArray=[]
        self.rel_pose=False
        self.rows=None
         
    def addBlock(self,b):
        pass
    
    def removeBlock(self,b):        
       pass
    
    
    def __getitem__(self,pose : Pose):
    
        #rows=len(self.worldArray)        
        return self.worldArray[self.rows-pose.y-1][pose.x]
    
    def __setitem__(self,pose,val):
        self.worldArray[self.rows-pose.y-1][pose.x] = val
    
        
    def read(self,fname,padding=2):
        self.padding=padding
        assert len(fname.split('.')) >= 2, 'Cannot tell format from extension'
        if fname.split('.')[-1] == 'idx':
            with open(fname,'r') as sfile:
                dims=sfile.readline()
                xdim,ydim = list(map(int,dims.split()))
                print(dims)
                self.worldArray=[]
                i=0
                for x in range(xdim+padding*2):
                    self.worldArray.append([0]*(ydim + padding*2))
                
                for l in sfile:
                    #print(l)
                    i=i+1
                    xpos,ypos,h=list(map(int,l.split()))
                    self.worldArray[xpos+padding][ypos+padding]=h
                    
                    
                    
        elif fname.split('.')[-1] == 'pkl':
            with open(fname,'rb') as sfile:
               raw_array=pickle.load(sfile)
               cols=len(raw_array[0])
               self.worldArray=[]
               for _ in range(padding):
                   self.worldArray.append([0]*(cols + 2*padding))
               for row in raw_array:
                   self.worldArray.append([0]*padding 
                                          + list(int(i) for i in row) 
                                          + [0]*padding)
               for _ in range(padding):
                   self.worldArray.append([0]*(cols + 2*padding))
               
        elif fname.split('.')[-1] == 'csv':
            with open(fname,'r',encoding='gbk') as sfile:
               reader = csv.reader(sfile)
               world_row=[0]*padding
               c_idx=padding
               r_idx=padding
               for line in reader:
                    for c in line:
                        if c == 's' or c == 'S':
                            world_row.append(1)
                            print(f'Start @ {c_idx} {r_idx}')
                        elif c == 'x' or c == 'X':
                            world_row.append(1)
                            print(f'Exit @ {c_idx} {r_idx}')
                        else:
                            world_row.append(int(c))
                        c_idx += 1
                    for _ in range(padding):
                        world_row.append(0)
                    self.worldArray.append(world_row)
                    world_row = [0]*padding
                    c_idx=padding
                    r_idx += 1
            pad_array=[]
            for _ in range(padding):
                pad_array.append([0]*len(self.worldArray[0]))
                self.worldArray.append([0]*len(self.worldArray[0]))
            self.worldArray = pad_array +self.worldArray
            self.worldArray.reverse() #for structure something messed up

                
               #self.worldArray=pickle.load(sfile)
        elif fname.split('.')[-1] == '2da':
            with open(fname,'r') as sfile:
                self.worldArray=[]
                world_row=[0]*padding
                c_idx=padding
                r_idx=padding
                for line in sfile:
                    for c in line.split():
                        if c == 's' or c == 'S':
                            world_row.append(1)
                            print(f'Start @ {c_idx} {r_idx}')
                        elif c == 'x' or c == 'X':
                            world_row.append(1)
                            print(f'Exit @ {c_idx} {r_idx}')
                        else:
                            world_row.append(int(c))
                        c_idx += 1
                    for _ in range(padding):
                        world_row.append(0)
                    self.worldArray.append(world_row)
                    world_row = [0]*padding
                    c_idx=padding
                    r_idx += 1
            pad_array=[]
            for _ in range(padding):
                pad_array.append([0]*len(self.worldArray[0]))
                self.worldArray.append([0]*len(self.worldArray[0]))
            self.worldArray = pad_array +self.worldArray
    
        self.rows=len(self.worldArray) #Store size of array   
        #self.worldArray = np.array(self.worldArray)
    
    def c_array(self):     
       
        return list(list( str(x) for x in rows ) for rows in self.worldArray)      
            
    
    def show(self, pose=None):
			#Todo 
        
        # added by Z. Huang, clear the terminal prints.
        # os.system('clear')
        rows=len(self.worldArray)
        cols=len(self.worldArray[0])
        
        
        if not pose is None:
            pshow='*'
            if pose.heading.value == heading.NORTH.value:
                pshow='^'
            elif pose.heading.value == heading.EAST.value:
                pshow='>'
            elif pose.heading.value == heading.WEST.value:
                pshow='<'
            elif pose.heading.value == heading.SOUTH.value:
                pshow='v'


        if pose is None:
            
            for r in range(rows):
                print(('{}'*cols).format(*self.worldArray[r]))
                

        else:
            
            for r in range(rows):

                if r == (rows-pose.y-1):
                    rshow=self.worldArray[r].copy()
                    rshow[pose.x]=pshow
                else:
                    rshow = self.worldArray[r]
                    
                print(('{}'*cols).format(*rshow))
            
    def relfun(self,o):
        me=o[0]
        return tuple(min(2, max(-2,x-me)) for x in o)
            
    def obs (self, p:Pose):        
        '''
        Not very efficient, creates lots of pose classes       
        '''
        #hold values of observations froward left backward right
        rp=None
        
        # F, R, B, L, FL, FR, BR, BL, FF
        if p.heading.value == heading.NORTH.value:
            # rp=[[0,1],[1,0],[0,-1],[-1,0]]
            rp=[[0,1],[1,0],[0,-1],[-1,0],[-1,1],[1,1],[1,-1],[-1,-1],[0, 2]]
        elif p.heading.value == heading.EAST.value:
            # rp=[[1,0],[0,-1],[-1,0],[0,1]]
            rp=[[1,0],[0,-1],[-1,0],[0,1],[1,1],[1,-1],[-1,-1],[-1,1],[2, 0]]
        elif p.heading.value == heading.SOUTH.value:
            # rp=[[0,-1],[-1,0],[0,1],[1,0]]
            rp=[[0,-1],[-1,0],[0,1],[1,0],[1,-1],[-1,-1],[-1,1],[1,1],[0, -2]]
        elif p.heading.value == heading.WEST.value:
            # rp=[[-1,0],[0,1],[1,0],[0,-1]]
            rp=[[-1,0],[0,1],[1,0],[0,-1],[-1,-1],[-1,1],[1,1],[1,-1], [-2, 0]]
       
        tmpPose=Pose(p)
        o=[self[p]]
        for r in rp:
            xn=p.x + r[0]
            if (xn < len(self.worldArray[0])) and (xn >= 0):
                tmpPose.x=xn
                
            yn=p.y + r[1]
            if (yn < len(self.worldArray)) and (yn >= 0):
                tmpPose.y=yn
                
            o.append(self[tmpPose])   
            
        if self.rel_pose:
            return self.relfun(o)
        else:
            return o


    def motion_check(self,pi: Pose , pf: Pose) -> bool:
        if pi.x<0 or pi.y<0 or pf.x<0 or pf.y<0:
            return False
        elif pi.x >= len(self.worldArray[0]) or pf.x >= len(self.worldArray[0]):
            return False
        elif pi.y >= len(self.worldArray) or pf.y >= len(self.worldArray):
            return False
        elif abs(self[pi]-self[pf])>1:
            return False
        else:
            return True
 
    def random_pose(self):
        x=randint(0,len(self.worldArray[0])-1)
        y=randint(0,len(self.worldArray)-1)
        h=randint(0,3)
        p=Pose([x,len(self.worldArray)-1-y],h=heading(h))
        z=self[p]
        p.z=z
        return p
    

class World:
    '''
    Class to wrap structure and agents
    TODO:
    The spatial, and temporal interactions between agetns are modeled here.
    Agents, get sensor readings and time-slots to exectue actions.
    '''
        
    def __init__(self,num_agents=1,structure=None, init_pose=Pose()):
        self.agents=[]
        for idx in range(num_agents):
            self.agents.append(Agent(pose=init_pose, ID=idx))
        if structure is None:            
            self.struct=Structure()
            self.agent=Agent(pose=init_pose)
        else:
            self.struct=structure            
            
    def obs(self,p):
        '''
        Call observation function from structure
        * Do collision checking here
        '''             
  
        
        return self.struct.obs(p)

    def path_check(self, pose_list):
         assert len(pose_list) >=2, 'A path needs to have 2 or more poses'
         assert False, 'path-check, Not yet implemented'        

    def move(self,u,p):
        '''
        compute next pose and update it if it can be applied
        '''
        assert u in ACTIONS
                
        new_pose = Pose(p)    
        relpose=None
        
        if u== 'l':
            relpose=Pose([0,0],h=heading.WEST)    
        if u == 'r':
            relpose=Pose([0,0],h=heading.EAST)
        if u == 'f':
            relpose=Pose([0,1])
        if u == 'u':
            relpose=Pose([0,0])
        if u == 'p':
            relpose=Pose([0,0])
                            
        assert not relpose is None, 'Motion somehow failed to produce a relpose'
                
        new_pose.add(relpose)
        
        if self.struct.motion_check(p,new_pose):
            new_pose.z =self.struct[new_pose]
            return new_pose
        else:
            return p
            print("Can't move!")
        #print(self.pose)
    
    def _heading_to_char(self,h):
        if h.value == heading.NORTH.value:
            return '^'
        elif h.value == heading.EAST.value:
            return '>'
        elif h.value == heading.WEST.value:
            return '<'
        elif h.value == heading.SOUTH.value:
            return 'v'
    
    def show(self):
        chars = self.struct.c_array()
                
        rows=len(self.struct.worldArray)
        
        for a in self.agents:
            col = a.pose.x
            row = rows - a.pose.y -1
            chars[row][col] = self._heading_to_char(a.pose.heading)

        # added by Z. Huang, to clear the terminal.
        os.system('cls')

        print(sum(a.my_time for a in self.agents))
        for c_row in chars:
            print(''.join(c_row))

