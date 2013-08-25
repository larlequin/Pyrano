#!/usr/bin/python
# -*- coding: utf-8 -*-
import rpy2.robjects as robjects

import os
import sys
import csv
import platform
import RunRScript as rsc
import SaveFile as savef
from PyQt4 import QtGui
from PyQt4 import QtCore
from multiprocessing import Process
from threading import Thread

__pname__ = "Run R ANOVA on RT"
__version__ = "1.0.0"
__date__ = "2013/08/22"
__author__ = "G.T. Vallet"


# -----------------------------------------------------------------------------
# SUMMARY
# -----------------------------------------------------------------------------
class Summary(QtGui.QWidget):
    """Summary tab to summarized variables
    """
    def __init__(self, parent=None):
        super(Summary, self).__init__()
        self.sums = QtGui.QWidget()
        self.main = parent
        # Widgets to display the summary variables
        sum_layout = self.sum_vars()
        self.r = rsc.RunRScript(self.main.csv)
        # Run R button
        raov_layout = self.run_aov()
        # Final layout
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(sum_layout)
        vbox.addWidget(raov_layout)
        self.sums.setLayout(vbox)

    def run_aov(self):
        aov = QtGui.QWidget()
        aov_button = QtGui.QPushButton('Run ANOVA', aov)
        # Layout button run AOV
        hbox_aov = QtGui.QHBoxLayout()
        hbox_aov.addStretch(1)
        hbox_aov.addWidget(aov_button)
        aov.setLayout(hbox_aov)
        # Connection -------------------------------------------------#
        self.connect(aov_button, QtCore.SIGNAL('clicked()'), self.buttonClicked)
        return aov

    def buttonClicked(self):
        self.main.status.showMessage("Running ANOVA", 5000)        
        if self.main.exp['run_cr']:
            self.r.desc_data(self.main.exp, 'CR')
            self.r.anova(self.main.exp, self.main.filtrt, 'CR')
        if self.main.filtrt['min'] != 'NULL' or self.main.filtrt['sdv'] != 'NULL':
            self.r.desc_data(self.main.exp, 'CR')
            self.r.anova(self.main.exp, self.main.filtrt, 'RT')
        else:
            self.r.desc_data(self.main.exp, 'RT')
            self.r.anova(self.main.exp, None, 'RT')    
        self.main.status.showMessage("ANOVA completed", 2500)
        stats = self.r.get_stats()
        aov = self.r.get_aov()
        for dv in stats.keys():
            if dv == "RT":
                self.r_rt = r_results(self, self.main, stats[dv], aov[dv], "REACTION TIMES")
                self.r_rt.show()    
            elif dv == "CR":
                self.r_cr = r_results(self, self.main, stats[dv], aov[dv], "CORRECT RESPONSES RATE")                
                self.r_cr.show()    

    def startR(self):
        self.r = rsc.RunRScript(self.main.csv)
        return True

    def get_ranova(self):
        return self.r.get_layout()

    def sum_vars(self):
        sumvar = QtGui.QWidget()
        # Data
        dt_txt = QtGui.QLabel("Data")
        self.dt_disp = QtGui.QLineEdit('Not defined', sumvar)
        self.dt_disp.setReadOnly(True)
        # DV
        dv_txt = QtGui.QLabel("DV")
        self.dv_disp = QtGui.QLineEdit('Not defined', sumvar)
        self.dv_disp.setReadOnly(True)        
        # Within
        with_txt = QtGui.QLabel("Within")
        self.with_disp = QtGui.QLineEdit('Not defined', sumvar)
        self.with_disp.setReadOnly(True)
        # Between
        betw_txt = QtGui.QLabel("Between")
        self.betw_disp = QtGui.QLineEdit('Not defined', sumvar)
        self.betw_disp.setReadOnly(True)
        # Data Filtered 
        filtr_grp = QtGui.QGroupBox("RT Filtered")
        min_txt = QtGui.QLabel("Min RT")
        max_txt = QtGui.QLabel("Max RT")
        std_txt = QtGui.QLabel("STD")
        self.min = QtGui.QLineEdit()
        self.min.setReadOnly(True)
        self.max = QtGui.QLineEdit()
        self.max.setReadOnly(True)
        self.std = QtGui.QLineEdit()
        self.std.setReadOnly(True)
        # Layout groupbox
        grp_box = QtGui.QGridLayout()
        grp_box.addWidget(min_txt, 0, 0)  
        grp_box.addWidget(self.min, 0, 1)
        grp_box.addWidget(max_txt, 1, 0)
        grp_box.addWidget(self.max, 1, 1)
        grp_box.addWidget(std_txt, 2, 0)
        grp_box.addWidget(self.std, 2, 1)
        filtr_grp.setLayout(grp_box)          
        # Grid Layout --------------------------------------------------#
        grid_layout = QtGui.QGridLayout(sumvar)
        grid_layout.addWidget(dt_txt, 0, 0)
        grid_layout.addWidget(self.dt_disp, 0, 1)
        grid_layout.addWidget(filtr_grp, 0, 2, 3, 1)
        grid_layout.addWidget(dv_txt, 1, 0)        
        grid_layout.addWidget(self.dv_disp, 1, 1)
        grid_layout.addWidget(with_txt, 2, 0)        
        grid_layout.addWidget(self.with_disp, 2, 1)
        grid_layout.addWidget(betw_txt, 3, 0)        
        grid_layout.addWidget(self.betw_disp, 3, 1)
        sumvar.setLayout(grid_layout)
        return sumvar

    def update_sum(self):
        self.dt_disp.setText(self.main.csv['file'])
        self.dv_disp.setText(self.format_txt(self.main.exp['dv']))
        self.with_disp.setText(self.format_txt(self.main.exp['within']))
        self.betw_disp.setText(self.format_txt(self.main.exp['between']))
        self.min.setText(self.main.filtrt['min'])
        self.max.setText(self.main.filtrt['max'])
        self.std.setText(self.main.filtrt['sdv'])

    def format_txt(self, raw_txt):
        if len(raw_txt) > 1 and type(raw_txt) is list:
            return "; ".join(raw_txt)
        elif len(raw_txt) == 1 and type(raw_txt) is list:
            return str(raw_txt[0])
        else:
            return str(raw_txt)

    def get_layout(self):
        return self.sums


