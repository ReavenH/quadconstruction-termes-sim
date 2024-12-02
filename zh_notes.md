# Notes of TERMES Simulator

## 1. Data Structure of the Input Plan Graph
The input plan graph is the output of the compiler, which is essentially a directed graph (networkX.DiGraph) representing the locations of the structure (nodes of the DiGraph) and the paths (direction and probabilities of edges) for each agent to choose.

**How to visit each node**

```python
# read the DiGraph from pickle file.
with open('structures/bfd_output_graph_Castle_opt_10_100.pkl','rb') as fb:
    plan = pickle.load(fb)
```

```python
# check the attributes of a DiGraph object.
dir(plan)
```

```bash
['__class__', '__contains__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_adj', '_node', '_pred', '_succ', 'add_edge', 'add_edges_from', 'add_node', 'add_nodes_from', 'add_weighted_edges_from', 'adj', 'adjacency', 'adjlist_inner_dict_factory', 'adjlist_outer_dict_factory', 'clear', 'clear_edges', 'copy', 'degree', 'edge_attr_dict_factory', 'edge_subgraph', 'edges', 'get_edge_data', 'graph', 'graph_attr_dict_factory', 'has_edge', 'has_node', 'has_predecessor', 'has_successor', 'in_degree', 'in_edges', 'is_directed', 'is_multigraph', 'name', 'nbunch_iter', 'neighbors', 'node_attr_dict_factory', 'node_dict_factory', 'nodes', 'number_of_edges', 'number_of_nodes', 'order', 'out_degree', 'out_edges', 'pred', 'predecessors', 'remove_edge', 'remove_edges_from', 'remove_node', 'remove_nodes_from', 'reverse', 'size', 'subgraph', 'succ', 'successors', 'to_directed', 'to_directed_class', 'to_undirected', 'to_undirected_class', 'update']
```
The above are the internal methods of `networkx.DiGraph`, which are not customized.

```python
# view the nodes
plan.nodes
```
```bash
NodeView(((0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2), (0, 3), (0, 16), (1, 16), (0, 17), (0, 18), (0, 19), (2, 0), (2, 1), (2, 2), (1, 3), (1, 6), (2, 6), (1, 7), (1, 12), (2, 12), (1, 13), (2, 16), (1, 17), (1, 18), (1, 19), (3, 0), (3, 1), (3, 2), (2, 3), (2, 4), (2, 5), (2, 7), (2, 8), (2, 11), (3, 11), (2, 13), (2, 14), (2, 15), (2, 17), (2, 18), (2, 19), (4, 2), (3, 8), (4, 11), (3, 17), (3, 18), (3, 19), (5, 2), (4, 8), (5, 11), (4, 17), (6, 2), (5, 8), (6, 11), (5, 17), (6, 1), (7, 1), (7, 2), (6, 8), (6, 17), (6, 18), (8, 2), (7, 17), (7, 18), (9, 2), (8, 17), (9, 1), (10, 1), (10, 2), (9, 17), (9, 18), (11, 2), (10, 17), (10, 18), (12, 2), (11, 17), (12, 1), (13, 1), (13, 2), (12, 17), (12, 18), (14, 2), (13, 3), (13, 16), (13, 17), (13, 18), (15, 2), (14, 3), (14, 16), (14, 17), (16, 2), (15, 3), (15, 16), (15, 17), (16, 0), (17, 0), (16, 1), (17, 1), (17, 2), (16, 3), (16, 16), (16, 17), (16, 18), (16, 19), (18, 0), (18, 1), (18, 2), (17, 3), (17, 4), (17, 5), (17, 6), (18, 6), (17, 7), (17, 8), (17, 9), (18, 9), (17, 10), (17, 11), (17, 12), (18, 12), (17, 13), (17, 14), (17, 15), (17, 16), (18, 16), (17, 17), (17, 18), (17, 19), (19, 0), (19, 1), (19, 2), (18, 3), (18, 7), (18, 10), (18, 13), (19, 16), (18, 17), (18, 18), (18, 19), (19, 3), (19, 17), (19, 18), (19, 19)))
```
There are 144 nodes in the graph.

