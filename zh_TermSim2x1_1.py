# -*- coding: utf-8 -*-
"""
Created on Thu May  4 15:18:00 2017
@author: nnapp

Simulation of Termes moving in a partailly built srtructure 
and running a SLAM like algorithm to place a brick

"""

from termes.world import World
from termes.pose import Pose
from termes.agent import ACTIONS,Observation, Agent
import networkx as nx
import pickle
import time
import copy

mode = 'custom'  # choose between 'default' and 'custom' to select input files.

if __name__ == '__main__':
    
    wrld=World(num_agents=1)
    #wrld.struct.read('10x10.strct.idx')
    #wrld.struct.read('10x10_single.idx')
    #wrld.struct.read('random_srct.2da')
    '''
    # does NOT work.
    wrld.struct.read('../termes-bfd/bfd_structure_25.pkl')
    with open('../termes-bfd/bfd_plan_graph_25.pkl','rb') as fh:
        plan=pickle.load(fh)
    '''
    
    if mode == 'default':
        # works well.
        wrld.struct.read('structures/Castle_small.csv')    # may be padded. the 2D array is deserialized.
        with open('structures/bfd_output_graph_Castle_opt_10_100.pkl','rb') as fh: 
            plan=pickle.load(fh)
    elif mode == 'custom':
        wrld.struct.read('structures/matrix_output_utf8.csv')    # may be padded. the 2D array is deserialized.
        with open('structures/zh_graph5LayerWall.pkl','rb') as fh: 
            plan=pickle.load(fh)

    
    '''
    Hold Actions and observations that go into grid filter
    '''
    
    agent=wrld.agents[0]
    agent.pose=Pose((4,1))  # assigning the x and y locations. z will be defaulted to 0. can also assign (x, y, z)
    agent.set_plan_graph(plan)

    
    actions=[]
    observations=[]
    u=''
    for a in wrld.agents:
        a.set_plan_graph(plan)  # this function reads the input plan graph and adds other attributes.

    
    for n in wrld.agents[0].plan_graph.nodes:
        if not wrld.agents[0].plan_graph.nodes[n]['start']:
            wrld.struct[Pose(n)] = 0  # if this is not a start position, this place's height is assignd a 0.
    
    while not (u == 'q' or u == 'e') :
        print(f'On structure = {agent.on_structure}')
        print(f'Next To Start = {agent._next_to_start()}')
        print(agent.pose)
        wrld.show()
        #add multi input actions
        ustring=input('action: ')
        if len(ustring) > 0:
            for u in ustring:  # it allows a sequence of instructions to input.
                if u in ACTIONS: 
                    agent.pose=wrld.move(u,agent.pose)
                    actions.append(u)
                    observations.append(wrld.obs(agent.pose))
                elif u == 'n': #next termes action (automatically select)
                    obs = wrld.obs(agent.pose)
                    observations.append(obs)
                    robot_obs=Observation(obs)
                    actns = agent.pick_actions(robot_obs)
                    for a in actns:
                        if a == 'p':
                            wrld.struct[agent.pose] += 1  # add 1 layer height to the structure.
                        else:
                            agent.pose=wrld.move(a,agent.pose)
                elif u == 'q':
                    print('Bye!')
                    break
                elif u == 'e': # start to run actions automatically.
                    print('Starting to run agent.')
                    break
                
    print("about to enter second loop.")     
    actns = ''
    wrldTemp = copy.deepcopy(wrld)
    while u == 'e':
        #add multi input actions
        # obs = wrld.obs(agent.pose)
        mode = '0'
        intermPos = []  # store the intermediate positions to trace back. 
        obs = wrld.obs(agent.pose)
        observations.append(obs)
        robot_obs=Observation(obs)
        actns = agent.pick_actions(robot_obs, mode = mode, debug_print = True)
        
        if 'p' in actns:
            # recursively explore.
            intermPos.append(agent.pose)  # position of the 1st cell.
            for a in actns:
                actions.append(a)
                if a == 'p':
                    wrldTemp.struct[agent.pose] += 1
                else:
                    agent.pose = wrldTemp.move(a, agent.pose)
                    # agent.pose = wrld.move(a, agent.pose)
                    if a == 'f':
                        intermPos.append(agent.pose)  # position of the 2nd cell.
            mode = '1'
            '''
            # print pose.
            print(f'Next To Start = {agent._next_to_start()}')
            print(agent.pose)
            wrld.show()  # print the world.
            time.sleep(0.01)
            '''
            # 2nd block check.
            obs = wrldTemp.obs(agent.pose)
            observations.append(obs)
            robot_obs=Observation(obs)
            actns = agent.pick_actions(robot_obs, mode = mode, debug_print = True)
            if 'p' in actns:
                mode = '2'
                # real world observation to get heights.
                obs = wrld.obs(agent.pose)
                robot_obs=Observation(obs)
                if robot_obs.heights[0] == robot_obs.heights[1] and robot_obs.heights[0] == robot_obs.heights[-2]:
                    # if the consective heights are equal.
                    # move forward.
                    agent.pose = wrldTemp.move('f', agent.pose)
                    # gent.pose = wrld.move('f', agent.pose)
                    # turn around.
                    agent.pose = wrldTemp.move('r', agent.pose)
                    # agent.pose = wrld.move('r', agent.pose)
                    agent.pose = wrldTemp.move('r', agent.pose)
                    # agent.pose = wrld.move('r', agent.pose)
                    # place.
                    wrldTemp.struct[intermPos[-1]] += 1
                    wrld = copy.deepcopy(wrldTemp)  # update wrld
                    agent.has_brick = False
                    agent.trip_cnt_productive += 1
            else:
                # abort, go back to the start.
                wrldTemp = copy.deepcopy(wrld)  # reset wrld.
                mode = '0'
                rot = agent.dx_dy_to_turn((intermPos[-2].x - agent.pose.x, intermPos[-2].y - agent.pose.y))
                if rot != '':
                    for a in rot:
                        agent.pose = wrld.move(a, agent.pose)
                agent.pose = wrld.move('f', agent.pose)
        else:
            mode = '0'
            # wrldTemp = copy.deepcopy(wrld)  # reset wrld.
            for a in actns:
                actions.append(a)
                agent.pose = wrld.move(a, agent.pose)

        # agent.pose=wrld.pose
        print(f'Next To Start = {agent._next_to_start()}')
        # print(wrld.pose)
        print(agent.pose)
        wrldTemp.show()  # print the world.
        time.sleep(0.01)
                

#--World--> Sense

#Robot
## Pose
## Estimate
## Target
## Motion Command
## Planner 


#World (x,y,z)

#Robot
#Structure
#TargetStructure

#Pose
## x,y,z,h

#move_input
#Visualize

#Sensor
#Motion

#Probability
