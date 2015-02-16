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
 This is the main dialog file.
"""
# Import the PyQt and QGIS libraries
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import string
import os
# Import the interface code
from ui_norm import Ui_Norm

class NormDialog(QtGui.QDialog, Ui_Norm):

    def __init__(self):

        QtGui.QDialog.__init__(self)
        self.ui = Ui_Norm()
        self.ui.setupUi(self)
        # traverse all the map layers to get raster layers and add their names to layercomboBox
        layers=QgsMapLayerRegistry.instance().mapLayers().values()
        for layer in layers: 
            if layer.type() == QgsMapLayer.RasterLayer:          
                self.ui.layercomboBox.addItem(layer.name())
          
        self.ui.tableWidget.setEnabled(False)

        # Connect the signals to the functions 
        QObject.connect(self.ui.normcomboBox, SIGNAL("currentIndexChanged(const QString&)"), self.choosenorm)
        QObject.connect(self.ui.OKButton, SIGNAL("clicked()"), self.ok)
        QObject.connect(self.ui.CancelButton, SIGNAL("clicked()"),self.reject)
        QObject.connect(self.ui.Button_path, SIGNAL("clicked()"), self.outputpath)
        QObject.connect(self.ui.helpButton, SIGNAL("clicked()"), self.show_help)
        # set default values of rejection bounds
        self.ui.lineEditNL.setPlaceholderText("0")
        self.ui.lineEditNH.setPlaceholderText("100")

        
    def choosenorm(self):               
        # set the layers to be normalized 
        normitem=self.ui.normcomboBox.currentText()
                          
        # choose method "MIN_MAX"
        if normitem == "MIN_MAX":
                       
            self.ui.tableWidget.setEnabled(False)
            self.ui.minmaxframe.setEnabled(True)
                    
        # choose method "LOGARITHMIC"
        if normitem == "LOGARITHMIC":
           
            self.ui.tableWidget.setEnabled(True)
            self.ui.minmaxframe.setEnabled(True)
        # choose method "QUADRATIC"            
        if normitem == "QUADRATIC":

            self.ui.tableWidget.setEnabled(True)
            self.ui.minmaxframe.setEnabled(True)
        # choose method "INV-LOGIT"        
        if normitem == "INV-LOGIT":
                       
            self.ui.tableWidget.setEnabled(True)
            self.ui.minmaxframe.setEnabled(True)
        # choose method "LOG-SQUARE"            
        if normitem == "LOG-SQUARE":
                                  
            self.ui.tableWidget.setEnabled(True)
            self.ui.minmaxframe.setEnabled(True)

    # set acceptance condition of ok button
    def ok(self):
        # set the layers to be normalized 
#        normitem=self.ui.normcomboBox.currentText()
        if len(self.ui.lineEditNL.text())==0 or len(self.ui.lineEditNH.text())==0:            
            N_L=0
            N_H=100                
        else:
            a=self.ui.lineEditNL.text();
            N_L=string.atof(a);
            b=self.ui.lineEditNH.text();
            N_H=string.atof(b);

        if N_L<0 or N_H>100 or N_L>=N_H:
            QtGui.QMessageBox.information(self, "Normalization", "Please check parameters again, N_L and N_H should be in (1~100) and N_L must be smaller than N_H!")
            return

        self.accept()

    # function outputpath, to define the output image path    
    def outputpath(self):
        fileName = QFileDialog.getSaveFileName(self,"Output Image", "~/","GeoTIFF (*.tiff *.tif)");           
        if fileName !="":
            if  os.path.splitext(fileName)[1] :
                if  os.path.splitext(fileName)[1] == ".tif" or os.path.splitext(fileName)[1] == ".tiff":
                    self.ui.lineEdit_outputpath.setText(fileName)
                else:
                    self.ui.lineEdit_outputpath.setText(os.path.splitext(fileName)[0]+'.tif')
            else:
                self.ui.lineEdit_outputpath.setText(fileName+'.tif')
    
    # function show_help, helps to show help document to users
    def show_help(self):
        help_file = 'file:///%s/normhtml/help.html' % os.path.dirname(__file__)
        QDesktopServices.openUrl(QUrl(help_file))
        