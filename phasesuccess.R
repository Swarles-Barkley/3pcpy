phasesuccess<-function(timeDistro, timeout, failureProb, permaFails, quarumThreshold, nodeWeights){
  nodefailures = 0.0
  failureDistro = lolrly(avgFailChance, nodes)
  for(i in 1:length(timeDistro)){
    failureDistro[i] = (failureDistro[i] || permaFails[i])
  }
  for(i in 1:length(timeDistro)){
    tmpbool = nodesuccess(timeDistro[i], timeout, failureDistro[i])
    if(isFALSE(tmpbool)){
      #return(FALSE)
      nodefailures = nodefailures+(1*nodeWeights[i])
    }
  }
  #tmpbool = lolrly(failureProb, 1)
  #if(isTRUE(tmpbool)){
  #  return(FALSE)
  #}
  if(nodefailures>=quarumThreshold){
    return(FALSE)
  }
  return(TRUE)
}