# -----------------------------------------------------------------------------
# LOAD DATA FILE
# -----------------------------------------------------------------------------
class Data(QtGui.QWidget):
    """Data tab to load data set
    """
    def __init__(self, parent=None, exp=None):
        super(Data, self).__init__()
        self.data = QtGui.QWidget()
        self.main = parent
        self.exp = exp
        file_layout = self.select_file()
        opt_csv = self.csv_opt()
        opt_cr = self.cor_resp()
        # Finale widget layout
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(opt_csv)
        vbox.addWidget(opt_cr)
        vbox.addLayout(file_layout)
        self.data.setLayout(vbox)

    def select_file(self):
        # Define the label
        txt_data = QtGui.QLabel("<b>Data set</b>", self.data)
        # Feedback to display the filename
        self.cur_data = QtGui.QLineEdit("Null", self.data)
        self.cur_data.setReadOnly(True)
        # Button to launch the choose file dialog
        open_button = QtGui.QPushButton("...", self.data)
        open_button.setFixedWidth(50)
        open_button.setToolTip("Select the data file to load")
        self.connect(open_button, QtCore.SIGNAL('clicked()'), self.buttonClicked)
        # Select file layout
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(txt_data)
        hbox.addWidget(self.cur_data)
        hbox.addWidget(open_button)
        return hbox

    def csv_opt(self):
        # Groupbox ----------------------------------------------------------------#
        opt_csv = QtGui.QGroupBox("CSV Options")
        opt_csv.setCheckable(True)
        opt_csv.setChecked(False)
        # Delimiter widgets------------------------------------------------------#
        txt_delim = QtGui.QLabel("CSV delimiter", self)
        # Create a ComboBox to select the CSV delimiter
        self.csv_delim = QtGui.QComboBox(self)
        delims = [";", ",", ":", "\t", "."]
        self.csv_delim.addItems(delims)
        # Layout
        hbox_delim = QtGui.QHBoxLayout()
        hbox_delim.addWidget(txt_delim)
        hbox_delim.addWidget(self.csv_delim)
        hbox_delim.addStretch(1)
        # Lines to skip widgets------------------------------------------------#
        txt_skip = QtGui.QLabel("Number of lines to skip", self)
        # Create a line edit to enter number of lines to skip
        self.lines = QtGui.QLineEdit(self)
        self.lines.setMaxLength(4)
        self.lines.setText("0")
        # Layout ---------------------------------------------------------------------#
        hbox_lines = QtGui.QHBoxLayout()
        hbox_lines.addWidget(txt_skip)
        hbox_lines.addWidget(self.lines)
        hbox_lines.addStretch(1)
        # Intern layout ------------------------------------------------------------#
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox_delim)
        vbox.addLayout(hbox_lines)
        opt_csv.setLayout(vbox)
        # Connections -------------------------------------------------------------#
        self.csv_delim.activated[int].connect(lambda: self.get_csvopt(opt_csv))
        self.lines.textEdited.connect(lambda: self.get_csvopt(opt_csv))
        opt_csv.clicked.connect(lambda: self.get_csvopt(opt_csv))
        return opt_csv

    def cor_resp(self):
        # Groupbox ----------------------------------------------------------------#
        opt_resp = QtGui.QGroupBox("Correct responses")
        opt_resp.setCheckable(True)
        opt_resp.setChecked(False)
        # Define correct responses
        txt_cr = QtGui.QLabel("Correct responses   ", self.exp)
        cur_cr = QtGui.QLineEdit()
        cur_cr.setFixedWidth(200)
        cr_button = QtGui.QPushButton("...", self.exp)
        cr_button.setFixedWidth(50)
        cr_button.setToolTip("Select the correct responses column (0 false, 1 correct)")
        txt = "Please select the <b>correct responses</b> column"        
        # Connections --------------------------------------------------------------#
        self.connect(cr_button, QtCore.SIGNAL('clicked()'), lambda: self.exp.buttonClicked(txt, "cr", cur_cr))
        self.connect(opt_resp, QtCore.SIGNAL('clicked()'), lambda: self.crClicked(opt_resp))
        # Layout ----------------------------------------------------------------------#
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(txt_cr)
        hbox.addWidget(cur_cr)
        hbox.addWidget(cr_button)
        # Intern layout ------------------------------------------------------------#
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox)
        opt_resp.setLayout(vbox)
        return opt_resp

    def crClicked(self, opt_resp):
        if opt_resp.isChecked():
            self.main.exp['run_cr'] = True
        else:
            self.main.exp['run_cr'] = False

    def buttonClicked(self):
        self.emit(QtCore.SIGNAL("clicked()"))
    
    def set_filename(self, fname):
        self.cur_data.setText(fname)

    def get_csvopt(self, opt_csv):
        if opt_csv.isChecked():
            self.main.csv['sep'] = map(str, self.csv_delim.currentText())[0]
            self.main.csv['toskip'] = map(str, self.lines.text())[0]
        else:
            self.main.csv['sep'] = ";"
            self.main.csv['toskip'] = "0"

    def get_layout(self):
        return self.data


