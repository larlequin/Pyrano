## Summarizes data, handling within-subjects variables by removing inter-subject variability.
## It will still work if there are no within-S variables.
## Gives count, un-normed mean, normed mean (with same between-group mean),
##   standard deviation, standard error of the mean, and confidence interval.
## If there are within-subject variables, calculate adjusted values using method from Morey (2008).
##   data: a data frame.
##   dv: the name of a column that contains the variable to be summariezed
##   between: a vector containing names of columns that are between-subjects variables
##   within: a vector containing names of columns that are within-subjects variables
##   wid: the name of a column that identifies each subject (or matched subjects)
##   na.rm: a boolean that indicates whether to ignore NA's
##   conf.interval: the percent range of the confidence interval (default is 95%)
summarySEwithin <- function(data = NULL, dv, between = NULL, within = NULL,
                            wid = NULL, na.rm = FALSE, conf.interval = .95, 
                            .drop = TRUE) {
  
  source("rscripts/summarySE.R")
  source("rscripts/normDataWithin.R")
  
  # Ensure that the between and within are factors
  factorvars <- vapply(data[, c(between, within), drop = FALSE],
                       FUN = is.factor, FUN.VALUE = logical(1))
  
  if (!all(factorvars)) {
    nonfactorvars <- names(factorvars)[!factorvars]
    message("Automatically converting the following non-factors to factors: ",
            paste(nonfactorvars, collapse = ", "))
    data[nonfactorvars] <- lapply(data[nonfactorvars], factor)
  }
  
  # Get the means from the un-normed data
  datac <- summarySE(data, dv, groupvars=c(between, within),
                     na.rm = na.rm, conf.interval = conf.interval, 
                     .drop = .drop)
  
  # Drop all the unused columns (these will be calculated with normed data)
  datac$sd <- NULL
  datac$se <- NULL
  datac$ci <- NULL
  
  # Norm each subject's data
  ndata <- normDataWithin(data, wid, dv, between, na.rm, .drop = .drop)
  
  # This is the name of the new column
  dv_n <- paste(dv, "_norm", sep = "")
  
  # Collapse the normed data - now we can treat between and within vars the same
  ndatac <- summarySE(ndata, dv_n, groupvars = c(between, within),
                      na.rm = na.rm, conf.interval = conf.interval, .drop = .drop)
   
  # Apply correction from Morey (2008) to the standard error and confidence interval
  #  Get the product of the number of conditions of within-S variables
  nWithinGroups    <- prod(vapply(ndatac[,within, drop = FALSE], FUN = nlevels,
                                  FUN.VALUE = numeric(1)))
  correctionFactor <- sqrt( nWithinGroups / (nWithinGroups-1) )
  
  # Apply the correction factor
  ndatac$sd <- ndatac$sd * correctionFactor
  ndatac$se <- ndatac$se * correctionFactor
  ndatac$ci <- ndatac$ci * correctionFactor
  
  # Combine the un-normed means with the normed results
  merge(datac, ndatac)
}
