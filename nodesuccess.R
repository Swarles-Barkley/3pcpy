nodesuccess<-function(time, timeout, otherfailure){
  #print(typeof(otherfailure))
  if(isTRUE(otherfailure) | (time>timeout)){
    failedmsgs <<- failedmsgs+1
    #print("node failed")
    return(FALSE)
  }
  return(TRUE)
}