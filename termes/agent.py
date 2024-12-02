# -*- coding: utf-8 -*-
"""
@author: nnapp

Classes for TERMES simulation

Simulation of Termes moving in a partailly built structure 
and running a SLAM like algorithm to place a brick
"""

#__name__='agent'


from .pose import Pose, heading
import networkx as nx
import random

#from world import World

#__name__='termes.agent'

'''
List of possible actions that a robot has
FForward
turn LLeft
turn RRight
pick UUp a brick
PPlace a brick
'''
ACTIONS=['f','l','r','u','p']

PROB_ON = True
MAX_ELEM = False


class Observation: 
    # def __init__(self,obs=[0,0,0,0,0],rel_height=False,detect_robot=False):
    def __init__(self,obs=[0,0,0,0,0,0,0,0,0],rel_height=False,detect_robot=False):
        self.relative_height=rel_height
        self.detect_robot=False
        # self.heights=obs # [ne,N,E,S,W] from local view
        self.heights=obs # [ne,N,E,S,W,NE,SE,SW,NW] from local view
        self.height=obs[0]
        
    def __getitem__(self,heading):
        return self.heights[heading.value + 1]

class Agent:
    
    def __init__(self,pose=None,brick=False,world=None,time=0,plan_graph=None,ID = None):
        if pose is None:
            self.pose = Pose()
        else:
            self.pose = pose
        self.has_brick=brick
        self.my_world=world
        self.my_time=time
        self.on_structure=False
        self.start_loc = None
        self.action_buffer=''
        
        self.trip_cnt=0
        self.trip_cnt_wasted=0
        self.trip_cnt_productive=0
        
        self.max_set=None     #Set this when initializing elements
        self.max_visited=set()#Set this 
        
        self.comp_time=0

        self.ID = ID
        
        if not plan_graph is None:
            self.set_plan_graph(plan_graph)

    def _init_plan_graph(self):
        for n in self.plan_graph.nodes:
            if self.plan_graph.nodes[n]['start']:
                self.start_loc=self.plan_graph.nodes[n]['xy-location']
        self._parrent_digraph=nx.reverse(self.plan_graph)                
    
    
    ##Add comparson on time so you can use a heapq to get the next agent
    def __lt__(self,o):
        return self.my_time < o.my_time

    def __leq__(self,o):
        return self.my_time <= o.my_time

    def __gt__(self,o):
        return self.my_time > o.my_time

    def __geq__(self,o):
        return self.my_time >= o.my_time

    def __eq__(self,o):
        return self.my_time == o.my_time
    
    def _next_to_start(self):
        if self.start_loc is None:
            return False
        else:
            if self.pose.x == self.start_loc[0] and abs(self.pose.y - self.start_loc[1]) == 1:
                return True
            elif self.pose.y == self.start_loc[1] and abs(self.pose.x - self.start_loc[0]) == 1:
                return True
            else:
                return False
    
    def set_plan_graph(self,plan_graph):
        self.plan_graph = nx.DiGraph()

        node_trans={}
        for n in plan_graph.nodes:
            n_dict=plan_graph.nodes[n]
            n_dict['row-col-coordinates']=n
            xy=n_dict['xy-location']
            node_trans[n]=xy
            self.plan_graph.add_node(xy,**n_dict)
        for u,v in plan_graph.edges:
            e_dict=plan_graph.edges[u,v]
            self.plan_graph.add_edge(node_trans[u],node_trans[v],**e_dict)
           
        #now fix up graph    
        to_add=[]
        for n in self.plan_graph.nodes:
            if self.plan_graph.nodes[n]['start']:
                self.start_loc=n
            elif self.plan_graph.nodes[n]['exit']:
                e_nbrs=[]
                for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):
                    e_nbr=(n[0]+dx,n[1]+dy)
                    if not e_nbr in self.plan_graph.nodes:
                        e_nbrs.append(e_nbr)
                to_add.append((n,tuple(e_nbrs)))
                
        for n, e_nbrs in to_add:
            for e_nbr in e_nbrs:        
                self.plan_graph.add_node(e_nbr)
                self.plan_graph.nodes[e_nbr]['height']=0
                self.plan_graph.nodes[e_nbr]['start']=False
                self.plan_graph.nodes[e_nbr]['exit']=False
                self.plan_graph.nodes[e_nbr]['xy-location']=e_nbr
                self.plan_graph.nodes[e_nbr]['row-col-coordinates']=(-1,-1)
             
                self.plan_graph.add_edge(n,e_nbr)
                self.plan_graph.edges[n,e_nbr]['prob']=1/len(e_nbrs)
                
        self._parent_digraph=nx.reverse(self.plan_graph)                

    def dx_dy_to_turn(self,dp):
        dx,dy= dp
        if dx == 1:
            if self.pose.heading == heading.EAST:
                return ''
            elif self.pose.heading == heading.SOUTH:
                return 'l'
            elif self.pose.heading == heading.WEST:
                return 'll'
            elif self.pose.heading == heading.NORTH:
                return 'r'
            else:
                assert False, f'Should not get here: dx={dx}, dy={dy}.'
        elif dx == -1:
            if self.pose.heading == heading.EAST:
                return 'rr'
            elif self.pose.heading == heading.SOUTH:
                return 'r'
            elif self.pose.heading == heading.WEST:
                return ''
            elif self.pose.heading == heading.NORTH:
                return 'l'
            else:
                assert False, f'Should not get here: dx={dx}, dy={dy}.'
        elif dy == 1:
            if self.pose.heading == heading.EAST:
                return 'l'
            elif self.pose.heading == heading.SOUTH:
                return 'll'
            elif self.pose.heading == heading.WEST:
                return 'r'
            elif self.pose.heading == heading.NORTH:
                return ''
            else:
                assert False, f'Should not get here: dx={dx}, dy={dy}.'
        elif dy == -1:
            if self.pose.heading == heading.EAST:
                return 'r'
            elif self.pose.heading == heading.SOUTH:
                return ''
            elif self.pose.heading == heading.WEST:
                return 'l'
            elif self.pose.heading == heading.NORTH:
                return 'rr'
            else:
                assert False, f'Should not get here: dx={dx}, dy={dy}.'
        else:
            assert False, f'Not a valid relative pose. dx={dx}, dy={dy}.'
    
    def pick_actions(self,observation, mode = '0', debug_print=False, agents = None):
            #check building
            #do_motion
        self.my_time += 1
            
        # deal with congestion waiting.
        if agents != None and self.my_time > 0:
            #use this to get the rel-dx-dy from from the heading
            #This could be nicer  
            dxdy=None
            if self.pose.heading.value == heading.NORTH.value:
                dxdy=((0,1),(1,0),(0,-1),(-1,0))  # order: N, E, S, W in the coordinate frame of robot.
            elif self.pose.heading.value == heading.EAST.value:
                dxdy=((1,0),(0,-1),(-1,0),(0,1))  # order: N, E, S, W in the coordinate frame of robot.
            elif self.pose.heading.value == heading.SOUTH.value:
                dxdy=((0,-1),(-1,0),(0,1),(1,0))  # order: N, E, S, W in the coordinate frame of robot.
            elif self.pose.heading.value == heading.WEST.value:
                dxdy=((-1,0),(0,1),(1,0),(0,-1))  # order: N, E, S, W in the coordinate frame of robot.

            for a in agents:
                if a.ID != self.ID:
                    if self.pose.x + dxdy[0][0] == a.pose.x and self.pose.y + dxdy[0][1] == a.pose.y:
                        print(f'Agent {self.ID} at {self.pose} is waiting for Agent {a.ID} at {a.pose}.')
                        return ''
            
        if (observation.heights[0] == 0) and not self.on_structure and mode == '0':
            '''
            Behavior on Ground
            1) First check if next to start and then hop on
            2) If not next to start then wall follow CCW
            '''
            #if self.pose
            
            if self._next_to_start():
            
                dx=self.start_loc[0] - self.pose.x 
                dy=self.start_loc[1] - self.pose.y 
                
                u = self.dx_dy_to_turn((dx,dy))
                
                if not u == '': #still need to turn
                    return u
                else:
                    #heading in the right direction
                    #hop on and pick up a brick
                    self.has_brick=True
                    self.on_structure=True
                    self.trip_cnt += 1
                    return 'fu'  # u is picking up a block.
                

            '''
            Wall Following Behavior
            '''
            # wall following in a counter clock wise direction.
            if observation[heading.NORTH] == 0 and observation[heading.WEST] > 0:
                return 'f'
            elif observation[heading.NORTH] == 0 and observation[heading.WEST] == 0:
                return 'lf'
            elif observation[heading.NORTH] > 0:
                return 'r'
        else: # On structure
            
            #use this to get the rel-dx-dy from from the heading
            #This could be nicer  
            dxdy=None
            if self.pose.heading.value == heading.NORTH.value:
                dxdy=((0,1),(1,0),(0,-1),(-1,0))  # order: N, E, S, W in the coordinate frame of robot.
            elif self.pose.heading.value == heading.EAST.value:
                dxdy=((1,0),(0,-1),(-1,0),(0,1))  # order: N, E, S, W in the coordinate frame of robot.
            elif self.pose.heading.value == heading.SOUTH.value:
                dxdy=((0,-1),(-1,0),(0,1),(1,0))  # order: N, E, S, W in the coordinate frame of robot.
            elif self.pose.heading.value == heading.WEST.value:
                dxdy=((-1,0),(0,1),(1,0),(0,-1))  # order: N, E, S, W in the coordinate frame of robot.
                
            dxy_heading_dir=dict((d,h) for d,h in zip(dxdy,heading))

        
            loc=(self.pose.x,self.pose.y) #fix for padding
            if loc in self.plan_graph.nodes:
                # agent.plan_graph[(x, y)] returns an AtlasView of its children nodes.
                children=tuple(n for n in self.plan_graph[loc])  # all neighboring nodes of loc, with edge attributes.
                # agent._parent_digraph[(x, y)] returns an AtlasView of its parent nodes.
                parents=tuple(n for n in self._parent_digraph[loc])
            else:
                children=tuple()
                parents=tuple()
                
            child_heights=tuple(self.plan_graph.nodes[ch]['height'] for ch in children)
            parent_heights=tuple(self.plan_graph.nodes[p]['height'] for p in parents)

            child_dxy=tuple((chx-self.pose.x,chy-self.pose.y) for chx,chy in children)
            parent_dxy=tuple((px-self.pose.x,py-self.pose.y) for px,py in parents)
            
            child_h_dir=dict((dxy_heading_dir[dxy] ,h) for dxy,h in  zip(child_dxy,child_heights))
            parent_h_dir=dict((dxy_heading_dir[dxy],h) for dxy,h in zip(parent_dxy,parent_heights))
            
            if debug_print:
                print(f'Robot pose: {self.pose}')
                print(f'children: {children}')
                print(f'child_dxdy: {child_dxy}')
                print(f'child_dirs: {child_h_dir}\n')
                print(f'parents: {parents}')
                print(f'parent_dxdy: {parent_dxy}')
                print(f'parent_dirs: {parent_h_dir}')
        
        
            '''
            Check if you should build
            '''
            
            build = False
            if self.pose.x == 13 and self.pose.y == 7:
                print(f'Robot {self.ID} at the parent of branch {self.pose}.')
            if (observation.heights[0] < self.plan_graph.nodes[loc]['height']) and self.has_brick: # observation.heights is [ne,N,E,S,W] from local view               
                build=True
                print("entering check place.")
                for ph, pnode in zip(parent_h_dir.keys(), parents):  # ph is one of heading.NORTH, ...
                    if not (observation[ph] > observation.heights[0]  # observation is the heights of the current location and its 4 neighbors.
                            or observation[ph] == parent_h_dir[ph]):  # the block placed shall not be higher than its parents, unless the parent has reached design.
                        build=False
                        print("Abort placing, case 1.")
                    # deal with branching, after the intersection has been placed.
                    elif self.plan_graph.out_degree(pnode) >= 2:
                        if debug_print: print(f'observation.heights {observation.heights}')
                        if not (observation.heights[1] == observation.heights[-1]):
                            build=False
                            print("Abort placing, case 4.")
                for chh, cnode in zip(child_h_dir.keys(), children):  # Z Huang modified.
                    if not (observation[chh] == observation.heights[0]  # the block placed shall not create cliffs, unless designed.
                            or abs(self.plan_graph.nodes[loc]['height'] - child_h_dir[chh]) > 1):
                        build=False
                        print("Abort placing, case 2.")
                    # deal with branching.
                    if self.plan_graph.out_degree(cnode) == 1:
                        # do not block the way forward. do not form a cliff when the blocks are not staggered
                        if ((observation.heights[1] == observation.heights[0] and (observation.heights[1] - observation.heights[-1]) >= 1)):
                            if debug_print: print(f'Abort placing, case 5. indeg {self.plan_graph.in_degree((self.pose.x, self.pose.y))}, outdeg {self.plan_graph.in_degree((self.pose.x, self.pose.y))}')
                            build=False
                    elif self.plan_graph.out_degree(cnode) == 2:  # default 2.
                        # if the out degree of the current child node is greater than 2.
                        p1 = chh.value + 5
                        p2 = chh.value + 6 if chh.value + 6 <= 8 else chh.value + 1
                        if debug_print: print(f'observation.heights {observation.heights}')
                        # avoid cliff resulted from the distal end at the cross.
                        if not observation.heights[p1] == observation.heights[p2] == observation.heights[1]:  # TODO not considering two adjacent branches.
                            build=False 
                            print("Abort placing, case 3.")
                    elif self.plan_graph.out_degree(cnode) > 2:  # default 2.
                        # if the out degree of the current child node is greater than 2.
                        p1 = chh.value + 5
                        p2 = chh.value + 6 if chh.value + 6 <= 8 else chh.value + 1
                        if debug_print: print(f'observation.heights {observation.heights}')
                        # avoid cliff resulted from the distal end at the cross.
                        if not (observation.heights[p1] == observation.heights[p2] == observation.heights[-1]):  # TODO not considering two adjacent branches.
                            build=False 
                            print(f"Abort placing, case 7, outdegree {self.plan_graph.out_degree(cnode)}.")

                # deal with the cliff resulted from the distal end of the block ----------------------------------------------------
                # abort placement if the distal end results in an undesired height at the end of a wall.
                locDistalEnd = list(self.plan_graph.successors((self.pose.x, self.pose.y)))
                if len(locDistalEnd) == 0:
                    build = False
                    if debug_print: print("Abort placing, case 6, due to distal end of block out of plan graph.")
                # abort placement at the exit location.
                if self.plan_graph.nodes[loc]['exit']:
                    build = False
                # ------------------------------------------------------------------------------------------------------------------

            if build:
                b='p'
                if mode == '0':
                    self.has_brick=False
                    self.trip_cnt_productive += 1
            else:
                b=''
                        
            
            if (observation.heights[0] == 0) and mode == '0':  
                
                if self.on_structure and self.has_brick:
                    self.trip_cnt_wasted += 1
                    
                self.on_structure = False
                if b == '':
                    if debug_print:
                        print('Just got to ground floor, with nothing to do.')                                    
                    return ''
                   
            
            if len(children) == 0:
                if debug_print:
                    print('Just hopped of structrue.')                
                return ''

            if PROB_ON and not self.plan_graph.nodes[loc]['exit']:            
                p_draw=random.random()
                ch=None
                pmax=0
                active_children=[]
                
                if MAX_ELEM:
                    #Get Active Children
                    #Somehow not checking for the h-difference got them all stuck
                    #Even though there should have been another action. 
                    for c in children:
                        t_max_paths=self.plan_graph.edges[loc,c]['max_path']
                        dh=self.plan_graph.nodes[c]['height']-self.plan_graph.nodes[loc]['height']
                        if len(t_max_paths - self.max_visited) > 0 and abs(dh) <= 1:
                            active_children.append((c,self.plan_graph.edges[loc,c]['prob'] ))
                            pmax += self.plan_graph.edges[loc,c]['prob']
                
                if len(active_children) > 0:
                    p_draw *= pmax
                    for c,p_child in active_children:
                        ch=c
                        if p_draw <p_child:
                            break
                        p_draw -= p_child
                else:                
                    for c in children:
                        ch=c
                        t_prob=self.plan_graph.edges[loc,c]['prob']    
                        if p_draw < t_prob:
                            break
                        p_draw -= t_prob
            
            else:   
                ch=random.choice(children) # This is the direction you go (Fix with exit)
            
            assert not ch is None, "Somehow Choice was empty. Check agent code."
            
            a=self.dx_dy_to_turn((ch[0]-self.pose.x,ch[1]-self.pose.y))
            
            if debug_print:
                print(f'Chosing {ch}')
          
            
            #should have at most one turn
            return a + b +'f'
            
            
        
        
    def actions_to_reach_pose(self,target_pose):
        rel_pose=Pose(self.pose)
        rel_pose.reverse()
        rel_pose.add(target_pose)
        
            
            
            
        