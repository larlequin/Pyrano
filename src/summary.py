from PyQt4 import QtGui
from PyQt4 import QtCore
import runrscript as rsc
import rresults as printr

import dataview as dtv

class Summary(QtGui.QWidget):
    """Summary tab to summarized variables and
            options chosen.
    """
    def __init__(self, parent=None):
        super(Summary, self).__init__()
        self.sums = QtGui.QWidget()
        self.main = parent
        # Widgets to display the summary variables
        sum_layout = self.sum_vars()
        self.r = rsc.RunRScript(self.main.csv, self.main.msg)
        # Run R button
        raov_bt = self.run_aov()
        # Viewdata button
        viewdt_bt = self.viewdtbutton()
        # ------------------------------------------------
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(viewdt_bt)
        hbox.addWidget(raov_bt)
        # Final layout
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(sum_layout)
        vbox.addLayout(hbox)
        self.sums.setLayout(vbox)

    def viewdata(self):
        try:
            dview = dtv.ViewData(self, self.main.csv['dtmodel'], self.main.vars)
            dview.exec_()
        except:
            self.main.msg.critical("No data file selected!")

    def viewdtbutton(self):
        viewdt_button = QtGui.QPushButton('View data', self.sums)
        viewdt_button.clicked.connect(self.viewdata)
        return viewdt_button

    def run_aov(self):
        aov_button = QtGui.QPushButton('Run ANOVA', self)
        self.connect(aov_button, QtCore.SIGNAL('clicked()'), self.buttonClicked)
        return aov_button

    def buttonClicked(self):
        if self.main.csv['file'] == None:
            self.main.msg.critical("No data file selected!")
        elif self.main.exp['dv'] == 'NULL' or self.main.exp['wid']== 'NULL':
            self.main.msg.critical("The depend variable and subjects columns should be provided!")
        elif self.main.exp['within'] == 'NULL' and self.main.exp['between'] == 'NULL':
            self.main.msg.critical("A least one within or between factor should be indicated!")
        else:
            self.main.status.showMessage("Running ANOVA", 5000)        
            if self.main.exp['run_cr']:
                stats_done = self.r.desc_data(self.main.exp, self.main.filtrt, 'CR')
                if stats_done:
                    self.r.anova(self.main.exp, 'CR')
            if self.main.filtrt['min'] != 'NULL' or self.main.filtrt['sdv'] != 'NULL':
                stats_done = self.r.desc_data(self.main.exp, self.main.filtrt, 'RT')
                if stats_done:
                    self.r.anova(self.main.exp, 'RT')
            else:
                stats_done = self.r.desc_data(self.main.exp, None, 'RT')
                if stats_done:
                    self.r.anova(self.main.exp, 'RT')    
            if stats_done:
                self.main.status.showMessage("ANOVA completed", 2500)
                stats = self.r.get_stats()
                aov = self.r.get_aov()
                for dv in stats.keys():
                    if dv == "RT":
                        self.r_rt = printr.r_results(self, self.main, stats[dv], aov[dv], "DEPENDENT VARIABLE")
                        self.r_rt.show()    
                    elif dv == "CR":
                        self.r_cr = printr.r_results(self, self.main, stats[dv], aov[dv], "CORRECT RESPONSES RATE")                
                        self.r_cr.show()    

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
