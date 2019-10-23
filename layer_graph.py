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

    geometry_nodes={}

    def add_point(point):
        if point.asWkt() not in geometry_nodes:
            n=Node()
            n["__geometry"]=point
            graph.add_node(n)
            geometry_nodes[point.asWkt()]=n

    for edge in layer.dataProvider().getFeatures():
        geometry = edge.geometry()
        line=[v for v in geometry.vertices()]
        start = line[0]
        end = line[-1]
        add_point(start)
        add_point(end)
        e=Edge({"weight":edge[text],"__geometry":geometry},weight="weight")
        graph.add_edge(geometry_nodes[start.asWkt()],geometry_nodes[end.asWkt()],e)

    return graph


def layer_from_graph(name,the_set,crs):
    # we assume graph have proper __geometry field in nodes and edges
    # Take any n
    element=the_set.pop()
    the_set.add(element) # but put it back
    #
    field_list=[]
    fields=QgsFields()
    for i in element:
        if i!="__geometry":
            fields.append(QgsField(str(i),QVariant.String))
            field_list.append(i)

    if type(element["__geometry"])==QgsPoint:
        layer_type="Point"
    else:
        layer_type="LineString"

    vl=QgsVectorLayer("{}?crs={}".format(
                            layer_type,
                            crs),
                     name,
                     "memory")

    dp = vl.dataProvider()
    dp.addAttributes(fields)
    vl.updateFields()
    # #features=[]
    for element in the_set:
         f=QgsFeature()
         f.setGeometry(QgsGeometry(element["__geometry"]))
         f.setAttributes([str(element[att]) for att in field_list])
         dp.addFeatures([f])

    vl.updateExtents()
    QgsProject.instance().addMapLayer(vl)

def sammon_graph(layer,colums):
    pass
