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
s_size=1

def save_growth(fname='growth.pkl'):
    with open(fname,'wb') as fh:
        pickle.dump(growth,fh)
        
def save_result(fname='run_result'):
    with open(fname + '.pkl','wb') as fh:
        pickle.dump(wrld,fh)
    with open(fname + '_growth.pkl','wb') as fh:
        pickle.dump(growth,fh)
            

if __name__ == '__main__':
    
    wrld=World(num_agents=10)
    
    #wrld.struct.read('10x10.strct.idx')
    #wrld.struct.read('10x10_single.idx')
    #wrld.struct.read('random_srct.2da')
    #wrld.struct.read('../termes-slapm/tests/vittoria_complete.csv')
 
    #with open('../termes-bfd/bfd_plan_graph_15.pkl','rb') as fh:

    #wrld.struct.read('../termes-slapm/tests/vittoria_complete.csv')
    ##with open('../termes-slapm/tests/bfd_output_graph_opt_10_100.pkl','rb') as fh: 
    #with open('max_plan_vittoria.pkl','rb') as fh: 
    #    plan=pickle.load(fh)
    #    plan.edges[(20,1),(19,1)]['prob']=0.98
    #    plan.edges[(20,1),(20,2)]['prob']=0.02
    

    #wrld.struct.read('../termes-slapm/tests/Castle_small.csv')    
    # ##with open('../termes-slapm/tests/bfd_output_graph_Castle_opt_10_100.pkl','rb') as fh: 
    #with open('max_plan_castle_fix.pkl','rb') as fh: 
    #    plan=pickle.load(fh)
    
    #max_ele={(0, 0, 7),(0, 3, 7),(0, 16, 7),(0, 19, 7),(2, 11, 5),
    #         (3, 0, 7),(3, 19, 7),(16, 0, 7),(16, 19, 7),(19, 0, 7),
    #         (19, 3, 7),(19, 16, 7),(19, 19, 7)}
    
    wrld.struct.read('../termes-slapm/tests/samurai_small_structure.csv')    
    ##with open('../termes-slapm/tests/samurai_small_graph_opt_10_100.pkl','rb') as fh: 
    with open('max_plan_samurai_fix.pkl','rb') as fh: 
        plan=pickle.load(fh)
   
    
    max_ele=set()
    for u,v in plan.edges:
        max_ele.update(plan.edges[u,v]['max_path'])
        if(len(plan.edges[u,v]['max_path'])==0):
            print(f'Warning: edge {u}-{v} as no max dependents.')
   
    max_size=sum(plan.nodes[n]['height'] for n in plan.nodes)
   #    {(0, 0, 7),(0, 3, 7),(0, 16, 7),(0, 19, 7),(2, 11, 5),
   #         (3, 0, 7),(3, 19, 7),(16, 0, 7),(16, 19, 7),(19, 0, 7),
   #         (19, 3, 7),(19, 16, 7),(19, 19, 7)}
   
    
    '''
     
    '''
    
   
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
        a.max_set=max_ele
        
    
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
    done=False
    
    while not done:
        
        #pickle.dump(wrld,log_fh)
        
        if wrld.agents[0].my_time - show_time > show_delta:        
            show_time = wrld.agents[0].my_time
            print(f'Built {s_size}/{max_size}')
            wrld.show()
            show_new=True
            #pickle.dump(wrld,log_fh)
            #if check_done():
            #    print(f'Done!')
            #    break
            
        agents_done=[]
        
        for a in wrld.agents:
        
            if len(max_ele - a.max_visited) == 0:
                if a.comp_time == 0:
                    a.comp_time=a.my_time
                
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
                    if (a.pose.y-2,a.pose.x-2,a.pose.z+1) in max_ele:
                        a.max_visited.add( (a.pose.y-2,a.pose.x-2,a.pose.z+1))
                else:
                    n_pose=wrld.move(u,a.pose)
                    a.pose=n_pose
                    if (a.pose.y-2,a.pose.x-2,a.pose.z) in max_ele:
                        a.max_visited.add( (a.pose.y-2,a.pose.x-2,a.pose.z))
            if a.comp_time > 0:
                agents_done.append(True)
            else:
                agents_done.append(False)
            
        if all(agents_done):
            done=True
            print("All agents are done!")
            wrld.show()
        show_new = False
 


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