# -----------------------------------------------------------------------------
# DEFINE THE EXPERIMENTAL VARIABLES
# -----------------------------------------------------------------------------
class DefVariables(QtGui.QWidget):
    """Class to define the different experimental variables
    """
    def __init__(self, parent=None):
        super(DefVariables, self).__init__()
        self.main = parent
        self.exp = QtGui.QWidget()
        subj_layout = self.subj()
        dv_layout = self.dependentvar()
        between_layout = self.betweenvar()
        within_layout = self.withinvar()
        # Finale widget layout
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(subj_layout)
        vbox.addLayout(dv_layout)
        vbox.addLayout(within_layout)
        vbox.addLayout(between_layout)
        self.exp.setLayout(vbox)

    def subj(self):
        txt_subj = QtGui.QLabel("Subjects variable     ", self.exp)
        cur_subj = QtGui.QLineEdit()
        cur_subj.setFixedWidth(200)
        subj_button = QtGui.QPushButton("...", self.exp)
        subj_button.setFixedWidth(50)
        subj_button.setToolTip("Select the subject column")
        txt = "Please select the <b>between</b> variable(s), if any"
        self.connect(subj_button, QtCore.SIGNAL('clicked()'), lambda: self.buttonClicked(txt, "wid", cur_subj))
        # Layout --------------------------------------------------------#
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(txt_subj)
        hbox.addWidget(cur_subj)
        hbox.addWidget(subj_button)
        return hbox

    def dependentvar(self):
        txt_dv = QtGui.QLabel("Dependent variable ", self.exp)
        cur_dv = QtGui.QLineEdit()
        cur_dv.setFixedWidth(200)
        dv_button = QtGui.QPushButton("...", self.exp)
        dv_button.setFixedWidth(50)
        dv_button.setToolTip("Select the dependent variable column")
        txt = "Please select the <b>between</b> variable(s), if any"        
        self.connect(dv_button, QtCore.SIGNAL('clicked()'), lambda: self.buttonClicked(txt, "dv", cur_dv))
        # Layout --------------------------------------------------------#
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(txt_dv)
        hbox.addWidget(cur_dv)
        hbox.addWidget(dv_button)
        return hbox

    def withinvar(self):
        txt_within = QtGui.QLabel("Within variable(s)    ", self.exp)
        cur_within = QtGui.QLineEdit()
        cur_within.setFixedWidth(200)
        within_button = QtGui.QPushButton("...", self.exp)
        within_button.setFixedWidth(50)
        within_button.setToolTip("Select the within variable(s) column(s), if any")
        txt = "Please select the <b>between</b> variable(s), if any"
        self.connect(within_button, QtCore.SIGNAL('clicked()'), lambda: self.buttonClicked(txt, "within", cur_within))
        # Layout --------------------------------------------------------#
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(txt_within)
        hbox.addWidget(cur_within)
        hbox.addWidget(within_button)
        return hbox

    def betweenvar(self):
        txt_betw = QtGui.QLabel("Between variable(s)", self.exp)
        cur_betw = QtGui.QLineEdit()
        cur_betw.setFixedWidth(200)
        between_button = QtGui.QPushButton("...", self.exp)
        between_button.setFixedWidth(50)
        between_button.setToolTip("Select the between variable(s) column(s), if any")
        txt = "Please select the <b>between</b> variable(s), if any"
        self.connect(between_button, QtCore.SIGNAL('clicked()'), lambda: self.buttonClicked(txt, "between", cur_betw))
        # Layout --------------------------------------------------------#
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(txt_betw)
        hbox.addWidget(cur_betw)
        hbox.addWidget(between_button)
        return hbox   

    def buttonClicked(self, txt, cur_var, cur_lineedit):
        chvar = ChooseVars(self, txt, self.main.vars, self.main.msg)
        if chvar.exec_() == QtGui.QDialog.Accepted:
            var_select =  chvar.getValues()
            self.main.exp[cur_var] = var_select
            if cur_var == 'dv':
                self.main.filtrt["RTidx"] = self.main.vars.index(self.main.exp['dv'][0])+1
            cur_lineedit.setText(("; ".join(var_select)))

    def get_layout(self):
        return self.exp


