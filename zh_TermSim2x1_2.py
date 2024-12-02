# -*- coding: utf-8 -*-
"""
Created on Thu May  4 15:18:00 2017
@author: nnapp

Simulation of Termes moving in a partailly built srtructure 
and running a SLAM like algorithm to place a brick

"""

'''
TODO:
1. change names of files, make back-ups; Later
2. compile and build a larger wall, with only one side of stairs; Done.
3. compile and build a L-shape corner; Done.
4. compile and build a T shape; Done.
5. openGL visualizer if needed. Done.
6. choose the direction to go at the branch.
7. build a cross.
'''

from termes.world import World
from termes.pose import Pose, heading
from termes.agent import ACTIONS,Observation, Agent
import networkx as nx
import pickle
import time

# for visualization
import sys
sys.path.append(r'F:\\Hiwonder_SharedFiles\\robot_localization')
from zh_Utilities import brickMap, hmRPYG, hmRPYP, drawFloor, keyboardCtrl, robot, R, np, poseTags, drawRigidBodyOG, drawBrickOG
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
useOpenGL = True
myBrickMap = brickMap(hmRPYG, None)
myRobot = robot(hmRPYG, None, poseTags, None)
myRobot.feetPosControl(myRobot.initFeetPos)
myRobot.propagateAllLegJointPoses()
floorRegion = np.array([[-4.5, -4.5, -0.02],
                        [4.5, -4.5, -0.02],
                        [4.5, 4.5, -0.02],
                        [-4.5, 4.5, -0.02]])

