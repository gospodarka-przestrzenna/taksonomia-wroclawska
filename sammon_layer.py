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
from .graph import Graph,Node,Edge
from qgis.core import *
from PyQt5.QtCore import  QVariant
import uuid
import numpy as np
from scipy.spatial.distance import pdist, squareform

def graph_from_layer(layer,text,directed=False):
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


def layer_from_graph(name,data,org_data:'list[list[float]]',unique_field,layer,iface):
    fields=QgsFields()
    
    #unique_field_type = layer.dataProvider().fields().field(unique_field).typeName()
    #print(unique_field_type)
    # TODO check if unique_field is a string and make filed form there

    dimensions = len(org_data[0]) # any row will do

    fields.append(QgsField(str(unique_field),QVariant.String))

    unique_field_column=[feature[unique_field] if unique_field else None
        for feature in layer.dataProvider().getFeatures() ]

    crs=iface.mapCanvas().mapSettings().destinationCrs().authid()
    vl=QgsVectorLayer("Point?crs={}".format(crs),
                     name,
                     "memory")

    dp = vl.dataProvider()
    dp.addAttributes(fields)
    vl.updateFields()
    # #features=[]
    for i,element in enumerate(data):
         f=QgsFeature()
         p=QgsPoint(*[float(e) for e in element])
         g=QgsGeometry(p)
         #print(p,g)
         f.setGeometry(g)
         f.setAttributes([str(unique_field_column[i])])
         dp.addFeatures([f])

    vl.updateExtents()
    QgsProject.instance().addMapLayer(vl)
    #########################################
    fields=QgsFields()
    fields.append(QgsField(str("weight"),QVariant.Double))

    vl=QgsVectorLayer("LineString?crs={}".format(crs),
                     name,
                     "memory")

    dp = vl.dataProvider()
    dp.addAttributes(fields)
    vl.updateFields()

    def dorg(i:int,j:int):
        return sum((org_data[i][dimension]-org_data[j][dimension])**2
                        for dimension in range(dimensions))**0.5

    for i,element in enumerate(data):
        for j,element2 in enumerate(data):
            if i<j:
                f=QgsFeature()
                p1=QgsPoint(*[float(e) for e in element])
                p2=QgsPoint(*[float(e) for e in element2])
                #p=QgsLine(p1,p2)
                g=QgsGeometry.fromPolyline([p1,p2])
                #print(p,g)
                f.setGeometry(g)
                f.setAttributes([float(dorg(i,j))])
                dp.addFeatures([f])

    vl.updateExtents()
    QgsProject.instance().addMapLayer(vl)

def pca_initialization(X, target_dim):
    # Center the data
    X_mean = np.mean(X, axis=0)
    X_centered = X - X_mean
    
    # Compute covariance matrix
    covariance_matrix = np.cov(X_centered, rowvar=False)
    
    # Eigen decomposition
    eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)
    
    # Sort eigenvalues and eigenvectors in descending order
    sorted_indices = np.argsort(eigenvalues)[::-1]
    sorted_eigenvectors = eigenvectors[:, sorted_indices]
    
    # Select the top target_dim eigenvectors
    principal_components = sorted_eigenvectors[:, :target_dim]
    
    # Project the data onto the principal components
    Y_initial = np.dot(X_centered, principal_components)
    
    return Y_initial

# Function to calculate pairwise distances
def pairwise_distances(A):
    sum_A = np.sum(np.square(A), axis=1)
    D = np.sqrt(np.maximum(sum_A[:, np.newaxis] + sum_A[np.newaxis, :] - 2 * np.dot(A, A.T), 0))
    return D

