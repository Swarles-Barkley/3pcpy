genTimeout<-function(tmpProb, maxBackoff){
  failures = 0
  for(i in 1:200){
    #tmpFail = lolrly(tmpProb,1)
    tmpFail = rbern(1,tmpProb)
    if (isTRUE(tmpFail)){
      failures = failures+1
    }else{
      failures = 0
    }
  }
  backoff = (2^failures)-1
  if(backoff>maxBackoff){
    backoff = maxBackoff
  }
  return(backoff)
}