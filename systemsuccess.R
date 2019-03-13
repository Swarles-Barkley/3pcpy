systemsuccess<-function(expTime, timeout, failProb, permaFailChance, quorumThreshold, nodes, retrythresh){
  phasethresh = retrythresh
  phaseretry = 0
  lambda = 1/expTime
  times = rexp(nodes, lambda)
  nodeWeights = rep(1,nodes)
  threshold = quorumThreshold
  failures = lolrly(failProb, nodes)
  permaFailures = lolrly(permaFailChance,nodes)
  #canCommit
  tmpbool = lolrly(permaFailChance,1)
  if(isTRUE(tmpbool)){
    return(FALSE)
  }
  tmp = phasesuccess(times, timeout, failProb, permaFailures, threshold,nodeWeights)
  while(isFALSE(tmp) && phaseretry<phasethresh){
    failures = lolrly(failProb, nodes)
    times = rexp(nodes, 0.5) # 1/0.05=20
    tmp = phasesuccess(times, timeout, failProb, permaFailures, threshold,nodeWeights)
    phaseretry = phaseretry + 1
  }
  if(phaseretry==phasethresh && isFALSE(tmp)){
    return(FALSE)
  }
  
  #preCommit
  
  phaseretry = 0
  failures = lolrly(failProb, nodes)
  times = rexp(nodes, 0.5) # 1/0.05=20
  tmp = phasesuccess(times, timeout, failProb, permaFailures, threshold,nodeWeights)
  while(isFALSE(tmp) && phaseretry<phasethresh){
    failures = lolrly(failProb, nodes)
    times = rexp(nodes, 0.5) # 1/0.05=20
    tmp = phasesuccess(times, timeout, failProb, permaFailures, threshold,nodeWeights)
    phaseretry = phaseretry + 1
  }
  if(phaseretry==phasethresh && isFALSE(tmp)){
    return(FALSE)
  }
  #Commit
  phaseretry=0
  tmpbool = lolrly(failProb,1)
  while(isTRUE(tmpbool) && phaseretry<phasethresh){
    tmpbool = lolrly(failProb,1)
    if(isFALSE(tmpbool)){
      return(TRUE)
    }
    phaseretry = phaseretry+1
  }
  return(TRUE)
  
}