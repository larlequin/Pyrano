#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import csv
import platform
from PyQt4 import QtGui
from PyQt4 import QtCore

import src.filtrt as filt
import src.runrscript as rsc
import src.defdata as tabdata
import src.defvars as tabvars
import src.summary as tabsum

__pname__ = "Python script to run R ANOva (pyrano)"
__version__ = "1.0.0"
__date__ = "2013/08/25"
__author__ = "G.T. Vallet"


# -----------------------------------------------------------------------------
# SIMPLE CLASS TO DISPLAY SHORT MESSAGES
# -----------------------------------------------------------------------------
class MessageBox(QtGui.QWidget):
    """ Simple message box to display short messages 
    """
    def __init__ (self, parent=None):
        """ Class initialiser """
        QtGui.QWidget.__init__(self, parent)

    def critical(self, txt):
        QtGui.QMessageBox.critical(self, 'WARNING', txt,
            QtGui.QMessageBox.Ok)


# -----------------------------------------------------------------------------
# MAIN WINDOW RAn
# -----------------------------------------------------------------------------
class MainWindow(QtGui.QMainWindow):
    """ Initiate the main window with a tab widget,
           menu and status bar
    """
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.vars = None
        self.csv = {'file': 'data.csv', 'fpath': '/home/gtvallet/Documents/Divers/AnaR.py/data.csv', 'sep': ';', 'toskip': '0'}
        self.filtrt = {'RTidx': '6', 'min': '200', 'max': '2000', 'sdv': '2.5'}
        self.exp = {'dv': ['RT_raw'], 'wid': ['Subjects'], 'within': ['encodage', 'catego'], 'between': 'NULL', 'cr': ['Resp_raw'], 'run_cr': True}
        # Summary class
        sc = tabsum.Summary(self)
        sc.startR()
        # Initiate the message display class
        self.msg = MessageBox()
        self.menu()
        self.create_main_frame(sc)
        # Create a status bar
        self.status = self.statusBar()
        self.status.showMessage("Ready", 2500)

    def create_main_frame(self, sc):        
        tabs = QtGui.QTabWidget()
        # Summary tab
        summary = sc.get_layout()
        # Variables tab
        expvar = tabvars.DefVariables(self)
        exp = expvar.get_layout()
        # Data tab
        dt = tabdata.DefData(self , expvar)
        data = dt.get_layout()
        # Filter RT tab
        filrt = filt.FilterRT(self)
        frt = filrt.get_layout()
        # Layout
        tabs.addTab(summary, 'Summary')
        tabs.addTab(data, 'Data')
        tabs.addTab(exp, "Variables")
        tabs.addTab(frt, "RT Filtering")
        self.setCentralWidget(tabs)
        # Connections ---------------------------------------------#
        self.connect(dt, QtCore.SIGNAL("clicked()"), lambda: self.load_dtfile(dt))
        self.connect(tabs, QtCore.SIGNAL('currentChanged(int)'), lambda: self.update_sum(tabs, sc))

    def update_sum(self, tabs, sc):
        if tabs.currentIndex()==0:
            sc.update_sum()

    def load_dtfile(self, dt):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '~', "Text / CSV files (*.txt *.csv)")
        dt.set_filename(fname)
        fname_shrt = os.path.split(str(fname))[1]
        self.csv['file'] = fname_shrt
        self.csv['fpath'] = fname
        if str(fname).endswith(".csv") or str(fname).endswith(".txt"):
            self.status.showMessage("Data {0} loaded".format(fname), 5000)
        else:
            self.msg.critical("Please select a text or CSV file")
            self.load_dtfile(dt)   
        dtmodel = QtGui.QStandardItemModel(self)
        try:
            with open(fname) as fdata:
                r = csv.reader(fdata, delimiter=self.csv['sep'])
                if self.csv['toskip'] == '0':
                    pass
                else:
                    for i in range(int(self.csv['toskip'])):
                        r.next()
                self.vars = r.next()
                for row in r:
                    items = [QtGui.QStandardItem(field)
                                                        for field in row]
                    dtmodel.appendRow(items)
        except IOError:
                self.msg.critical("Please select a data file")
                self.load_dtfile(dt)
        self.csv['dtmodel'] = dtmodel

    def menu(self):
        """ Define the action in the Menu and Toolbar
        """
        # Exit
        exitAction = QtGui.QAction(QtGui.QIcon('exit2.jpeg'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        # About
        about = QtGui.QAction(QtGui.QIcon('about.jpeg'), 'About', self)
        about.setStatusTip('More information about %s' % __pname__)
        about.triggered.connect(self.about)
        # Main Menu
        menubar  = self.menuBar()
        main_menu = menubar.addMenu('&Menu')
        main_menu.addAction(exitAction)
        # Help menu
        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(about)  

    def about(self):
        """ Define the action in the help menu
        """
        QtGui.QMessageBox.about(self, "About %s" %  __pname__,
        """<b>%s</b> v %s
        <p><b>Licence:</b> GPLv3 by %s
        <p>This application can be run an R Script on raw data to compute 
        mean, sd, se, error per condition, with or without RT filtering.
        <p>Python %s on %s""" % (
          __pname__, __version__, __author__, 
           platform.python_version(), platform.system()
            )
        )


# --------------------------------------------------------------
# START THE APPLICATION
# --------------------------------------------------------------
def main():
    """Define the main application
        Calling the UI
    """
    app = QtGui.QApplication(sys.argv)
    RAn = MainWindow()
    RAn.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()