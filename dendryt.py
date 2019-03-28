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
import os
from PyQt5.QtWidgets import QAction,QMessageBox,QApplication
from PyQt5.QtCore import Qt, QBasicTimer
from qgis.gui import QgsMapLayerComboBox
from qgis.core import *
from bmst import LayerGraph

class Dendryt(QAction):
    """
    Action for opening dock widget for database connections
    """
    def __init__(self,plugin):
        super(Dendryt,self).__init__(
			plugin.qicon,
			"Create Spanning Tree",
			plugin.iface.mainWindow()
	           )
        self.triggered.connect(self.run)

        self.plugin=plugin
        self.iface=plugin.iface
        # dailog cannot be set in function variable (it is GCed)
        self.dlg=None
        # binding frontend actions with logic

    def run(self):
        """
        Just show/dock Widget
        """
        self.dlg=self.plugin.ui_loader('main_window1.ui')
        self.dlg.guziczek.clicked.connect(self.clicked)
        #self.dlg.warstwaBox.activated[str].connect(self.combo_Box_2)
        #self.dlg.warstwaBox.currentIndexChanged.connect(self.selectionchange)
        self.dlg.LayerComboQ.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.dlg.LayerComboQ.layerChanged.connect(self.layer_change)

        #self.dlg.show()
        #self.iface.addWindow(self.dlg)


    def clicked(self):
        layer=QgsProject.instance().mapLayersByName('example')[0]
        layer_graph=LayerGraph(layer)

    def combo_Box_2(self,text):
        self.dlg.kolumnaBox.setEnabled(False)
        self.dlg.kolumnaBox.clear()
        self.dlg.comboBox_3.setEnabled(False)
        self.dlg.comboBox_3.clear()
        self.dlg.warstwaBox.setEnabled(True)

    def selectionchange(self, i):
        print("Items in the list are :")
        for count in range(self.dlg.warstwaBox.count()):
            print(self.dlg.warstwaBox.itemText(count))
        print("Current index",i,"selection changed ",self.dlg.warstwaBox.currentText())

    def layer_change(self):
        print(self.dlg.LayerComboQ.currentText())
        #print(self.dlg.LayerComboQ.currentLayer())
        fid=1
        #for feature in
        iterator=self.dlg.LayerComboQ.currentLayer().getFeatures(QgsFeatureRequest().setFilterFid(fid))
        feature=next(iterator)
        attrs = feature.attributes()
        geom=feature.geometry().asGeometryCollection()
        geom_str=str(geom[0]).split(" ((")[1][:-3].split(", ")
        print(geom_str)
        #self.dlg.QwarstwaBox.setLayer()
