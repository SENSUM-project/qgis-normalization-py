# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Normalization
                                 QGIS Normalization plugin
 Template QGIS Plugin
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
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # load main class from file main
    from main import Main
    return Main(iface)