mode = 'custom4'  # choose between 'default' and 'custom' to select input files.

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
    elif mode == 'custom1':  # L wall.
        wrld.struct.read('structures/zh_3LayerL.csv')
        with open('structures/zh_graph3LayerLShape.pkl', 'rb') as fh:
            plan=pickle.load(fh)
    elif mode == 'custom2':  # T wall in serial.
        wrld.struct.read('structures/zh_5LayerTShape.csv')
        with open('structures/zh_graph5LayerTShape.pkl', 'rb') as fh:
            plan=pickle.load(fh)
    elif mode == 'custom3':
        wrld.struct.read('structures/zh_3LayerTShape.csv')
        with open('structures/zh_graph3LayerTShape.pkl', 'rb') as fh:
            plan=pickle.load(fh)
    elif mode == 'custom4':
        wrld.struct.read('structures/zh_6LayerTShape.csv')
        with open('structures/zh_graph6LayerTShape.pkl', 'rb') as fh:
            plan=pickle.load(fh)

    # init OpenGL and pygame if needed.
    if useOpenGL:
        pygame.init()  # init the pygame lib.

        window = (1600, 1200)  # in pixels.

        pygame.display.set_mode(window, DOUBLEBUF|OPENGL)
        pygame.display.set_caption('DEMO Scene Simulation')

        # enable depth test. This avoids the incorrect transparency between objects.
        # this should be AFTER the pygame / glfw window is initialized.
        glEnable(GL_DEPTH_TEST)

        glClearColor(0.5, 0.5, 0.5, 1.0)

        gluPerspective(60, (window[0] / window[1]), 0.001, 10.0)

        # glTranslatef(-0.5, -0.5, -1.7) # default.
        # glTranslatef(-1.5, -0.5, -1.7) # shift the camera to the right.
        glTranslatef(-2.5, -0.3, -2.74)
        # glRotatef(-45, 1, 0, 0)  
        glRotatef(-75, 1, 0, 0) 
        glRotatef(45, 0, 0, 1) 
        glTranslatef(0.5, 0, 0)

        # get the current view angle.
        hmScene = hmRPYP(-45, 0, 0, np.array([-0.5, -0.5, -1.7])).dot(hmRPYP(0, 0, 45, np.array([0.5, 0, 0])))
        angle_x, angle_y, angle_z = R.from_matrix(hmScene[:3, :3]).as_euler('zyx', degrees=True)[::-1]
        transScene = hmScene[:3, -1].flatten()
        distance = transScene[-1]
        print("angles XYZ: {} {} {}".format(angle_x, angle_y, angle_z))
        print("Translation XYZ: ", transScene)

    # wrld.show()

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
    childNodesStart = [()]  # init the child nodes of the start.
    for n in wrld.agents[0].plan_graph.nodes:
        if not wrld.agents[0].plan_graph.nodes[n]['start'] and n != childNodesStart[0]:
            wrld.struct[Pose(n)] = 0  # if this is not a start position, this place's height is assignd a 0.
        elif wrld.agents[0].plan_graph.nodes[n]['start']: # set the initial block to 2x1. Only enter once.
            childNodesStart = list(wrld.agents[0].plan_graph.successors(n))
            print(f"Start at {n}, pose {Pose(n)}, child nodes {childNodesStart}, len {len(childNodesStart)}, first child node {childNodesStart[0]}.")
            if len(childNodesStart) > 0:
                wrld.struct[Pose(childNodesStart[0])] = 1
                print(f"Set {Pose(childNodesStart[0])} to 1.")
                # store the start block into map.
                if useOpenGL:
                    # translate block coordinates.
                    blockPose = np.zeros(6).astype('float')
                    # blockPose[4] = - 0.2 * (n[0] + childNodesStart[0][0]) / 2  # actual y
                    blockPose[4] = -(0.2*n[0] + 0.1*(childNodesStart[0][0] - n[0]))  # actual y 
                    # blockPose[3] = 0.2 * (n[1] + childNodesStart[0][1]) / 2  # actual x
                    blockPose[3] = 0.2 * n[1] + 0.1*(childNodesStart[0][1] - n[1])  # actual x
                    blockPose[5] = myBrickMap.brickThickness / 2 # actual z of com.
                    blockPose[2] = 0.0 if n[0] == childNodesStart[0][0] else 90.0  # actual orientation.
                    myBrickMap.map = np.append(myBrickMap.map, blockPose).reshape(-1, 6)
        # wrld.show()
        # time.sleep(0.1)
    # wrld.show()

    # manual control.
    while not (u == 'q' or u == 'e') :
        wrld.show()
        print(f'On structure = {agent.on_structure}')
        print(f'Next To Start = {agent._next_to_start()}')
        print(agent.pose)
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
                            # add 1 layer to the current location.
                            wrld.struct[agent.pose] += 1  # add 1 layer height to the structure.
                            # add 1 layer to the front location.
                            # check the heading of agent.
                            tempPose = agent.pose
                            if agent.pose.heading == heading.NORTH:
                                tempPose.y += 1
                            elif agent.pose.heading == heading.EAST:
                                tempPose.x += 1
                            elif agent.pose.heading == heading.SOUTH:
                                tempPose.y -= 1
                            elif agent.pose.heading == heading.WEST:
                                tempPose.x -= 1
                            wrld.struct[tempPose] += 1
                            # store block to map
                            # translate block coordinates.
                            if useOpenGL:
                                blockPose = np.zeros(6).astype('float')
                                # blockPose[4] = - 0.2 * (agent.pose.x + tempPose.x) / 2  # actual y
                                blockPose[4] = 0.5 * (myRobot.bodyPose[4] - tempPose.x * 0.2)  # actual y
                                # blockPose[3] = 0.2 * (agent.pose.y + tempPose.y) / 2  # actual x
                                blockPose[3] = 0.5 * (myRobot.bodyPose[3] + tempPose.y * 0.2)  # actual x
                                blockPose[5] = myBrickMap.brickThickness / 2 + (wrld.struct[agent.pose] - 1) * myBrickMap.brickThickness # actual z of com.
                                blockPose[2] = 0.0 if (agent.pose.heading == heading.NORTH or agent.pose.heading == heading.SOUTH) else 90.0  # actual orientation.
                                myBrickMap.map = np.vstack((myBrickMap.map, blockPose.reshape(-1, 6)))
                        else:
                            agent.pose=wrld.move(a,agent.pose)
                            # translate robot pose in grid cell to the real world.
                            # world y axes are opposite
                            robotPose = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
                            robotPose[2] = -90.0 * agent.pose.heading.value
                            robotPose[3] = 0.2 * agent.pose.y
                            robotPose[4] = -0.2 * agent.pose.x
                            robotPose[5] = 0.1 + myBrickMap.brickThickness / 2 + (wrld.struct[agent.pose] - 1) * myBrickMap.brickThickness # actual z of com.
                            myRobot.bodyPose = robotPose
                elif u == 'q':
                    print('Bye!')
                    break
                elif u == 'e': # start to run actions automatically.
                    print('Starting to run agent.')
                    break
                
    # automatic decision.
    print("about to enter second loop.")            
    while u == 'e':
        # agent.pose=wrld.pose
        wrld.show()  # print the world.
        time.sleep(0.1)
        # visualize using openGL
        if useOpenGL:
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)  # clear the screen.
            # interactive view angle.
            keyboardCtrl()
            drawFloor(vertices = floorRegion)
            # draw robot body
            myRobot.drawRobotBody(colored = True)
            myRobot.propagateAllLegJointPoses()
            myRobot.drawAllLegLinkagesOG()
            # time.sleep(0.1)
            # draw the block on the robot's body
            if agent.has_brick:
                # if the robot has a block draw it.
                backBlockPose = myRobot.bodyPose
                backBlockPose[-1] += 0.08
                drawRigidBodyOG(hmRPYG(*backBlockPose[:3], backBlockPose[3:]).dot(myBrickMap.brickVertices))
                drawBrickOG(myRobot.bodyPose, myBrickMap.brickVertices)
            # draw block.
            for pose in myBrickMap.map:
                drawRigidBodyOG(hmRPYG(*pose[:3], pose[3:]).dot(myBrickMap.brickVertices))
                drawBrickOG(pose, myBrickMap.brickVertices)
            pygame.display.flip()
            pygame.time.wait(2)  # default 5


        print(f'Next To Start = {agent._next_to_start()}')
        # print(wrld.pose)
        print(agent.pose)
        time.sleep(0.01)
        #add multi input actions
        obs = wrld.obs(agent.pose)
        observations.append(obs)
        robot_obs=Observation(obs)
        actns = agent.pick_actions(robot_obs, debug_print = True)
        for a in actns:
            if a == 'p':
                # add 1 layer to the current location.
                wrld.struct[agent.pose] += 1  # add 1 layer height to the structure.
                # add 1 layer to the front location.
                # check the heading of agent.
                tempPose = agent.pose
                if agent.pose.heading == heading.NORTH:
                    tempPose.y += 1
                elif agent.pose.heading == heading.EAST:
                    tempPose.x += 1
                elif agent.pose.heading == heading.SOUTH:
                    tempPose.y -= 1
                elif agent.pose.heading == heading.WEST:
                    tempPose.x -= 1
                wrld.struct[tempPose] += 1
                # store block to map
                # translate block coordinates.
                if useOpenGL:
                    blockPose = np.zeros(6).astype('float')
                    # blockPose[4] = - 0.2 * (agent.pose.x + tempPose.x) / 2  # actual y
                    blockPose[4] = 0.5 * (myRobot.bodyPose[4] - tempPose.x * 0.2)  # actual y
                    # blockPose[3] = 0.2 * (agent.pose.y + tempPose.y) / 2  # actual x
                    blockPose[3] = 0.5 * (myRobot.bodyPose[3] + tempPose.y * 0.2)  # actual x
                    blockPose[5] = myBrickMap.brickThickness / 2 + (wrld.struct[agent.pose] - 1) * myBrickMap.brickThickness # actual z of com.
                    blockPose[2] = 0.0 if (agent.pose.heading == heading.NORTH or agent.pose.heading == heading.SOUTH) else 90.0  # actual orientation.
                    myBrickMap.map = np.vstack((myBrickMap.map, blockPose.reshape(-1, 6)))
            else:
                agent.pose=wrld.move(a,agent.pose)
                # translate robot pose in grid cell to the real world.
                # x axes are opposite
                robotPose = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
                robotPose[2] = -90.0 * agent.pose.heading.value
                robotPose[3] = 0.2 * agent.pose.y
                robotPose[4] = -0.2 * agent.pose.x
                robotPose[5] = 0.1 + myBrickMap.brickThickness / 2 + (wrld.struct[agent.pose] - 1) * myBrickMap.brickThickness # actual z of com.
                myRobot.bodyPose = robotPose
       
                

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
