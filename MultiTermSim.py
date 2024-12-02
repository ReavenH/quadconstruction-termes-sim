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

log_file='multi_sim_trace_3.pkl'

log_fh=open(log_file,'wb')

growth=[]
s_size=0

def save_growth(fname='growth.pkl'):
    with open(fname,'wb') as fh:
        pickle.dump(growth,fh)


if __name__ == '__main__':
    
    wrld=World(num_agents=10)
    #wrld.struct.read('10x10.strct.idx')
    #wrld.struct.read('10x10_single.idx')
    #wrld.struct.read('random_srct.2da')
    #wrld.struct.read('../termes-slapm/tests/vittoria_complete.csv')
 
    #with open('../termes-bfd/bfd_plan_graph_15.pkl','rb') as fh:

    #wrld.struct.read('../termes-slapm/tests/vittoria_complete.csv')
    #with open('../termes-slapm/tests/bfd_output_graph_opt_10_100.pkl','rb') as fh: 
    #    plan=pickle.load(fh)
    #    plan.edges[(20,1),(19,1)]['prob']=0.98
    #    plan.edges[(20,1),(20,2)]['prob']=0.02
    

    wrld.struct.read('structures/Castle_small.csv')    
    with open('structures/bfd_output_graph_Castle_opt_10_100.pkl','rb') as fh: 
        plan=pickle.load(fh)
    
    #wrld.struct.read('../termes-slapm/tests/samurai_small_structure.csv')    
    #with open('../termes-slapm/tests/samurai_small_graph_opt_10_100.pkl','rb') as fh: 
    #    plan=pickle.load(fh)
    
    '''
    Hold Actions and observations that go into grid filter
    '''
    
    #agent=Agent(pose=Pose((4,1)))
    #agent.set_plan_graph(plan)

    actions=[]
    observations=[]
    u=''
    
    exits=[]
    starts=[]

    for a in wrld.agents:
        a.set_plan_graph(plan)
    
    for n in wrld.agents[0].plan_graph.nodes:
        
        if not wrld.agents[0].plan_graph.nodes[n]['start']:
            wrld.struct[Pose(n)] = 0
        else:        
            wrld.struct[Pose(n)] = 1
            
        if wrld.agents[0].plan_graph.nodes[n]['exit']:
            exits.append(n)

    for a in wrld.agents:
        a.pose=Pose(a.start_loc)
    
    def check_done():
        for e in exits:
            if not wrld.struct[Pose(e)] > 0:
                return False
        return True
    
    show_new=True
    show_time=0
    show_delta=100
    
    while True:
        
        #pickle.dump(wrld,log_fh)
        
        if wrld.agents[0].my_time - show_time > show_delta:        
            wrld.show()
            show_time = wrld.agents[0].my_time
            show_new=True
            #pickle.dump(wrld,log_fh)
            #if check_done():
            #    print(f'Done!')
            #    break
            
        for a in wrld.agents:
        
            if show_new:
                #print(f'On structure = {a.on_structure}')
                #print(f'Next To Start = {a._next_to_start()}')
                pass
                
            a_obs=Observation(wrld.obs(a.pose))
            actns = a.pick_actions(a_obs)

            if show_new:
               #print(f'Actions: {actns}')
               pass
            for u in actns:
                if u == 'p':
                    wrld.struct[a.pose] += 1
                    s_size += 1
                    growth.append((a.my_time,s_size,a.pose))
                else:
                    n_pose=wrld.move(u,a.pose)
                    a.pose=n_pose
        show_new = False
 

    # ??? What are these for?
    pickle.dump((show_time,wrld.struct.worldArray),log_fh)


    with open(f'castle_{show_time}.pkl','wb') as fh:
        pickle.dump(wrld.struct.worldArray,fh)


    log_fh.close()


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
