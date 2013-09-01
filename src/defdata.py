import os
import csv
from PyQt4 import QtGui
from PyQt4 import QtCore

# -----------------------------------------------------------------------------
# LOAD DATA FILE
# -----------------------------------------------------------------------------
class DefData(QtGui.QWidget):
    """Data tab to load a data set
    """
    def __init__(self, parent=None, exp=None):
        super(DefData, self).__init__()
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
        """Select a file through the file dialog window
        """
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
        """User can specified the file delimiter and a number
              of lines to skip to read the csv file.
        """
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
        """User can define a column where the correct/incorrect 
              responses are indicated (1 == OK, 0 == OUT).
            If the option is checked, an ANOVA on correct response rates
              will automatically be computed.
        """
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
        """Define if correct response rate should be computed
              based on the checked/unchecked status.
        """
        if opt_resp.isChecked():
            self.main.exp['run_cr'] = True
        else:
            self.main.exp['run_cr'] = False

    def buttonClicked(self):
        # self.emit(QtCore.SIGNAL("clicked()"))
        self.fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '~', "Text / CSV files (*.txt *.csv)")
        if self.fname:
            self.set_filename(self.fname)
            self.load_vars()
        
    def load_vars(self):
        if self.fname:
            fname_shrt = os.path.split(str(self.fname))[1]
            self.main.csv['file'] = fname_shrt
            self.main.csv['fpath'] = self.fname
            self.main.status.showMessage("Data {0} loaded".format(self.fname), 5000)
            dtmodel = QtGui.QStandardItemModel(self)
            try:
                with open(self.fname) as fdata:
                    r = csv.reader(fdata, delimiter=self.main.csv['sep'])
                    if self.main.csv['toskip'] == '0':
                        pass
                    else:
                        for i in range(int(self.main.csv['toskip'])):
                            r.next()
                    self.main.vars = r.next()
                    for row in r:
                        items = [QtGui.QStandardItem(field)
                                                            for field in row]
                        dtmodel.appendRow(items)
            except IOError:
                    self.msg.critical("Please select a data file")
                    self.buttonClicked()
            self.main.csv['dtmodel'] = dtmodel
    
    def set_filename(self, fname):
        self.cur_data.setText(fname)

    def get_csvopt(self, opt_csv):
        """Define the csv options based on the checked/unchecked status.
        """
        if opt_csv.isChecked():
            self.main.csv['sep'] = map(str, self.csv_delim.currentText())[0]
            self.main.csv['toskip'] = map(str, self.lines.text())[0]
        else:
            self.main.csv['sep'] = ";"
            self.main.csv['toskip'] = "0"
        self.load_vars()
        print self.main.vars

    def get_layout(self):
        return self.data
