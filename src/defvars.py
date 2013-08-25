from PyQt4 import QtGui
from PyQt4 import QtCore

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
        """Define the subject variable column
        """
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
        """Define the dependent variable column
        """
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
        """Define the within variable(s) column(s)
        """
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
        """Define the between variable(s) column(s)
        """
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
# DIALOG WINDOW TO SELECT VARIABLES
# -----------------------------------------------------------------------------
class ChooseVars(QtGui.QDialog):
    """Dialog window to display and select the column(s) for a 
            specified variable.
    """
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

    def getValues(self):
        newvars = []
        [newvars.append(str(x.text())) for x in self.lvars.selectedItems()]
        return newvars