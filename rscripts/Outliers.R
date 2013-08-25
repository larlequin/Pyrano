Outliers  <- function(data, target, sdv){
#
#   A function to keep only the RT value within 'sdv' standard deviations from the mean.
#      Take a matrix of data 'data', the column number where are the RT values and the number of standard deviation to consider
#
#   The function will compute the high and low cut-off scores based on this formula
#            cut-off = mean +/- standard deviation.
#
#   Return the matrix with only the good RT values.
#  
# GTV and BR - 13/10/2011 - v01
ndt  <- nrow(data)
  
mean_cond  <- mean(data[,target], na.rm=T)   # Compute the mean of the matrix
std_dev    <- sd(data[,target], na.rm=T)     # Compute the standard deviation of the matrix

cut_off_high  <- mean_cond + sdv*std_dev  # Compute the high cut-off score
cut_off_low   <- mean_cond - sdv*std_dev  # Compute the low cut-off score

# Find RT values within the two cut-off scores
temp  <- which( data[,target]< cut_off_high & data[,target]> cut_off_low )
data  <- data[temp,]
data["pFilter"]  <- round((ndt-nrow(data))/ndt, 3)

return(data)

}