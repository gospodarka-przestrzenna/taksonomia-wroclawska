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
prefix="___dw_"

class Node(dict):
    # Node is an object witch may have some property
    # consider this as kind of a dict
    def __init__(self,properties={}):
        self.update(properties)

class Edge(dict):
    # Edge sets two Nodes in relation and
    # asigns properties to this relation
    # so this is dict with start end end (a Nodes)
    def __init__(self,start,end,properties={}):
        assert type(start)==Node
        assert type(end)==Node
        self.start=start
        self.end=end
        self.update(properties)

class Graph(list):
    # Graph is a list of nodes
    # Graph must have edges and nodes
    def __init__(self):
        #self.nodes=[] # list of Node objects
        self.edges=[] # list of Edge objects
        # with each edge  index

    def add_node(self,node):
        assert type(node)==Node
        if node in self:
            return
        node_idx=len(self) # the node id
        node[prefix+"id"] = node_idx
        node[prefix+"outgoing"] = []
        node[prefix+"ingoing"] = []
        self.append(node)

    def add_edge(self,edge):
        assert type(edge)==Edge
        self.add_node(edge.start)
        self.add_node(edge.end)

        edge.start[prefix+"outgoing"].append(edge)
        edge.end[prefix+"ingoing"].append(edge)

        self.edges.append(edge)

    def merge_nodes(node,included_node):
        # do nothing if this is same node
        if node==included_node:
            return

        # outgong edges from included_node are now
        # edges of the node
        for included_edge in included_node[prefix+"outgoing"]:
            included_edge.start = node
            node[prefix+"outgoing"].append(included_edge)

        # ingong edges from included_node are now
        # edges of the node
        for included_edge in included_node[prefix+"ingoing"]:
            included_edge.end = node
            node[prefix+"ingoing"].append(included_edge)
        # The included_node object diappears
        # node with this id is now None
        self[included_supernode[prefix+"id"]]=Node

    def __iter__(self):
        return iter([elemet for element in self if element is not None])


class LayerGraph(Graph):
    def __init__(self,layer,weight_colum_name,both_ways=True):
        # we create Graph from layer
        # The linestring ends describes Graph nodes
        self.node_geometries=[] # list for node geometries
                            # (geometry index is same as node index in self.nodes)
                            # seeds are stored also separately from Nodes
        self.weight_colum_name=weight_colum_name

        # data provider
        data_provider=layer.dataProvider()
        features=data_provider.getFeatures()
        geometries=[feature.geometry() for feature in features]
        ok_geometries=[geometry.convertToSingleType() for geometry in geometries ]
        assert all(ok_geometries)

        for geometry in geometries:
            start=geometry_seed_node(geometry.asPolyline()[0])
            end=geometry_seed_node(geometry.asPolyline()[-1])
            self.add_edge(Edge(start,end,{prefix+"weight":0}))
            if both_ways:
                self.add_edge(Edge(end,start,{prefix+"weight":0}))

    def geometry_seed_node(self,geometry):
        # function gets real geometry
        # returns new or existing Node with this geoetry as property
        if geometry not in self.node_geometries:
            node=Node({prefix+"geometry":geometry})
            self.add_node(node)
            return node
        else:
            node_index=self.node_geometries.index(geometry)
            return self.nodes[node_index]

#class CSVGraph(Graph): ?

class Bmst(Graph):
    # the main idea of this class will be to represent
    # supernodes and its relations
    # supernodes will be created out of input graph nodes
    # supernodes contains multiple nodes agregated
    # supernodes represents algorithm clustering behaviour on ech phase
    # We will refer to Bmst nodes as supernodes
    def __init__(self,graph,phase_column_name):
        # during init we will create supernode for each input graph node and
        for node in graph:
            # Supernode contains one node at beginning
            self.add_node(
                Node({prefix+"bmst_nodes":[node]}) # this is supernode
            )

            # each graph node is in one sumernode
            # we denote
            node[prefix+"bmst_supernode_in"]=supernode

        proper_edges=[edge for edge in graph.edges if edge.start != edge.end]

        for edge in proper_edges:
            superedge=Edge(\
                            edge.start[prefix+"bmst_supernode"],
                            edge.end[prefix+"bmst_supernode"],
                            edge.properties,
                            )
            self.add_edge(superedge)

        # later we will merge supernodes according to the shortes edge

        # get each node minimum outgoing edge
        minimal_edges=[
            min(
                supernode[prefix+"outgoing"],
                key=lambda x:x[prefix+"weight"])
            for supernode in self
            if len(supernode[prefix+"outgoing"])>0
        ]

        for edge in minimal_edges:
            self.merge_nodes(edge.start,edge.end)

        if len(minimal_edges)==0:
            return self
        else:
            return Bmst(self)


    def merge_nodes(self,supernode,included_supernode):
        # nodes merging
        super().merge_nodes(supernode,included_supernode)

        # supernode now must contain all nodes from included_supernode
        supernode[prefix+"bmst_nodes"].extend(included_supernode[prefix+"bmst_nodes"])

        # uptate each node in included_supernode to point proper node they are in
        for node in included_supernode[prefix+"bmst_nodes"]:
            node[prefix+"bmst_supernode"]=supernode
