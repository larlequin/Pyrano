from PyQt4 import QtGui
import rpy2.robjects as robjects

class SaveFile(QtGui.QDialog):
    """Qt save file interface
     """
    def __init__(self, parent=None):
        super(SaveFile, self).__init__()
        self.main = parent

    def fname_save(self, ftype="."):
        return QtGui.QFileDialog.getSaveFileName(self, 'Save File', ftype)
        
    def write_raov(self, fname, aov_name, stat_name='NULL'):
        """Save ANOVA and descriptive data R objects as a csv file
              using a custom R function
        """
        robjects.r("""source('~/R_Functions/WriteAOV.R')""")
        toeval = "WriteAOV({0}, {1}, data={2})".format("'" + fname + "'", aov_name, stat_name)
        robjects.r(toeval)