nodeWeighter<-function(failures, maxFailures){
  if(failures>=maxFailures){
    return(0)
  }
  return(1-(failures/maxFailures))
}