def sammon_mapping(X, d=2, max_iter=300, alpha=0.3, tol=1e-9):
    """
    Perform Sammon mapping on the dataset X to reduce it to d dimensions.
    """
    X=np.array(X)
    N, D = X.shape
    
    # Step 1: Initialize with PCA
    Y = pca_initialization(X, d)
    
    # Step 2: Compute high-dimensional distances
    D_high = squareform(pdist(X, 'euclidean'))
    
    # Avoid division by zero
    D_high[D_high == 0] = 1e-12
    
    # Step 3: Main loop
    for iter in range(max_iter):
        # Compute low-dimensional distances
        D_low = squareform(pdist(Y, 'euclidean'))
        
        # Avoid division by zero
        D_low[D_low == 0] = 1e-12
        
        # Compute the gradient
        print((N,d))
        E = np.zeros((N, d))

        for i in range(N):
            for j in range(N):
                if i != j:
                    delta_ij = D_high[i, j] - D_low[i, j]
                    grad = (delta_ij / (D_high[i, j] * D_low[i, j])) * (Y[i] - Y[j])
                    E[i] -= grad

        # Update the positions
        Y_new = Y - alpha * E
        
        # Compute stress to check for convergence
        stress = np.sum((D_high - D_low)**2 / D_high)
        
        if np.abs(stress) < tol:
            break
        
        Y = Y_new

    return Y.tolist()


# def map_dimensions(data,do_3d):
#     dlen=len(data)
#     dims=len(data[0]) # original dims
#     #pdims=3 if do_3d else 2 # projection dims
#     # functions used in sammon
#     # scale = lambda x:(x**2.0)
#     # distscale = lambda x,y:(x-y)**2 if x>y else 2**(y-x)
#     scale = lambda x:(x)
#     distscale = lambda x,y:(x-y)**2

#     def pdims(projection):
#         return len(projection[0])

#     def dorg(i,j):
#         return sum((data[i][d]-data[j][d])**2
#                         for d in range(dims))**0.5

#     def dproj(i,j,projection):
#         pdim=pdims(projection)
#         return sum((projection[i][d]-projection[j][d])**2
#                         for d in range(pdim))**0.5

#     def make_projection(columns):
#         return [[e[i]
#                     for i in columns]
#                         for e in data]

#     def projversor(i,j,projection):
#         pdim=pdims(projection)
#         t=[projection[j][d]-projection[i][d]
#                         for d in range(pdim)]
#         l=sum(d**2 for d in t)**0.5
#         return [d/l if l>0 else 0    for d in t]

#     def vectorsum(v1,v2,projection):
#         pdim=pdims(projection)
#         return [v1[i]+v2[i] for i in range(pdim)]

#     def vectormul(v1,n,projection):
#         pdim=pdims(projection)
#         return [v1[i]*n for i in range(pdim)]

#     def sstress(projection):
#         E=sum([
#             distscale(dproj(i,j,projection),dorg(i,j))/
#             (scale(dorg(i,j)))
#                 for i in range(dlen)
#                     for j in range(dlen) if i<j])
#         return E/sum([(scale(dorg(i,j)))
#                         for i in range(dlen)
#                             for j in range(dlen) if i<j])

#     # LET the fun begin
#     current_projection=make_projection(range(dims))

#     while pdims(current_projection)>(3 if do_3d else 2):

#         minimals={}
#         for i in range(pdims(current_projection)):
#             projection = make_projection([e for e  in range(pdims(current_projection)) if e!=i])
#             prevstress=sstress(projection)
#             # lets iterate
#             alpha=1.0
#             for step in range(20):
#                 newprojection=[]
#                 for i,p in enumerate(projection):
#                     vs=list(p) # vector where to move point
#                     for j in range(len(projection)):
#                         if i!=j:
#                             vs=\
#                             vectorsum(vs,
#                                 vectormul(
#                                     projversor(i,j,projection),
#                                     (-1 if (dproj(i,j,projection)<dorg(i,j)) else 1)*\
#                                     alpha*\
#                                     distscale(dproj(i,j,projection),dorg(i,j))/\
#                                     (scale(dorg(i,j))),
#                                     projection),
#                                 projection
#                             )
#                     newprojection.append(vs)

#                 currstress=sstress(newprojection)
#                 if currstress<prevstress:
#                     projection=newprojection
#                     prevstress=currstress
#                     #print('after',currstress)
#                 else:
#                     alpha=alpha/2
#                     if alpha<0.0000001:
#                         break
#             minimals[currstress]=projection
#         # this is the best for normal cast
#         current_projection=minimals[min(minimals.keys())]

#     return current_projection

def get_data_dimensions(layer,columns):
    # Lets try to cast to float it might be a string or float
    # If it is a scring we may test if it is a number with dot or comma
    data=[[
        
        float(str(feature[index]).replace(",",".")) # this will always work if it is a string or number
             
             for index in columns ]
                for feature in layer.dataProvider().getFeatures() ]

    return data
