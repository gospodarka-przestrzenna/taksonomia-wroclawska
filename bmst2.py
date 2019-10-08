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

from .graph import Graph,Node,Edge

class Bmst(Graph):
    # the main idea of this class will be to copy Graph
    # and produce supernode at each level
    # supernodes are the node that are connected
    # supernodes contain multiple nodes (supernodes) agregated
    # supernodes represent algorithm clustering behaviour on each phase

    # We provide graph to be copied
    # as well as weight name and new names for step in edge
    # and name of the supernode that node is in for each step
    def __init__(self,graph,weight_name='weight',supernode_name='supernode',phase_name='phase'):
        assert isinstance(graph,Graph)

        self.weight_name = weight_name
        self.supernode_name = supernode_name
        self.phase_name = phase_name
        self.supernode_id=lambda x: id(x) # function taht returns some identifier for describing supernode
        self.copiednodes={}

        # at first we copy original graph to self as self is a graph
        # this graph will be new layer later
        super().__init__(graph.is_directed)
        for node in graph.nodes:
            # copy node's name and properties
            copynode=Node(node)
            self.add_node(copynode)
            copynode["__original_nodes"] = [copynode]
            copynode[self.supernode_name] = [self.supernode_id(copynode)]
                        # this list will be used later on each lavel
                        # it will describe supernode that contains this node
                        # [supernode_on_level0 that's just me , supernode_on_level1 some supernode ,... ]

            self.copiednodes[node]=copynode          # we will need this to properly copy edges

        for edge in graph.edges:
            # copy node and properties
            copyedge=Edge(edge,weight=self.weight_name)
            n1,n2=graph.edge_connection[edge]
            self.add_edge(self.copiednodes[n1],self.copiednodes[n2],copyedge)
            copyedge[self.phase_name]=0 # if edge will be used we attache phase nuber to it

        self.__bmst_step(self,1)
        # we dont need this so DELETE
        for node in self.nodes:
             del(node["__original_nodes"])

        # we may rewrite this list as set of columns
        maximum_supernode=max(len(node[self.supernode_name]) for node in self.nodes)
        for node in self.nodes:
            for i in range(maximum_supernode):
                node[self.supernode_name+str(i)]=node[self.supernode_name][i]
                del(node[self.supernode_name])

    def __bmst_step(self,graph,phase):
        # print(phase,graph)
        node_nodeset={} # {node1:{node1, node3 ,node77 ...} node2:{node2 } node44:{node1, node3 ,node77 ...}}
        # With each note a set of node is releated
        # Each edge merges only two sets
        # every node is used
        # print(graph.nodes)
        for node in graph.nodes:
            # print("node: ",node)
            # no outgoing edge ?
            if len(graph.node_outgoing_edges[node]) == 0:
                merge_nodes[node]=[node] # meybe node will be only one as new supernode
                continue
            # if there are edge let's grab one
            # and put them back in place
            e1=graph.node_outgoing_edges[node].pop()
            graph.node_outgoing_edges[node].add(e1)
            # lets see if there is another edge inside ?
            # As heap preserves insert order
            # if there is more than one shortesedge we will find it out
            e2=graph.node_outgoing_edges[node].pop()
            graph.node_outgoing_edges[node].add(e2)

            if (e2<=e1 and e1<=e2) and (e1 is not e2): # they are two different edges equal in value
                raise ValueError(("Two edges must not have same weight: ",e1,e2))

            # lets use this edge in this phase
            e1[self.phase_name]=phase

            n1,n2=graph.edge_connection[e1]
            # print('used_edge',n1,n2)
            # let's make set of nodes that will represent future supernode
            # we alwais combine only two sets of n1 and n2
            l1=node_nodeset.get(n1,[n1])
            l2=node_nodeset.get(n2,[n2])
            if l1==l2: # we may end up with already connected nodes (action is no necessairy then)
                continue
            lcombined=l1+l2
            # print(l1,l2)
            # print(lcombined)
            # and later designate this set to all their containing nodes
            for n in lcombined:
                node_nodeset[n]=lcombined
        # print(node_nodeset)
        # this graf will be super_graph in this level
        # we create graph from the sets computed above
        # each set well be supernode
        super_graph=Graph(graph.is_directed)
        # copies nodes it will become supernodes on the current level
        id_nodesets={id(nodeset):nodeset for nodeset in node_nodeset.values()}
        nodeslist=[tuple(l) for l in id_nodesets.values()]

        nodeset_supernode={}
        for nodsets in nodeslist:
            supernode=Node()
            super_graph.add_node(supernode)
            # we gathher underling nodes into one set
            original_nodes=sum([original_node["__original_nodes"] for original_node in nodsets],[])
            supernode["__original_nodes"]=original_nodes

            for orgn in original_nodes:
                orgn[self.supernode_name].append(self.supernode_id(supernode))

            # lets keep what we made the supernode of
            for node in nodsets:
                nodeset_supernode[node]=supernode


        # after all the supernodes were created
        # we must review edges and add necessairy
        for nodeset in nodeslist: # nodeset (like taking bunch of nodes from one supernode)
            for node in nodeset: # take each node in set
                for edge in graph.node_outgoing_edges[node]:
                    n1,n2=graph.edge_connection[edge] # this is original connection
                    sn1,sn2=nodeset_supernode[n1],nodeset_supernode[n2]
                    # this represent connection in supergraph
                    # we dont need to copy edge
                    # we use current edge in connection in supergraph
                    if sn1 is sn2 or edge in super_graph.edges:
                        continue
                    super_graph.add_edge(sn1,sn2,edge)

        # we repeat until there are edges that we can use for merging
        if len(super_graph.edges)>0:
            self.__bmst_step(super_graph,phase+1)
