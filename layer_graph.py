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
from qgis.core import *
from PyQt5.QtCore import  QVariant
import uuid

def graph_from_layer(layer,text):
    graph=Graph(is_directed=False)

    futurenodes=set()
    data_provider = layer.dataProvider()
    for feature in data_provider.getFeatures():
        xyline=feature.geometry().asPolyline()
        futurenodes.add(xyline[0])
        futurenodes.add(xyline[-1])

    geometry_nodes={}
    for node in futurenodes:
        n=Node()
        n["__geometry"]=node
        graph.add_node(n)
        geometry_nodes[node]=n

    for feature in data_provider.getFeatures():
        geometry=feature.geometry()
        xyline=geometry.asPolyline()
        e=Edge({"weight":feature[text],"__geometry":geometry},weight="weight")
        start=geometry_nodes[xyline[0]]
        end=geometry_nodes[xyline[-1]]
        graph.add_edge(start,end,e)

        if "n" not in start:
            start["n"]=[]
        if "n" not in end:
            end["n"]=[]
        start["n"].append(id(end)%1000)
        end["n"].append(id(start)%1000)

    return graph


# def graph_from_table(layer,text):
#     graph=Graph(is_directed=False)
#
#     nodes=set()
#     data_provider = layer.dataProvider()
#     for feature in data_provider.getFeatures():
#         xyline=feature.geometry().asPolyline()
#         nodes.add(xyline[0])
#         nodes.add(xyline[-1])
#
#     geometry_nodes={}
#     for node in nodes:
#         n=Node()
#         n["__geometry"]=node
#         graph.add_node(n)
#         geometry_nodes[node]=n
#
#     for feature in data_provider.getFeatures():
#         geometry=feature.geometry()
#         xyline=geometry.asPolyline()
#         e=Edge({"weight":feature[text],"__geometry":geometry})
#         graph.add_edge(geometry_nodes[xyline[0]],geometry_nodes[xyline[-1]],e)
#     return graph
#



def pointlayer_from_graph( graph):
    # we assume graph have proper __geometry field in nodes and edges (If not make it there first)
    #Take any node
    node=graph.nodes.pop()
    graph.nodes.add(node) # but put it back
    #
    field_list=[]
    fields=QgsFields()
    for i in node:
        if i!="__geometry":
            fields.append(QgsField(str(i),QVariant.String))
            field_list.append(i)

    vl=QgsVectorLayer("Point?crs=EPSG:2177",
                     "graphnodes"+'-'+str(id(graph)%1000),
                     "memory")

    dp = vl.dataProvider()
    dp.addAttributes(fields)
    vl.updateFields()
    # #features=[]
    for node in graph.nodes:
         f=QgsFeature()
         f.setGeometry(QgsGeometry.fromPointXY(node["__geometry"]))
         f.setAttributes([str(node[att]) for att in field_list])
         dp.addFeatures([f])

    vl.updateExtents()
    #vl.startEditing()
    #vl.commitChanges()
    QgsProject.instance().addMapLayer(vl)


def linelayer_from_graph( graph):
    # we assume graph have proper __geometry field in nodes and edges (If not make it there first)
    #Take any edge
    edge=graph.edges.pop()
    graph.edges.add(edge) # but put it back
    #
    field_list=[]
    fields=QgsFields()
    for i in edge:
        if i!="__geometry":
            fields.append(QgsField(str(i),QVariant.String))
            field_list.append(i)

    vl=QgsVectorLayer("LineString?crs=EPSG:2177",
                     "graphlines"+'-'+str(id(graph)%1000),
                     "memory")

    dp = vl.dataProvider()
    dp.addAttributes(fields)
    vl.updateFields()
    # #features=[]
    for edge in graph.edges:
         f=QgsFeature()
         f.setGeometry(edge["__geometry"])
         f.setAttributes([str(edge[att]) for att in field_list])
         dp.addFeatures([f])

    vl.updateExtents()
    #vl.startEditing()
    #vl.commitChanges()
    QgsProject.instance().addMapLayer(vl)

#
# class LayerGraph(Graph):
#     def __init__(self,linestring_layer,point_layer=None,directed=False):
#         super().__init__(is_directed=directed)
#
#         # we create Graph from layer
#         # The linestring ends describes Graph nodes
#         self.node_geometries=[] # list for node geometries
#                             # (geometry index is same as node index in self.nodes)
#                             # seeds are stored also separately from Nodes
#         self.weight_colum_name = weight_colum_name
#
#         # data provider
#         data_provider = layer.dataProvider()
#         features = data_provider.getFeatures()
#         # extraction of weight parameter from features table
#         weights = [feature[weight_colum_name] for feature in features]
#         #print(weights)
#         features = data_provider.getFeatures()
#         geometries = [feature.geometry() for feature in features]
#         #print(geometries)
#         ok_geometries = [geometry.convertToSingleType() for geometry in geometries ]
#         assert all(ok_geometries)
#
#         for g,w in zip(geometries,weights):
#             start = self.geometry_node(g.asPolyline()[0])
#             end = self.geometry_node(g.asPolyline()[-1])
#             self.add_edge(Edge(start,end,{prefix+"weight":w}))
#             if both_ways:
#                 self.add_edge(Edge(end,start,{prefix+"weight":w}))
    #
    # def geometry_node(self,geometry):
    #     # function gets real geometry
    #     # returns new or existing Node with this geoetry as property
    #     if geometry not in self.node_geometries:
    #         node = Node({prefix+"geometry":geometry})
    #         self.add_node(node)
    #         self.node_geometries.append(geometry)
    #         return node
    #     else:
    #         node_index = self.node_geometries.index(geometry)
    #         return self[node_index]
    #
    #
    #
    # def get_point_layer(self):
    #     #
    #     pass
    #
    # def get_linestring_layer(self):
    #     # return copy
    #     pass
    #
    # def update_property_in_point_layer(self,property_name):
    #     #
    #     pass
    #
    # def update_property_in_linestring_layer(self,property_name):
    #     #
    #     pass
