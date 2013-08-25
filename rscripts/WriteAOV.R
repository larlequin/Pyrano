WriteAOV  <- function(fname, anova, data=NULL, posthoc=NULL){
#
#   A function to write the results of an ANOVA conducted with the ez package
#   Take the file name, the ez anova object and possibly the post-hoc analyses
#
#   Write a csv (sep = ;) file with the ANOVA, the Mauchly test if significant and 
#     the post-hoc results
#  
# GT Vallet - Lyon 2 University 
# 2013/04/18 - v01
  
  if( length(anova)>1 ){ 
    if( length(anova[[2]][1,])>3){
      spher=T
    }else{
      spher=F
    }
  }else{ 
    spher=F
  }
  # format the dataframes to round the numbers
  anova[[1]][,c(4:5,7)]  <- round(anova[[1]][,c(4:5,7)], digits=2)
  if( length(anova)>1 & spher ){
    anova[[2]][,c(-1,-4)] <- round(anova[[2]][,c(-1,-4)], digits=2)
    anova[[3]][,c(2:3,5:6)] <- round(anova[[3]][,c(2:3,5:6)], digits=2)
  }
  # open the file and write the ANOVA table
  f  <- file(fname, open="w")
  writeLines("ANOVA\n", con=f)
  write.table(format(as.matrix(anova[[1]], digits=2)), sep=';', file=f, quote=F, na="", append=T, col.names=NA)  
  # write the Mauchly test and the corrected ANOVA table only if Mauchly is significant
  if( length(anova)>1 & spher ){
      writeLines("\n\nTest de Mauchly; (sphéricité)\n", con=f)
      write.table(format(as.matrix(anova[[2]], digits=2)), sep=';', file=f, quote=F, na="", append=T, col.names=NA)
      writeLines("\n\nANOVA corrigée\n", con=f)
      write.table(format(as.matrix(anova[[3]], digits=2)), sep=';', file=f, quote=F, na="", append=T, col.names=NA)
  }
  # write data's means and standard deviation if such a table is provided
  if( !is.null(data) ){
    writeLines("\n\nStats", con=f)
    write.table(format(as.matrix(data[], digit=2)), sep=';', file=f, quote=F, na="", append=T, col.names=NA)
  }
  # write the post-hoc results if such results are provided
  if( !is.null(posthoc) ){
    writeLines(paste("\n\nPost-hoc; (", posthoc$p.adjust.method, ")\n", sep=''), con=f)
    write.table(round(posthoc$p.value, digits=2), sep=';', file=f, quote=F, na="", append=T, col.names=NA)
  }
  # close the file
  close(f)   
  
}