```python
# check the attributes of each node
plan.nodes[(0, 0)]
```
```bash
{'height': 7, 'start': False, 'exit': False, 'xy-location': (2, 2)}
```
The attributes of each node is stored in a dictionary.

```python
# check all the edges of the DiGraph.
plan.edges
```
```bash
OutEdgeView([((0, 0), (1, 0)), ((1, 0), (2, 0)), ((0, 1), (1, 1)), ((0, 1), (0, 0)), ((1, 1), (2, 1)), ((1, 1), (1, 0)), ((0, 2), (1, 2)), ((0, 2), (0, 1)), ((1, 2), (2, 2)), ((1, 2), (1, 1)), ((0, 3), (0, 2)), ((0, 16), (1, 16)), ((1, 16), (2, 16)), ((0, 17), (0, 16)), ((0, 18), (0, 17)), ((0, 19), (0, 18)), ((2, 0), (3, 0)), ((2, 1), (3, 1)), ((2, 1), (2, 0)), ((2, 2), (3, 2)), ((2, 2), (2, 1)), ((1, 3), (0, 3)), ((1, 3), (1, 2)), ((1, 6), (2, 6)), ((2, 6), (2, 5)), ((1, 7), (1, 6)), ((1, 12), (2, 12)), ((2, 12), (2, 11)), ((1, 13), (1, 12)), ((2, 16), (2, 15)), ((1, 17), (0, 17)), ((1, 17), (1, 16)), ((1, 18), (0, 18)), ((1, 18), (1, 17)), ((1, 19), (0, 19)), ((1, 19), (1, 18)), ((3, 0), (3, 1)), ((3, 1), (3, 2)), ((3, 2), (4, 2)), ((2, 3), (1, 3)), ((2, 3), (2, 2)), ((2, 4), (2, 3)), ((2, 5), (2, 4)), ((2, 7), (1, 7)), ((2, 7), (2, 6)), ((2, 8), (2, 7)), ((2, 11), (3, 11)), ((3, 11), (4, 11)), ((2, 13), (1, 13)), ((2, 13), (2, 12)), ((2, 14), (2, 13)), ((2, 15), (2, 14)), ((2, 17), (1, 17)), ((2, 17), (2, 16)), ((2, 18), (1, 18)), ((2, 18), (2, 17)), ((2, 19), (1, 19)), ((2, 19), (2, 18)), ((4, 2), (5, 2)), ((3, 8), (2, 8)), ((4, 11), (5, 11)), ((3, 17), (2, 17)), ((3, 17), (3, 18)), ((3, 18), (2, 18)), ((3, 18), (3, 19)), ((3, 19), (2, 19)), ((5, 2), (6, 2)), ((4, 8), (3, 8)), ((5, 11), (6, 11)), ((4, 17), (3, 17)), ((6, 2), (7, 2)), ((6, 2), (6, 1)), ((5, 8), (4, 8)), ((5, 17), (4, 17)), ((6, 1), (7, 1)), ((7, 1), (7, 2)), ((7, 2), (8, 2)), ((6, 8), (5, 8)), ((6, 17), (5, 17)), ((6, 18), (6, 17)), ((8, 2), (9, 2)), ((7, 17), (6, 17)), ((7, 17), (7, 18)), ((7, 18), (6, 18)), ((9, 2), (10, 2)), ((9, 2), (9, 1)), ((8, 17), (7, 17)), ((9, 1), (10, 1)), ((10, 1), (10, 2)), ((10, 2), (11, 2)), ((9, 17), (8, 17)), ((9, 18), (9, 17)), ((11, 2), (12, 2)), ((10, 17), (9, 17)), ((10, 17), (10, 18)), ((10, 18), (9, 18)), ((12, 2), (13, 2)), ((12, 2), (12, 1)), ((11, 17), (10, 17)), ((12, 1), (13, 1)), ((13, 1), (13, 2)), ((13, 2), (14, 2)), ((13, 2), (13, 3)), ((12, 17), (11, 17)), ((12, 18), (12, 17)), ((14, 2), (15, 2)), ((14, 2), (14, 3)), ((13, 17), (12, 17)), ((13, 17), (13, 16)), ((13, 17), (13, 18)), ((13, 18), (12, 18)), ((15, 2), (16, 2)), ((15, 2), (15, 3)), ((14, 3), (13, 3)), ((14, 16), (13, 16)), ((14, 17), (13, 17)), ((14, 17), (14, 16)), ((16, 2), (17, 2)), ((16, 2), (16, 1)), ((16, 2), (16, 3)), ((15, 3), (14, 3)), ((15, 16), (14, 16)), ((15, 17), (14, 17)), ((15, 17), (15, 16)), ((16, 0), (17, 0)), ((17, 0), (18, 0)), ((17, 0), (17, 1)), ((16, 1), (17, 1)), ((16, 1), (16, 0)), ((17, 1), (18, 1)), ((17, 1), (17, 2)), ((17, 2), (18, 2)), ((17, 2), (17, 3)), ((16, 3), (15, 3)), ((16, 16), (15, 16)), ((16, 17), (15, 17)), ((16, 17), (16, 16)), ((16, 18), (16, 17)), ((16, 19), (16, 18)), ((18, 0), (19, 0)), ((18, 0), (18, 1)), ((18, 1), (19, 1)), ((18, 1), (18, 2)), ((18, 2), (19, 2)), ((18, 2), (18, 3)), ((17, 3), (16, 3)), ((17, 3), (17, 4)), ((17, 4), (17, 5)), ((17, 5), (17, 6)), ((17, 6), (18, 6)), ((17, 6), (17, 7)), ((18, 6), (18, 7)), ((17, 7), (17, 8)), ((17, 8), (17, 9)), ((17, 9), (18, 9)), ((17, 9), (17, 10)), ((18, 9), (18, 10)), ((17, 10), (17, 11)), ((17, 11), (17, 12)), ((17, 12), (18, 12)), ((17, 12), (17, 13)), ((18, 12), (18, 13)), ((17, 13), (17, 14)), ((17, 14), (17, 15)), ((17, 15), (17, 16)), ((17, 16), (16, 16)), ((17, 16), (18, 16)), ((17, 16), (17, 17)), ((18, 16), (19, 16)), ((18, 16), (18, 17)), ((17, 17), (16, 17)), ((17, 17), (17, 18)), ((17, 18), (16, 18)), ((17, 18), (17, 19)), ((17, 19), (16, 19)), ((19, 0), (19, 1)), ((19, 1), (19, 2)), ((19, 2), (19, 3)), ((18, 3), (17, 3)), ((18, 7), (17, 7)), ((18, 10), (17, 10)), ((18, 13), (17, 13)), ((19, 16), (19, 17)), ((18, 17), (17, 17)), ((18, 17), (18, 18)), ((18, 18), (17, 18)), ((18, 18), (18, 19)), ((18, 19), (17, 19)), ((19, 3), (18, 3)), ((19, 17), (18, 17)), ((19, 17), (19, 18)), ((19, 18), (18, 18)), ((19, 18), (19, 19)), ((19, 19), (18, 19))])
```
The above contains 194 pairs of directed edges, $((x_1, y_1), (x_2, y_2))$. Since the graph is directed, the two tuples are not interchangeable (e.g. ((1, 2), (2, 1)) and ((2, 1), (1, 2)) are different in their direction).
```python
# visit the attributes of each edge.
plan.edges[((11, 17), (10, 17))]
```
```bash
{'prob': 0.9999999999999999}
```

