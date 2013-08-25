import rpy2.robjects as robjects

class RunRScript(object):
    """A class to run a R script through python.
        Allow to load a data set (csv file), 
        Filter reaction times through a custom R function,
        Subset data based on a correct response column and 
          compute correct response rates by subject and conditions,
        Compute descriptive data,
        Run ANOVA through the ez package.
    """
    def __init__(self, fdata):
        super(RunRScript, self).__init__()
        robjects.r("""library('ez')""")
        self.csvfile = fdata
        self.dt = None
        self.aov = {}
        self.stats = {}

    def getdata(self):
        """Load a data set through a csv file.
        """
        toeval = "dt = read.table(%s, sep=%s, header=T)" % (self.format_r(self.csvfile['fpath']), self.format_r(self.csvfile['sep']))
        self.dt = robjects.r(toeval)  

    def filter(self, daov, dfilter):
        """Filter reaction time with minimum/maximum values and/or
              specified standard deviations.
        """
        self.getdata()
        robjects.r("""source('rscripts/filtRT.R')""")
        expvars = self.format_vector(daov)
        if dfilter['min'] == 'NULL' and dfilter['max'] == 'NULL':
            toeval = "dt = filtRT(dt, RTidx={0}, vars={1}, fpass=NULL, sdv={2})".format(dfilter['RTidx'], expvars, dfilter['sdv'])
        else:
            toeval = "dt = filtRT(dt, RTidx={0}, vars={1}, fpass=c({2}, {3}), sdv={4})".format(dfilter['RTidx'], expvars, dfilter['min'], dfilter['max'], dfilter['sdv'])
        dt_filter = robjects.r(toeval)

    def correct_resp(self, daov, dfilter):
        """Compute the correct response rates by subject and conditions
               and keep only the correct responses to compute the ANOVA
               on the reaction times.
        """
        if dfilter:
                self.filter(daov, dfilter)
        # Create a new data frame with the correct responses as DV 
        cur_var = self.format_ddply(daov)
        toeval = "dt_cr = ddply(dt, {0}, function(x) 1-(nrow(x)-nrow(x[x${1}==1,]))/nrow(x))".format(cur_var, daov['cr'][0])
        print toeval
        cr = robjects.r(toeval)
        print cr
        # Keep only the good responses for the analyses
        toeval = "dt = dt[ dt${0} == 1, ]".format(daov['cr'][0])
        dt_ok = robjects.r(toeval)

    def desc_data(self, daov, dfilter, dv):    
        """Compute descriptive data (mean, sd, se, ci)
        """
        robjects.r("""source('rscripts/summarySEwithin.R')""")
        if self.dt:
            pass
        else:
            self.getdata()
        if dv == 'CR':
            self.correct_resp(daov, dfilter)
            toeval = "stats_cr = summarySEwithin(data=dt_cr, wid='{0}', dv='{1}', between={2}, within={3})".format(daov['wid'][0], 'V1', self.format_r(daov['between']), self.format_r(daov['within']))
        elif dv == 'RT':
            toeval = "stats_rt = summarySEwithin(data=dt, wid='{0}', dv='{1}', between={2}, within={3})".format(daov['wid'][0], daov['dv'][0], self.format_r(daov['between']), self.format_r(daov['within']))            
        self.stats[dv] = robjects.r(toeval)

    def anova(self, daov, dv):
        """Run ANOVA through the ez package
        """
        if dv == 'CR':
            toeval = "aov_cr = ezANOVA(dt_cr, dv=%s, wid=%s, between=%s, within=%s)" % ("V1", self.format_ez(daov['wid']), self.format_ez(daov['between']), self.format_ez(daov['within']))             
        elif dv == 'RT': 
            toeval = "aov_rt = ezANOVA(dt, dv=%s, wid=%s, between=%s, within=%s)" % (self.format_ez(daov['dv']), self.format_ez(daov['wid']), self.format_ez(daov['between']), self.format_ez(daov['within'])) 
        self.aov[dv] = robjects.r(toeval)

    def format_ddply(self, daov):
        """Format variable to fit into a ddply object
        """
        if daov['between'] != 'NULL':
            if type(daov['between']) is list and len(daov['between']) > 1:
                ivb = ", ".join(daov['between'])
            else: 
                ivb = daov['between'][0]
        else:
            ivb = ""
        if daov['within'] != 'NULL':
            if type(daov['within']) is list and len(daov['within']) > 1:
                ivw = ", ".join(daov['within'])
            else: 
                ivw = daov['within'][0]
        else:
                ivw = ""
        if daov['within'] != 'NULL' and daov['between'] != 'NULL':
            return ".(" + daov['wid'][0] + ", " + ivb + ", " + ivw + ")"
        else:
            return ".(" + daov['wid'][0] + ", " + ivb + ivw + ")"

    def format_ez(self, curvar):
        """Format variable to fit into an ez object
        """
        if curvar != 'NULL' and type(curvar) is list:
            if len(curvar) == 1:
                return curvar[0]
            else:
                return ".("+ ", ".join(curvar) + ")"
        else:
            return curvar

    def format_vector(self, daov):
        """Format variable to fit into a R vector object
        """
        if daov['between'] != 'NULL':
            if type(daov['between']) is list and len(daov['between']) > 1:
                ivb = (", ".join("'" + item + "'" for item in daov['between']))
            else: 
                ivb = "'" + daov['between'][0] + "'"
        else:
            ivb = ""
        if daov['within'] != 'NULL':
            if type(daov['within']) is list and len(daov['within']) > 1:
                ivw = (", ".join("'" + item + "'" for item in daov['within']))
            else: 
                ivw = "'" + daov['within'][0] + "'"
        else:
                ivw = ""
        if daov['within'] != 'NULL' and daov['between'] != 'NULL':
            return "c('" + daov['wid'][0] + "', " + ivb + ", " + ivw + ")"
        else:
            return "c('" + daov['wid'][0] + "', " + ivb + ivw + ")"

    def format_r(self, cur_var):
        """Format variable to fit into a ddply object
        """
        if cur_var != 'NULL':
            if type(cur_var) is list and len(cur_var) > 1:
                return "c(" + (", ".join("'" + item + "'" for item in cur_var)) + ")"
            elif type(cur_var) is list and len(cur_var) == 1:
                return "'" + cur_var[0] + "'"
            else: 
                return "'" + cur_var + "'"
        else:
            return "NULL"

    def get_aov(self):
        return self.aov

    def get_stats(self):
        return self.stats