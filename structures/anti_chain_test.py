# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 02:42:39 2023

@author: nen38
"""

import networkx as nx

def upper_comb(a,b,g):
    n=set(a+b)
    down=set()
    for e in n:
        down.update(nx.ancestors(g,e))
    return n - down
        