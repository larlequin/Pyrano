from PyQt4 import QtGui
from PyQt4 import QtCore
import csv

class ViewData(QtGui.QDialog):
    """Create a tab to display the csv file"""
    def __init__(self, parent=None, dtmodel=None, header=None):
        super(ViewData, self).__init__()
        self.parent = parent
        self.setGeometry(100, 100, 650, 900)
        # Tableview ----------------------------------------------------------------------#
        self.model = QtGui.QStandardItemModel(self)
        tableView = QtGui.QTableView(self)
        dtmodel.setHorizontalHeaderLabels(header)
        tableView.setModel(dtmodel)
        tableView.setSortingEnabled(True)
        tableView.horizontalHeader().setStretchLastSection(True)
        # Buttons
        but_layout = self.dial_buttons()
        # Final layout ---------------------------------------------------------------------#
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(tableView)
        vbox.addLayout(but_layout)
        self.setLayout(vbox)
        
    def dial_buttons(self):
        """Define and connect a Cancel and OK button.
        """
        cancel = QtGui.QPushButton('Cancel', self)
        ok  = QtGui.QPushButton('OK', self)
        # Connections
        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self.accept)
        # Buttons layout
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(cancel)
        hbox.addWidget(ok)
        return hbox