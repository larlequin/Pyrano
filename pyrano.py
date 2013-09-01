#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import platform
from PyQt4 import QtGui
from PyQt4 import QtCore

import src.filtrt as filt
import src.runrscript as rsc
import src.defdata as tabdata
import src.defvars as tabvars
import src.summary as tabsum

__pname__ = "PYthon running R ANOva (pyrano)"
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
        self.csv = {'file': 'Not defined', 'fpath': None, 'sep': ';', 'toskip': '0'}
        self.filtrt = {'RTidx': None, 'min': 'NULL', 'max': 'NULL', 'sdv': 'NULL'}
        self.exp = {'dv': 'NULL', 'wid': 'NULL', 'within': 'NULL', 'between': 'NULL', 'cr': None, 'run_cr': False}
        # Initiate the message display class
        self.msg = MessageBox()
        self.menu()
        self.create_main_frame()
        # Create a status bar
        self.status = self.statusBar()
        self.status.showMessage("Ready", 2500)

    def create_main_frame(self):        
        tabs = QtGui.QTabWidget()
        # Summary tab
        sc = tabsum.Summary(self)
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
        self.connect(tabs, QtCore.SIGNAL('currentChanged(int)'), lambda: self.update_sum(tabs, sc))

    def update_sum(self, tabs, sc):
        if tabs.currentIndex()==0:
            sc.update_sum()

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