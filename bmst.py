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
        if self.directed:
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
        if self.directed:
            edge.end[prefix+"ingoing"].append(edge)
        else:
            edge.end[prefix+"outgoing"].append(edge)
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

class LayerGraph(Graph):
    def __init__(self,layer,weight_colum_name,both_ways=True):

        # we create Graph from layer
        # The linestring ends describes Graph nodes
        self.node_geometries=[] # list for node geometries
                            # (geometry index is same as node index in self.nodes)
                            # seeds are stored also separately from Nodes
        self.weight_colum_name = weight_colum_name

        # data provider
        data_provider = layer.dataProvider()
        features = data_provider.getFeatures()
        # extraction of weight parameter from features table
        weights = [feature["weight"] for feature in features]
        geometries = [feature.geometry() for feature in features]
        ok_geometries = [geometry.convertToSingleType() for geometry in geometries ]
        assert all(ok_geometries)

        for geometry in geometries:
            start = geometry_seed_node(geometry.asPolyline()[0])
            end = geometry_seed_node(geometry.asPolyline()[-1])
            self.add_edge(Edge(start,end,{prefix+"weight":0}))
            if both_ways:
                self.add_edge(Edge(end,start,{prefix+"weight":0}))

    def geometry_seed_node(self,geometry):
        # function gets real geometry
        # returns new or existing Node with this geoetry as property
        if geometry not in self.node_geometries:
            node = Node({prefix+"geometry":geometry})
            self.add_node(node)
            return node
        else:
            node_index = self.node_geometries.index(geometry)
            return self.nodes[node_index]

#class CSVGraph(Graph): ?
class Bmst(Graph):
    # the main idea of this class will be to represent
    # supernodes and its relations
    # supernodes will be created out of input graph nodes
    # supernodes contain multiple nodes agregated
    # supernodes represent algorithm clustering behaviour on each phase
    # We will refer to Bmst nodes as supernodes
    def __init__(self,graph,phase=1):
        # initiate Graph
        super().__init__()
        # during init we will create supernode for each input graph node and
        for node in graph:
            # Supernode contains one node at beginning
            supernode = Node({prefix+"bmst_nodes":[node]}) # this is supernode
            self.add_node(supernode)
            # each graph node is in one supernode
            # we denote
            node[prefix+"bmst_supernode"] = supernode

        # we consider only edges that are not self-connecting
        # connects two diffrent nodes
        proper_edges = [edge for edge in graph.edges if edge.start != edge.end]

        # each edge that has supernodes as both start and end
        # is considered as a superedge
        for edge in proper_edges:
            superedge = Edge(\
                            edge.start[prefix+"bmst_supernode"],
                            edge.end[prefix+"bmst_supernode"],
                            {prefix+"original_edge":edge,prefix+"weight":edge[prefix+"weight"]}
                            )
            self.add_edge(superedge)

        # later we will merge supernodes according to the shortest edge
        # get each node minimum outgoing edge
        # but only if node has outgoing edges
        self.minimal_edges=[
            min(
                supernode[prefix+"outgoing"],
                key = lambda x:x[prefix+"weight"])
            for supernode in self
            if supernode[prefix+"outgoing"]
        ]

        # minimal_edges is empty then no new supernode will appear
        #
        if not self.minimal_edges:
            # we have no edges we put phase to
            self.edges_with_phase = []
        else:
            # merge start and end nodes of the minimum outgoing edge
            # into one supernode
            # this is the realization of algorithm behaviour
            for superedge in self.minimal_edges:
                self.merge_nodes(superedge.start,superedge.end)
            # After this step we have supernodes sucessfuly created
            # each node is in some supernode
            # supernode contains at least two nodes
            # the phase is fulfilled


            # computing next_phase
            self.next_phase = Bmst(self,phase+1)
            # after this our supernode[prefix+"phase_id"] is set
            # our edges don't have proper phase set for phase grater than our (current) phase
            # next_phase.edges_with_phase list contains edges from the next_phase object
            # list refers to their edges where phase is just set and updated (in next_phase level object)

            # let's revrite phase from edges created in next_phase
            # into our edges (edges in our object)
            for supersuperedge in self.next_phase.edges_with_phase:
                # we must get our superedges from next_phase supersuperedge
                # as it is the original egde that next_phase edge is created on
                # same as we create our superege as original (on top of) graph edge
                # and me must append phase from next_phase edge into our edge
                # their phase shoud be our phase
                supersuperedge[prefix+"original_edge"][prefix+"phase"] = supersuperedge[prefix+"phase"]

            # now our edges_with_phase are
            self.edges_with_phase = [
                supersuperedge[prefix+"original_edge"]
                for supersuperedge in self.next_phase.edges_with_phase
            ]

            # let's put current phase in edge from minimal_edges
            for minimal_edge in self.minimal_edges:
                minimal_edge[prefix+"phase"] = phase

            #lets denote that now also minimal_edges have phase stated
            self.edges_with_phase.extend(self.minimal_edges)

        if phase == 1:
            for node in graph:
                node[prefix+"bmst_supernode"] = self._containg_supenodes_id(node)


    def merge_nodes(self,supernode,included_supernode):
        # nodes merging
        super().merge_nodes(supernode,included_supernode)

        # supernode now must contain all nodes from included_supernode
        supernode[prefix+"bmst_nodes"].extend(included_supernode[prefix+"bmst_nodes"])

        # uptate each node in included_supernode to point proper node they are in
        for node in included_supernode[prefix+"bmst_nodes"]:
            node[prefix+"bmst_supernode"] = supernode

    def _containg_supenodes_id(self,supernode):
        # returns a list of id of supernodes on this and higher phase so:
        # [supernode_id,supernode_id_that_contains_it, supernode_id_that_contains_that_contains ...]
        if prefix+"bmst_supernode" not in supernode:
            return []
        else:
            id=supernode[prefix+"id"]
            return [id]+self._containg_supenodes_id(supernode[prefix+"bmst_supernode"])