# 2. Objects

## 2.1 `class` Pose 
primarily a class to store the (x, y, z, heading) of an agent, as well as the methods to relative position calculation.

## 2.2 `class` World
The behaviors of a group of `Agents` interacting with the `Structure`.

## 2.3 `class` Structure
- `self.read(self, fname, padding=2)`: Reads the legitimate structure file, and pads the structure by 2 grid for each side (by default, `padding=2`). Legitimate suffix: `idx`, `csv`, `pkl`, `2da`.
- `self.show(self, pose=None)`: visualizes the structure and the agent. `pshow` is the arrow indicating the agents heading. The visualization is done by printing the rows of the structure array (`worldArray`).
- `self.obs(self, p:Pose)`: the observation of each `Agent` of its 4 near neighbors. `rp` hold values of observations froward left backward right.


## 2.4 `class` Agent
The object of each robot, each `Agent` is aware of the path plan, and decides the next action.
- `self.set_plan_graph(self, plan_graph)`: 
    - stores each node's row-column position pair (i.e. index of this node) into its dictionary (created a new key `row-col-coordinates`);
    - extracts each node's x-y location pair into a temporary dictionary `node_trans` (`{(row, column): (x, y), ...}`);
    - stores each node into `self.plan_graph.nodes`, but the index of `self.plan_graph` is the actual x-y location pair instead of the row-column pairs, and it has an extra key `row-col-coordinates` as mentioned.
    - converts the row-column pair representation for edge into x-y pairs, and store the converted edges in `self.plan_graph.edges`;
    - stores the start x-y location into `self.start_loc`;
    - iterate over every node, store its neighbor (x-y locations) which is not included in the `self.plan_graph.nodes` into `e_nbrs`, these neighbors are then added to the `self.plan_graph.nodes`, with `{'height': 0, 'start': False, 'exit': False, 'xy-location': e_nbr, 'row-col-coordinates': (-1, -1)}`, where `e_nbr` is the x-y location of the neighbor to be added. Besides, each (loc, neighbor) pair will be added to the `self.plan_graph_edges` in the direction `loc -> neighbor`, with `{'prob': 1/len(e_nbrs)}` (uniform distribution over all neighbors of loc, which are not on the structure graph);
    - reverse the DiGraph and store in `self._parent_digraph`.
  - `pick_actions(self, observations, debug_print=False)`: It returns a string containing characters (0~2 characters) representing the next action of the agent.
    - Critical to know the structure of `Observation`.
    - If the agent is on the floor and not on the structure, it will:
      - If the agent is near the start location (at one of the 4 near neighbors), it will go to the start location and pick up a block. **Next to start checking is on top of all.** The function will return if the agent is next to the start.
      - If it is not near the start location, it will follow the wall.
    - If the agent is on the structure, check the heading of agent, and assign `dxdy` values.
      - 
        ```python
        dxy_heading_dir = {
            (dx1, dy1): angle1,
            (dx2, dy2): angle2,
            ...
        }
        ```
      - Initialize the children and parent nodes with respect to the current node at `loc`. 
        - If the agent is on the nodes of the plan graph:
          -
            ```python 
           children=tuple(n for n in self.plan_graph[loc])  # all neighboring nodes of loc, with edge attributes.
                parents=tuple(n for n in self._parent_digraph[loc])
            ```
        - If not on the nodes of the plan graph: init as empty tuples.
        - get the difference in (x, y) and the height between the current location and the children and parent nodes.
        - If the agent's height is less than the height of the plan graph, build a block (with two exceptions).
        - If the agent is not near exit, choose the path using the given probabilities on the edge or just uniformly choose one from its children nodes. 
        - Get the action from `dx_dy_to_turn`

# 3. TermSim.py
Input can be a series of instructions. Use `f, r, l` to control forward, left and right rotations, use `n` to automatically decide the action to take based on the local rules.

In the first loop:
- For `f, r, l`: update pose of agent, update the visualization, store the action, store the observation.
- For `n`: store the observation and make a decision based on observation, add 1 to the grid if `p` is decided (add 1 layer of block).

In the second loop:
- the robot decides the action to take automatically.
