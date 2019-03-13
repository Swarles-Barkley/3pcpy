systemsuccess<-function(expTime, timeout, failProb, quorumThreshold, nodes, retrythresh){
  phasethresh = retrythresh
  phaseretry = 0
  lambda = 1/expTime
  times = rexp(nodes, lambda)
  nodeWeights = rep(1,nodes)
  threshold = quorumThreshold
  failures = lolrly(failProb, nodes)
  
  #canCommit
  tmpbool = lolrly(failProb,1)
  if(isTRUE(tmpbool)){
    return(FALSE)
  }
  tmp = phasesuccess(times, timeout, failures,threshold,nodeWeights)
  while(isFALSE(tmp) && phaseretry<phasethresh){
    failures = lolrly(failProb, nodes)
    times = rexp(nodes, 0.5) # 1/0.05=20
    tmp = phasesuccess(times, timeout, failures,threshold,nodeWeights)
    phaseretry = phaseretry + 1
  }
  if(phaseretry==phasethresh && isFALSE(tmp)){
    return(FALSE)
  }
  
  #preCommit
  tmpbool = lolrly(failProb,1)
  if(isTRUE(tmpbool)){
    return(FALSE)
  }
  phaseretry = 0
  failures = lolrly(failProb, nodes)
  times = rexp(nodes, 0.5) # 1/0.05=20
  tmp = phasesuccess(times, timeout, failures,threshold,nodeWeights)
  while(isFALSE(tmp) && phaseretry<phasethresh){
    failures = lolrly(failProb, nodes)
    times = rexp(nodes, 0.5) # 1/0.05=20
    tmp = phasesuccess(times, timeout, failures,threshold,nodeWeights)
    phaseretry = phaseretry + 1
  }
  if(phaseretry==phasethresh && isFALSE(tmp)){
    return(FALSE)
  }
  #Commit
  tmpbool = lolrly(failProb,1)
  if(isTRUE(tmpbool)){
    return(FALSE)
  }
  return(TRUE)
  
}