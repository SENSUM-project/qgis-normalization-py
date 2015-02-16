# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Normalization
                                 QGIS Normalization plugin
QGIS Normalization Plugin
                             -------------------
        begin                : 2014-07-03
        copyright            : (C) 2014 by GFZ
        email                : wangying220062@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This file contains two functions: function getMapLayerByName helps users get a map layer by its name;
 Function addtocanva helps add the normalized layer to the project
"""

# Import the PyQt and QGIS libraries
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

# function to get layer by name, parameter layername passes the layer name into this function
def getMapLayerByName(layerName):
    # get all the map layers from project
    layermap = QgsMapLayerRegistry.instance().mapLayers()
    # for loop checking all the layers from the project
    for name,layer in layermap.iteritems():
        # check if the name of one layer is the same with the incoming layer name 
        if layer.name() == layerName:
            # check if the layer is valid
            if layer.isValid():
                # if yes, return this layer
                return layer
            else:
                # if not, return false
                return None
    # release
    return None
# function to add normalized layer to project, parameter normedimage passes the normalized image into this function
def addtocanva(normedimage):
    # get the file info of the incoming image
    file_info = QFileInfo(normedimage)
    # check if the file info exists
    if file_info.exists():
        # if exists, set the name in file info to be layer name
        layer_name = file_info.completeBaseName()
    else:
        # if not, return false
        return False
    # create a raster layer based on the incoming normalized image
    rlayer_new = QgsRasterLayer(normedimage,layer_name)
    # check if the new created raster layer is valid
    if rlayer_new.isValid():
        # if yes, add this raster layer to the project
        QgsMapLayerRegistry.instance().addMapLayer(rlayer_new)
        return True
    else:
        # if not, return false
        return False
    