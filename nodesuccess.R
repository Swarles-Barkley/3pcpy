nodesuccess<-function(time, timeout, otherfailure){
  #print(typeof(otherfailure))
  if(isTRUE(otherfailure) | (time>timeout)){
    return(FALSE)
  }
  return(TRUE)
}