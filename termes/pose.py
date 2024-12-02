# -*- coding: utf-8 -*-
"""
Created on Sat Nov 24 18:11:36 2018

@author: nnapp
"""
from enum import Enum
import numpy as np


#   ^
#   |             N 
# Y |           W   E
#   ----->        S 
#     X


# Assume robot is facing norht so forward is +1 in the y dir

padding = 2

class heading(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
  

class Pose:
    '''
    Keeps the pose of TERMES type robot
    This is a grid version of 2D, with the height determined by the structure.
    This means that the position is 3D, but that the rotation is only the heading
    '''
    
    def __init__(self,pos=None,x=0,y=0,z=0,h=heading.NORTH):
    
        if not pos is None:
            if isinstance(pos,(list,tuple)):
                assert isinstance(pos,(list,tuple)), "'pos' needs to be list|tuple"
                assert len(pos) >= 2 and len(pos) <=3, "pos arbuments needs to be either [x,y]|[x,y,z]" 
                self.x=pos[0]
                self.y=pos[1]     
                self.z=0
                
                if len(pos) == 3:
                    self.z = pos[2] 
                    
                self.heading=h
            elif str(type(pos)) == str(Pose):
                self.x=pos.x
                self.y=pos.y
                self.z=pos.z

                self.heading=pos.heading
            else:
                assert False, "pos is of inconsistent type"
                
        else:
            self.x=x
            self.y=y
            self.z=z
            self.heading=h
        
        self.T=np.eye(3)
        self.t=np.array((self.x,self.y,1))
        self.T[0,2]=self.x
        self.T[1,2]=self.y
        if self.heading==heading.SOUTH:
            self.T[0,0]=-1
            self.T[1,1]=-1
        if self.heading==heading.WEST:
            self.T[0,0]=0
            self.T[1,1]=0
            self.T[0,1]=-1
            self.T[1,0]=1
        if self.heading==heading.EAST:
            self.T[0,0]=0
            self.T[1,1]=0
            self.T[0,1]=1
            self.T[1,0]=-1
            

    def __eq__(self,o):
        return self.x == o.x and self.y == o.y and self.z == o.z and self.heading == o.heading
        
    def __add__(self,o):
        temp = Pose(self)
        temp.add(o)
        return temp

    def __sub__(self,o):
        temp = Pose(self)
        temp.sub(o)
        return temp

    def inv(self):
        pass


    def add(self, rpose):
        
        '''
        Add a realtive pose. The coordinate fram from rpose is alligned to 
        the NORTH (+y) direction of the the previous pose. In global coordiantes 
        the rpose angle is (self.heading + rpose.heading)
        '''         
        
        assert isinstance(rpose,Pose)
        
        '''
        add the translation
        '''
        if self.heading ==heading.NORTH :
            dx=rpose.x
            dy=rpose.y                
        elif self.heading ==heading.EAST :
            dx=rpose.y
            dy=-rpose.x  
        elif self.heading ==heading.SOUTH :
            dx=-rpose.x
            dy=-rpose.y  
        elif self.heading ==heading.WEST :
            dx=-rpose.y
            dy=rpose.x  
        else:
            assert False, "Relative pose does not have a valid heading"
            
        self.x += dx
        self.y += dy
        
        
        '''
        then rotate to new heading
        '''
        self.heading=heading((self.heading.value + rpose.heading.value)%4)


    def sub(self, rpose):
        '''
        Subtract a realtive pose (i.e. figure out the pose that would have resulted 
        in the current pose if a relateiv motion of rpose occured.. The coordinate 
        frame from rpose is alligned to the NORTH (+y) direction of the the previous 
        pose. In global coordiantes the rpose angle is (self.heading + rpose.heading)
        '''         
        assert isinstance(rpose,Pose)
        
        self.heading=heading((self.heading.value - rpose.heading.value)%4)

        '''
        now reverse the tralation
        '''
        if self.heading==heading.NORTH:
            dx=-rpose.x
            dy=-rpose.y                
        elif self.heading==heading.EAST:
            dx=-rpose.y
            dy=rpose.x  
        elif self.heading==heading.SOUTH:
            dx=rpose.x
            dy=rpose.y  
        elif self.heading==heading.WEST:
            dx=rpose.y
            dy=-rpose.x  
        else:
            assert False, "Relative pose does not have a valid heading"
        
        
        
        self.x += dx
        self.y += dy
        
        '''
        rotate backward first
        '''
        

    def reverse(self):
        
        '''
        Negate the pose (rotate by PI and negate x and y)
        This is useful for subtracting relative posese using add
        '''
        
        self.x = -self.x
        self.y = -self.y
        
        self.heading=heading((-self.heading.value)%4)

    def __repr__(self):
        return '(%d,%d,%d)-%s'%(self.x,self.y,self.z,self.heading.name)      

    def toTuple(self):
        return (self.x,self.y,self.z,self.heading.value)

## Pose
## Paths
                  
#class block:
#    __init__(self,pose=None):
#        self.pose=p


