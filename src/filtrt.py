from PyQt4 import QtGui


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
        """Define a minimal and/or maximal RT value.
        """
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
        """Define the number of standard deviations to filter the RT.
        """
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
