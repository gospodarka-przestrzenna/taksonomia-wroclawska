# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2018 Maciej Kamiński (kaminski.maciej@gmail.com) Politechnika Wrocławska
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
###############################################################################
__author__ = 'Maciej Kamiński Politechnika Wrocławska'
prefix = "___dw_"

class Node(dict):
    # Node is an object witch may have some property
    # consider this as kind of a dict
    def __init__(self,properties={}):
        self.update(properties)


class Edge(dict):
    # Edge sets two Nodes in relation and
    # asigns properties to this relation
    # so this is dict with start and end (Nodes)
    def __init__(self,start,end,properties={}):
        assert type(start) == Node
        assert type(end) == Node
        self.start = start
        self.end = end
        self.update(properties)

    # def end(self,node):
    #     # or maybe another end /
    #     # function returns the other end when start is node
    #     # this is useful in non directed graphs where node descibed end
    #     # might be a self.start node
    #     if node == self.start:
    #         return self.end
    #     elif node == self.end:
    #         return self.start
    #     else:
    #         raise ValueError("node might be only start or end")
    #
    # def end_set(self,node,node_to_set):
    #     # or maybe another end /
    #     # function returns the other end when start is node
    #     # this is useful in non directed graphs where node descibed end
    #     # might be a self.start node
    #     if node == self.start:
    #         self.end=node_to_set
    #     elif node == self.end:
    #         self.start=node_to_set
    #     else:
    #         raise ValueError("node might be only start or end")

class Graph(list):
    # Graph is a list of nodes
    # Graph must have edges and nodes
    def __init__(self,directed=True):
        #self.nodes=[] # list of Node objects
        self.edges = [] # list of Edge objects
        # with each edge  index
        self.directed = directed

    def add_node(self,node):
        assert type(node) == Node
        if node in self:
            return
        # the node id has the same value as the length of the list
        # in the moment of addition
        node_idx = len(self)
        node[prefix+"id"] = node_idx
        node[prefix+"outgoing"] = []
        node[prefix+"ingoing"] = []
        self.append(node)

    def add_edge(self,edge):
        assert type(edge) == Edge
        # both edge's stat and end are added to the Graph list of nodes
        self.add_node(edge.start)
        self.add_node(edge.end)
        # both edge's start and end are also added
        # to the edge class start and end dictionaries with specific keys
        edge.start[prefix+"outgoing"].append(edge)
        edge.end[prefix+"ingoing"].append(edge)
        # given edge is added to the edges list of Graph
        self.edges.append(edge)

    def merge_nodes(self,node,included_node):
        # do nothing if both given nodes are the same one
        # nothing to merge
        if node == included_node:
            return

        # outgong edges from included_node are now
        # edges of the node
        for included_edge in included_node[prefix+"outgoing"]:
            included_edge.start = node
            node[prefix+"outgoing"].append(included_edge)

        # ingong edges to included_node are now
        # edges of the node
        for included_edge in included_node[prefix+"ingoing"]:
            included_edge.end = node
            node[prefix+"ingoing"].append(included_edge)
        # The included_node object diappears
        # node with this id is now none
        self[included_node[prefix+"id"]] = None

    def __iter__(self):
        return iter([element for element in super().__iter__() if element is not None])
