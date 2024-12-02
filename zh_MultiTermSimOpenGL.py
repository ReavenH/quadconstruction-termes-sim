# -*- coding: utf-8 -*-
"""
Created on Thu May  4 15:18:00 2017
@author: nnapp

Simulation of Termes moving in a partailly built srtructure 
and running a SLAM like algorithm to place a brick

Modified in Dec. 2024
@author: Z. Huang
compatibility of 2x1 blocks and OpenGL 3D visualization.

"""

'''
TODO
1. DEBUG: robots will fly up in OpenGL when the block exceeds the plan graph; Done (constrained the block at the margin)
2. explore a cross, and a "fake" cross with 2 intersecting locations; DONE
3. build curved, layered structures: mapping from grids to real continuous coordinates. DONE
4. draw uneven terrain to illustrare the need of a curved struture (OPTIONAL).
5. Avoid collision in multi-agent simulation. DONE
'''

'''
TODO for the final paper experiment
Types of the structure: A) I and L walls; B) X walls; C) C walls, J walls, V walls.
Assumptions: robot does not break; locomotion is at a constant speed; extra time for climbing is ignored; blocks are placed right beneath the robot; 
            blocks don't span different layers when placement error occurs (assuming only augular and axial errors, as lateral error is caused by angular errors due to the gripper mechanism);
            T-pins mechanism doe not fail.
1. For each type of structure, explore the building time (steps) v.s. number of agents (1~10). Maybe affected by the congestion and number of crosses, otherwise it should be linear.
    prerequisites: detect congestion from the NW and NE directions of each agent.
2. [UNDECIDED] For X-shapes (with crosses), explore the 
3. For I and C walls (tilt from 0 to 20 degrees), given a fixed plan graph, explore how placement errors influence the structural stability.
    3.1 Definition of structural stability: 
        1) the number T-pins crossing two layers, for each block; 
            the block is considered insecure if there are <2 T-pins crossing two layers.
        2) the overlapping area (in percentage of the block, w/r to the layer beneath) of each block.
            the block is considered insecure if <75% of the block contacts the lower layer.
    3.2 experiment design
        given a fixed plan graph, the data table should be organized as follows:
            row headers: tilt angles, 0, 5, 10, 15, 20
            column headers: distribution set A (better than usual); distribution B (usual performance); distribution set C (worse than usual).
            each entry: mean and standard deviation of the number of first insecure block. Repeat 10 times for each entry.

'''

from termes.world import World
from termes.pose import Pose, heading
from termes.agent import ACTIONS,Observation, Agent
import networkx as nx
import pickle
import time
import copy

# for openGL visualization ----------------------
import sys
sys.path.append(r'F:\\Hiwonder_SharedFiles\\robot_localization')
from zh_Utilities import brickMap, hmRPYG, hmRPYP, drawFloor, keyboardCtrl, robot, R, np, poseTags, drawRigidBodyOG, drawBrickOG, renderTextOG, placeTiltBlock
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
useOpenGL = True
numAgents = 3
myBrickMap = brickMap(hmRPYG, None)
# init a list of robot instances.
myRobots = [robot(hmRPYG, None, poseTags, None) for i in range(numAgents)]
for i in range(numAgents):
    myRobots[i].feetPosControl(myRobots[i].initFeetPos)
    myRobots[i].propagateAllLegJointPoses()
# define the floor area canvas.
floorRegion = np.array([[-8.5, -8.5, -0.02],
                        [8.5, -8.5, -0.02],
                        [8.5, 8.5, -0.02],
                        [-8.5, 8.5, -0.02]])
# ----------------------------------------
growth=[]
s_size=0

mode = 'custom10'  # choose between 'default' and 'custom' to select input files.
isCurve = False  # identify whether the structure is curved.

