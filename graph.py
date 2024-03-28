# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2018 Wawrzyniec Zipser, Maciej Kamiński (kaminski.maciej@gmail.com) Politechnika Wrocławska
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
__author__ = 'Wawrzyniec Zipser, Maciej Kamiński Politechnika Wrocławska'

import heapq

class Node(dict):
    # Node is an object witch may have some other node connected
    # consider this as kind of a dict
    def __init__(self,properties={}):
        self.update(properties)

    def __lt__(self,element):
        return id(self) < id(element)

    def __eq__(self,element):
        return self is element

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return str((id(self)/4)%100)

class Edge(dict):
    # edge or properties (dict)
    # weight is the weight name in properties
    def __init__(self,edge={},weight=None):
        self.update(edge)
        self.weight=getattr(edge,'weight',weight) # if edgie is Edge

    def __lt__(self,edge):
        assert self.weight and \
                (self.weight in self) and \
                (edge.weight in edge)
        return  self[self.weight] < edge[edge.weight]


    def __le__(self,edge):
        assert self.weight and \
                (self.weight in self) and \
                (edge.weight in edge)
        return  self[self.weight] <= edge[edge.weight]

    # here ==  must mean same edge not weight equality
    # we must provide as we provide hash
    def __eq__(self,element):
        return self is element

    def __hash__(self):
        return id(self)


# this can be a list or a heap
class EdgeSet(list):
    def heapify(self):
        #self.sort()
        heapq.heapify(self)
    def add(self,edge):
        #super(EdgeSet,self).append(edge) # preserve order
        #self.sort()
        heapq.heappush(self,edge)
    def pop(self):
        return heapq.heappop(self)
        #return super(EdgeSet,self).pop(0)


class Graph(object):
    # Graph is a list of nodes
    # Graph must have edges and nodes
    def __init__(self,is_directed=True):
        self.is_directed = is_directed #

        self.nodes=set()
        self.edges=set()

        self.edge_connection={} # {Edge:(node1,node2)..
        self.connection_edges={} # {(node1,node2):EdgeSet([Edge,edge..])..

        self.node_outgoing_edges={} #{Node:EdgeSet([Edge,edge..])..}
        self.node_ingoing_edges={} #{Node:EdgeSet([Edge,edge..]..}

    def add_edge(self,node1,node2,edge):
        assert isinstance(edge,Edge)
        assert node1 in self.nodes
        assert node2 in self.nodes

        connection = self.connection(node1,node2)

        self.edges.add(edge)
        self.edge_connection[edge]=connection
        if connection not in self.connection_edges:
            self.connection_edges[connection]=EdgeSet()
        self.connection_edges[connection].add(edge)

        self.node_outgoing_edges[node1].add(edge)
        self.node_ingoing_edges[node2].add(edge)
        if not self.is_directed:
            self.node_outgoing_edges[node2].add(edge)
            self.node_ingoing_edges[node1].add(edge)


    def add_node(self,node):
        assert isinstance(node,Node)
        node.graph=self
        self.nodes.add(node)
        self.node_outgoing_edges[node]=EdgeSet()
        self.node_ingoing_edges[node]=EdgeSet()

    def order_by(self,name):
        for e in self.edges:
            e.weight=name
        for n,es in self.node_ingoing_edges.items():
            es.heapify()
        for n,es in self.node_outgoing_edges.items():
            es.heapify()
        for n,es in self.connection_edges.items():
            es.heapify()

    def connection(self,node1,node2):
        return (node1,node2) if self.is_directed or node1<node2 else (node2,node1)
        # basically connection is alwais a tuple
        # but if graph is undirected than we use directed/orderd tuple
        # therefor we can alwais describe connection

    def connected(self,node1,node2):
        if self.connection(node1,node2) in self.connection_edges:
            return True
        else:
            return False
