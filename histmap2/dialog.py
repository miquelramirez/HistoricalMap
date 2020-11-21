# -*- coding: utf-8 -*-
"""!@brief Call of UI form
/***************************************************************************
 HistoricalMapDialog
                                 A QGIS plugin
 Mapping old forests from historical  maps
                             -------------------
        begin                : 2016-01-26
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Karasiak & Lomellini
        email                : karasiak.nicolas@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# import os
from PyQt5.QtWidgets import QDockWidget

# OLD Call for UI form
#FORM_CLASS, _ = uic.loadUiType(os.path.join(
#    os.path.dirname(__file__), 'dialog_base.ui'))

from histmap2.dialog_base import Ui_HistoricalMap

# OLD Call for UI ext
# class HistoricalMapDialog(QtGui.QDialog, FORM_CLASS):
class HistoricalMapDialog(QDockWidget, Ui_HistoricalMap):
    def __init__(self, parent=None):
        """Constructor."""
        super(HistoricalMapDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        self.setupUi(self)