# -----------------------------------------------------------------------------
# FILTERING REACTION TIME
# -----------------------------------------------------------------------------
class FilterRT(QtGui.QWidget):
    """Class to filter the reaction time base on 
          minimum and maximum value and/or standard
          deviations from the mean
    """
    def __init__(self, parent=None):
        super(FilterRT, self).__init__()
        self.main = parent
        self.filrt = QtGui.QWidget()
        extr_rt_layout = self.min_max()
        std_layout = self.std()
        # Finale widget layout
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(extr_rt_layout)
        vbox.addWidget(std_layout)
        self.filrt.setLayout(vbox)

    def min_max(self):
         # Groupbox Min/Max-----------------------------------------------------#
        opt_minmax = QtGui.QGroupBox("Extreme Values Filter")
        opt_minmax.setCheckable(True)
        opt_minmax.setChecked(False)
        # Min/Max values widgets---------------------------------------------#
        txt_min = QtGui.QLabel("Min.", self)
        rtmin = QtGui.QLineEdit(self)
        rtmin.setMaximumWidth(65)
        txt_max = QtGui.QLabel("Max.", self)
        rtmax = QtGui.QLineEdit(self)
        rtmax.setMaximumWidth(65)
        # Layout ----------------------------------------------------------------------#
        hbox_extrt = QtGui.QHBoxLayout()
        hbox_extrt.addWidget(txt_min)
        hbox_extrt.addWidget(rtmin)
        hbox_extrt.addWidget(txt_max)
        hbox_extrt.addWidget(rtmax)
        hbox_extrt.addStretch(1)
        opt_minmax.setLayout(hbox_extrt)
        # Connections -------------------------------------------------------------#
        rtmin.textEdited.connect(lambda: self.get_opt(opt_minmax, 'min', rtmin))
        rtmax.textEdited.connect(lambda: self.get_opt(opt_minmax, 'max', rtmax))
        opt_minmax.clicked.connect(lambda: self.get_opt(opt_minmax, 'min', rtmin))
        opt_minmax.clicked.connect(lambda: self.get_opt(opt_minmax, 'max', rtmax))
        return opt_minmax

    def std(self):
         # Groupbox STD-----------------------------------------------------------#
        opt_std = QtGui.QGroupBox("Standard Deviation (std) Filter")
        opt_std.setCheckable(True)
        opt_std.setChecked(False)
        # STD values widgets----------------------------------------------------#
        txt_std = QtGui.QLabel("Std number", self)
        std = QtGui.QLineEdit(self)
        std.setMaximumWidth(65)
        # Layout ----------------------------------------------------------------------#
        hbox_std = QtGui.QHBoxLayout()
        hbox_std.addWidget(txt_std)
        hbox_std.addWidget(std)
        hbox_std.addStretch(1)
        opt_std.setLayout(hbox_std)
        # Connection ----------------------------------------------------------------#
        std.textEdited.connect(lambda: self.get_opt(opt_std, 'sdv', std))
        opt_std.clicked.connect(lambda: self.get_opt(opt_std, 'sdv', std))
        return opt_std

    def get_opt(self, cur_opt, cur_val, cur_wid):
        if cur_opt.isChecked():
            self.main.filtrt[cur_val] = str(cur_wid.text())
        else:
            self.main.filtrt[cur_val] = 'NULL'

    def get_layout(self):
        return self.filrt

