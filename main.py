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
 This is the main plugin file.
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtGui import *
from qgis.core import *
from gdalconst import *
import numpy as np
import string
import gdal
from scipy.optimize import curve_fit
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from maindialog import NormDialog
# Import the getMapLayerByName and addtocanva functions from library functions
from library.functions import getMapLayerByName, addtocanva
# standard drivers registration
gdal.AllRegister()

class Main:   
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        
    def initGui(self):
        self.toolBar = self.iface.addToolBar("Normalization")
        # Create action that will start plugin configuration
        self.action_norm = QAction(QIcon(":/plugins/Normalization/icons/Norm.PNG"), "Norm", self.iface.mainWindow())
        # Connect the action to the run method
        self.action_norm.triggered.connect(self.norm)
        # Add toolbar button and menu item
        self.toolBar.addAction(self.action_norm)
        self.iface.addPluginToMenu(u"&Normalization", self.action_norm)
   
    def unload(self):
        self.iface.removePluginMenu(u"&Normalization", self.action_norm)
        self.iface.removeToolBarIcon(self.action_norm)
        
        
    def NormMethods(self):
        # get layer using function getMapLayerByName       
        layer = getMapLayerByName(self.dlg.ui.layercomboBox.currentText())  
        # get the original layer source's path 
        sourcepath=layer.source()      
        # get layer source
        datasource=gdal.Open(sourcepath)
        # get No. of rows of layer source
        rows=datasource.RasterYSize
        # get No. of columns of layer source
        cols=datasource.RasterXSize
        # get projection of layer source
        proj=datasource.GetProjection() 
        # get Geo Transform of layer source    
        transform=datasource.GetGeoTransform()        
        # get no datavalue of layer source
        nodatavalue=datasource.GetRasterBand(1).GetNoDataValue()
        # read data source into a 2D array 
        layerarray=datasource.ReadAsArray(0,0,cols,rows)  

        f1=open("per.txt","wb")
        
        # get all the values that are not none and save them into a txt file
        nempty=[]    # declare a array
        for y in range(0,rows):
            for x in range(0,cols):
                if layerarray[y][x]!=nodatavalue:
                    nempty.append(layerarray[y][x])     # add layerarray[y][x] to array nempty if it is not none
        # save array nempty into txt file
        np.savetxt("nempty.txt", nempty)


        if len(self.dlg.ui.lineEditNL.text())==0:
            # set the default low rejection bound
            self.dlg.ui.lineEditNL.setText("0")
        # get the input str and convert them to float
        N_L=string.atof(self.dlg.ui.lineEditNL.text())
            
        if len(self.dlg.ui.lineEditNH.text())==0:
            # set the default high rejection bound
            self.dlg.ui.lineEditNH.setText("100")       
        # get the input str and convert them to float
        N_H=string.atof(self.dlg.ui.lineEditNH.text())  
                     
        # get percentile of the low value
        minper=np.percentile(nempty,N_L)
        # get percentile of the high value
        maxper=np.percentile(nempty,N_H)
               
        # get all the input X and Y values and store them into arrays
        xvaluelist=[]
        yvaluelist=[]               
        for i in range(0,10):
            if self.dlg.ui.tableWidget.item(i,0).text():
                xvaluelist.append(string.atof(self.dlg.ui.tableWidget.item(i,0).text()))
            if self.dlg.ui.tableWidget.item(i,1).text():
                yvaluelist.append(string.atof(self.dlg.ui.tableWidget.item(i,1).text()))            
        xvalue=np.array(xvaluelist) 
        yvalue=np.array(yvaluelist)
        
        Beta0=0
        Beta1=0
        
        # choose MIN_MAX normalization method
        if self.dlg.ui.normcomboBox.currentText()=='MIN_MAX':
        
            if maxper<1e-8:
                QMessageBox.information(None, "MIN_MAX", "upper normalization value < 1e-8 (almost zero)")
                return
            # min-max normalization 
            for y in range(0,rows):
                for x in range(0,cols):
                    # only calculate for not none value
                    if layerarray[y][x]!= nodatavalue:
                        # calculation
                        layerarray[y][x]=(layerarray[y][x]-minper)/(maxper-minper)
                        # if calculation result is smaller than 0, reset it to be 0
                        if layerarray[y][x]<0:
                            layerarray[y][x]=0
                        # if calculation result is larger than 1, reset it to be 1
                        if layerarray[y][x]>1:
                            layerarray[y][x]=1    

        # choose LOGARITHMIC normalization method        
        if self.dlg.ui.normcomboBox.currentText()=='LOGARITHMIC': 
           
            # if there is no input X and Y values, calculate the coefficients from rejection bounds
            if len(xvalue)==0 and len(yvalue)==0:
                if maxper<1e-8:
                    QMessageBox.information(None, "Error", "upper normalization value < 1e-8 (almost zero)")
                    return 
                Beta1=1/np.log(maxper/(minper+1e-5))
                Beta0=-Beta1*np.log(minper+1e-5)
                f1.write(str(Beta0))
                f1.write(str(Beta1))
            # if number of X values is different from number of Y values, popup warning message
            elif len(xvalue)!=len(yvalue):
                QMessageBox.information(None, "Error!","X and Y must be in the same dimension!")
                return
            # if Indicator value pairs are less than 2, popup warning message
            elif len(xvalue)==len(yvalue)<2:
                QMessageBox.information(None, "Error!","Please input at least 2 pairs of values!")
                return
            # calculate coefficients using least square method
            else:
                def logarithmic(x, Beta0, Beta1):
                    return Beta0+Beta1*np.log(x+0.00001)
                popt, pcov = curve_fit(logarithmic, xvalue, yvalue)
                Beta0=popt[0]
                Beta1=popt[1]
                f1.write(str(Beta0))
                f1.write(str(Beta1))
            # logarithmic normalization 
            for y in range(0,rows):
                for x in range(0,cols):
                    # only calculate for not none value
                    if layerarray[y][x] != nodatavalue:
                        # calculation
                        layerarray[y][x]=Beta0+np.log(layerarray[y][x]+0.00001)*Beta1
                        # if calculation result is smaller than 0, reset it to be 0
                        if layerarray[y][x]<0:
                            layerarray[y][x]=0
                        # if calculation result is larger than 1, reset it to be 1
                        if layerarray[y][x]>1:
                            layerarray[y][x]=1  
         
        # choose QUADRATIC normalization method        
        if self.dlg.ui.normcomboBox.currentText()=='QUADRATIC':
            
            if len(xvalue)==0 and len(yvalue)==0:
                if maxper<1e-8:
                    QMessageBox.information(None, "Error", "upper normalization value < 1e-8 (almost zero)")
                    return 
                Beta1=1/(maxper*maxper-minper*minper)
                Beta0=-Beta1*minper*minper
            
            elif len(xvalue)!=len(yvalue):
                QMessageBox.information(None, "Error!","X and Y must be in the same dimension!")
                return
            elif len(xvalue)==len(yvalue)<2:
                QMessageBox.information(None, "Error!","Please input at least 2 pairs of values!")
                return
            else:
                def quadratic(x, Beta0, Beta1):
                    return Beta0+Beta1*x*x
                popt, pcov = curve_fit(quadratic, xvalue, yvalue)
                Beta0=popt[0]
                Beta1=popt[1]
                
            # QUADRATIC normalization 
            for y in range(0,rows):
                for x in range(0,cols):
                    # only calculate for not none value
                    if layerarray[y][x] != nodatavalue:
                        # calculation
                        layerarray[y][x]=Beta0+layerarray[y][x]*layerarray[y][x]*Beta1
                        # if calculation result is smaller than 0, reset it to be 0
                        if layerarray[y][x]<0:
                            layerarray[y][x]=0
                        # if calculation result is larger than 1, reset it to be 1
                        if layerarray[y][x]>1:
                            layerarray[y][x]=1  
               
        # choose INV-LOGIT normalization method            
        if self.dlg.ui.normcomboBox.currentText()=='INV-LOGIT':
            
            if len(xvalue)==0 and len(yvalue)==0:
                if maxper<1e-8:
                    QMessageBox.information(None, "Error", "upper normalization value < 1e-8 (almost zero)")
                    return 
                Beta1=np.log(99999*99999)/(maxper-minper)
                Beta0=np.log(99999)-maxper*Beta1
            
            elif len(xvalue)!=len(yvalue):
                QMessageBox.information(None, "Error!","X and Y must be in the same dimension!")
                return
            elif len(xvalue)==len(yvalue)<2:
                QMessageBox.information(None, "Error!","Please input at least 2 pairs of values!")
                return
            else:
                def invlogit(x, Beta0, Beta1):
                    return (np.e**(Beta0+Beta1*x))/(1+np.e**(Beta0+Beta1*x))
                popt, pcov = curve_fit(invlogit, xvalue, yvalue)
                Beta0=popt[0]
                Beta1=popt[1]

            # INV-LOGIT normalization 
            for y in range(0,rows):
                for x in range(0,cols):
                    # only calculate for not none value
                    if layerarray[y][x] != nodatavalue:
                        # calculation
                        layerarray[y][x]=Beta0+layerarray[y][x]*layerarray[y][x]*Beta1
                        layerarray[y][x]=np.exp(Beta0+Beta1*layerarray[y][x])/(1+np.exp(Beta0+Beta1*layerarray[y][x]))
                        # if calculation result is smaller than 0, reset it to be 0
                        if layerarray[y][x]<0:
                            layerarray[y][x]=0
                        # if calculation result is larger than 1, reset it to be 1
                        if layerarray[y][x]>1:
                            layerarray[y][x]=1  
         
        # choose LOG-SQUARE normalization method            
        if self.dlg.ui.normcomboBox.currentText()=='LOG-SQUARE':
            
            if len(xvalue)==0 and len(yvalue)==0:
                if maxper<1e-8:
                    QMessageBox.information(None, "Error", "upper normalization value < 1e-8 (almost zero)")
                    return 
                Beta1=1/(np.log(maxper*maxper/((minper+0.00001)**2)))
                Beta0=-Beta1*np.log((minper+0.00001)**2)
            
            elif len(xvalue)!=len(yvalue):
                QMessageBox.information(None, "Error!","X and Y must be in the same dimension!")
                return
            elif len(xvalue)==len(yvalue)<2:
                QMessageBox.information(None, "Error!","Please input at least 2 pairs of values!")
                return
            else:
                def logsquare(x, Beta0, Beta1):
                    return Beta0+Beta1*np.log((x+0.00001)**2)
                popt, pcov = curve_fit(logsquare, xvalue, yvalue)
                Beta0=popt[0]
                Beta1=popt[1]

            # LOG-SQUARE normalization 
            for y in range(0,rows):
                for x in range(0,cols):
                    # only calculate for not none value
                    if layerarray[y][x] != nodatavalue:
                        # calculation
                        layerarray[y][x]=Beta0+np.log(layerarray[y][x]+0.00001)*np.log(layerarray[y][x]+0.00001)*Beta1
                        # if calculation result is smaller than 0, reset it to be 0
                        if layerarray[y][x]<0:
                            layerarray[y][x]=0
                        # if calculation result is larger than 1, reset it to be 1
                        if layerarray[y][x]>1:
                            layerarray[y][x]=1  
        
        #show the coefficients in log message
        QgsMessageLog.logMessage("Beta0 = "+str(Beta0) ,None , QgsMessageLog.INFO)
        QgsMessageLog.logMessage("Beta1 = "+str(Beta1) ,None , QgsMessageLog.INFO)
        # give the normalized image the path          
        lsource=self.dlg.ui.lineEdit_outputpath.text()
        # get driver for the input file
        driver=datasource.GetDriver()                
        # create output file with driver
        output=driver.Create(lsource,cols,rows,1,GDT_Float32)        
#        outdriver = gdal.GetDriverByName('GTiff')
        # get the band to write to 
        outBand=output.GetRasterBand(1)
        # write array into the band
        outBand.WriteArray(layerarray,0,0)
        # set the output geo transform
        output.SetGeoTransform(transform)
        # set the output projection
        output.SetProjection(proj)
        # set nodata value 
        if nodatavalue:
            outBand.SetNoDataValue(nodatavalue)
        else:
            outBand.SetNoDataValue(-9999)
        # close gdal dataset
        output = None
        
        # add result to map canvas with function addtocanva, which is located in library.functions.py
        if self.dlg.ui.checkBox.checkState() :
            addtocanva(lsource)        
                       
    def norm(self):
        # Create the dialog (after translation) and keep reference
        self.dlg = NormDialog()        
        # Show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # Call function minmaxNorm
            self.NormMethods()

