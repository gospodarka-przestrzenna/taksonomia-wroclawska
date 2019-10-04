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

from graph import Graph,Node,Edge,prefix

def bmst(graph,weight_name,supernode_in_step_name,edge_step_name,step=1):
    s_graph=Graph(graph.directed)
    # copies nodes
    for node in graph.nodes:
        # Supernode contains one node at beginning
        supernode=s.add_node(node.id)
        supernode["nodes"]=[node.id]
        if step==1:
            node[supernode_in_step_name]=[node.id]
        node[supernode_in_step_name].append(supernode.id)
        # after all computation this will be replaced with list

    # we consider only edges that are not self-connecting
    # connects two diffrent nodes
    proper_edges = [
            edge
            for edge in graph.edges
            if edge.start.id != edge.end.id
    ]

    # each edge that has supernodes as both start and end
    # is considered as a superedge
    for edge in proper_edges:
        superedge=s_graph.add_edge(edge.start.id,edge.end.id)
        superedge[weight_name]=edge[weight_name]
        if step==1:
            superedge["original_edge"]=edge
            superedge[edge_step_name]=0
        else:
            superedge["original_edge"]=edge["original_edge"]

    minimal_edges = []
    # on phase we dont make supernodes

    for node in graph.nodes:
        edges=node.shortest_outgoing_edges(weight_name)
        # This is a list of shortest edges
        if len(edges)>1:
            raise ValueError((
                "Two edges have same weight: ",
                edges[0]['original_edge'],
                edges[0]['original_edge']
            ))
        else:
            minimal_edge.append(edges[0])

    if minimal_edges==[]:
        return
    else:
        for edge in minimal_edges:
            s_graph.merge_nodes(edge.start.id,edge.end.id)

            # supernode now must contain all nodes from included_supernode
            edge.start["nodes"].extend(edge.end["nodes"])

            # uptate each node in included_supernode to point proper node they are in
            for node in edge.end["nodes"]:
                node[supernode_in_step_name][-1] = edge.start.id
            edge['original_edge'][edge_step_name]=step
        bmst(s_graph,supernode_in_step_name,edge_step_name,step+1)

class Bmst(Graph):
    # the main idea of this class will be to copy Graph
    # and produce supernode at each level
    # supernodes are the node that are connected
    # supernodes contain multiple nodes (supernodes) agregated
    # supernodes represent algorithm clustering behaviour on each phase

    # We provide graph to be copied
    # as well as weight name and new names for step in edge
    # and name of the supernode that node is in for each step
    def __init__(self,graph,weight_name,supernode_name,edge_step_name):
        assert isinstance(graph,Graph)

        self.weight_name = weight_name
        self.supernode_name = supernode_name
        self.edge_step_name = edge_step_name
        self.original_graph =  graph
        self.copiednodes={}

        # at first we copy original graph to self as self is a graph
        # this graph will be new layer later
        super().__init__(graph.is_directed)
        for node in graph.nodes:
            # copy node's name and properties
            copynode=Node(node)
            self.add_node(copynode)
            copynode["__original_nodes"] = [copynode]
            copynode[self.supernode_name] = [id(copynode)] # this list will be used later on each lavel
                                                        # it will describe supernode that contain this node
                                                     # [supernode_on_level0==just me , supernode_on_level1,... ]
            self.copiednodes[node]=copynode

        for edge in graph.edges:
            # copy node and properties
            copyedge=Edge(edge,weight=self.weight_name)
            n1,n2=graph.edge_connection[edge]
            self.add_edge(self.copiednodes[n1],self.copiednodes[n2],copyedge)
            # this will be used later
            copyedge[self.edge_step_name]=None # if edge will be used we attache phase nuber to it

            copyedge["__original_edge"]=copyedge # as the supergraph is a copy for future process
                                                    # the original edge is su
        self.__bmst_step(self,1)


    def __bmst_step(self,graph,phase):

        node_nodeset={} # {node1:{node1, node3 ,node77 ...} node2:{node2 } node44:{node1, node3 ,node77 ...}}
        # With each note a set of node is releated
        # Each edge merges only two sets
        # every node is used
        for node in graph.nodes:
            # no outgoing edge ?
            if len(graph.node_outgoing_edges[node]) == 0:
                merge_nodes[node]={node}
            else:
                # if there are edge let's grab one`
                # and put them back in place
                e1=graph.node_outgoing_edges[node].pop()
                graph.node_outgoing_edges[node].add(e1)
                # lets see if there is another edge inside ?
                # As heap preserves order if there is more edge we will find out
                e2=graph.node_outgoing_edges[node].pop()
                graph.node_outgoing_edges[node].add(e2)
                #
                if (e2<=e1 and e1<=e2) and (e1 is not e2): # they are two different edges equal in value
                    raise ValueError((
                        "Two edges have same weight: ",
                        e1['__original_edge'],
                        e2['__original_edge']
                    ))

                # lets use this edge in this phase
                e1["__original_edge"][self.edge_step_name]=phase
                n1,n2=graph.edge_connection[e1]

                nodes_combined={n1,n2}
                # let's make set of nodes that will represent future supernode
                # we alwais combine only two sets of n1 and n2
                if n1 in node_nodeset:
                    nodes_combined.update(node_nodeset[n1])
                if n2 in node_nodeset:
                    nodes_combined.update(node_nodeset[n2])
                # and later designate this set to all their containing nodes
                for n in nodes_combined:
                    node_nodeset[n]=nodes_combined

        # this graf will be super_graph in this level
        # we create graph from the sets computed above
        # each set well be supernode
        super_graph=Graph(graph.is_directed)
        # copies nodes it will become supernodes on the current level
        nodesets=set([frozenset(sn) for sn in node_nodeset.values()])# ?????
        nodeset_supernode={}
        for nodsets in nodesets:
            supernode=Node()
            supernode["___nodes"]=nodsets
            super_graph.add_node(supernode)
            # this
            original_nodes=sum([original_node["__original_nodes"] for original_node in nodsets],[])
            supernode["__original_nodes"]=original_nodes

            for orgn in original_nodes:
                orgn[self.supernode_name].append(id(supernode))

            # lets keep what we made the supernode of
            for node in nodsets:
                nodeset_supernode[node]=supernode


        # after all the supernodes were created
        # we must review edges and add necessairy
        for nodeset in nodesets: # nodeset (like taking bunch of nodes from one supernode)
            for node in nodeset: # take each node in set
                for edge in graph.node_outgoing_edges[node]:
                    n1,n2=graph.edge_connection[edge] # this is original connection
                    sn1,sn2=nodeset_supernode[n1],nodeset_supernode[n2]
                    # this represent connection in supergraph
                    if sn1==sn2 or super_graph.connected(sn1,sn2):
                        continue
                    superedge = Edge(edge,weight=edge.weight_name)
                    super_graph.add_edge(ns1,ns2,superedge)
                    # we want edge to have reference to most original edge
                    superedge["__original_edge"] = edge["__original_edge"]

        if len(super_graph.edges)>0:
            self.__bmst_step(super_graph,phase+1)