# -----------------------------------------------------------------------------
# DIALOG WINDOW TO SELECT VARIABLES
# -----------------------------------------------------------------------------
class ChooseVars(QtGui.QDialog):
    def __init__(self, parent=None, txt="Please select the variables to use", vars=None, msg=None):
        QtGui.QDialog.__init__(self, parent)
        self.msg = msg
        # Initiate the window and the layout
        self.setWindowTitle('Variables selection')
        # Add some text tips
        info_txt = QtGui.QLabel(txt, self)
        # Create a list widget to display the variable names
        self.list_vars(vars)
        # Cancel and ok buttons
        bt_layout = self.dial_buttons()
        #  Widgets layout
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(info_txt)
        vbox.addWidget(self.lvars)
        vbox.addStretch(1)
        vbox.addLayout(bt_layout)
        self.setLayout(vbox)

    def list_vars(self, vars):
        self.lvars = QtGui.QListWidget(self)
        self.lvars.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        try:
            for var in vars:
                 self.lvars.addItem(var)
        except TypeError:
            self.msg.critical("Please defined a data set!")

    def dial_buttons(self):
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

    def getValues(self):
        newvars = []
        [newvars.append(str(x.text())) for x in self.lvars.selectedItems()]
        return newvars


# -----------------------------------------------------------------------------
# DIALOG WINDOW TO SELECT VARIABLES
# -----------------------------------------------------------------------------
class r_results(QtGui.QDialog):
    """docstring for r_results"""
    def __init__(self, parent=None, main=None, stats=None, aov=None, title="R Results"):
        super(r_results, self).__init__()
        self.main = main
        self.parent = parent
        # Main window properties ---------------------------------------------#
        self.setWindowTitle(title)
        if title == "CORRECT RESPONSES RATE":
            self.setGeometry(425, 300, 450, 550)
            # Cancel and ok buttons
            bt_layout = self.dial_buttons("aov_cr")
        else:
            self.setGeometry(350, 100, 450, 550)
            # Cancel and ok buttons
            bt_layout = self.dial_buttons("aov_rt")
        # --------------------------------------------------------------------------------#
        displ = QtGui.QTextEdit("", self)
        displ.setReadOnly(True)
        cursor = displ.textCursor()
        self.add_text("DESCRIPTIVE STATISTICS", displ, cursor)
        self.print_table(stats, True, cursor)
        for idx, cur_aov in enumerate(aov):
            if idx == 0:
                 self.add_text("ANOVA", displ, cursor)
            elif idx == 1:
                 self.add_text("Mauchly's Test", displ, cursor)
            else:
                self.add_text("ANOVA Corrected", displ, cursor)
            self.print_table(cur_aov, False, cursor)
        # Layout ----------------------------------------------------------------------#
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(displ)
        vbox.addLayout(bt_layout)
        self.setLayout(vbox)

    def add_text(self, txt, displ, cursor):
        displ.append("<b>"+ txt + "</b>")
        cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor) 
        cursor.insertText("\n\n")

    def print_table(self, data, factors, cursor):
        nb_vars = len(data) - 6
        cursor.insertTable(len(data[0])+1, len(data))
        for i in data.names:
            cursor.insertText(str(i))
            cursor.movePosition(QtGui.QTextCursor.NextCell)
        for row in range(len(data[0])):
            for col in range(len(data)):
                if factors:
                    if col in range(nb_vars):
                        factor_level = data[col][row]
                        txt = data[col].levels[data[col][factor_level]-1]
                    else:
                        txt = self.format_txt(data[col][row])
                else:
                    txt = self.format_txt(data[col][row])
                cursor.insertText(str(txt))
                cursor.movePosition(QtGui.QTextCursor.NextCell)
        cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor) 
        cursor.insertText("\n\n")
        
    def format_txt(self, txt):
            if type(txt) is float:
                if str(txt).endswith(".0"):
                    return int(txt)
                else:
                    return round(float(txt), 2)
            else:
                return txt

    def dial_buttons(self, dt):
        save = QtGui.QPushButton('Save', self)
        cancel = QtGui.QPushButton('Cancel', self)
        ok  = QtGui.QPushButton('OK', self)
        # Connections
        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self.accept)
        save.clicked.connect(lambda: self.saveit(dt))
        # Buttons layout
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(save)
        hbox.addStretch(1)
        hbox.addWidget(cancel)
        hbox.addWidget(ok)
        return hbox

    def saveit(self, dt):
        fsv = savef.SaveFile(self)
        fsave= fsv.fname_save(".csv")
        fsv.write_raov(fsave, dt)


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
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.vars = None
        self.csv = {'file': 'data.csv', 'fpath': '/home/gtvallet/Documents/Divers/AnaR.py/data.csv', 'sep': ';', 'toskip': '0'}
        self.filtrt = {'RTidx': None, 'min': 'NULL', 'max': 'NULL', 'sdv': 'NULL'}
        self.exp = {'dv': ['RT_raw'], 'wid': ['Subjects'], 'within': ['encodage', 'catego'], 'between': 'NULL', 'cr': ['Resp_raw'], 'run_cr': True}
        # Summary class
        sc = Summary(self)
        # Initiate the message display class
        self.msg = MessageBox()
        self.menu()
        self.create_main_frame(sc)
        # Create a status bar
        self.status = self.statusBar()
        self.status.showMessage("Ready", 2500)
        # Start R and ez package through another process
        thr = Thread(target=self.runner, args=(sc,))
        thr.setDaemon(True)
        thr.start()
    
    def runner(self, sc):
        robjects.r("""library('ez')""")

    def create_main_frame(self, sc):        
        tabs = QtGui.QTabWidget()
        # Summary tab
        summary = sc.get_layout()
        # Variables tab
        expvar = DefVariables(self)
        exp = expvar.get_layout()
        # Data tab
        dt = Data(self , expvar)
        data = dt.get_layout()
        # Filter RT tab
        filrt = FilterRT(self)
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
        try:
            with open(fname) as fdata:
                r = csv.reader(fdata, delimiter=self.csv['sep'])
                if self.csv['toskip'] == '0':
                    pass
                else:
                    for i in range(int(self.csv['toskip'])):
                        r.next()
                self.vars = r.next()
        except IOError:
                self.msg.critical("Please select a data file")
                self.load_dtfile(dt)

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