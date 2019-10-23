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
from .layer_graph import *
from .bmst2 import Bmst
#from .example_use import *

class Dendryt(QAction):
    """
    Action for opening dock widget for database connections
    """
    def __init__(self,plugin):
        super(Dendryt,self).__init__(
			plugin.icon('cluster_icon.png'),
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
        self.dlg=self.plugin.ui_loader('lines.ui')
        self.iface.addDockWidget(Qt.LeftDockWidgetArea,self.dlg)
        self.dlg.accept_button.clicked.connect(self.compute)
        self.dlg.cb_layer.layerChanged.connect(self.layer_change)
        self.dlg.cb_column.fieldChanged.connect(self.column_change)
        self.dlg.cb_layer.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.reset_gui()


    def reset_gui(self):
        self.dlg.accept_button.setEnabled(False)
        self.dlg.cb_column.setEnabled(False)

    def layer_change(self):
        self.dlg.cb_column.setEnabled(True)
        self.dlg.cb_column.setLayer(self.dlg.cb_layer.currentLayer())
        self.dlg.cb_column.setFilters(QgsFieldProxyModel.Int | QgsFieldProxyModel.Double)

    def column_change(self,text):
        self.dlg.accept_button.setEnabled(True)
        self.dlg.check_twoway.setEnabled(True)

    def compute(self):
        graph = graph_from_layer(
                    self.dlg.cb_layer.currentLayer(),
                    self.dlg.cb_column.currentText())
        result= Bmst(graph)
        layer_from_graph("nodes-{}".format(id(result)%10000),result.nodes,self.dlg.cb_layer.currentLayer().crs().authid())
        layer_from_graph("lines-{}".format(id(result)%10000),result.edges,self.dlg.cb_layer.currentLayer().crs().authid())
        self.reset_gui()
