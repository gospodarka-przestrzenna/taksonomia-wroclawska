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
import os
from PyQt5.QtWidgets import QAction,QMessageBox,QApplication
from PyQt5.QtCore import Qt, QBasicTimer
from qgis.gui import QgsMapLayerComboBox
from qgis.core import *
from .sammon_layer import *

class MDS(QAction):
    """
    Action for opening dock widget for database connections
    """
    def __init__(self,plugin):
        super(MDS,self).__init__(
			plugin.icon('mds_icon.png'),
			"Create Multidimensional Scalling",
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
        self.dlg=self.plugin.ui_loader('table.ui')
        self.iface.addDockWidget(Qt.LeftDockWidgetArea,self.dlg)
        self.dlg.accept_button.clicked.connect(self.compute)
        self.dlg.cb_layer.layerChanged.connect(self.layer_change)
        self.dlg.cb_layer.setFilters(QgsMapLayerProxyModel.NoGeometry)
        self.reset_gui()

    def reset_gui(self):
        self.dlg.accept_button.setEnabled(False)
        self.dlg.check3d.setEnabled(False)
        self.dlg.check3d.setChecked(False)
        self.dlg.column_label.setEnabled(False)
        self.dlg.text_label.setEnabled(False)
        self.dlg.cb_column.setEnabled(False)

        self.dlg.column_label.setText("No columns:")
        self.dlg.text_label.setText("'dimension1' or 'dimension2' or ... ")
        self.dlg.repaint()

    def layer_change(self):
        layer=self.dlg.cb_layer.currentLayer()
        self.dimmension_field_ids_list,consecutives_list=self.dimmension_field_ids(layer)

        self.dlg.column_label.setEnabled(True)
        self.dlg.text_label.setEnabled(True)

        self.dlg.cb_column.setEnabled(True)
        self.dlg.cb_column.setLayer(self.dlg.cb_layer.currentLayer())


        if len(self.dimmension_field_ids_list)<2:
            pass
        else:
            self.dlg.column_label.setText("Found columns:")
            # found dimmension columns
            consecutive_texts = list(map(
                (lambda x:
                    "dimension{}-{}".format(x[0],x[1]) if x[0]!=x[1] else
                    "dimension{}".format(x[0])),
                consecutives_list 
            ))
            self.dlg.text_label.setText(", ".join(list(consecutive_texts)))
            self.dlg.accept_button.setEnabled(True)
            if len(self.dimmension_field_ids_list)>=3:
                self.dlg.check3d.setEnabled(True)
                self.dlg.check3d.setChecked(True)


    def dimmension_field_ids(self,layer):
        column_ids=[]
        # create list of consequtive dimension columns
        counter=0
        consecutives=[]
        while True:
            index=layer.fields().indexFromName("dimension{}".format(counter))
            if index>=0:
                column_ids.append(index)
                if(len(consecutives)>0 and consecutives[-1][1]==counter-1):
                    consecutives[-1][1]=counter
                else:
                    consecutives.append([counter,counter])
            else:
                # we must allow to sikip some columns
                if counter>1000:
                    
                    break
            counter+=1
        return column_ids,consecutives

    def compute(self):
        layer=self.dlg.cb_layer.currentLayer()
        checked3d=self.dlg.check3d.isChecked()
        unique_field_name=self.dlg.cb_column.currentText()

        data_dimensions=get_data_dimensions(layer,self.dimmension_field_ids_list)
        target_dimensions=3 if checked3d else 2
        try:
            data_mapped_dimensions=sammon_mapping(data_dimensions,target_dimensions)
        except Exception as e:
            QMessageBox.critical(self.iface.mainWindow(),
                "Error",
                "Error during MDS computation: {}".format(e),
                QMessageBox.Ok)
            return    
        id_=id(data_mapped_dimensions)%10000 # this will give us unique id for layer
        layer_from_graph("nodes-{}".format(id_),
                        data_mapped_dimensions,
                        data_dimensions,
                        unique_field_name,
                        layer,
                        self.iface)
        #layer_from_graph("lines-{}".format(id_),data_mapped_dimensions,self.iface)
        self.reset_gui()
