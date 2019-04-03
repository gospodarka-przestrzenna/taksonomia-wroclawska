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

class LayerGraph(Graph):
    def __init__(self,layer,weight_colum_name,both_ways=True):
        super().__init__()
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
        weights = [feature[weight_colum_name] for feature in features]
        #print(weights)
        features = data_provider.getFeatures()
        geometries = [feature.geometry() for feature in features]
        #print(geometries)
        ok_geometries = [geometry.convertToSingleType() for geometry in geometries ]
        assert all(ok_geometries)

        for g,w in zip(geometries,weights):
            start = self.geometry_node(g.asPolyline()[0])
            end = self.geometry_node(g.asPolyline()[-1])
            self.add_edge(Edge(start,end,{prefix+"weight":w}))
            if both_ways:
                self.add_edge(Edge(end,start,{prefix+"weight":w}))

    def geometry_node(self,geometry):
        # function gets real geometry
        # returns new or existing Node with this geoetry as property
        if geometry not in self.node_geometries:
            node = Node({prefix+"geometry":geometry})
            self.add_node(node)
            self.node_geometries.append(geometry)
            return node
        else:
            node_index = self.node_geometries.index(geometry)
            return self[node_index]