if __name__ == '__main__':
    
    wrld=World(num_agents=numAgents)

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
    elif mode == 'custom5':
        wrld.struct.read('structures/zh_6LayerTShape1.csv')
        with open('structures/zh_graph6LayerTShape1.pkl', 'rb') as fh:
            plan=pickle.load(fh)
    elif mode == 'custom6':
        wrld.struct.read('structures/zh_6LayerCrossShape.csv')
        with open('structures/zh_graph6LayerCross.pkl', 'rb') as fh:
            plan=pickle.load(fh)
    elif mode == 'custom7':
        wrld.struct.read('structures/matrix_output_utf8.csv')
        with open('structures/zh_graph5LayerCurvedWall.pkl', 'rb') as fh:
            plan=pickle.load(fh)
        isCurve = True
    elif mode == 'custom8':
        wrld.struct.read('structures/zh_12LayerCurvedWall.csv')
        with open('structures/zh_graph12LayerCurvedWall.pkl', 'rb') as fh:
            plan=pickle.load(fh)
        isCurve = True
    elif mode == 'custom9':
        wrld.struct.read('structures/zh_12LayerCurvedWall.csv')
        with open('structures/zh_graph12LayerCurvedWall1.pkl', 'rb') as fh:
            plan=pickle.load(fh)
        isCurve = True
    elif mode == 'custom10':
        wrld.struct.read('structures/zh_12LayerCurvedWall.csv')
        with open('structures/zh_graph12LayerCurvedWall2.pkl', 'rb') as fh:
            plan=pickle.load(fh)
        isCurve = True
    numTotalCellsTBD = np.sum(wrld.struct.worldArray)
    
    # init OpenGL and pygame if needed.------------------------
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
        # glTranslatef(-2.5, -0.3, -2.74)
        glTranslatef(-4.5, -0.55, -2.74)
        # glTranslatef(-6.5, -0.3, -2.74)  # for large x-shapes.
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
    # -------------------------------------------------------
    '''
    Hold Actions and observations that go into grid filter
    '''
    
    actions=[]
    observations=[]
    u=''
    
    exits=[]
    starts=[]

    # initialize agents: plan graph and initial locations.
    for a in wrld.agents:
        a.set_plan_graph(plan)

    for a in wrld.agents:
        a.pose=Pose(a.start_loc)

    # ---------------------------------------------------

    # initialize the world structure map -----------------
    childNodesStart = [()]  # init the child nodes of the start.
    if isCurve: 
        mapGridBlockIdx = [[]]  # each row: height, grid coordinates, idx of block in the myBrickMap.map.
        mapGridLoc = [[]]
    for n in wrld.agents[0].plan_graph.nodes:
        if not wrld.agents[0].plan_graph.nodes[n]['start'] and n != childNodesStart[0]:
            wrld.struct[Pose(n)] = 0  # if this is not a start position, this place's height is assignd a 0.
        elif wrld.agents[0].plan_graph.nodes[n]['start']: # set the initial block to 2x1. Only enter once.
            childNodesStart = list(wrld.agents[0].plan_graph.successors(n))
            print(f"Start at {n}, pose {Pose(n)}, child nodes {childNodesStart}, len {len(childNodesStart)}, first child node {childNodesStart[0]}.")
            if len(childNodesStart) > 0:
                wrld.struct[Pose(childNodesStart[0])] = 1
                # establish connection between gridcell coordinates and the block.
                if isCurve: mapGridBlockIdx[0] = [1, (Pose(n).x, Pose(n).y), 0]
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
                    if isCurve:
                        dxdyInitialBlock = (childNodesStart[0][0] - n[0], childNodesStart[0][1] - n[1])
                        if dxdyInitialBlock == (1, 0):
                            blockPose[2] = -90
                        elif dxdyInitialBlock == (0, 1):
                            blockPose[2] = 0
                        elif dxdyInitialBlock == (-1, 0):
                            blockPose[2] = 90
                        elif dxdyInitialBlock == (0, -1):
                            blockPose[2] = 180
                    else:
                        blockPose[2] = 0.0 if n[0] == childNodesStart[0][0] else 90.0  # actual orientation.
                    myBrickMap.map = np.append(myBrickMap.map, blockPose).reshape(-1, 6)
                    # establish connection between gridcell coordinates and the block.
                    if isCurve: 
                        mapGridBlockIdx = np.vstack((mapGridBlockIdx, [1, (Pose(childNodesStart[0]).x, Pose(childNodesStart[0]).y), len(myBrickMap.map) - 1]))
                        locProximalTrans = hmRPYG(*blockPose[:3], blockPose[3:]).dot(np.array([-0.1, 0, 0, 1]))[:3]
                        locDistalTrans = hmRPYG(*blockPose[:3], blockPose[3:]).dot(np.array([0.1, 0, 0, 1]))[:3]
                        mapGridLoc[0] = [n, np.array([0, 0, blockPose[2], locProximalTrans[0], locProximalTrans[1], locProximalTrans[2]])]
                        mapGridLoc = np.vstack((mapGridLoc, [childNodesStart[0], np.array([0, 0, blockPose[2], locDistalTrans[0], locDistalTrans[1], locDistalTrans[2]])]))
                        for trans, dxdy in zip([(-0.1, -0.2), (0.1, -0.2), (-0.1, 0.2), (0.1, 0.2), (0.3, 0.0)], [(1, 0), (1, 1), (-1, 0), (-1, 1), (0, 2)]):
                            cellPose = hmRPYG(*blockPose[:3], blockPose[3:]).dot(np.array([trans[0], trans[1], 0, 1]))[:3]
                            dxdy = np.round(hmRPYG(0, 0, blockPose[2], np.array([0,0,0])).dot(np.array([dxdy[0], dxdy[1], 0, 1]))[:2])
                            mapGridLoc = np.vstack((mapGridLoc, [(a.pose.x + dxdy[0], a.pose.y + dxdy[1]), np.array([blockPose[0], blockPose[1], blockPose[2], cellPose[0], cellPose[1], cellPose[2]])]))
    # ----------------------------------------------------
    
    show_time=0
    show_delta=1  # default 100
    
    while True:
        
        if wrld.agents[0].my_time - show_time > show_delta:        
            wrld.show()
            show_time = wrld.agents[0].my_time
            # visualize using OpenGL ---------------------------
            if useOpenGL:
                glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)  # clear the screen.
                # interactive view angle.
                keyboardCtrl()
                drawFloor(vertices = floorRegion)
                # draw robot body for each agent.
                for i in range(numAgents):
                    myRobots[i].drawRobotBody(colored = True)
                    myRobots[i].propagateAllLegJointPoses()
                    myRobots[i].drawAllLegLinkagesOG()
                    if wrld.agents[i].has_brick:
                        # if the robot has a block draw it.
                        backBlockPose = myRobots[i].bodyPose
                        backBlockPose[-1] += 0.08
                        drawRigidBodyOG(hmRPYG(*backBlockPose[:3], backBlockPose[3:]).dot(myBrickMap.brickVertices))
                        drawBrickOG(myRobots[i].bodyPose, myBrickMap.brickVertices)
                # draw block.
                for pose in myBrickMap.map:
                    drawRigidBodyOG(hmRPYG(*pose[:3], pose[3:]).dot(myBrickMap.brickVertices))
                    drawBrickOG(pose, myBrickMap.brickVertices)
                # draw text.
                textToShow = "Wasted Travels - "
                for i, a in enumerate(wrld.agents):
                    uselessTravels = a.trip_cnt_wasted
                    textToShow += "Agent "+str(i)+": "+str(uselessTravels)+" | "
                renderTextOG(textToShow, (10, 20))
                textToShow = "No. Blocks: " + str(s_size)
                renderTextOG(textToShow, (10, 40))
                textToShow = "No. Gridcells TBD: "+str(numTotalCellsTBD - np.sum(wrld.struct.worldArray))
                renderTextOG(textToShow, (10, 60))
                pygame.display.flip()
                pygame.time.wait(4)  # default 5
            # --------------------------------------------------
            time.sleep(0.1)

        for i, a in enumerate(wrld.agents):
                
            a_obs=Observation(wrld.obs(a.pose))
            actns = a.pick_actions(a_obs, agents = wrld.agents)

            for u in actns:
                if u == 'p':
                    # modify the structure map
                    wrld.struct[a.pose] += 1
                    tempPose = copy.deepcopy(a.pose)
                    if a.pose.heading == heading.NORTH:
                        tempPose.y += 1
                    elif a.pose.heading == heading.EAST:
                        tempPose.x += 1
                    elif a.pose.heading == heading.SOUTH:
                        tempPose.y -= 1
                    elif a.pose.heading == heading.WEST:
                        tempPose.x -= 1
                    wrld.struct[tempPose] += 1
                    # translate block coordinates.
                    if useOpenGL:
                        if isCurve:  # TODO bug, only 5 blocks visible, duplicate blocks.
                            # find the parent node of the current location.
                            parentLoc = list(a.plan_graph.predecessors((a.pose.x, a.pose.y)))
                            currentLoc = (a.pose.x, a.pose.y)
                            if len(parentLoc) > 0:  # maybe meaningless. TODO the case when the robot is at the start.
                                parentLoc = parentLoc[0]
                                parentLocHeight = wrld.struct.worldArray[-parentLoc[1] - 1][parentLoc[0]]
                                # find the corresponding block's pose.
                                parentBlockIdx = [idx for idx, row in enumerate(mapGridBlockIdx) if row[0] == parentLocHeight and row[1] == parentLoc]
                                if len(parentBlockIdx) > 0:
                                    parentBlockIdx = parentBlockIdx[0]
                                    parentBlockIdx = mapGridBlockIdx[parentBlockIdx, -1]
                                    parentBlockPose = myBrickMap.map[parentBlockIdx]
                                    if parentLocHeight > wrld.struct[a.pose] - 1:
                                        pparentLoc = list(a.plan_graph.predecessors((parentLoc)))
                                        childLoc = list(a.plan_graph.successors((currentLoc)))
                                        if len(pparentLoc) > 0 or len(childLoc) > 0:
                                            
                                            pparentLoc = pparentLoc[0]
                                            childLoc = childLoc[0]
                                            tilt = a.plan_graph.edges[(parentLoc, currentLoc)]['tilt']
                                            if (a.plan_graph.edges[(parentLoc, currentLoc)]['tilt'] != a.plan_graph.edges[(pparentLoc, parentLoc)]['tilt']):
                                                tilt = (tilt + a.plan_graph.edges[(pparentLoc, parentLoc)]['tilt']) / 2
                                            '''
                                            if (a.plan_graph.edges[(parentLoc, currentLoc)]['tilt'] != a.plan_graph.edges[(currentLoc, childLoc)]['tilt']):
                                                tilt = (a.plan_graph.edges[(currentLoc, childLoc)]['tilt'] + a.plan_graph.edges[(pparentLoc, parentLoc)]['tilt']) / 2
                                            '''
                                            blockPose = placeTiltBlock(1, tilt, parentBlockPose)
                                            
                                        else:
                                            blockPose = placeTiltBlock(1, a.plan_graph.edges[(parentLoc, (a.pose.x, a.pose.y))]['tilt'], parentBlockPose)
                                    elif parentLocHeight == wrld.struct[a.pose] - 1:
                                        blockPose = placeTiltBlock(0, a.plan_graph.edges[(parentLoc, (a.pose.x, a.pose.y))]['tilt'] / 2, parentBlockPose)
                            else:  # at the start location.
                                assert len(parentLoc) == 0, "ERROR: Robot Attemps to place at the start location"
                                blockPose = placeTiltBlock(0, -5, myBrickMap.map[0])
                            # store the pose of each grid cell.
                            locProximalTrans = hmRPYG(*blockPose[:3], blockPose[3:]).dot(np.array([-0.1, 0, 0, 1]))[:3]
                            locDistalTrans = hmRPYG(*blockPose[:3], blockPose[3:]).dot(np.array([0.1, 0, 0, 1]))[:3]
                            mapGridLoc = np.vstack((mapGridLoc, [(a.pose.x, a.pose.y), np.array([0, 0, blockPose[2], locProximalTrans[0], locProximalTrans[1], locProximalTrans[2]])]))
                            mapGridLoc = np.vstack((mapGridLoc, [(tempPose.x, tempPose.y), np.array([0, 0, blockPose[2], locDistalTrans[0], locDistalTrans[1], locDistalTrans[2]])]))
                            if wrld.struct[a.pose] == 1:  # the first layer should append the adjacent pose linked to the grid cell.
                                for trans, dxdy in zip([(-0.1, -0.2), (0.1, -0.2), (-0.1, 0.2), (0.1, 0.2), (0.3, 0.0)], [(1, 0), (1, 1), (-1, 0), (-1, 1), (0, 2)]):
                                    cellPose = hmRPYG(*blockPose[:3], blockPose[3:]).dot(np.array([trans[0], trans[1], 0, 1]))[:3]
                                    dxdy = np.round(hmRPYG(0, 0, -90 * a.pose.heading.value, np.array([0,0,0])).dot(np.array([dxdy[0], dxdy[1], 0, 1]))[:2])
                                    mapGridLoc = np.vstack((mapGridLoc, [(a.pose.x + dxdy[0], a.pose.y + dxdy[1]), np.array([blockPose[0], blockPose[1], blockPose[2], cellPose[0], cellPose[1], cellPose[2]])]))
                        else:
                            blockPose = np.zeros(6).astype('float')
                            blockPose[4] = 0.5 * (myRobots[i].bodyPose[4] - tempPose.x * 0.2)  # actual y
                            blockPose[3] = 0.5 * (myRobots[i].bodyPose[3] + tempPose.y * 0.2)  # actual x
                            blockPose[5] = myBrickMap.brickThickness / 2 + (wrld.struct[a.pose] - 1) * myBrickMap.brickThickness # actual z of com.
                            blockPose[2] = 0.0 if (a.pose.heading == heading.NORTH or a.pose.heading == heading.SOUTH) else 90.0  # actual orientation.
                        myBrickMap.map = np.vstack((myBrickMap.map, blockPose.reshape(-1, 6)))
                        if isCurve:
                            mapGridBlockIdx = np.vstack((mapGridBlockIdx, [wrld.struct[a.pose], (a.pose.x, a.pose.y), len(myBrickMap.map) - 1]))
                            mapGridBlockIdx = np.vstack((mapGridBlockIdx, [wrld.struct[tempPose], (tempPose.x, tempPose.y), len(myBrickMap.map) - 1]))
                    # logging
                    s_size += 1
                    growth.append((a.my_time,s_size,a.pose))
                else:
                    n_pose=wrld.move(u,a.pose)
                    a.pose=n_pose
                    if useOpenGL:
                        if isCurve:
                            # if on structure
                            if wrld.struct[a.pose] > 0:
                                idx = [i for i, row in enumerate(mapGridLoc) if row[0] == (a.pose.x, a.pose.y)]
                                if len(idx) >= 2:
                                    idx = idx[-1]
                                elif len(idx) == 1:
                                    idx = idx[0]
                                myRobots[i].bodyPose = mapGridLoc[idx][-1]
                                myRobots[i].bodyPose[-1] = 0.1 + myBrickMap.brickThickness / 2 + (wrld.struct[a.pose] - 1) * myBrickMap.brickThickness # actual z of com.
                            else:
                                # TODO: at the corners, the diagonal neighbors are not considered.
                                idx = [i for i, row in enumerate(mapGridLoc) if row[0] == (a.pose.x, a.pose.y)]
                                if len(idx) > 0:
                                    idx = idx[0]
                                    myRobots[i].bodyPose = mapGridLoc[idx][-1]
                                    myRobots[i].bodyPose[2] -= 90 * a.pose.heading.value
                                    myRobots[i].bodyPose[-1] = 0.1 + myBrickMap.brickThickness / 2
                        else:
                            robotPose = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
                            robotPose[2] = -90.0 * a.pose.heading.value
                            robotPose[3] = 0.2 * a.pose.y
                            robotPose[4] = -0.2 * a.pose.x
                            robotPose[5] = 0.1 + myBrickMap.brickThickness / 2 + (wrld.struct[a.pose] - 1) * myBrickMap.brickThickness # actual z of com.
                            myRobots[i].bodyPose = robotPose


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

# TODO:
'''
1. add random noise to the robots' placement, as placement errors;
2. figure out how to measure the placement accuracy;
'''