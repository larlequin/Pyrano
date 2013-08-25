filtRT  <- function(dt, RTidx=NULL, vars=NULL, fpass=c(200,1500), sdv=NULL ){
#   A function to filter reaction time (RT) data.
#   Take as input :
#      1. dt = a data frame in long format
#      2. RTidx = the column number where to find the RT data
#      3. vars = a vector of name of variables to filter by condition 
#          usually subjects and at least one dependent variable
#      4. fpass = a vector of 2 values for the lowest and highest accepted RT 
#      5. sdv = the number of standard deviation to use in the filter by condition
#
# GT Vallet    --  Lyon 2 University
#   2013/07/01 --  v01
  
  source("rscripts/Outliers.R")
  require("plyr")

  dt.fil = dt
  if( !is.null(fpass) ){
    dt.fil = dt[ dt[,RTidx]>fpass[1] & dt[,RTidx]<fpass[2], ]  
  }

  if( !is.null(sdv) ){
    dt.fil = ddply(dt.fil, vars, function(x) Outliers(x,RTidx,sdv)) 
  }

  return(dt.fil)
}
