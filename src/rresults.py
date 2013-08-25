from PyQt4 import QtGui
import src.savefile as savef

# -----------------------------------------------------------------------------
# PRINT R RESULTS
# -----------------------------------------------------------------------------
class r_results(QtGui.QDialog):
    """A class to display the results produce by R.
        Use a qtextedit widget and tables. 
    """
    def __init__(self, parent=None, main=None, stats=None, aov=None, title="R Results"):
        super(r_results, self).__init__()
        self.main = main
        self.parent = parent
        # Main window properties ---------------------------------------------#
        self.setWindowTitle(title)
        if title == "CORRECT RESPONSES RATE":
            self.setGeometry(425, 300, 450, 550)
            # Cancel and ok buttons
            bt_layout = self.dial_buttons("aov_cr", "stats_cr")
        else:
            self.setGeometry(350, 100, 450, 550)
            # Cancel and ok buttons
            bt_layout = self.dial_buttons("aov_rt", "stats_rt")
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
        """Basic function to send bold text to the qtextedit widget
        """
        displ.append("<b>"+ txt + "</b>")
        cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor) 
        cursor.insertText("\n\n")

    def print_table(self, data, factors, cursor):
        """Insert a table in the qtextedit widget,
              fill it with a R data frame object.
            Automatically add the column names
        """
        nb_vars = len(data) - 6
        cursor.insertTable(len(data[0])+1, len(data))
        for i in data.names:
            cursor.insertText(str(i))
            cursor.movePosition(QtGui.QTextCursor.NextCell)
        for row in range(len(data[0])):
            for col in range(len(data)):
                if factors:
                    if col in range(nb_vars):
                        factor_level = data[col][row] -1
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
        """Format text produced by R to an appropriate format
        """
        if type(txt) is float:
            if str(txt).endswith(".0"):
                return int(txt)
            else:
                return round(float(txt), 2)
        else:
            return txt

    def dial_buttons(self, dt, stats):
        """Create a Save, Cancel and OK buttons
        """
        save = QtGui.QPushButton('Save', self)
        cancel = QtGui.QPushButton('Cancel', self)
        ok  = QtGui.QPushButton('OK', self)
        # Connections
        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self.accept)
        save.clicked.connect(lambda: self.saveit(dt, stats))
        # Buttons layout
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(save)
        hbox.addStretch(1)
        hbox.addWidget(cancel)
        hbox.addWidget(ok)
        return hbox

    def saveit(self, dt, stats):
        """Save the R objects as csv file
              using a custom R function.
        """
        fsv = savef.SaveFile(self)
        fsave= fsv.fname_save(".csv")
        fsv.write_raov(fsave, dt, stats)
